
from utils import parse_geometry
from UIKit import Toplevel

class PyMSDialog(Toplevel):
	def __init__(self, parent, title, center=True, grabwait=True, hidden=False, escape=False, resizable=(True,True), set_min_size=(False,False)):
		Toplevel.__init__(self, parent)
		self.title(title)
		self.icon = parent.icon
		self.wm_iconbitmap(parent.icon)
		self.protocol('WM_DELETE_WINDOW', self.cancel)
		if escape:
			self.bind('<Escape>', self.cancel)
		#self.transient(parent)
		self.parent = parent
		focus = self.widgetize()
		self.update_idletasks()
		if not focus:
			focus = self
		focus.focus_set()
		w,h,_,_,_ = parse_geometry(self.winfo_geometry())
		screen_w = self.winfo_screenwidth()
		screen_h = self.winfo_screenheight()
		if center:
			self.geometry('+%d+%d' % ((screen_w-w)/2,(screen_h-h)/2))
		self.resizable(*resizable)
		min_w = 0
		max_w = screen_w
		min_h = 0
		max_h = screen_h
		if not resizable[0]:
			min_w = max_w = w
		elif set_min_size[0]:
			min_w = w
		if not resizable[1]:
			min_h = max_h = h
		elif set_min_size[1]:
			min_h = h
		self.minsize(min_w, min_h)
		self.maxsize(max_w, max_h)
		self.setup_complete()
		if grabwait:
			self.grab_wait()

	def grab_wait(self):
		self.grab_set()
		self.wait_window(self)

	def widgetize(self):
		pass
	def setup_complete(self):
		pass

	def dismiss(self):
		self.withdraw()
		self.update_idletasks()
		self.parent.focus_set()
		self.destroy()

	def ok(self, event=None):
		self.dismiss()

	def cancel(self, event=None):
		self.dismiss()