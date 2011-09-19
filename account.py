#!/usr/bin/env python
import gnomekeyring as gk
import glib

class Account():

	NAME = "login"
	ITEM = "gedit-pastebin-plugin"
	TYPE = gk.ITEM_GENERIC_SECRET
	
	def __init__(self):
		if not gk.is_available():
			raise AccountError("Gnome Keyring Unavailable")
		else:
			errors = []
			errors.append(gk.DeniedError)
			errors.append(gk.NoKeyringDaemonError)
			errors.append(gk.AlreadyUnlockedError)
			errors.append(gk.NoSuchKeyringError)
			errors.append(gk.BadArgumentsError)
			errors.append(gk.IOError)
			errors.append(gk.CancelledError)
			errors.append(gk.AlreadyExistsError)
			errors.append(gk.NoMatchError)
			self.GK_EXCEPT = tuple(errors)
			
	# Delete account details
	def delete_details(self):
		try:
			item = self.__get_item()
			if item is not None:
				gk.item_delete_sync(self.NAME, item)
				return True
			return False
		except self.GK_EXCEPT as e:
			raise AccountError(repr(e))
			
	# Whether account details exists
	def exists(self):
		try:
			if self.__get_item() is not None:
				return True
			return False
		except self.GK_EXCEPT as e:
			raise AccountError(repr(e))
				
	# Get the account details from the keyring 
	def get_details(self):
		try:
			item = self.__get_item()
			if item is not None:
				username = self.__get_usr(item)
				password = self.__get_pwd(item)
				return (username, password)
			else:
				raise AccountError("Keyring item doesn't exist")
		except self.GK_EXCEPT as e:
			raise AccountError(repr(e))
			
	# Set the account details with a username and password
	def set_details(self, usr, pwd):
		try:
			item = self.__get_item()
			if item is not None:
				self.__set_usr(usr, item)
				self.__set_pwd(pwd, item)
			else:
				attrs = {"username" : str(usr)}
				gk.item_create_sync(self.NAME, self.TYPE,
									self.ITEM, attrs, pwd, True)
		except self.GK_EXCEPT as e:
			raise AccountError(repr(e))
			
	# Get the username from the keyring
	def __get_usr(self, item):
		attrs = gk.item_get_attributes_sync(self.NAME, item)
		if "username" in attrs:
			return attrs.get("username")
		else:
			raise AccountError("Username could not be retrieved")
	
	# Set the username in the keyring item
	def __set_usr(self, usr, item):
		attrs = { "username" : str(usr)}
		gk.item_set_attributes_sync(self.NAME, item, attrs)
		
	# Get the password in the keyring item
	def __get_pwd(self, item):
		info = gk.item_get_info_sync(self.NAME, item)
		return info.get_secret()
				
	# Set the password in the keyring item	
	def __set_pwd(self, pwd, item):
		info = gk.item_get_info_sync(self.NAME, item)
		info.set_secret(pwd)
		gk.item_set_info_sync(self.NAME, item, info)
	
	# Get the keyring item
	def __get_item(self):
		keyrings = gk.list_keyring_names_sync()
		if self.NAME in keyrings:
			items = gk.list_item_ids_sync(self.NAME)
			for item in items:
				info = gk.item_get_info_sync(self.NAME, item)
				if self.ITEM == info.get_display_name():
					return item
		return None
		
class AccountError(Exception):
	def __init__(self, msg):
		self.msg = msg
	
	def __str__(self):
		return "AccountError Details: " + self.msg
	
	def get_type(self):
		return "AccountError Details"
		
	def get_msg(self):
		return self.msg
		
	
