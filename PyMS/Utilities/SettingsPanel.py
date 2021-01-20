
from ..FileFormats import PCX
from ..FileFormats import FNT
from ..FileFormats import GRP
from ..FileFormats import Palette
from ..FileFormats import TBL
from ..FileFormats import AIBIN
from ..FileFormats import DAT
from ..FileFormats import IScriptBIN

from utils import BASE_DIR, isstr
from Settings import SettingDict
from MPQSelect import MPQSelect
from ErrorDialog import ErrorDialog
from PyMSError import PyMSError

from Tkinter import *
import tkFileDialog

import os

# TODO: Update settings handling once all programs use Settings objects
class SettingsPanel(Frame):
	types = {
		'PCX':(PCX.PCX,'PCX','pcx',[('StarCraft Special Palette','*.pcx'),('All Files','*')]),
		'FNT':(FNT.FNT,'FNT','fnt',[('StarCraft FNT','*.fnt'),('All Files','*')]),
		'GRP':(GRP.GRP,'GRP','grp',[('StarCraft GRP','*.grp'),('All Files','*')]),
		'CacheGRP':(GRP.CacheGRP,'GRP','grp',[('StarCraft GRP','*.grp'),('All Files','*')]),
		'Palette':(Palette.Palette,'Palette','pal',[('RIFF, JASC, and StarCraft PAL','*.pal'),('StarCraft Tileset WPE','*.wpe'),('ZSoft PCX','*.pcx'),('All Files','*')]),
		'WPE':(Palette.Palette,'Palette','wpe',[('StarCraft Tileset WPE','*.wpe'),('RIFF, JASC, and StarCraft PAL','*.pal'),('ZSoft PCX','*.pcx'),('All Files','*')]),
		'TBL':(TBL.TBL,'TBL','tbl',[('StarCraft TBL Files','*.tbl'),('All Files','*')]),
		'AIBIN':(AIBIN.AIBIN,'aiscript.bin','bin',[('AI Scripts','*.bin'),('All Files','*')]),
		'UnitsDAT':(DAT.UnitsDAT,'units.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'WeaponsDAT':(DAT.WeaponsDAT,'weapons.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'FlingyDAT':(DAT.FlingyDAT,'flingy.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'SpritesDAT':(DAT.SpritesDAT,'sprites.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'ImagesDAT':(DAT.ImagesDAT,'images.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'UpgradesDAT':(DAT.UpgradesDAT,'uupgrades.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'TechDAT':(DAT.TechDAT,'techdata.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'SoundsDAT':(DAT.SoundsDAT,'sfxdata.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'IScript':(IScriptBIN.IScriptBIN,'iscript.bin','bin',[('IScripts','*.bin'),('All Files','*')]),
	}

	def __init__(self, parent, entries, settings, mpqhandler, setdlg=None):
		if setdlg == None:
			self.setdlg = parent.parent
		else:
			self.setdlg = setdlg
		self.settings = settings
		self.mpqhandler = mpqhandler
		self.find = PhotoImage(file=os.path.join(BASE_DIR,'Images','find.gif'))
		self.variables = {}
		inmpq = False
		Frame.__init__(self, parent)
		for entry in entries:
			if len(entry) == 5:
				f,e,v,t,c = entry
			else:
				f,e,v,t = entry
				c = None
			self.variables[f] = (IntVar(),StringVar(),[])
			if isinstance(v, tuple) or isinstance(v, list):
				profileKey,valueKey = v
				if issubclass(settings, SettingDict):
					profile = settings.settings.get(profileKey, autosave=False)
					v = settings.settings.profiles[profile].get(valueKey, autosave=False)
				else:
					profile = settings[profileKey]
					v = settings['profiles'][profile][valueKey]
			elif isinstance(settings, SettingDict):
				v = settings.settings.files.get(v)
			else:
				v = settings[v]
			m = v.startswith('MPQ:')
			self.variables[f][0].set(m)
			if m:
				self.variables[f][1].set(v[4:])
			else:
				self.variables[f][1].set(v)
			self.variables[f][1].trace('w', self.edited)
			datframe = Frame(self)
			if isstr(e):
				Label(datframe, text=f, font=('Courier', -12, 'bold'), anchor=W).pack(fill=X, expand=1)
				Label(datframe, text=e, anchor=W).pack(fill=X, expand=1)
			elif e:
				Label(datframe, text=f, font=('Courier', -12, 'bold'), anchor=W).pack(fill=X, expand=1)
			else:
				Label(datframe, text=f, anchor=W).pack(fill=X, expand=1)
			entryframe = Frame(datframe)
			e = Entry(entryframe, textvariable=self.variables[f][1], state=DISABLED)
			b = Button(entryframe, image=self.find, width=20, height=20, command=lambda f=f,t=self.types[t],e=e,c=c: self.setting(f,t,e,c))
			self.variables[f][2].extend([e,b])
			if not t == 'Palette':
				inmpq = True
				y = Checkbutton(entryframe, text='', variable=self.variables[f][0])
				self.variables[f][2].append(y)
				y.pack(side=LEFT)
			e.pack(side=LEFT, fill=X, expand=1)
			e.xview(END)
			b.pack(side=LEFT, padx=1)
			entryframe.pack(fill=X, expand=1)
			datframe.pack(side=TOP, fill=X)
		if inmpq:
			Label(self, text='Check the checkbox beside an entry to use a file in the MPQs').pack(fill=X)

	def edited(self, *_):
		if hasattr(self.setdlg, 'edited'):
			self.setdlg.edited = True

	def select_file(self, t, e, f):
		if isinstance(self.settings, SettingDict):
			return self.settings.lastpath.settings.select_file(t, self, "Open a " + t, '.' + e, f)
		else:
			path = self.settings.get('lastpath', BASE_DIR)
			file = tkFileDialog.askopenfilename(parent=self, title="Open a " + t, defaultextension='.' + e, filetypes=f, initialdir=path)
			if file:
				self.settings['lastpath'] = os.path.dirname(file)
			return file

	def setting(self, f, t, e, cb):
		file = ''
		if self.variables[f][0].get():
			m = MPQSelect(self.setdlg, self.mpqhandler, t[1], '*.' + t[2], self.settings)
			if m.file:
				self.mpqhandler.open_mpqs()
				if t[1] == 'FNT':
					file = (self.mpqhandler.get_file(m.file, False),self.mpqhandler.get_file(m.file, True))
				else:
					file = self.mpqhandler.get_file(m.file)
				self.mpqhandler.close_mpqs()
		else:
			file = self.select_file(t[1],t[2],t[3])
		if file:
			c = t[0]()
			if t[1] == 'FNT':
				try:
					c.load_file(file[0])
					self.variables[f][1].set(file[0].file)
				except PyMSError:
					try:
						c.load_file(file[1])
						self.variables[f][1].set(file[0].file)
					except PyMSError, err:
						ErrorDialog(self.setdlg, err)
						return
			else:
				try:
					c.load_file(file)
				except PyMSError, e:
					ErrorDialog(self.setdlg, e)
					return
				self.variables[f][1].set(file)
			e.xview(END)
			if cb:
				cb(c)
			else:
				self.setdlg.edited = True

	def save(self, d, m, settings):
		for s in d[1]:
			v = ['','MPQ:'][self.variables[s[0]][0].get()] + self.variables[s[0]][1].get().replace(m,'MPQ:',1)
			if isinstance(settings, SettingDict):
				settings.settings.files[s[2]] = v
			else:
				settings[s[2]] = v