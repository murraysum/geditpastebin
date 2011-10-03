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
			
	def delete_details(self):
		""" Delete account details """
		try:
			item = self.__get_item()
			if item is not None:
				gk.item_delete_sync(self.NAME, item)
				return True
			return False
		except self.GK_EXCEPT as e:
			raise AccountError(repr(e))
			
	def exists(self):
		""" Whether account details are stored """
		try:
			if self.__get_item() is not None:
				return True
			return False
		except self.GK_EXCEPT as e:
			raise AccountError(repr(e))
 
	def get_details(self):
		""" Get the account details """
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
			
	def set_details(self, usr, pwd):
		""" Set the account details with a username and password """
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
			
	def __get_usr(self, item):
		""" Get the username from the account details """
		attrs = gk.item_get_attributes_sync(self.NAME, item)
		if "username" in attrs:
			return attrs.get("username")
		else:
			raise AccountError("Username could not be retrieved")
	
	def __set_usr(self, usr, item):
		""" Set the username of the account details """
		attrs = { "username" : str(usr)}
		gk.item_set_attributes_sync(self.NAME, item, attrs)
		
	def __get_pwd(self, item):
		""" Get the password from the account details """
		info = gk.item_get_info_sync(self.NAME, item)
		return info.get_secret()
				
	def __set_pwd(self, pwd, item):
		""" Set the password of the account details """
		info = gk.item_get_info_sync(self.NAME, item)
		info.set_secret(pwd)
		gk.item_set_info_sync(self.NAME, item, info)
	
	def __get_item(self):
		""" Get the keyring item """
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
		
	
