class Offer:
	
	def __init__(self,title,level,area, business, description,\
				 requirements, locality, modality, salary, others, pubDate = None):

		self.title = title
		self.level = level
		self.area = area
		self.business = business
		self.description = description
		self.requirements = requirements
		self.locality = locality
		self.modality = modality
		self.salary = salary
		self.others = others

		self.pubDate = pubDate


#	def show(self):
#		print("Oferta: ")
#		print(" Titulo:               " + str(self.title))
#		print(" Nivel: 								" + str(self.level))
#		print(" Area: 								" + str(self.area))
#		print(" Empresa:              " + str(self.business))
#		print(" Descripcion:          " + str(self.description))
#		print(" Modalidad: 						" + str(self.modality))
#		print(" Salario: 							" + str(self.salary))
#		print(" Fecha de publicacion: " + str(self.pubDate))
#		print("")
#


