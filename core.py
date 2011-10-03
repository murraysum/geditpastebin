import os
import re
import urllib
import xml.dom.minidom

class Core():

	API_DEV_KEY = "api_dev_key"
	API_USER_KEY = "api_user_key"
	API_PASTE_CODE = "api_paste_code"
	API_PASTE_PRIVATE = "api_paste_private"
	API_PASTE_NAME = "api_paste_name"
	API_PASTE_EXPIRE_DATE = "api_paste_expire_date"
	API_PASTE_FORMAT = "api_paste_format"
	API_OPTION = "api_option"
	API_USER_NAME = "api_user_name"
	API_USER_PASSWORD = "api_user_password"
	API_RESULTS_LIMIT = "api_results_limit"
	
	API_URL_POST = "http://pastebin.com/api/api_post.php"
	API_URL_LOGIN = "http://pastebin.com/api/api_login.php"
	API_URL_RAW = "http://pastebin.com/raw.php"
	
	DEV_KEY = "1d6e3cfe11d7f9d2b72a060662c1009d"
	API_FILE = "api.xml"
	
	def __init__(self):
		""" Create a core object to communicate with Pastebin """
		self.langs = {}
		self.dates = {}
		self.visibilities = {}
		self.__load_api_options()
		
	def __load_api_options(self):
		""" Load the pastebin api options from file """
		try:
			dirname = os.path.dirname(__file__)
			fd = os.path.join(dirname, self.API_FILE)
			doc = xml.dom.minidom.parse(fd)
			langs = doc.getElementsByTagName("language")
			self.__store_api_options(langs, self.langs)
			dates = doc.getElementsByTagName("date")
			self.__store_api_options(dates, self.dates)
			visibilities = doc.getElementsByTagName("visibility")
			self.__store_api_options(visibilities, self.visibilities)
		except IOError as e:
			raise CoreError(e)
		
	def __store_api_options(self, options, store):
		""" Store the api options into a store dictionary """
		for option in options:
			name = option.getElementsByTagName("name").item(0)
			value = option.getElementsByTagName("value").item(0)
			store[name.firstChild.data] = value.firstChild.data

	def __set_dev_key(self, parameters):
		""" Set the developer key """
		parameters[self.API_DEV_KEY] = self.DEV_KEY
	 
	def __set_usr_key(self, key, parameters):
		""" Set a valid user session key """
		parameters[self.API_USER_KEY] = key
	
	def __set_paste_text(self, text, parameters):
		""" Set the paste text """
		parameters[self.API_PASTE_CODE] = text
			
	def __set_paste_name(self, name, parameters):
		""" Sets the paste name or title """
		parameters[self.API_PASTE_NAME] = name
		
	def __set_private(self, private, parameters):
		""" Sets whether a paste is public or private """
		if private in self.visibilities:
			p = self.visibilities.get(private)
			parameters[self.API_PASTE_PRIVATE] = p
		else:
			raise CoreError("Bad API request, invalid api_paste_private")
 
	def __set_paste_expire(self, date, parameters):
		""" Sets the expiration date of the paste """
		if date in self.dates:
			d = self.dates.get(date)
			parameters[self.API_PASTE_EXPIRE_DATE] = d
		else:
			raise CoreError("Bad API request, invalid api_expire_date")

	
	def __set_paste_lang(self, lang, parameters):
		""" Sets the syntax highlighting of the paste """
		pattern = "(\s|^)" + lang + "(\s|$)"
		for name, value in self.langs.iteritems():
			matches = re.findall(pattern, name, re.I)
			if len(matches) != 0:
				parameters[self.API_PASTE_FORMAT] = value	
	
	def __set_option(self, option, parameters):
		""" Sets the api action """
		parameters[self.API_OPTION] = option

	def __set_usr_details(self, usr, pwd, parameters):
		""" Sets the username of paste """
		parameters[self.API_USER_NAME] = usr
		parameters[self.API_USER_PASSWORD] = pwd		

	# NOT Integrated Sets the number of results returned
	#def set_results_limit(self, limit, parameters):
	#	if limit >= 1 and limit <=1000:
	#		parameters[self.API_RESULTS_LIMIT] = limit
	#	else:
	#		raise CoreError("API Result Limit cannot be set")
	
	
	def __post_request(self, url, parameters):
		""" Make a POST request """
		encoded = urllib.urlencode(parameters)
		fd = urllib.urlopen(url, encoded)
		try:
			response = fd.read()
		finally:
			fd.close()
		del fd
		if "Bad API request" in response:
			raise CoreError(response)
		return response
	
	
	def __get_request(self, url, parameters):
		""" Make a URL GET request """
		encoded = urllib.urlencode(parameters)
		fd = urllib.urlopen("%s?%s" % (url, encoded))
		try:
			response = fd.read()
		finally:
			fd.close()
		del fd
		return response

	def __login(self, usr, pwd):
		""" Login to pastebin to get user session key """
		parameters = {}
		self.__set_dev_key(parameters)
		self.__set_usr_details(usr, pwd, parameters)
		return self.__post_request(self.API_URL_LOGIN, parameters)
	
	# DO NOT REMOVE Not Integrated Set raw key of paste
	#def __set_raw_query_key(self, key, parameters):
	#	parameters["i"] = key
	
	# DO NOT REMOVE Not Integrated Get a list of a users' pastes
	#def get_paste_list(self, usr_key, limit):
	#	parameters = {}
	#	self.__set_dev_key(parameters)
	#	self.__set_usr_key(usr_key, parameters)
	#	self.__set_results_limit(limit, parameters)
	#	self.__set_option("list", parameters)
	#	return self.__post_request(self.API_URL_POST, parameters)

	# DO NOT REMOVE Not Included Get raw paste text
	#def get_raw_paste(self, paste_key):
	#	parameters = {}
	#	self.__set_raw_query_key(paste_key, parameters)
	#	return self.__get_request(self.API_URL_RAW, parameters)
	
	def get_langs(self):
		return sorted(self.langs.keys())
		
	def get_dates(self):
		return self.dates.keys()
		
	def get_visibilities(self):
		return self.visibilities.keys()
		
	def paste(
			self, text, name=None, visibility=None, date=None,
			lang=None, usr=None, pwd=None):
		""" Make a paste to pastebin """
		parameters = {}
		self.__set_dev_key(parameters)
		self.__set_option("paste", parameters)
		self.__set_paste_text(text, parameters)
		if(visibility is not None):
			self.__set_private(visibility, parameters)
		if(name is not None):
			self.__set_paste_name(name, parameters)
		if(date is not None):
			self.__set_paste_expire(date, parameters)
		if(lang is not None):
			self.__set_paste_lang(lang, parameters)
		if(usr is not None and pwd is not None):
			usr_key = self.__login(usr, pwd)
			self.__set_usr_key(usr_key, parameters)
		return self.__post_request(self.API_URL_POST, parameters)
					
class CoreError(Exception):
	
	def __init__(self, msg):
		self.msg = msg
	
	def __str__(self):
		return "CoreError Details: " + self.msg
	
	def get_type(self):
		return "CoreError Details"
		
	def get_msg(self):
		return self.msg
