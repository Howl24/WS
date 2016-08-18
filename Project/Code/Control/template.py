import requests
import bs4
import importlib

import datetime
from time import mktime

from Utils.message import MessageList
from Utils import utils
from Utils.utils import eprint
from Control.scraper import Scraper

from Model.offer import Offer


class Template:
	
	def __init__(self, jobCenter, funcFilename, urlBase, period, areaUrl, \
							 areasSource, numOffSource, linksPerPage, numSources, listSources):

		self.jobCenter = jobCenter
		self.funcFilename = funcFilename
		self.urlBase = urlBase
		self.period = period
		self.areaUrl = areaUrl
		self.areasSource = areasSource
		self.numOffSource = numOffSource
		self.linksPerPage = linksPerPage
		self.numSources = numSources
		self.listSources = listSources

		self.module = None


	@staticmethod
	def readAttributesFromFile(file,mainList):
		file.readline() #Global:
			
		jobCenter = utils.readTextFromFile(file)
		if jobCenter is None: mainList.addMsg("Failed to read the jobcenter", MessageList.ERR)

		funcFilename = utils.readTextFromFile(file)
		if funcFilename is None: mainList.addMsg("Failed to read the functions filename", MessageList.ERR)

		urlBase = utils.readUrlFromFile(file)
		if urlBase is None: mainList.addMsg("Failed to read the url Base", MessageList.ERR)

		period = utils.readTextFromFile(file)
		if period is None: mainList.addMsg("Failed to read the period", MessageList.ERR)

		areaUrl = utils.readUrlFromFile(file)
		if areaUrl is None: mainList.addMsg("Failed to read the url to get areas", MessageList.ERR)

		areasSource = utils.readSourceFromFile(file)
		if areasSource is None: mainList.addMsg("Failed to read the source to get areas", MessageList.ERR)

		numOffSource = utils.readSourceFromFile(file)
		if numOffSource is None: mainList.addMsg("Failed to read the source to get the number of offers", MessageList.ERR)

		linksPerPage = utils.readIntFromFile(file)
		if linksPerPage is None: mainList.addMsg("Failed to read the number of links per page", MessageList.ERR)

		numSources = utils.readIntFromFile(file)
		if numSources is None: mainList.addMsg("Failed to read the number of sources to get offers", MessageList.ERR)
		else:
			listSources = []
			for i in range(0, numSources):
				offSource = utils.readSourceFromFile(file)
				if offSource is None:	mainList.addMsg("Failed to read the offer source #"+ str(i+1), MessageList.ERR)
				else: listSources.append(offSource)
			
		if mainList.size() is not 0:
			return None
		else:
			return jobCenter, funcFilename, urlBase, period, areaUrl, areasSource, numOffSource, linksPerPage, numSources, listSources	



	@classmethod
	def fromFile(cls, file,mainList):
		attributes = cls.readAttributesFromFile(file, mainList)
		if attributes is None:
			return None
		else:
			return cls(*attributes)


	def getAreas(self,mainList):
		try:
			web = requests.get(self.areaUrl)
			soup = bs4.BeautifulSoup(web.text,"lxml")
		except:
			mainList.setTitle("Cannot connect: "+ self.areaUrl,MessageList.ERR)
			return None
		
		scraper = Scraper(soup,self.areasSource)
		data = scraper.scrap()

		areas = data[0]

		#print(areas)
		areas = ["administracion-y-finanzas"]

		if areas is None:
			mainList.setTitle("Failed to scrap areas. Check areas source",MessageList.ERR)
			return None
		else:
			mainList.setTitle(str(len(areas)) + " Areas obtained",MessageList.INF)
			return areas




	def getNumOffers(self,dateUrl):
		mainList = MessageList()
		
		try:
			web = requests.get(dateUrl)
			soup = bs4.BeautifulSoup(web.text,"lxml")
		except:
			mainList.addMsg("Cannot access to the url " + dateUrl,MessageList.ERR)
			return None

		scraper = Scraper(soup, self.numOffSource)
		numOff = scraper.scrap()[0]
		numOff = int(numOff.split()[0])


		if numOff is None:
			mainList.addMsg("Fail scraping number of offers.",MessageList.ERR)
			return None

		return numOff


	def getOffersFromPageUrl(self,pageUrl):

		try:
			web = requests.get(pageUrl)
			soup = bs4.BeautifulSoup(web.text,"lxml")

		except:
			eprint("Cannot access to the url: "+ pageUrl + "\n")
			return None


		totLinks = []
		totDates = []

		for source in self.listSources:
			levels = source.split('->')
			index = 0

			scraper = Scraper(soup,source)
			data = scraper.scrap()

			offLinks = data[0]
			dates = data[1]
				

			if offLinks is None or len(offLinks) == 0:
				#Useless source
				eprint("No offers obtained using Source: " + source)
				continue

			else:
				#Remember:offLink must be a list

				for index, link in enumerate(offLinks):
					if not link in totLinks:
						totLinks.append(link)
						totDates.append(dates[index])

		totOffers = []
		for index,link in enumerate(totLinks):
			eprint("Offer #"+str(index+1))
			offer = self.getOfferFromLink(link)
			if offer is not None:
				passTime = totDates[index]
				offer.pubDate = self._toPublicationDate(passTime)
				totOffers.append(offer)
			else:
				totOffers.append(offer)

		return totOffers


	def _toPublicationDate(self, passTime):
		curDate = datetime.date.today()
		parts = passTime.split()
		
		type = parts[2]
		value = int(parts[1])

		if type in ['segundos','segundo']:
			pubDate = curDate - datetime.timedelta(seconds = value)

		if type in ['minutos', 'minuto']:
			pubDate = curDate - datetime.timedelta(minutes = value)

		if type in ['hora', 'horas']:
			pubDate = curDate - datetime.timedelta(hours = value)

		if type in ["día", "días"]:
			pubDate = curDate - datetime.timedelta(days = value)

		if type in ["semana", "semanas"]:
			pubDate = curDate - datetime.timedelta(weeks = value)

		if type in ["mes", "meses"]:
			pubDate = curDate - datetime.timedelta(months = value)
		
		return pubDate


	def getOffersFromPeriodUrl(self,periodUrl, mainList):

		self.numOff = self.getNumOffers(periodUrl)

		if self.numOff is None:
			mainList.setTitle("Failed to get the number of offers", MessageList.ERR)
			return None

		mainList.addMsg("Number of Offers filtered: " + str(self.numOff),MessageList.INF)

		max = 2000
		numPag = 0
		totalOffers = []

		while numPag < max and len(totalOffers) < self.numOff:
			numPag += 1

			try:
				pageUrl = self.module.makePageUrl(numPag,periodUrl)
			except:
				mainList.setTitle("makePageUrl is not working propertly", MessageList.ERR)
				#Abort everything
				return None #Return totalOffers if you dont wanna abort all

			eprint("Page #"+str(numPag))
			offers = self.getOffersFromPageUrl(pageUrl)
			eprint("")

			if offers is None:
				#Error page
				break
			else:
				totalOffers += offers
				if len(offers)!=self.linksPerPage and len(totalOffers)!=self.numOff:
					mainList.addMsg("Unexpected number of offers at page #"+ str(numPag), MessageList.INF)

		mainList.setTitle(str(len(totalOffers)) + " offers obtained in total (Invalid included)",MessageList.INF)
		return totalOffers
					


	def getOffersFromAreaUrl(self,areaUrl,mainList):

		periodUrl = self.module.makePeriodUrl(self.period,areaUrl)
		try:
			periodUrl = self.module.makePeriodUrl(self.period,areaUrl)
		except:
			mainList.setTitle("makePeriodUrl function is not working propertly",MessageList.ERR)
			return None

		msgList = MessageList()
		offers = self.getOffersFromPeriodUrl(periodUrl,msgList)
		mainList.addMsgList(msgList)

		if offers is None:
			mainList.setTitle("Cannot obtain offers",MessageList.ERR)
			return None

		else:
			validOffers = []
			for offer in offers:
				if offer is not None:
					validOffers.append(offer)

			mainList.setTitle(str(len(validOffers))+ " valid offers selected",MessageList.INF)
			return validOffers


	def execute(self,db, mainList):

		#Importing Custom Functions
		msgList = MessageList()
		mod = customImport(self.funcFilename,msgList)
		mainList.addMsgList(msgList)

		if mod is not None:
			self.module = mod

			msgList = MessageList()
			areas = self.getAreas(msgList)
			mainList.addMsgList(msgList)

			if areas is not None:
				
				try:
					urls = self.module.makeAreaUrls(areas,self.urlBase)
					areaUrls = list(urls)
				except:
					mainList.addMsg("makeAreaUrls function is not working propertly",MessageList.ERR)
					mainList.setTitle("Failed to execute Template "+ self.jobCenter, MessgaeList.ERR)
					return None

				for index,areaUrl in enumerate(areaUrls):
					
					mainList.addMsg("Area #"+str(index+1),MessageList.INF)
					msgList = MessageList()
					offers = self.getOffersFromAreaUrl(areaUrl,msgList)
					mainList.addMsgList(msgList)

					if offers is not None:
						msgList = MessageList()
						db.loadOffers(offers,msgList)
						mainList.addMsgList(msgList)

				mainList.setTitle("Template " + self.jobCenter + " executed.", MessageList.INF)
				return 

		mainList.setTitle("Failed to execute Template " +self.jobCenter,MessageList.ERR)
		return
		

def customImport(filename, mainList):

	modname = "Functions." + filename

	try:
		mod = importlib.import_module(modname)
	except:
		mainList.setTitle("Incorrect function module filename", MessageList.ERR)
		return None

	#Check function existence
	customFunctions = dir(mod)

	if not "makeAreaUrls" in customFunctions:
		mainList.addMsg("Missing makeAreaUrls function",MessageList.ERR)

	if not "makePeriodUrl" in customFunctions:
		mainList.addMsg("Missing makePeriodUrl function", MessageList.ERR)

	if not "makePageUrl" in customFunctions:
		mainList.addMsg("Missing makePageUrl function",MessageList.ERR)

	if mainList.size() is not 0:
		mainList.setTitle("Fail importing function file", MessageList.ERR)
		return None
	else:
		mainList.setTitle("Function file imported", MessageList.INF)
		return mod 



class OfferTemplate(Template):
	def __init__(self, globalAttributes, titleSource, levelSource, areaSource ,businessSource, descSource,\
							reqSource, localitySource, modalitySource, salarySource, othersSource):

		Template.__init__(self,*globalAttributes)

		self.titleSource = titleSource
		self.levelSource = levelSource
		self.areaSource = areaSource
		self.businessSource= businessSource
		self.descSource = descSource
		self.reqSource = reqSource
		self.localitySource = localitySource
		self.modalitySource = modalitySource
		self.salarySource = salarySource
		self.othersSource = othersSource


	@staticmethod
	def readAttributesFromFile(file,mainList):
		globalAttr = Template.readAttributesFromFile(file,mainList)
		file.readline() #newline
		file.readline() #Offer Detail:

		titleSource = utils.readSourceFromFile(file)
		if titleSource is None: mainList.addMsg("Failed to read the offer title source",MessageList.ERR)

		levelSource = utils.readSourceFromFile(file)
		if levelSource is None: mainList.addMsg("Failed to read the offer level source",MessageList.ERR)

		areaSource = utils.readSourceFromFile(file)
		if areaSource is None: mainList.addMsg("Failed to read the offer area source", MessageList.ERR)

		businessSource = utils.readSourceFromFile(file)
		if businessSource is None: mainList.addMsg("Failed to read the offer business source", MessageList.ERR)

		descSource = utils.readSourceFromFile(file)
		if descSource is None: mainList.addMsg("Failed to read the offer description source", MessageList.ERR)

		reqSource = utils.readSourceFromFile(file)
		if reqSource is None: mainList.addMsg("Failed to read the offer requirements source", MessageList.ERR)

		
		localitySource = utils.readSourceFromFile(file)
		if localitySource is None: mainList.addMsg("Failed to read the offer locality source", MessageList.ERR)

		modalitySource = utils.readSourceFromFile(file)
		if modalitySource is None: mainList.addMsg("Failed to read the offer modality source", MessageList.ERR)

		salarySource = utils.readSourceFromFile(file)
		if salarySource is None: mainList.addMsg("Failed to read the offer salary source", MessageList.ERR)

		othersSource = utils.readSourceFromFile(file)
		if othersSource is None: mainList.addMsg("Failed to read the offer others source", MessageList.ERR)

		if mainList.size() is not 0:
			return None
		else:
			return globalAttr, titleSource, levelSource, areaSource, businessSource, descSource, reqSource, \
			localitySource, modalitySource, salarySource, othersSource
						

	def getDataFromSource(self, soup, source):
		if source == "":
			return None
		else:
			scraper = Scraper(soup, source)
			data = scraper.scrap()[0]
			return data


	def getOfferFromLink(self,link):

		try:
			web = requests.get(link)
			soup = bs4.BeautifulSoup(web.text,"lxml")

		except:
			eprint("Cannot access to the link "+link)
			return None

		title = self.getDataFromSource(soup, self.titleSource)
		if title is None: eprint("  Title source problem")
		if title == "": eprint("  Empty Title")

		level = self.getDataFromSource(soup, self.levelSource)
		if level is None: eprint("  Level source problem")
		if level == "": eprint("  Empty level")

		area = self.getDataFromSource(soup, self.areaSource)
		if area is None: eprint("  Area source problem")
		if area == "": eprint("  Empty area")

		business = self.getDataFromSource(soup, self.businessSource)
		if business is None: eprint("  Business source problem")
		if business == "": eprint("  Empty business")

		description = self.getDataFromSource(soup, self.descSource)
		if description is None: eprint("  Description source problem. INVALID OFFER")
		if description == "": eprint("  Empty description. INVALID OFFER")

		requirements = self.getDataFromSource(soup, self.reqSource)
		if requirements is None: eprint("  Requirements sourcde problem")
		if requirements == "": eprint("  Empty requirements")

		locality = self.getDataFromSource(soup, self.localitySource)
		if locality is None: eprint("  Locality source problem")
		if locality == "": eprint("  Empty locality")

		modality = self.getDataFromSource(soup, self.modalitySource)
		if modality is None: eprint("  Modality source problem")
		if modality == "": eprint("  Empty modality")

		salary = self.getDataFromSource(soup, self.salarySource)
		if salary is None: eprint("  Salary source problem")
		if salary == "": eprint("  Empty salary")

		others = self.getDataFromSource(soup, self.othersSource)
		if others is None: eprint("  Others source problem")
		if others == "": eprint("  Empty others")

		eprint("  Link: " + link)

		if description is None or description == "":
			return None
		else:

			offer = Offer(title, level, area, business, description, requirements, locality, modality, salary, others)
			return offer
		

