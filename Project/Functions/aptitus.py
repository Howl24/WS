def makeAreaUrls(areas,urlBase):
	str = urlBase
	str += "/de-"
	str += areas[0]

	for i in range(1,len(areas)):
		str += "--" + areas[i]
	
	return [str]  



def makePeriodUrl(period,url):
	periodUrl = url + "/publicado-" + period
	return periodUrl



def makePageUrl(pageNum, url):
	if pageNum == 1:
		return url
	else:
		newUrl= url + "?page=" + str(pageNum)
		return newUrl


def makeLinkUrl(link, url):
	return link

		

	




