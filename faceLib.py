from selenium import *
from selenium import webdriver
import selenium.webdriver.remote.webelement
import facebook
import json
from time import sleep
import requests
from random import randrange
# ===========================================================================================
# ================================ FaceLib v2.0 by Mikey & Smoo =============================
# ===========================================================================================

# TODO: update bot with new funcs
# TODO: method of opening files for read is f***d up - DONE
# TODO: make everything send log! - Done (probably)
# TODO: file getters & setters - Done!!!

# ================================ Basic Funcs ==============================================


def getSourceByQuery(d, id, query_arg, output):
    '''
    if (username_arg != "" and password_arg != "" and id_arg != "" and query_arg != ""):
        username = username_arg
        password = password_arg
        id  = id_arg
        query = query_arg
    else:

        # Username & Pass
        username = "mdstrauss91@gmail.com"
        password = "googlygoo"

        # Enter object ID and Query

        id = "296245663755291"
        id = "179848418782690" #short one for demo
        query = "/employees/present"
    '''

    addr = "https://www.facebook.com/search/" + id + query_arg

    # Get page by query
    if(query_arg != "None"):
        d.get(addr)

    count = 0
    # Loop exits when end of results string is in the source
    while ("End of Results" not in d.page_source)  and ("Bing Privacy Policy" not in d.page_source): #and ("Sorry" not in d.page_source)
        sourceSample = d.page_source
        d.execute_script("window.scrollBy(0,10000)", "")
        count += 1
        if(sourceSample == d.page_source):
            break
       # if(count >= 700):
         #   break

    # Write output to file
    if output == "string":
        return d.page_source.encode("utf8")
    else:
        f = open(output, "w+")
        f.write(d.page_source.encode("utf8"))
        f.close()

    sendLog("getSourceByQuery Finished for " + id + "," + query_arg)

def filterOutId(name):
    if(name.find("profile")!=-1):
        subS="id="
        subE="&amp"
        start = name.find(subS, 0)
        start += len(subS)
        end = name.find(subE, start)
        return name[start:end]

    return name


def getNamesFromSource(sourceFile, output):

    try:
        f = open(sourceFile, "r")
        lines = f.read()
        f.close()
    except:
            #sendLog("getNamesFromSource got string and not file.")
        lines = sourceFile

    res = ""

    start = 0
    count = 0

    # if not found, don't do work...
    if ("Sorry" not in lines) and ("Bing Privacy Policy" not in lines) or True:

        # OLD subS = '<div class="_1zf"><div class="_zs fwb" data-bt="{&quot;ct&quot;:&quot;title&quot;}"><a href="https://www.facebook.com/'
        subS= '</div><div class="_gll"><div><a href="https://www.facebook.com/'
        subE = 'ref=br_rs'

        while (True):
            start = lines.find(subS, start)
            if (start == -1): break
            start += len(subS)
            end = lines.find(subE, start) - 1
            if lines[start:end].strip() != "":
                name =  lines[start:end]
                name = filterOutId(name)  + "\n"
                res += name
            start = end
            count = count + 1

    errorString = "getNamesFromSource Finished for " + sourceFile[:10] + ", Count: " + str(count)
    #print errorString
    #sendLog(errorString)

    if output == "string":
        return res
    else:
        try:
            resFile = open(output, "w+")
            resFile.write(res)
            resFile.close()
            return res
        except:
            pass

def getIdsByAccount(d,accountFile, output):
    #get Token from server.
    print "hello"
    ACCESS_TOKEN = getToken(d)
    print ACCESS_TOKEN
    g = facebook.GraphAPI(ACCESS_TOKEN)
    args = {'fields' : 'id,name', }

    try:
        f = open(accountFile, "r")
        lines = f.readlines()
        f.close()
    except:
        sendLog("getIdsByAccount got string and not file.")
        lines = []
        lines.insert(0,accountFile.encode("utf8"))

    hash = ()
    res = ""

    count = 0

    for line in lines:
        if (line.find("profile.php") == -1):
            try:
                id = g.get_object(line.strip(), **args)
            except:
                print "not existing   ID: ", line.strip()#, count
                continue
            if output == "hash":
                hash += (line.strip(),id.get("id"))
            else:
                res += id.get("id") + ":" + line.strip() + ":" + id.get("name") + "\n"
        else:
            found = line.find("id=")
            foundid = line[found+3:-5]
            if output == "hash":
                hash += (line.strip(),foundid)
            else:
                id = g.get_object(foundid, **args)
                res += foundid + ":" + line.strip() + ":" + id.get("name") + "\n"

        count = count + 1
        print line.strip(), id.get("name") #, count

    sendLog("getIdsByAccount Finished")
    print "[+] TOMER KING. really!!!!! <3"
    print res
    if output == "string":
        return res
    elif output == "hash":
        return hash
    else:
        resFile = open(output, "wb+")
        resFile.write(res.encode("utf-8"))
        resFile.close()

# ================================ Wrapper Funcs ============================================

def getIDFWorkersByAccount(d, id_arg, output):
    # IDF different IDs
    works = ["296245663755291","211528359010807","125249070831305","104217862948019","106084022763842","272938169387278","112287748796691","140282239320067"]

    res = []

    query = "/employees/present/" + id_arg + "/friends/intersect"

    for work in works:

        sourceRes = getSourceByQuery(d, work, query, "string")
        namesRes = getNamesFromSource(sourceRes, "string").split("\n")
        for name in namesRes:
            if name not in res:
                res.insert(0, name.strip())

    resFile = open(output, "w+")
    resFile.write("\n".join(res))
    resFile.close()




# https://www.facebook.com/zuck/friends?and=ChrisHughes -- new wat if finding mutal friends
def getMutualFriendsById(d, id_arg, idFile, output):
    # We need to remove id_arg once we have a naming standard (so I can extract the ID)
    # Open ids file
    try:
        f = open(idFile, "r")
        lines = f.readlines()
        f.close()
    except:
        sendLog("getMutualFriendsById got string and not file.")
        lines = idFile.split("\n")


    #build hash table
    length = len(lines)
    print "length"
    print length
    count = 0
    hash ={}
    hash2 = {}
    for line in lines:
        splitLIne = line.split(":")
        i = splitLIne[0].strip()
        a = splitLIne[1].strip()
        hash.update({a:i})
        hash2.update({i:a})
        count += 1

    print hash
    res = ""

    users = []
    passs = []

    # Loop all lines
    count = 0
    size = len(hash)
    for i in hash.itervalues():
        if(count < 420):
            count += 1
            continue
        print "getting friends" , count ,"/",size
        friendName = hash2[i]
        friendId = i

        if (count % 5 == 0):
            tempFile = open("tempFile_" + id_arg,"w+")
            tempFile.write(res)
            tempFile.close()
        if (count % 10 == 0):
            exitLogin(d)
            tryLogin(d,users[(count/10)%4],passs[(count/10)%4])



        # Build query
        query = "/friends/" + friendId + "/friends/intersect"


        # Run low-level funcs, output is string
        src = getSourceByQuery(d, id_arg, query, "string")
        names = getNamesFromSource(src, "string")
        print "NUMBER OF FRIENDS MUTUTAL:"
        print len(names.split("\n"))
        # Needs to be more efficient!

        res += friendId + ":" + friendName + "-"
        if (names != ""):
            for name in names.split("\n"):
                value = hash.get(name)
                if value != None:
                    res += name + ":" +  value + ","
        res = res[:-1] + "\n"

        count += 1
        sleep(randrange(0,1))
    sendLog("getMutualFriendsById Finished for " + id_arg)

    # Write to file
    if output == "string":
        return res
    else:
        resFile = open(output, "w+")
        resFile.write(res)
        resFile.close()

def getMutualFriendsById_SEARCHBAR(d, id_arg, idFile, output):

    d.get("http://www.facebook.com")

    # We need to remove id_arg once we have a naming standard (so I can extract the ID)
    # Open ids file
    try:
        f = open(idFile, "r")
        lines = f.readlines()
        f.close()
    except:
        sendLog("getMutualFriendsById got string and not file.")
        lines = idFile.split("\n")

    mainfriendNameDetails = getIdsByAccount(d,id_arg,"string")
    mainFriendName = mainfriendNameDetails.split(":")[2].strip("\n")

    #build hash table
    length = len(lines)
    count = 0
    hash ={}
    for line in lines:
        splitLine = line.split(":")
        #print splitLine
        #print splitLine[2].strip("\n")
        i = splitLine[0]
        a = splitLine[1]
        n = splitLine[2].strip()
        hash.update({a:[i,n]})
        count += 1

    res = ""

    # Loop all lines
    count = 0
    size = len(hash)
    for i in hash.itervalues():

        print "getting friends" , count ,"/",size
        friendName = i[1]
        print friendName
        #query = "friends of " + mainFriendName + " and " + friendName.decode('utf-8')

        #d.get("http://www.facebook.com")
        searchBar = d.find_element_by_class_name("_586i")
        searchBar.clear()
        searchBar.send_keys("friends of ")
        searchBar.send_keys(mainFriendName.decode('utf-8'))
        searchBar.send_keys(" and ")
        searchBar.send_keys(friendName.decode('utf-8'))
        sleep(1)
        searchBar.send_keys("\n")

        # Run low-level funcs, output is string
        src = getSourceByQuery(d, id_arg, "None", "string")
        names = getNamesFromSource(src, "string").strip()
        print "NUMBER OF MUTUAL FRIENDS:"
        print len(names)
        # Build query

        # Needs to be more efficient!
        if (names != ""):
            res += i[0] + "-" # not [1]??
            for name in names.split("\n"):
                name = name.encode('utf-8').strip()
                if name == "":
                    continue
                #print "name to find: " + name
                val =  hash.get(name)
                if val == None:
                    continue
                #print "value:"
                #print val
                #print "value[0]"
                #print val[0]
                value = val[0]
                if value != None:
                    res += name + ":" +  value + ","
            res = res[:-1] + "\n"

        count += 1
        sleep(randrange(5,10))
    sendLog("getMutualFriendsById Finished for " + id_arg)

    # Write to file
    if output == "string":
        return res
    else:
        resFile = open(output, "w+")
        resFile.write(res)
        resFile.close()

# ================================ Filter Funcs =============================================

def colorUnitByAccount(d, account, wordlist_arg):

    wordlist = wordlist_arg.decode('utf-8')
    units = wordlist.split(":")

    addr = "http://www.facebook.com/" + account
    d.get(addr)
    src = d.page_source

    myUnit = ""
    c = 0
    maxCount = 0

    for unit in units:
        c = src.count(unit)
        if c > maxCount:
            maxCount = c
            myUnit = unit

    return myUnit

def getUnits(d, idFile, wordlist, output):
    try:
        f = open(idFile, "r")
        lines = f.readlines()
        f.close()
    except:
        sendLog("getUnits got string and not file.")
        lines = idFile.split("\n")

    res = ""

    for line in lines:
        account = line.split(":")[1]
        print "Searching unit for: " + account
        u = colorUnitByAccount(d, account, wordlist)
        if u != "":
            print " -> FOUND! " + u
            res += account + ":" + u + "\n"

    # Write to file
    if output == "string":
        return res
    else:
        resFile = open(output, "w+")
        resFile.write(res.encode("utf-8"))
        resFile.close()

def getLivesIn2(d, account):
    addr = "http://www.facebook.com/" + account + "/about"
    d.get(addr)

    src = d.page_source
    res = ""

    # Cut Float Perimeter
    src = src[src.find("Places Lived"):src.find("Basic Information")]

    if src == "" or src.count("Ask for ") > 1:
        return res

    afterName = src.find('</a></div><div class="aboutSubtitle fsm fwn fcg">')

    new = src[:afterName]
    arr = new.split(">")
    res = arr[len(arr)-1]

    print "[+] " + account + " Lives in " + res

    sleep(1)
    return res



# ======================== Replace Old Versions ===================================
def runFilterWithParam(d, sourceFile, filter_func, param, output):

    # Open source file
    try:
        f = open(sourceFile, "r")
        lines = f.readlines()
        f.close()
    except:
        sendLog("runFilter got string and not file.")
        lines = sourceFile.split("\n")

    res = ""

    func =None
    for fil in filterList:
        if fil == filter_func:
            print fil
            print filterList[fil]
            func = filterList[fil]

    if(func == None):
        sendLog("no filter found")
        raise NameError

    # filter lines by filter_func (boolean)
    arr = filter(lambda x: func(d, x, param), lines)

    res += "".join(arr)
    # There are already \n for some reason...

    sendLog("runFilter Finished for " + sourceFile + str(filter_func))

    # Write to file
    if output == "string":
        return res
    else:
        resFile = open(output, "w+")
        resFile.write(res)
        resFile.close()

def boolLivesInSamePlace(d, account, place):
    r = getLivesIn2(d, account.split(":")[1])

    if r == place:
        print " -> TRUE!"
        return True
    else:
        print " -> FALSE!"
        return False

def runFilterWithParam(d, sourceFile, filter_func, param, output):

    # Open source file
    try:
        f = open(sourceFile, "r")
        lines = f.readlines()
        f.close()
    except:
        sendLog("runFilter got string and not file.")
        lines = sourceFile.split("\n")

    res = ""

    func =None
    for fil in filterList:
        if fil == filter_func:
            print fil
            print filterList[fil]
            func = filterList[fil]

    if(func == None):
        sendLog("not filter found")
        raise NameError

    # filter lines by filter_func (boolean)
    arr = filter(lambda x: func(d, x, param), lines)

    res += "\n".join(arr)

def getLivesIn(d, account):

    addr = "http://www.facebook.com/search/" + account + "/friends"
    d.get(addr)

    src = d.page_source
    res = ""

    # Cut Float Perimeter
    src = src[src.find('<div class="_69_ rfloat _ohf" role="complementary">'):]

    # There are number of matching expressions...
    # Last is the most informative
    expList = ["From <","Lives in <"]

    for exp in expList:
        foundExp = src.find(exp)
        if foundExp != -1:
            foundBr = src[foundExp:].find(">")
            start = foundExp + foundBr + 1

            startStr = src[start:]
            end = start + startStr.find("<")

            # Finds last Match!
            res = src[start:end]

    return res

def boolLivesInSamePlace(d, account, place):
    r = getLivesIn(d, account.split(":")[0])

    if r == place:
        return True
    else:
        return False

def getProfilePageSource(d, account_arg, content_arg, output):
    # Requires account name, not id!

    # If gives only name, won't split :)
    name = account_arg

    # /info || /groups || /events
    addr = "https://www.facebook.com/" + name + content_arg
    print addr
    d.get(addr)

    # 1000 scrolls is enough, no way to know when finished - very nor predictable
    for i in range(0,1000):
        d.execute_script("window.scrollBy(0,30)", "")

    sendLog("getProfilePageSource Finished for " + account_arg)

    # Write output to file
    if output == "string":
        return d.page_source.encode("utf8")
    else:
        f = open(output, "w+")
        f.write(d.page_source.encode("utf8"))
        f.close()

    print "[+] getProfileSource Finished for " + account_arg

def getAttributeFromSource(sourceFile, attr):
    # Open source file
    try:
        f = open(sourceFile, "r")
        lines = f.read()
        f.close()
    except:
        sendLog("getAttributeFromSource got string and not file.")
        lines = sourceFile

    res = ""

    subS = '<th class="_3sts">' + attr + '</th><td class="_480u"><div class="clearfix"><div>'
    subE = '</div></div>'

    start = lines.find(subS)
    if (start != -1):
        start += len(subS)
        end = lines.find(subE, start) - 1
        res += lines[start:end]

    sendLog("getAttributeFromSource Finished for " + sourceFile + attr)

    return res

def getSentencesfromSource(d, sourceFile, wordsList, output):
    # Open wordsList file
    try:
        f = open(wordsList, "r")
        words = f.readlines()
        f.close()
    except:
        sendLog("getSentencesfromSource got string and not file.")
        words = wordsList.split("\n")

    # Open source file
    try:
        f = open(sourceFile, "r")
        lines = f.readlines()
        f.close()
    except:
        lines = sourceFile

    res = ""

    for word in words:

        start = 0
        while (True):
            start = lines.find(">", start)
            if (start == -1): break
            end = lines.find("<", start)
            if (end == -1): break
            sentence = lines[start + 1:end]
            if sentence.find(word) != -1:
                res += sentence + "\n"
            start = end

    sendLog("getSentencesfromSource Finished for " + sourceFile)

    # Write to file
    if output == "string":
        return res
    else:
        resFile = open(output, "w+")
        resFile.write(res)
        resFile.close()

def exampleBoolFilter(d, account):
    return True

def runFilter(d, sourceFile, filter_func, output):

    # Open source file
    try:
        f = open(sourceFile, "r")
        lines = f.readlines()
        f.close()
    except:
        sendLog("runFilter got string and not file.")
        lines = sourceFile.split("\n")

    res = ""

    func =None
    for filter in filterList:
        if filter[0] == filter_func:
            func = filter[1]

    if(func == None):
        sendLog("not filter found")
        raise NameError

    # filter lines by filter_func (boolean)
    arr = filter(lambda x: func(d, x), lines)

    res += "\n".join(arr)

    sendLog("runFilter Finished for " + sourceFile + str(filter_func))

    # Write to file
    if output == "string":
        return res
    else:
        resFile = open(output, "w+")
        resFile.write(res)
        resFile.close()

# ================================ Misc. Funcs ==============================================

def exitLogin(d):
    try:
        #logout = d.find_element_by_id("userNavigationLabel")
        #logout.click()

        #sleep(1)
        #logout_b = d.find_element_by_link_text("Log Out")
        #logout_b.click()

        d.delete_all_cookies()
        d.get("https://www.facebook.com")
        sleep(1)
    except:
        sendLog("could not EXIT")

def tryLogin(d,username,password):
    try:
        print "user: "+username + " pass: " + password
        login(d,username,password)
    except:
        try:
            #SendKeys("%+")
            #raise NameError

            #sleep(2)
            #SendKeys("mdstrauss91")
            #login(d,username,password)

            '''SendKeys("%+")
            d.get("https://www.facebook.com")
            SendKeys("mdstrauss91")

            passElem = d.find_element_by_id("pass")
            buttonElem = d.find_element_by_id("u_0_n")

            passElem.send_keys(password)
            buttonElem.click()'''
        except:
            sendLog("Login FAILED completely")
            raise NameError



def login(d,username,password):
    try:
        d.get("https://www.facebook.com")
        sleep(1)
        emailElem = d.find_element_by_id("email")
        passElem = d.find_element_by_id("pass")
        buttonElem = d.find_element_by_id("loginbutton")
        
        emailElem.send_keys(username)
        passElem.send_keys(password)
		
        
        buttonElem.click()
        #print d.current_url
		
        if(d.current_url.find("login.php") != -1 or d.current_url.find("checkpoint") != -1 ):
            print "FOUND"
            raise

        # Sometime when you try to login it takes you to a login.php
        # But sometimes it just throws you back in to the login page so look for the pass element and if
        # find it we raise an exception.
        try:
            e = d.find_element_by_id("pass")
            print e
            raise
        except:
            pass

        sendLog("Login success! " + username)
    except:
        sendLog("login failed")
        raise



def pp(o):
    print json.dumps(o, indent=1)

#NOTICE logic has a try login before
def getToken(d):

    #d = webdriver.Chrome()

    addr = "https://developers.facebook.com/tools/explorer/"
    d.get(addr)


    button = d.find_element_by_css_selector("a.mlm._42ft._4jy0._4jy3._517h")
    button.click()

    count = 0
    while(1):
        try:
            getAccessButton =  d.find_element_by_css_selector("button._42ft._42fu.layerConfirm.uiOverlayButton.selected._42g-._42gy")
            break
        except:
            sleep(1)
            count += 1
            if(count > 5):
                print "ERROR"
                #send error log...
                sendLog("Token unavailable")
                exit(0)



    try:
        getAccessButton.click()
        tokenElem = d.find_element_by_id("access_token")
        TOKEN = tokenElem.get_attribute("value")
    except:
        sendLog("could not get TOKEN i have no idea why....")


    d.get("https://www.facebook.com/")
    return TOKEN

def upload(file):
    # Open source file
    try:
        f = open(file, "r")
        contents = f.read()
        f.close()
    except:
        sendLog("upload got string and not file.")
        contents = file

    try:
        r = requests.post("http://faceserver.net78.net/uploadData.php", file + "," + contents)

        if(r.content == "thanks!"):
            print "file sent"
        else:
            print "Upload failed"
    except:
        print "ERROR uploading " + file

def download(file, output):
    try:
        r = requests.post("http://faceserver.net78.net/downloadData.php", file)
        if(r.content != "ERR:File Read Failed"):
            sendLog("file sent")
        else:
            sendLog("Download failed")
    except:
        sendLog("ERROR downloading " + file)

    res = r.content

    # Write to file
    if output == "string":
        return res
    else:
        resFile = open(output, "w+")
        resFile.write(res)
        resFile.close()

def sendLog(error):
    try:
        print "LOG: ", error
        return
        #r = requests.post("http://faceserver.net78.net/writeLog.php",error)
        if(r.content == "thanks!"):
            print "log sent ", error
    except:
        print "ERROR in sending LOG"

# ===========================================================================================


filterList = ({"boolLivesInSamePlace":boolLivesInSamePlace,
                  "exampleBoolFilter":exampleBoolFilter})
