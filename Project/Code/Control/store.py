from cassandra.cluster import Cluster

from Model.offer import Offer

from unidecode import unidecode

from Utils.utils import eprint

from Utils.message import MessageList




class Store:
	
	def __init__(self,keyspace,ip= None):

		self.keyspace = keyspace
		self.ip = ip
		self.sesion = None

	def connect(self):

		if self.ip is None:
			cluster = Cluster()
		else:
			cluster = Cluster(self.ip)

		try:
			self.sesion = cluster.connect()
		except:
			print("Unable to connect to database. (Hint: Start cassandra)")
		self.createKeyspace()
		self.createTable("offers")


	def createKeyspace(self):
		self.sesion.execute("CREATE KEYSPACE IF NOT EXISTS {0}"\
		.format(self.keyspace) + \
		"	WITH REPLICATION = {'class':'SimpleStrategy','replication_factor':1};")



	def createTable(self,table):
		self.sesion.execute("""CREATE TABLE IF NOT EXISTS {0}.{1}
		( month int,
			year int,
			description text,
			title text,
			level text,
			area text,
			business text,
			requirements text,
			locality text,
			modality text,
			salary text,
			others text,
			pubDate timestamp,
			PRIMARY KEY( (month,year), description) );"""\
		.format(self.keyspace, table))


	def loadOffers(self, offers,mainList):

		errorLoading = False

		cntLoad = 0
		cntDisc = 0
		cntErr = 0
		for offer in offers:
			repeated = self.insertOffer(offer)
			if repeated is None:
				cntErr += 1
				errorLoading = True
			else:
				if not repeated:
					cntLoad += 1
				else:
					cntDisc += 1

		
		mainList.addMsg(str(cntLoad)+ " Offers succesfully loaded to database", MessageList.INF)
		mainList.addMsg(str(cntDisc)+ " Offers discarted because of duplication in database", MessageList.INF)
		mainList.addMsg(str(cntErr) + " Offers failed to load to database", MessageList.ERR)

		if errorLoading:
			mainList.setTitle("Some offers couldn't be loaded. Check detail file", MessageList.ERR)
		else:
			mainList.setTitle("All offers were loaded", MessageList.INF)


	@staticmethod
	def dbFormat(value):
		if value is None:
			return ""

		if type(value) is str:
			return value.replace("'","''")
		else:
			return value



	def insertOffer(self, offer):
		month = offer.pubDate.month
		year = offer.pubDate.year

		desc = Store.dbFormat(offer.description)
		title = Store.dbFormat(offer.title)
		level = Store.dbFormat(offer.level)
		area = Store.dbFormat(offer.area)
		business = Store.dbFormat(offer.business)
		requirements = Store.dbFormat(offer.requirements)
		locality = Store.dbFormat(offer.locality)
		modality = Store.dbFormat(offer.modality)
		salary = Store.dbFormat(offer.salary)
		others = Store.dbFormat(offer.others)
		pubDate = Store.dbFormat(offer.pubDate)

		command = """ insert into btpucp.offers(month, year, description, title, level, area,
									business, requirements,locality, modality, salary, others, pubdate) values (
									{0}, {1}, '{2}','{3}', '{4}' ,'{5}','{6}','{7}','{8}', '{9}', '{10}', '{11}', '{12}') if not exists;
							""".format(str(month), str(year), desc, title, level, area, business, requirements,\
							locality, modality, salary, others, pubDate)

		command = unidecode(command)

		try:
			result = self.sesion.execute(command)
			return not result[0][0]
		except:
			eprint("")
			eprint("Error running the cql command: "+ command)
			eprint("--------------------------------------------------------------------------------------------------------------------")
			return None


