__author__ = 'mikey'

from faceLib import *
from pickle import *
from datetime import *
import os
import sys
#from IPython import *

import time

#TODO may want to duplicate the global hash in case of problems.
users = []
passes = []

def read_user_file():
    global users
    global passes
    file = open("users",'r+')
    for line in file.readlines():
        U_P = line.split(":")
        users += [U_P[0].replace("\n","")]
        passes += [U_P[1].replace("\n","")]

    print users
    file.close()
    #print users
    #print passes


def printGroupsToCheck(d):
    f = open("group_ids.txt","r+")
    groups = []
    TOKEN = getToken(d)
    for id in f.readlines():
        id = id.replace("\n","")
        print "ID: " +  id + ":" + "name " + str(getIdsByAccount(d,TOKEN,id).encode("utf-8"))
    f.close()


    f.close()
    return groups

def getGroupsToCheck(restartOn):
    f = open("group_ids.txt","r+")
    groups = []
    for id in f.readlines():

        #TODO CHECK THIS TWO LINES WORK
        idandName = id.split(":")
        id = idandName[0]

        id = id.replace("\n","")
        if(restartOn):
            groups += [id]
            continue

        try:
            file = open("accounts\\accounts_" + id + ".txt","r")
            #print "ERROR a file for " + id + " already made"
            f.close()
        except:
            groups += [id]

    f.close()
    return groups

def getGroupMembers(d, group_id_list):
    # IDF different IDs
    #works will be a list of new group ids to add to hash list.
    #works = ["216260441885304","261416140609043","277156988971707"]
    #tryLogin(d,users[0],passes[0])
    res = []
    hash = {}

    query =  "/members"
    count = 0
    for work in group_id_list:
        print "analyzing" + str(count) + "/" + str(len(group_id_list))
        #if we want to change users this is the spot
        try:
            sourceRes = getSourceByQuery(d, work, query, "string")
            namesRes = getNamesFromSource(sourceRes, "accounts\\accounts_" + work +".txt")
            print namesRes
            updateHash(namesRes.split("\n"),work)
        except:
            print "NOTICE "+ work + " has failed " + "you should delete it's accounts file.."

        #exitLogin(d)
        #count += 1
        #tryLogin(d,users[count % (len(users))],passes[count% (len(passes))])



        #for name in namesRes:
         #   if name not in res:
          #      res.insert(0, name.strip())

    #resFile = open(output, "w+")
    #resFile.write("\n".join(res))
    #resFile.close()



#read_user_file()
#getGroupMembers(d,"somthing")

def printHash(fromHash):
#    f = open("global_hash","r+")
#    hash = load(f)

    sortedList = sorted(fromHash.items(), key=lambda x:x[1][0],reverse=True)
    return sortedList

#def buildCSV(output):
#    f = open(output,"w+")
#    f = open("global_hash","r+")
#    hash = load(f)
#    res = ""
#    for i in hash.itervalues():
#        res += i[0] + ","
#        for name in i[1]:
#            res += name


def updateHash(names,group_id):
    found = False
    f = open("global_hash","r+")
    hash_value = []
    hash = load(f)
    f.close()
    #print hash
    for name in names:
        hash_value = hash.get(name,[0])

        #see if group allready counted
        for group in hash_value[1:]:
            if(group == group_id):
                found = True

        #if not then add it
        if(found == False):
            hash_value[0] += 1
            hash_value += [group_id]
            hash.update({name:hash_value})

    f = open("global_hash","r+")
    dump(hash,f)
    f.close()
    #print hash


def createCSV(name,fromHash):
    hash = printHash(fromHash)

    output = ""
    print "creating CSV file may take a while (or not i have no idea)..."

    for line in hash:
        if(line[0] == ""):
            allGroups = sorted(line[1][1:])
            break

    for line in hash:

        #number of groups
        param_list = str(line[1][0]) + ","

        #sort groups
        count = 0
        sortedGroups = sorted(line[1][1:])

        index = 0
        if(len(sortedGroups) != 0):
            for group in allGroups:
                if(group != sortedGroups[index]):
                    param_list += ","
                else:
                    param_list += str(group) + ","
                    index += 1
                    if(index == len(sortedGroups)):
                        break

        fullLine = line[0] + "," + param_list + "\n"

        if(line[0] == ""):
            output = fullLine + output
        else:
            output = output + fullLine

    fileName = name + ".csv"
    f = open(fileName, "w+")
    f.write(output)
    f.close()

def initHash():
    f = open("global_hash","r+")
    hash = {"":[0]}
    dump(hash,f)
    f.close()


def restart(d):
    initHash()
    groups = getGroupsToCheck(True)
    getGroupMembers(d,groups)
    createCSV("CSV\\MainHash_" + datetime.strftime(datetime.today(),"%d_%m_%y#%H-%M"),getHash())

def getHash():
    f = open("global_hash","r+")
    hash = load(f)

    sortedList = sorted(hash.items(), key=lambda x:x[1][0],reverse=True)
    f.close()
    return hash

def deleteGroup(id):
    hash = getHash()
    for line_value in hash.itervalues():
        count = 0
        for group in line_value[1:]:
            if(group ==  id):
                count += 1
                line_value.remove(id)

        line_value[0] -= count

    f = open("global_hash","r+")

    backup = open("./backup/Back_up_global_hash_" + datetime.strftime(datetime.today(),"%d_%m_%y#%H-%M"),"w+")
    dump(getHash(),backup)
    backup.close()

    dump(hash,f)
    f.close()

    os.remove("accounts\\accounts_" + id + ".txt")

def getIdsByAccount(d,ACCESS_TOKEN,id):
    #get Token from server.
    g = facebook.GraphAPI(ACCESS_TOKEN)
    args = {'fields' : 'id,name', }

    try:
        id = g.get_object(id, **args)
        return id.get("name")
    except:
        print "not existing ID"

    return id


def getGroupIdByQuery(d,query_arg, groupName):

    addr = "https://www.facebook.com/search/" + query_arg + groupName


    d.get(addr)
    sleep(1)


    h = d.page_source.encode("utf8")
    index = h.find('data-bt="{&quot;id&quot;:')
    endIndex = h[index:].find(',&quot;rank&quot;:')
    return h[index+26:index+endIndex-1]
    #return h


    #return d.page_source.encode("utf8")


#d = webdriver.Chrome()
#tryLogin(d,"mdstrauss91@gmail.com","boogybar91")

'''
groups = getGroupsToCheck(False)
print groups
getGroupMembers(d,groups)
printCSV()'''

'''d = webdriver.Chrome()
tryLogin(d,"mdstrauss91@gmail.com","boogybar91")
groups = getGroupsToCheck(True)
print groups
getGroupMembers(d,groups)
printCSV()'''


def readGroupsAndGetIds(d,input):
    inFile = open(input,"r+")
    outFile = open(input+"_with_ids.txt","w+")
    for line in inFile.readlines():
        id = getGroupIdByQuery(d,"more/?q=",line.strip())
        print id
        outFile.write(id+":"+line.strip()+"\n")

    inFile.close()
    outFile.close()

#    except:
 #       print "ERROR IN readGroupsAndGetIds"


def getGroupsList(d,inputFile,outFileName):

    inFile = open(inputFile,"r+")


    for line in inFile.readlines():
        id = line.decode('utf8')
		

		
        source = getSourceByQuery(d,"str/"+ id , "/keywords_groups?ref=top_filter","string")
        #embed()
        outFile = open(outFileName,"a+")
        outFile.write("\r\n\r\n #############    ")
        outFile.write(id.encode("utf-8").strip())
        outFile.write("    ############# " + "\n\n")
        result = getGroupNamesFromSource(source,"string")
        outFile.write(result)
        outFile.close()

    inFile.close()



def getGroupNamesFromSource(sourceFile, output):

    try:
        f = open(sourceFile, "r")
        lines = f.read().decode('utf8')
    except:
        #sendLog("getNamesFromSource got string and not file.")
        lines = sourceFile


    res = ""

    start = 0
    count = 0

    # if not found, don't do work...
    if ("Sorry" not in lines) and ("Bing Privacy Policy" not in lines) or True:

        subS = '<div class="_gll"'
        subE = '</a></div></div>'

        while (True):
            start = lines.find(subS, start)
            if (start == -1): break
            start += len(subS)
            end = lines.find(subE, start) - 1
            if lines[start:end].strip() != "":
                startGroupId = start+len('><a href="/groups/')
                endGroupId = lines[startGroupId:end].find('/?ref=br_rs')
                groupId = lines[startGroupId:startGroupId + endGroupId]

                startGroupName = startGroupId + endGroupId + len('/?ref=br_rs<"')
                groupName =  lines[startGroupName:end]

                res += groupId + ":" + groupName + "\n"
                #print groupId.encode("utf-8") + ":" + groupName.encode("utf-8") + "\n"
            start = end
            count = count + 1

    errorString = "getGroupNamesFromSource Finished for " + sourceFile + ", Count: " + str(count)
    #print errorString
    #sendLog(errorString)


    if output == "string":
        return res
    else:
        try:
            resFile = open(output, "w+")
            resFile.write(res).decode("utf8")
            resFile.close()
            return res
        except:
            pass

def filterOutId(name):
    if(name.find("profile")!=-1):
        subS="id="
        subE="&amp"
        start = name.find(subS, 0)
        start += len(subS)
        end = name.find(subE, start)
        return name[start:end]

    return name

def getNamesFromMutalFormSource(sourceFile, output):

    try:
        f = open(sourceFile, "r")
        lines = f.read().decode('utf8')
    except:
        #sendLog("getNamesFromSource got string and not file.")
        #print "not a file"
        lines = sourceFile

    res = ""

    start = 0
    count = 0

    # if not found, don't do work...
    if ("Sorry" not in lines) and ("Bing Privacy Policy" not in lines):

        subS = '<div class="_6a _6b"><div class="fsl fwb fcb"><a href="https://www.facebook.com/'
        subE = 'fref=pb'



        while (True):
            start = lines.find(subS, start)

            if (start == -1): break

            start += len(subS)
            end = lines.find(subE, start) - 1

            if lines[start:end].strip() != "":
                name = lines[start:end]
                name = filterOutId(name)
                res += name.strip() + "\n"
                print name.strip()

            start = end
            count = count + 1

    errorString = "getNamesFromMutalFormSource Finished for " + sourceFile + ", Count: " + str(count)
    #print errorString
    #sendLog(errorString)


    if output == "string":
        return res
    else:
        try:
            resFile = open(output, "w+")
            resFile.write(res).decode("utf8")
            resFile.close()
            return res
        except:
            pass

def areFriends(d):
    try:
        a = d.find_element_by_class_name("fbProfileBylineLabel")
        if(a.text.find("Facebook friends since") != -1): 
			return 'y'
        return 'n'
    except:
        return 'n'

def getMutalFriendSource(d, id_arg, member, output):


    #addr =  "https://www.facebook.com/" + id_arg + "/friends?and=" + member
    addr =  "https://www.facebook.com/friendship/" + id_arg + "/" + member
    print addr
    countScroll = 0
    isFriend='n'
    try:
        d.get(addr)
        isFriend = areFriends(d)
        a = d.find_element_by_partial_link_text("mutual")
        d.get(a.get_attribute("href"))
    except:
        print "no mutual friends"
        return "",isFriend


    # Loop exits when end of results string is in the source
    while ("End of results" not in d.page_source) and ("Sorry" not in d.page_source) and ("Bing Privacy Policy" not in d.page_source):
        sourceSample = d.page_source
        d.execute_script("window.scrollBy(0,10000)", "")
        if(sourceSample == d.page_source):
            #print "done scrolling"
            break


    # Write output to file
    if output == "string":
        return d.page_source.encode("utf8"),isFriend
    else:
        f = open(output, "w+")
        f.write(d.page_source.encode("utf8"))
        f.close()


def getIdtoGroupConnection(d, userName, groupMembersListFile,groupId, output):
    # We need to remove id_arg once we have a naming standard (so I can extract the ID)
    # Open ids file
    res = ""
    userList = []

    try:
        f = open(groupMembersListFile, "r")
        lines = f.readlines()
        f.close()
    except:
        sendLog("got string and not file parsing as list of ids.")
        lines = groupMembersListFile.split(" ")


    #TODO chenge members and temp file
    #TODO chenge members and temp file
    count  = 0
    userCount = 0
    stringRes = ""
    countMembers = 0
    isMemberAFriend = "n"
    for member in lines:

        print "parsing " + str(countMembers) + "/" + str(len(lines))
        countMembers += 1

        if(count % 10 == 9):
            print "Changing user (should save to temp file..TODO)"
            exitLogin(d)
            #d.quit()
            #d = webdriver.Chrome()
            userCount += 1
            tryLogin(d,users[userCount% len(users)],passes[userCount% len(users)])
            count = 0

        count += 1

        member = filterOutId(member)
        if (userName.split("\n") == member.strip("\n")):
            continue
        
        source,isMemberAFriend = getMutalFriendSource(d,userName,member,"string")


        if (source.find("Sorry, this page isn't available") != -1):
            print "page not available"
            continue

        res = getNamesFromMutalFormSource(source,"string")
        returnList = res.split("\n")
		
        if(isMemberAFriend == "y"):
            print "are friends ################"
            returnList += [member.strip()]
		
        stringRes += member.strip() + ",,"
        if (res != ""):
            for name in returnList:
                stringRes += name + ","

        stringRes = stringRes[:-1] + "\n"
        userList = list(set(userList + returnList))

    fileName = "mutalFriendFiles\\mutal_"+ userName + "_with_group_" + groupId
	
    mutalFile = open(fileName + "_FULL_LIST" +".csv ",'w+')
    mutalFile.write(stringRes)
    mutalFile.close()
	
    friendsListFileName = "friendsList\\"+userName+"_with_group_"+groupId+".txt"
    friendsListFile = open(friendsListFileName,'w+')

    hash = getHash()
    mutalFriendHash = {}

    for name in userList:
        try:
            print name
            friendsListFile.write(name)
            friendsListFile.write("\n")
            mutalFriendHash.update({name:hash[name.strip()]})
        except:
            if(name.isdigit()):
                try:
				    mutalFriendHash.update({name:hash["profile.php?id="+name.strip()+"&amp"]})
                except:
				    pass
            pass

    friendsListFile.close()
    print fileName
    # CSV all mutual friends with <group> users and get from there group lists that there are members of.
    #print mutalFriendHash
    createCSV(fileName,mutalFriendHash)

    #createCSV("testing123")

    # Write to file
    if output == "string":
        return userList
    else:
        print "do nothing for now"
        resFile = open(output,'w+')
        resFile.write(res)
        #resFile.close()



def moveGroupIds(inputFile, outputFile):
    f = open(inputFile, "r")
    lines = f.readlines()
    f.close()

    f = open(outputFile,"w")

    for line in lines:
        end = line.find(":")
        if(end != -1) and line[:end].isdigit():
            f.write(line[:end])
            f.write("\n")

    f.close()

def outputIdToGroupConnection(id_arg, nameList):
    print "nothing yet."


def printHelp():
    print "USAGE: "
    print " groups_crawler.py run"
    print " groups_crawler.py delete [GROUP ID]"
    print " groups_crawler.py reboot"
    print " groups_crawler.py keywordSearch [keyword file] [output file]"
    print " groups_crawler.py userToGroupConnection [username] [groupId]"

if __name__  == "__main__":
    #print len(sys.argv)
    if(len(sys.argv) == 2):
            if(sys.argv[1] == "run"):
                read_user_file()
                groups = getGroupsToCheck(False)
                if(len(groups) != 0):
                    d = webdriver.Chrome()
                    tryLogin(d,users[0],passes[0])
                    getGroupMembers(d,groups)
                    createCSV("CSV\\MainHash_" + datetime.strftime(datetime.today(),"%d_%m_%y#%H-%M"),getHash())
                    d.quit()
            elif( sys.argv[1] == "reboot" ):
                read_user_file()
                d = webdriver.Chrome()
                tryLogin(d,users[0],passes[0])
                initHash()
                groups = getGroupsToCheck(True)
                getGroupMembers(d,groups)
                createCSV("CSV\\MainHash_" + datetime.strftime(datetime.today(),"%d_%m_%y#%H-%M"),getHash())
                d.quit()
            else:
                printHelp()
                exit()
    elif(len(sys.argv) == 3):
        if(sys.argv[1] == "delete" and sys.argv[2].isdigit()):
            deleteGroup(sys.argv[2])
            createCSV("CSV\\MainHash_" + datetime.strftime(datetime.today(),"%d_%m_%y#%H-%M"),getHash())
        elif(sys.argv[1] == "getGroupIds"):
            read_user_file()
            d = webdriver.Chrome()
            tryLogin(d,users[0],passes[0])
            readGroupsAndGetIds(d, sys.argv[2].strip())
            d.quit()
        else:
            printHelp()
            exit()

    elif(len(sys.argv) == 4 ):
        if(sys.argv[1] == "keywordSearch"):
            read_user_file()
            d = webdriver.Chrome()
            tryLogin(d,users[0],passes[0])
            getGroupsList(d,sys.argv[2],sys.argv[3])
        elif(sys.argv[1] == "userToGroupConnection"):
            read_user_file()
            d = webdriver.Chrome()
            tryLogin(d,users[0],passes[0])
            res = getIdtoGroupConnection(d,sys.argv[2],"accounts\\accounts_" + sys.argv[3] + ".txt",sys.argv[3],"string")
        else:
            printHelp()
            exit()


    else:
        printHelp()
        exit()
		
		
		
#mutual_friends/?uid=100000711298218&node=566265768