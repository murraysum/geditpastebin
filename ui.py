import pygtk
pygtk.require("2.0")
import gtk
import os

from account import Account, AccountError
from core import Core, CoreError

class ConfigureDialog():
		
	def create_dialog(self):
		try:
			self.builder = gtk.Builder()
			f = os.path.join(os.path.dirname(__file__), "configure.glade")
			self.builder.add_from_file(f)
			self.builder.connect_signals(self)
			self.account = Account()
			self.init_widgets()
			return self.dialog
			
		except AccountError as e:
			dialog = ExceptionDialog(e)
			return dialog.get_dialog()
		
	def get_widgets(self):
		self.dialog = self.builder.get_object("config_dialog")
		self.usr_entry = self.builder.get_object("usr_entry")
		self.pwd_entry = self.builder.get_object("pwd_entry")
		self.acct_radio = self.builder.get_object("acct_radio")
		self.anon_radio = self.builder.get_object("anon_radio")
		self.acct_cont = self.builder.get_object("acct_container")	
	
	def init_widgets(self):
		self.get_widgets()
		if self.account.exists():
			usr, pwd = self.account.get_details()
			self.usr_entry.set_text(usr)
			self.pwd_entry.set_text(pwd)
			self.acct_radio.set_active(True)
		else:
			self.set_sensitive(False)
		self.dialog.show()
		
	def on_show_check_toggled(self, show_check, data=None):
		if show_check.get_active():
			self.pwd_entry.set_visibility(True)
		else:
			self.pwd_entry.set_visibility(False)
	
	def on_entry_clear(self, entry, icon_pos, data=None):
		entry.set_text("")
		
	def on_close_button_clicked(self, widget, data=None):
		if self.anon_radio.get_active():
			self.account.delete_details()
		else:
			pwd = self.pwd_entry.get_text()
			usr = self.usr_entry.get_text()
			self.account.set_details(usr, pwd)	
		self.dialog.destroy()

	def set_sensitive(self, hide):
		self.acct_cont.set_sensitive(hide)
		
	def on_anon_radio_toggled(self, widget, data=None):
		self.set_sensitive(False)
		
	def on_acct_radio_toggled(self, widget, data=None):
		self.set_sensitive(True)

class UploadDialog():
	
	def __init__(self, doc):
		self.doc = doc
		self.core = Core()
		self.account = Account()
		
	def create_dialog(self):
		self.builder = gtk.Builder()
		f = os.path.join(os.path.dirname(__file__), "upload.glade")
		self.builder.add_from_file(f)
		self.builder.connect_signals(self)
		self.dialog = self.builder.get_object("upload_dialog")
		self.init_widgets()
		self.dialog.show()

	def init_widgets(self):
		self.name_entry = self.builder.get_object("name_entry")
		self.set_name(self.doc)
		self.langs_combo = self.builder.get_object("langs_combo")
		self.set_langs(self.doc)
		self.dates_combo = self.builder.get_object("dates_combo")
		self.set_dates()
		self.private_combo = self.builder.get_object("private_combo")
		self.set_private()
		
	def fill_combo_box(self, combo, items, active_item):
		model = combo.get_model()
		i = 0
		for item in items:
			model.append([item])
			if item.lower() == active_item.lower():
				combo.set_active(i)
			i = i + 1
		if combo.get_active() == -1:
			combo.set_active(0)
		cell = gtk.CellRendererText()
		combo.pack_start(cell, True)
		combo.add_attribute(cell, "text", 0)
		
	def set_name(self, doc):
		name = doc.get_short_name_for_display()
		self.name_entry.set_text(name)
	
	def set_langs(self, doc):
		src_lang = doc.get_language()
		lang = "None"
		if src_lang is not None:
			lang = src_lang.get_name()
		langs = self.core.get_langs()
		self.fill_combo_box(self.langs_combo, langs, lang)
		
	def set_dates(self):
		dates = self.core.get_dates() 
		self.fill_combo_box(self.dates_combo, dates, "")
	
	def set_private(self):
		self.fill_combo_box(self.private_combo, ["Yes","No"], "")
	
	def on_cancel_button_clicked(self, widget, data=None):
		self.dialog.destroy()
	
	def on_upload_button_clicked(self, widget, data=None):
		
		# Get paste text
		start = self.doc.get_start_iter()
		end = self.doc.get_end_iter()
		text = start.get_text(end)
		
		args = {}
		args["name"] = self.name_entry.get_text()
		
		lang_index = self.langs_combo.get_active()
		lang_model = self.langs_combo.get_model()
		args["lang"] = lang_model[lang_index][0]
		
		date_index = self.dates_combo.get_active()
		date_model = self.dates_combo.get_model()
		args["date"] = date_model[date_index][0]
		
		# Get usr & pwd
		if self.account.exists():
			usr, pwd = self.account.get_details()
			args["usr"] = usr
			args["pwd"] = pwd
		
		self.dialog.destroy()
		try:
			url = self.core.paste(text, **args)
			opts={}
			opts["buttons"] = gtk.BUTTONS_OK
			opts["message_format"] = "Pastebin URI"
			dialog = gtk.MessageDialog(**opts)
			dialog.connect("response", lambda d, r: d.destroy())
			dialog.set_title("Gedit Pastebin Plugin")
			dialog.format_secondary_text(url)
			dialog.show() 
		except CoreError as e:
			ed = ExceptionDialog(e)
			dialog = ed.get_dialog()
			dialog.show()
		
	def on_name_entry_icon_press(self, entry, icon_pos, data=None):
		entry.set_text("")
		
class ExceptionDialog():
	
	def __init__(self, exception):
		opts = {}
		self.set_msg_type(opts)
		self.set_button_type(opts)
		self.set_type(opts, exception)
		self.dialog = gtk.MessageDialog(**opts)
		self.set_title()
		self.set_msg(exception)
		self.dialog.connect("response", lambda d, r: d.destroy())
		
	def set_msg_type(self, opts):
		opts["type"] = gtk.MESSAGE_ERROR
		
	def set_button_type(self, opts):
		opts["buttons"] = gtk.BUTTONS_OK
		
	def set_type(self, opts, exception):
		opts["message_format"] = exception.get_type()
	
	def set_msg(self, exception):
		msg = exception.get_msg()
		self.dialog.format_secondary_text(msg)
		
	def set_title(self):
		self.dialog.set_title("Gedit Pastebin Plugin")
		
	def get_dialog(self):
		return self.dialog

class MenuItem():
	
	ui_str = """<ui>
	<menubar name="MenuBar">
		<menu name="ToolsMenu" action="Tools">
		<placeholder name="ToolsOps_1">
			<menuitem name="Upload" action="Upload"/>
		</placeholder>
		</menu>
	</menubar>
	</ui>
	"""
	
	def __init__(self):
		self.core = Core()
		self.account = Account()
		
	def create_menu(self, window):
		self._window = window
		manager = self._window.get_ui_manager()
		self.group = gtk.ActionGroup("PastebinPlugin")
		self.group.add_actions([("Upload", None, _("Upload to Pastebin"),
										 "<control>U", _("Upload to Pastebin"),
										 self.on_upload)])
		manager.insert_action_group(self.group, -1)
		self.menu_id = manager.add_ui_from_string(self.ui_str)

	def remove_menu(self):
		manager = self._window.get_ui_manager()
		manager.remove_ui(self.menu_id)
		manager.remove_action_group(self.group)
		manager.ensure_update()

	# Upload menu item handler
	def on_upload(self, action, data=None):
		doc = self._window.get_active_document()
		upload = UploadDialog(doc)
		upload.create_dialog()
		## Get paste text
		#doc = self._window.get_active_document()
		#start = doc.get_start_iter()
		#end = doc.get_end_iter()
		#text = start.get_text(end)
		
		#args = {}	
		## Get language
		#lang = doc.get_language()
		#if lang is not None:
			#args["lang"] = lang.get_name()
		
		## Get title	
		#args["name"] = doc.get_short_name_for_display()
		
		## Get usr & pwd
		#if self.account.exists():
			#usr, pwd = self.account.get_details()
			#args["usr"] = usr
			#args["pwd"] = pwd
		
		#try:
			#url = self.core.paste(text, **args)
			#opts={}
			#opts["buttons"] = gtk.BUTTONS_OK
			#opts["message_format"] = "Pastebin URI"
			#dialog = gtk.MessageDialog(**opts)
			#dialog.connect("response", lambda d, r: d.destroy())
			#dialog.set_title("Gedit Pastebin Plugin")
			#dialog.format_secondary_text(url)
			#dialog.show()
			 
		#except CoreError as e:
			#ed = ExceptionDialog(e)
			#dialog = ed.get_dialog()
			#dialog.show()
