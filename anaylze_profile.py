__author__ = 'mikey'

from groups_crawler import *

def getSource(d, query_arg, output):
    addr = "https://www.facebook.com/" + query_arg

    # Get page by query
    if(query_arg != "None"):
        d.get(addr)

    count = 0
    # Loop exits when end of results string is in the source
    while ("End of Results" not in d.page_source)  and ("Bing Privacy Policy" not in d.page_source): #and ("Sorry" not in d.page_source)
        sourceSample = d.page_source
        d.execute_script("window.scrollBy(0,10000)", "")
        if(sourceSample == d.page_source):
			count += 1
			print count
			#in case something goes wrong if source doesn't update for 300 rounds go on..
			if(count >= 10):
				break

    # Write output to file
    if output == "string":
        return d.page_source.encode("utf8")
    else:
        f = open(output, "w+")
        f.write(d.page_source.encode("utf8"))
        f.close()


		
def getParamFromSource(sourceFile,subS,subE,output):
	try:
		f = open(sourceFile, "r")
		lines = f.read()
		f.close()
	except:
		lines = sourceFile

	res = ""

	start = 0
	count = 0


	while (True):
		start = lines.find(subS, start)
		if (start == -1): 
			break
			
		start += len(subS)
		end = lines.find(subE, start) - 1
		
		if lines[start:end].strip() != "":
			name =  lines[start:end]
			name = filterOutId(name)  + "\n"
			res += name
		start = end
		count = count + 1
		
	if output == "string":
		print "length:", len(res)
		return res
	else:
		try:
			resFile = open(output, "w+")
			print "length:", len(res)
			resFile.write(res)
			resFile.close()
			return res
		except:
			pass
			
			
def getTwoParamsFromSource(sourceFile,subS,subE,secondSubS,secondSubE,output):
	try:
		f = open(sourceFile, "r")
		lines = f.read()
		f.close()
	except:
		lines = sourceFile

	res = ""
	firstArr = []
	secondArr = []
	start = 0
	count = 0


	while (True):
		start = lines.find(subS, start)
		if (start == -1): 
			break
			
		start += len(subS)
		end = lines.find(subE, start) - 1
		
		if lines[start:end].strip() != "":
			param1 =  lines[start:end]
			param1 = filterOutId(param1)
			firstArr += [param1]
		start = end
		count = count + 1
		
		start = lines.find(secondSubS,start)
		if (start == -1): 
			break
			
		start += len(secondSubS)
		end = lines.find(secondSubE, start)
		
		if lines[start:end].strip() != "":
			param2 =  lines[start:end]
			param2 = filterOutId(param2)
			secondArr += [param2]
		start = end
	
	

	if output == "string":
		print "length:", len(res)
		return firstArr,secondArr
	else:
		try:
			resFile = open(output, "w+")
			print "length:", len(res)
			resFile.write(res)
			resFile.close()
			return res
		except:
			pass
			
def get_profile_groups(d, user):

	f = open("group_ids.txt","a+")
	source = getSource(d,user + "/groups","string")
	firstParam,secondParam = getTwoParamsFromSource(source,'<a href=\"/groups/','/\" lang=','mbs fcg\">',' members',"string")
	
	for groupIndex in range(0,len(firstParam)):
	
		if(groupIndex >= len(secondParam)):
			print "missing secondParam"
			break

		stripedNum = secondParam[groupIndex].replace(',','')	
		if (stripedNum.isdigit()):
			groupNumMembers = int(stripedNum)
		else:
			print "error parsing number of members: ",secondParam[groupIndex]
		
		if(groupNumMembers < 2000):
			print firstParam[groupIndex]
			f.write(firstParam[groupIndex] + "\n")
			
	f.close()
			
	
	
if __name__  == "__main__":
	read_user_file()
	opt = fixWebdriverOptions()
	d = webdriver.Chrome(chrome_options=opt)
	tryLogin(d,users[0],passes[0])
	get_profile_groups(d,"romanov123")