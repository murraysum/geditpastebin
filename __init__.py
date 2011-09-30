import gedit
import gtk

from ui import ConfigureDialog
from ui import MenuItem
from ui import ExceptionDialog

class PastebinWindowHelper:

	def __init__(self, plugin, window):
		self._window = window
		self._plugin = plugin
		self.menu = MenuItem()
		try:
			self.menu.create_menu(window)
		except CoreError as e:
			ExceptionDialog(repr(e))
		
	def deactivate(self):
		self.menu.remove_menu()
		self._window = None
		self._plugin = None
		
	def update_ui(self):
		pass

class PastebinPlugin(gedit.Plugin):

	def __init__(self):
		gedit.Plugin.__init__(self)
		self._instances = {}
		
	def activate(self, window):
		print "Pastebin Plugin Activated"
		self._instances[window] = PastebinWindowHelper(self, window)
		
	def deactivate(self, window):
		print "Pastebin Plugin Deactivated"
		self._instances[window].deactivate()
		del self._instances[window]

	def update_ui(self, window):
		self._instances[window].update_ui()

	def is_configurable(self):
		return True

	def create_configure_dialog(self):
		config = ConfigureDialog()
		return config.create_dialog()
