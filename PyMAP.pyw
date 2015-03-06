from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs.SFmpq import *
from Libs import TBL, AIBIN, DAT, Tilesets, GRP
from Libs.CHK import *

from Tkinter import *
from tkMessageBox import *
import tkFileDialog,tkColorChooser
from Libs.SpecialLists import TreeList
from PIL import Image as PILImage
from PIL import ImageDraw as PILDraw
from PIL import ImageTk

from thread import start_new_thread
from math import ceil
import optparse, os, webbrowser, sys

VERSION = (0,1)
LONG_VERSION = 'v%s.%s' % VERSION

# class Sprite()

class EditLayer:
	INACTIVE = 0
	ACTIVE = 1

	def __init__(self, ui, name):
		self.ui = ui
		self.name = name
		self.list_group = None
		self.mode = EditLayer.INACTIVE

	def list_select(self, info):
		pass

	def set_mode(self, mode, x1,y1, x2,y2):
		isNew = mode != self.mode
		self.mode = mode
		return isNew

	def update_display(self, x1,y1, x2,y2, mouseX,mouseY):
		pass

class EditLayerTerrain(EditLayer):
	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Terrain")

	def set_mode(self, mode, x1,y1, x2,y2):
		if EditLayer.set_mode(self, mode, x1,y1, x2,y2):
			tag = 'tile_border'
			if self.mode == EditLayer.INACTIVE:
				self.ui.mapCanvas.delete(tag)
			else:
				self.ui.mapCanvas.create_rectangle(0,0,0,0, outline='#FF0000', tags=tag)

	def update_display(self, x1,y1, x2,y2, mouseX,mouseY):
		if self.mode == EditLayer.ACTIVE:
			tag = 'tile_border'
			x = int((x1+mouseX) / 32.0) * 32
			y = int((y1+mouseY) / 32.0) * 32
			self.ui.mapCanvas.coords(tag, x,y, x+32,y+32)
			self.ui.mapCanvas.tag_raise(tag)

class EditLayerDoodads(EditLayer):
	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Doodads")

class EditLayerFogOfWar(EditLayer):
	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Fog of War")

class EditLayerLocations(EditLayer):
	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Locations")
		self.always_display = self.ui.settings.get('always_show_locations', False)
		self.locations = {}

	def set_mode(self, mode, x1,y1, x2,y2):
		if EditLayer.set_mode(self, mode, x1,y1, x2,y2):
			if self.mode == EditLayer.ACTIVE:
				# dims = self.chk.sections[CHKSectionDIM.NAME]
				locations = self.ui.chk.sections.get(CHKSectionMRGN.NAME)
				if locations:
					strings = self.ui.chk.sections[CHKSectionSTR.NAME]
					for l,location in enumerate(locations.locations):
						if l == 63:
							continue
						if location.inUse():
							name = strings.strings[location.name-1]
							name = TBL.decompile_string(name)
							tag = 'location%d' % l
							x1 = min(location.start[0],location.end[0])
							y1 = min(location.start[1],location.end[1])
							x2 = max(location.start[0],location.end[0])
							y2 = max(location.start[1],location.end[1])
							self.locations[tag] = self.ui.mapCanvas.create_rectangle(x1,y1, x2,y2, width=2, outline='#0080ff', stipple='gray75', tags=tag) #, fill='#5555FF'
							self.ui.mapCanvas.create_text(x1+2,y1+2, anchor=NW, text=name, font=('courier', -10, 'normal'), fill='#00FF00', width=x2-x1-4, tags=tag + '-name')
 			else:
 				for tag in self.locations.keys():
 					self.ui.mapCanvas.delete(tag)
 					self.ui.mapCanvas.delete(tag + '-name')
 				self.locations = {}

class EditLayerUnits(EditLayer):
	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Units")

class EditLayerSprites(EditLayer):
	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Sprites")

class EditLayerPreviewFog(EditLayer):
	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Preview Fog")

class MinimapLayer:
	def __init__(self, ui):
		self.ui = ui
		self.image = None
		self.scaled_raw = None
		self.scaled = None
		self.size = None

	def redraw(self):
		self.image = None
		if not self.ui.chk:
			return
		dims = self.ui.chk.sections[CHKSectionDIM.NAME]
		points = min(256 / dims.width, 256 / dims.height)
		size = (dims.width*points,dims.height*points)
		self.image = PILImage.new('RGBA', size)
		drawer = PILDraw.ImageDraw(self.image)
		self.draw(drawer, size, points)

	def draw(self, drawer, size, points):
		pass

	def get_image(self, size):
		if size == self.size and self.scaled:
			return self.scaled
		if not self.image:
			return None
		scale = min(size[0] / float(self.image.size[0]),size[1] / float(self.image.size[1]))
		self.size = (int(round(self.image.size[0] * scale)), int(round(self.image.size[1] * scale)))
		self.scaled_raw = self.image.resize(self.size)
		self.scaled = ImageTk.PhotoImage(self.scaled_raw)
		return self.scaled

class MinimapLayerTerrain(MinimapLayer):
	def draw(self, drawer, size, points):
		dims = self.ui.chk.sections[CHKSectionDIM.NAME]
		tiles = self.ui.chk.sections[CHKSectionTILE.NAME]
		for y in range(dims.width):
			for x in range(dims.height):
				tile = [0,0]
				if y < len(tiles.map) and x < len(tiles.map[y]):
					tile = tiles.map[y][x]
				group = self.ui.tileset.cv5.groups[tile[0]]
				mega = group[13][tile[1]]
				minis = self.ui.tileset.vx4.graphics[mega]
				mini = minis[0]
				mini_image = self.ui.tileset.vr4.images[mini[0]]
				index = mini_image[7][2 if mini[1] else 6]
				color = self.ui.tileset.wpe.palette[index] + [255]
				drawer.rectangle((x*points,y*points,x*points+points,y*points+points), fill=tuple(color))

class MinimapLayerUnits(MinimapLayer):
	def draw(self, drawer, size, points):
		dims = self.ui.chk.sections[CHKSectionDIM.NAME]
		unit = self.ui.chk.sections[CHKSectionUNIT.NAME]
		def compare(unit1, unit2):
			elevation1 = self.ui.unitsdat.get_value(unit1.unitID, 'ElevationLevel')
			elevation2 = self.ui.unitsdat.get_value(unit2.unitID, 'ElevationLevel')
			if elevation1 < elevation2:
				return -1
			if elevation1 > elevation2:
				return 1
			if unit1.position[0] < unit2.position[1]:
				return -1
			if unit1.position[0] > unit2.position[1]:
				return 1
			return 0
		print len(unit.units)
		units = sorted(unit.units, cmp=compare)
		colr = self.ui.chk.sections[CHKSectionCOLR.NAME]
		for unit in units:
			w = self.ui.unitsdat.get_value(unit.unitID, 'StarEditPlacementBoxWidth') / (dims.width*32.0) * size[0]
			h = self.ui.unitsdat.get_value(unit.unitID, 'StarEditPlacementBoxHeight') / (dims.height*32.0) * size[0]
			x = unit.position[0] / (dims.width*32.0) * size[0] - w/2.0
			y = unit.position[1] / (dims.height*32.0) * size[1] - h/2.0
			color = CHKSectionCOLR.NEUTRAL
			if unit.owner < 8:
				color = colr.colors[unit.owner]
			color = self.ui.tileset.wpe.palette[CHKSectionCOLR.PALETTE_INDICES(color)] + [255]
			drawer.rectangle((x, y, x+w, y+h), fill=tuple(color))

class MapLayer:
	def __init__(self, ui):
		self.ui = ui

	def update_display(self, x1,y1, x2,y2):
		pass

class MapLayerTerrain(MapLayer):
	def __init__(self, ui):
		MapLayer.__init__(self, ui)
		self.tile_cache = {}
		self.map = {}

	def update_display(self, x1,y1, x2,y2):
		tiles = self.ui.chk.sections[CHKSectionTILE.NAME]
		tx1 = int(x1 / 32.0)
		ty1 = int(y1 / 32.0)
		tx2 = int(ceil(x2 / 32.0))
		ty2 = int(ceil(y2 / 32.0))
		for y in range(ty1,ty2):
			for x in range(tx1,tx2):
				tag = '%s,%s' % (x,y)
				item = self.map.get(tag)
				if not item:
					tile = [0,0]
					if y < len(tiles.map) and x < len(tiles.map[y]):
						tile = tiles.map[y][x]
					group = self.ui.tileset.cv5.groups[tile[0]]
					mega = group[13][tile[1]]
					image = self.tile_cache.get(mega)
					if image == None:
						image = Tilesets.megatile_to_photo(self.ui.tileset, mega)
						self.tile_cache[mega] = image
					self.map[tag] = self.ui.mapCanvas.create_image((x+0.5) * 32, (y+0.5) * 32, image=image, tags=tag)
					self.ui.mapCanvas.tag_lower(tag)

class PyMAP(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyMAP',
			{
				'profiles':{
					'Default':{
						'stat_txt':'MPQ:rez\\stat_txt.tbl',
						'aiscript':'MPQ:scripts\\aiscript.bin',
						'imagestbl':'MPQ:rez\\images.tbl',
						'sfxdatatbl':'MPQ:rez\\sfxdata.tbl',
						'portdatatbl':'MPQ:rez\\portdata.tbl',
						'mapdatatbl':'MPQ:rez\\mapdata.tbl',
						'iscriptbin':'MPQ:scripts\\iscript.bin',
						'unitsdat':'MPQ:arr\\units.dat',
						'spritesdat':'MPQ:arr\\sprites.dat',
						'imagesdat':'MPQ:arr\\images.dat'
					}
				},
				'profile':'Default'
			}
		)
		#Window
		Tk.__init__(self)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyTILE.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyTILE.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		setup_trace(self, 'PyMAP')

		# self.dosave = [False,False]
		self.profile = self.settings['profiles'][self.settings['profile']]
		self.stat_txt = None
		self.unitsdat = None
		self.aibin = None

		self.map = None
		self.chk = None
		self.file = None
		self.edited = False
		self.tileset = None

		self.minimap_raw_image = None

		self.editlayer_terrain = EditLayerTerrain(self)
		self.editlayer_doodads = EditLayerDoodads(self)
		self.editlayer_fogofwar = EditLayerFogOfWar(self)
		self.editlayer_locations = EditLayerLocations(self)
		self.editlayer_units = EditLayerUnits(self)
		self.editlayer_sprites = EditLayerSprites(self)
		self.editlayer_previewfog = EditLayerPreviewFog(self)
		self.edit_layers = [self.editlayer_terrain,self.editlayer_doodads,self.editlayer_fogofwar,self.editlayer_locations,self.editlayer_units,self.editlayer_sprites,self.editlayer_previewfog]
		self.current_editlayer = None

		self.minimaplayer_terrain = MinimapLayerTerrain(self)
		self.minimaplayer_units = MinimapLayerUnits(self)
		self.minimap_layers = [self.minimaplayer_terrain,self.minimaplayer_units]

		self.maplayer_terrain = MapLayerTerrain(self)
		self.map_layers = [self.maplayer_terrain]

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			2,
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			2,
			('asc3topyai', self.file_settings, 'Manage data files (Ctrl+M)', NORMAL, 'Ctrl+M'),
			10,
			('register', self.register, 'Set as default map editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyMAP', NORMAL, ''),
			10,
			('exit', self.exit, 'Exit (Alt+F4)', NORMAL, 'Alt+F4'),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2])
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
				a = btn[4]
				if a:
					if not a.startswith('F'):
						self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
					else:
						self.bind('<%s>' % a, btn[1])
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		self.edit_layer_index = IntVar(0)
		self.edit_layer_index.trace('w', self.change_edit_layer)
		DropDown(toolbar, self.edit_layer_index, [l.name for l in self.edit_layers], width=25).pack(side=LEFT, padx=2)
		toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.panes = PanedWindow(self, orient=HORIZONTAL)
		self.panes.pack(fill=BOTH, expand=1)

		left = Frame(self.panes)
		self.panes.add(left)
		minimap_wide_container = Frame(left, bd=1, relief=SUNKEN)
		def place_minimap_wide_container():
			minimap_wide_container.place(in_=left, x=0,y=0, width=left.winfo_width(),height=min(left.winfo_width(),262))
		place_minimap_wide_container()
		minimap_container = Frame(left, bd=1, relief=SUNKEN)
		def place_minimap_container():
			size = minimap_wide_container.winfo_height() - 6
			pad = (minimap_wide_container.winfo_width() - size)/2.0
			minimap_container.place(in_=minimap_wide_container, x=pad,y=2, width=size,height=size)
			self.resized_minimap()
		self.minimap = Canvas(minimap_container, background='#000000', highlightthickness=0)
		self.minimap.bind('<Button-1>', self.minimap_move)
		self.minimap.bind('<B1-Motion>', self.minimap_move)
		self.minimap.pack(fill=BOTH, expand=1)
		place_minimap_container()
		details = Frame(left)
		# listbox
		self.listbox = TreeList(details, groupsel=False, closeicon=os.path.join(BASE_DIR,'Images','treeclose.gif'), openicon=os.path.join(BASE_DIR,'Images','treeopen.gif'))
		self.listbox.pack(fill=BOTH, expand=True)
		self.listbox.bind('<Button-1>', self.list_select)
		def place_details():
			y = minimap_wide_container.winfo_height() + 5
			details.place(in_=left, x=0,y=y, width=left.winfo_width(),height=left.winfo_height()-y)
		place_details()
		def place_left_children(event=None):
			place_minimap_wide_container()
			place_minimap_container()
			place_details()
		left.bind('<Configure>', place_left_children)
		self.after(500, place_left_children)

		self.panes.paneconfigure(left, minsize=128)

		right = Frame(self.panes, bd=1, relief=SUNKEN)
		self.panes.add(right)

		self.mapCanvas = Canvas(right, background='#000000', highlightthickness=0)
		self.mapCanvas.grid(sticky=NSEW)
		self.mapCanvas.bind('<Motion>', self.edit_update)
		print self.mapCanvas.tag_raise.__doc__

		xscrollbar = Scrollbar(right, orient=HORIZONTAL)
		xscrollbar.config(command=self.mapCanvas.xview)
		xscrollbar.grid(sticky=EW)
		yscrollbar = Scrollbar(right)
		yscrollbar.config(command=self.mapCanvas.yview)
		yscrollbar.grid(sticky=NS, row=0, column=1)
		def scroll(l,h,bar):
			bar.set(l,h)
			self.update_viewport()
		self.mapCanvas.config(xscrollcommand=lambda l,h,s=xscrollbar: scroll(l,h,s),yscrollcommand=lambda l,h,s=yscrollbar: scroll(l,h,s))
		right.grid_rowconfigure(0,weight=1)
		right.grid_columnconfigure(0,weight=1)


		if 'pane' in self.settings:
			self.panes.sash_place(0, *self.settings['pane'])

		#Statusbar
		self.status = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, width=75, anchor=W).pack(side=LEFT, padx=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load or create a Map.')
		statusbar.pack(side=BOTTOM, fill=X)

		self.update_title()

		if 'window' in self.settings:
			loadsize(self, self.settings, 'window', True)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if not 'mpqs' in self.settings:
			self.mpqhandler.add_defaults()
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self,))

		if e:
			self.file_settings(err=e)

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			stat_txt = TBL.TBL()
			stat_txt.load_file(self.mpqhandler.get_file(self.profile['stat_txt']))
			imagestbl = TBL.TBL()
			imagestbl.load_file(self.mpqhandler.get_file(self.profile['imagestbl']))
			unitsdat = DAT.UnitsDAT(stat_txt)
			unitsdat.load_file(self.mpqhandler.get_file(self.profile['unitsdat']))
			spritesdat = DAT.SpritesDAT(stat_txt)
			spritesdat.load_file(self.mpqhandler.get_file(self.profile['spritesdat']))
			imagesdat = DAT.ImagesDAT(stat_txt)
			imagesdat.load_file(self.mpqhandler.get_file(self.profile['imagesdat']))
			aibin = AIBIN.AIBIN()
			aibin.load_file(self.mpqhandler.get_file(self.profile['aiscript']))
		except PyMSError, e:
			err = e
		else:
			self.stat_txt = stat_txt
			self.imagestbl = imagestbl
			self.unitsdat = unitsdat
			self.aibin = aibin
		self.mpqhandler.close_mpqs()
		return err

	def file_settings(self, key=None, err=None):
		data = [
			('File Settings',[
				('stat_txt.tbl', 'Contains Unit and AI Script names', ('profile','stat_txt'), 'TBL'),
				('aiscript.bin', "Contains AI ID's and references to names in stat_txt.tbl", ('profile','aiscript'), 'AIBIN'),
			])
		]
		SettingsDialog(self, data, (340,215), err)

	def change_edit_layer(self, *args):
		self.set_editmode(self.edit_layers[self.edit_layer_index.get()])

	def set_editmode(self, layer):
		coords = self.viewport_coords()
		if self.current_editlayer:
			self.current_editlayer.set_mode(EditLayer.INACTIVE, *coords)
		self.current_editlayer = layer
		self.current_editlayer.set_mode(EditLayer.ACTIVE, *coords)
		self.edit_layer_index.set(self.edit_layers.index(self.current_editlayer))

	def edit_update(self, event):
		if not self.chk:
			return
		dims = self.chk.sections[CHKSectionDIM.NAME]
		map_size = (dims.width*32, dims.height*32)
		x1,x2 = self.mapCanvas.xview()
		y1,y2 = self.mapCanvas.yview()
		for layer in self.edit_layers:
			layer.update_display(map_size[0]*x1,map_size[1]*y1, map_size[0]*x2,map_size[1]*y2,event.x,event.y)

	def minimap_move(self, event):
		if not self.chk:
			return
		dims = self.chk.sections[CHKSectionDIM.NAME]
		points = min(256 / dims.width, 256 / dims.height)
		size = (dims.width*points,dims.height*points)
		minimap_size = (self.minimap.winfo_width(), self.minimap.winfo_height())
		scale = min(minimap_size[0] / float(size[0]),minimap_size[1] / float(size[1]))
		map_size = (int(round(size[0] * scale)), int(round(size[1] * scale)))
		offset = ((minimap_size[0]-map_size[0])/2.0,(minimap_size[1]-map_size[1])/2.0)
		x = (event.x - offset[0]) / float(map_size[0])
		y = (event.y - offset[1]) / float(map_size[1])
		l,h = self.mapCanvas.xview()
		x -= (h - l) / 2.0
		l,h = self.mapCanvas.yview()
		y -= (h - l) / 2.0
		self.mapCanvas.xview_moveto(x)
		self.mapCanvas.yview_moveto(y)

	def redraw_minimap(self):
		for layer in self.minimap_layers:
			layer.redraw()
		self.resized_minimap()

	def viewport_coords(self):
		dims = self.chk.sections[CHKSectionDIM.NAME]
		x1,x2 = self.mapCanvas.xview()
		y1,y2 = self.mapCanvas.yview()
		map_size = (dims.width*32, dims.height*32)
		return (map_size[0]*x1,map_size[1]*y1, map_size[0]*x2,map_size[1]*y2)

	def update_viewport(self):
		if self.chk:
			dims = self.chk.sections[CHKSectionDIM.NAME]
			points = min(256 / dims.width, 256 / dims.height)
			size = (dims.width*points,dims.height*points)
			minimap_size = (self.minimap.winfo_width(), self.minimap.winfo_height())
			scale = min(minimap_size[0] / float(size[0]),minimap_size[1] / float(size[1]))
			map_size = (int(round(size[0] * scale)), int(round(size[1] * scale)))
			offset = ((minimap_size[0]-map_size[0])/2.0,(minimap_size[1]-map_size[1])/2.0)
			x1,x2 = self.mapCanvas.xview()
			y1,y2 = self.mapCanvas.yview()
			self.minimap.coords('viewport', offset[0]+map_size[0]*x1,map_size[1]*y1, offset[1]+map_size[0]*x2,map_size[1]*y2)
			map_size = (dims.width*32, dims.height*32)
			coords = (map_size[0]*x1,map_size[1]*y1, map_size[0]*x2,map_size[1]*y2)
			for layer in self.map_layers:
				layer.update_display(*coords)

	def resized_minimap(self):
		self.minimap.delete(ALL)
		for layer in self.minimap_layers:
			image = layer.get_image((self.minimap.winfo_width(),self.minimap.winfo_height()))
			if image:
				self.minimap.create_image(self.minimap.winfo_width()/2.0, self.minimap.winfo_height()/2.0, image=image)
		self.minimap.create_rectangle(0, 0, 0, 0, outline='#FFFFFF', tags='viewport')
		self.update_viewport()

	def setup_list(self):
		self.list_options = {}
		groupId = self.listbox.insert('-1', 'Terrain', False)
		self.editlayer_terrain.list_group = groupId
		groupId = self.listbox.insert('-1', 'Locations', False)
		self.editlayer_locations.list_group = groupId
		locations = self.chk.sections.get(CHKSectionMRGN.NAME)
		if locations:
			strings = self.chk.sections[CHKSectionSTR.NAME]
			for l,location in enumerate(locations.locations):
				if location.inUse():
					name = strings.strings[location.name]
					name = TBL.decompile_string(name)
					listId = self.listbox.insert(groupId + '.-1', name)
					self.list_options[listId] = (self.editlayer_locations, l)
		groupId = self.listbox.insert('-1', 'Units', False)
		self.editlayer_units.list_group = groupId
		groups = {}
		for u in range(self.unitsdat.count):
			race = 'Neutral'
			flags = self.unitsdat.get_value(u,'StarEditGroupFlags')
			if flags & 1:
				race = 'Zerg'
			elif flags & 2:
				race = 'Terran'
			elif flags & 4:
				race = 'Protoss'
			raceGroup = groups.get(race, {})
			if not race in groups:
				groups[race] = raceGroup
			name = self.stat_txt.strings[u]
			split = name.split('\0')
			if len(split) == 4:
				groupName = split[-2]
			else:
				groupName = 'Other'
			items = raceGroup.get(groupName, [])
			if not groupName in raceGroup:
				raceGroup[groupName] = items
			items.append({'name':TBL.decompile_string(name), 'id':u})
		for raceName in sorted(groups.keys(), reverse=True):
			raceGroupId = self.listbox.insert(groupId + '.-1', raceName, False)
			for groupName in sorted(groups[raceName]):
				subGroupId = self.listbox.insert(raceGroupId + '.-1', groupName, False)
				for info in groups[raceName][groupName]:
					listId = self.listbox.insert(subGroupId + '.-1', info['name'])
					self.list_options[listId] = (self.editlayer_units, info['id'])
		# self.listbox.insert(groupId + '.-1', name)
		groupId = self.listbox.insert('-1', 'Sprites', False)
		self.editlayer_sprites = groupId
		groupId = self.listbox.insert('-1', 'Doodads', False)
		self.editlayer_doodads = groupId

	def list_select(self, event=None):
		selected = self.listbox.cur_selection()
		if selected and selected[0] > -1:
			list_index = self.listbox.index(selected[0])
			print list_index
			layer,select = self.list_options.get(list_index, (None,None))
			print layer,select
			if layer:
				if layer != self.current_editlayer:
					self.set_editmode(layer)
				layer.list_select(select)

	def unsaved(self):
		if self.chk and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.scx'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def select_file(self, title, open=True, ext='.scx', filetypes=[('BroodWar Map','*.scx'),('StarCraft Map','*.scm'),('Raw Map','*.chk'),('All Files','*')], parent=None):
		if parent == None:
			parent = self
		path = self.settings.get('lastpath', BASE_DIR)
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](title=title, defaultextension=ext, filetypes=filetypes, initialdir=path, parent=parent)
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		file = [NORMAL,DISABLED][not self.chk]
		for btn in ['save','saveas','close']:
			self.buttons[btn]['state'] = file
		self.buttons['asc3topyai']['state'] = [NORMAL,DISABLED][not not self.chk]

	def update_title(self, file=None):
		title = 'PyMAP %s' % LONG_VERSION
		if file == None and self.file:
			file = os.path.basename(self.file)
		if file:
			title += ' (%s)' % file
		self.title(title)

	def new(self, key=None):
		if not self.unsaved():
			self.chk = CHK()
			self.file = None
			self.status.set('Editing new Map.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.update_title('Unnamed.scx')
			self.action_states()

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.select_file('Open Map')
				if not file:
					return
			scmap = None
			if not file.endswith('.chk'):
				scmap = MpqOpenArchiveForUpdateEx(file)
				if SFInvalidHandle(scmap):
					scmap = None
			chk = CHK()
			chkfile = None
			tileset = None
			try:
				if scmap:
					chkfile = SFileOpenFileEx(scmap, 'staredit\\scenario.chk')
					if not SFInvalidHandle(chkfile):
						data = SFileReadFile(chkfile)[0]
						chk.load_data(data)
						SFileCloseFile(chkfile)
						chkfile = None
					SFileCloseArchive(scmap)
				else:
					chk.load_file(file)
				era = chk.sections.get(CHKSectionERA.NAME)
				if era:
					tilesetName = CHKSectionERA.TILESET_FILE(era.tileset)
					tilesetPaths = [
						'MPQ:tileset\\%s.cv5',
						'MPQ:tileset\\%s.vf4',
						'MPQ:tileset\\%s.vx4',
						'MPQ:tileset\\%s.vr4',
						'MPQ:tileset\\%s\\dddata.bin',
						'MPQ:tileset\\%s.wpe'
					]
					tilesetFiles = []
					self.mpqhandler.open_mpqs()
					for pathFormat in tilesetPaths:
						path = pathFormat % tilesetName
						tilesetFile = self.mpqhandler.get_file(path)
						# if isinstance(tilesetFile, BadFile):
						# 	path = pathFormat % (tilesetName + '-nc')
						# 	tilesetFile = self.mpqhandler.get_file(path)
						# 	if isinstance(tilesetFile, BadFile):
						# 		path = pathFormat % (tilesetName[0].upper() + tilesetName[1:])
						# 		tilesetFile = self.mpqhandler.get_file(path)
						if isinstance(tilesetFile, BadFile):
							break
						tilesetFiles.append(tilesetFile)
					if len(tilesetFiles) == len(tilesetPaths):
						tileset = Tilesets.Tileset()
						tileset.load_file(*tilesetFiles)
					self.mpqhandler.close_mpqs()
			except PyMSError, e:
				self.mpqhandler.close_mpqs()
				if not SFInvalidHandle(chkfile):
					SFileCloseFile(chkfile)
				if scmap:
					SFileCloseArchive(scmap)
				ErrorDialog(self, e)
				return
			if not chk or not chk.sections:
				askquestion(parent=self, title='Open', message='"%s" is not a valid map.' % file, type=OK)
				return
			if not tileset:
				askquestion(parent=self, title='Open', message='"%s" has an invalid tileset.' % file, type=OK)
				return
			self.scmap = scmap
			self.chk = chk
			self.tileset = tileset
			self.file = file
			self.edited = False
			dims = self.chk.sections[CHKSectionDIM.NAME]
			self.mapCanvas.config(scrollregion=(0,0,dims.width*32,dims.height*32))
			self.update_title()
			self.status.set('Load successful!')
			self.editstatus['state'] = DISABLED
			self.action_states()
			self.setup_list()
			self.redraw_minimap()
			self.set_editmode(self.editlayer_terrain)

	def save(self, key=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.chk.save_file(self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
		except PyMSError, e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.select_file('Save Map As', False)
		if not file:
			return True
		self.file = file
		self.save()

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.edited = False
			self.chk = None
			self.file = None
			self.edited = False
			self.update_title()
			self.status.set('Load or create a Map.')
			self.editstatus['state'] = DISABLED
			self.action_states()
			self.listbox.delete(ALL)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyMAP.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyMAP', LONG_VERSION, [('staredit.net','CHK file specs.')])

	def exit(self, e=None):
		if not self.unsaved():
			savesize(self, self.settings)
			self.settings['pane'] = self.panes.sash_coord(0)
			try:
				f = file(os.path.join(BASE_DIR,'Settings','PyMAP.txt'),'w')
				f.write(pprint(self.settings))
				f.close()
			except:
				pass
			self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pymap.py','pymap.pyw','pymap.exe']):
		gui = PyMAP()
		gui.mainloop()
	else:
		p = optparse.OptionParser(usage='usage: PyMAP [options]', version='PyMAP %s' % LONG_VERSION)
		# p.add_option('-v', '--vf4', metavar='FILE', help='Choose a palette for GRP to BMP conversion [default: %default]', default='')
		# p.add_option('-p', '--palette', metavar='FILE', help='Choose a palette for GRP to BMP conversion [default: %default]', default='Units.pal')
		# p.add_option('-g', '--grptobmps', action='store_true', dest='convert', help="Converting from GRP to BMP's [default]", default=True)
		# p.add_option('-b', '--bmpstogrp', action='store_false', dest='convert', help="Converting from BMP's to GRP")
		# p.add_option('-u', '--uncompressed', action='store_true', help="Used to signify if the GRP is uncompressed (both to and from BMP) [default: Compressed]", default=False)
		# p.add_option('-o', '--onebmp', action='store_true', help='Used to signify that you want to convert a GRP to one BMP file. [default: Multiple]', default=False)
		# p.add_option('-f', '--frames', type='int', help='Used to signify you are using a single BMP with alll frames, and how many frames there are.', default=0)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyMAP(opt.gui)
			gui.mainloop()

if __name__ == '__main__':
	# import profile
	# profile.run('main()')
	main()