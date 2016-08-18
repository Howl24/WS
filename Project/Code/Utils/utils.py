#Printint Error File
from __future__ import print_function
import sys

def eprint(*args,**kwargs):
	print(*args, file = sys.stderr, **kwargs)


	
from Utils.message import MessageList

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

def readUrlFromFile(tempFile):
	str = tempFile.readline()
	data = str.split('|')

	err = False
	if (len(data)!=3):
		return None
	else:
		validate = URLValidator()
		try:
			validate(data[1])
		except ValidationError:
			return None

		return data[1]


def readTextFromFile(tempFile):
	str = tempFile.readline()
	data = str.split('|')

	err = False

	if (len(data)!=3):
		return None
	else:
		return data[1]
		

def readIntFromFile(tempFile):
	str = tempFile.readline()
	data = str.split('|')

	err = False
	if(len(data)!=3):
		return None
	else:
		try:
			val = int(data[1])
		except:
			return None
		return val


def _validateTagFormat(tag):
	tagParts = tag.split()
	if len(tagParts) is not 2:
		return False
	else:
		index = tagParts[0]
		if index.isdigit() or index == '*':
			return True
		else:
			return False


def _validateDiccionaryFormat(dicc):
	try:
		diccionary = eval(dicc)
	except:
		return False

	if type(diccionary) is dict:
		return True
	else:
		return False

def _validateAttributeFormat(attr):
	return attr.isalpha() or attr == ""


def readSourceFromFile(tempFile):
	str = tempFile.readline()
	data = str.split('|')

	if (len(data)!=3):
		return None

	else:
		if (data[1] == ""):
			return data[1]

		levels = data[1].split('->')
		if len(levels)==0:
			return None

		else:

			for level in levels:
				parts = level.split('/')
				if (len(parts)!=3):
					return None
				else:

					tag = parts[0]
					if not _validateTagFormat(tag):
						return None

					dicc = parts[1]
					if not _validateDiccionaryFormat(dicc):
						return None

					attr = parts[2]
					if not _validateAttributeFormat(attr):
						return None

					return data[1]
					

		"""

		mainList = MessageList()

		#Old format.

		#Validate format

		#Levels must be separated by "->"
		levels = data[1].split('->')
		if (len(levels)==0):
			mainList.addMsg("Levels incorrectly separated. (Hint: use ->)" \
											, MessageList.ERR)
			return None

		else:

			for level in levels:
				#Every level has 3 parts (tag/diccionary/attributes)
				parts = level.split('/')
				if (len(parts)!=3):
					mainList.addMsg("Parts incorrectly separated."+ \
													"(Hint: 3 parts per level separated by /", \
													MessageList.ERR)


													

					return None
				else:

					err = False
					tag = parts[0]

					if not (tag.isalpha() or \
									(tag!= "" and tag[0] == '*' and tag[1:].isalpha())):
						mainList.addMsg("Incorrect tag format ",MessageList.ERR)
						err = True

					try:	
						dicc = eval(parts[1])
					except:
						mainList.addMsg("Diccionary part is not a diccionary instance")
						err = True
					
					attr = parts[2]
					if not (attr.isalpha() or attr == ""):
						mainList.addMsg("Attribute part must be alphabetic" + \
														"or an empty string", MessageList.ERR)
						err = True

					if err:
						return None
					else:	
						return data[1]

		"""




	
		





















		









