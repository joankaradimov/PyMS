from utils import *
from fileutils import *

import sys,struct,itertools
try:
	from PIL import Image as PILImage
	from PIL import ImageTk
except:
	try:
		import ImageTk
	except:
		e = DependencyError('PyMS','PIL is missing. Consult the Source Installation section of the Documentation.', ('Documentation','file:///%s' % os.path.join(BASE_DIR, 'Docs', 'intro.html')))
		e.mainloop()
		sys.exit()

def rle_normal(pal, index, player_colors=None):
	rgb = pal[index]
	if player_colors != None and len(player_colors) >= 8 and 8 <= index <= 15:
		rgb = player_colors[index - 8]
	return (rgb[0],rgb[1],rgb[2], 255)

def rle_shadow(pal, index, _=None):
	return (0,0,0, 255)

OUTLINE_ENEMY = 0
OUTLINE_SELF = 1
OUTLINE_ALLY = 2
def rle_outline(pal, index, ally_status=OUTLINE_SELF):
	rgb = pal[index]
	if 1 <= index <= 9:
		if ally_status == OUTLINE_ENEMY:
			rgb = (155,21,23)
		elif ally_status == OUTLINE_SELF:
			rgb = (36,152,36)
		else:
			rgb = (220,220,60)
	return (rgb[0],rgb[1],rgb[2], 255)

def image_bounds(image, transindex=0):
	width = len(image[0])
	bounds = [-1,-1,-1,-1]
	for y,yd in enumerate(image):
		if yd.count(transindex) != width:
			if bounds[1] == -1:
				bounds[1] = y
			bounds[3] = y + 1
			line = yd
			for x,xd in enumerate(line):
				if xd != transindex:
					if bounds[0] == -1 or x < bounds[0]:
						bounds[0] = x
					if x + 1 > bounds[2]:
						bounds[2] = x + 1
	return bounds

# transindex=None for no transparency
def image_to_pil(image, palette, transindex=0, image_bounds=None, flipHor=False, draw_function=rle_normal, draw_info=None):
	if image_bounds:
		x_min,y_min,x_max,y_max = image_bounds
		image = list(line[x_min:x_max+1] for line in image[y_min:y_max+1])
	width = len(image[0])
	height = len(image)
	i = PILImage.new('RGBA', (width,height))
	data = []
	pal = map(lambda i: draw_function(palette,i,draw_info), xrange(len(palette)))
	if transindex != None:
		pal[transindex] = (0,0,0,0)
	if flipHor:
		image = map(reversed, image)
	data = itertools.chain.from_iterable(image)
	data = map(pal.__getitem__, data)
	i.putdata(data)
	return i

def image_to_tk(image, palette, transindex=0, image_bounds=None, flipHor=False, draw_function=rle_normal, draw_info=None):
	pil = image_to_pil(image, palette, transindex, image_bounds, flipHor, draw_function, draw_info)
	return ImageTk.PhotoImage(pil)

def frame_to_photo(p, g, f=None, buffered=False, size=True, trans=True, transindex=0, flipHor=False, draw_function=None, draw_info=None):
	if f != None:
		if buffered:
			d = g[f]
		elif f == -1:
			d = g.image
		else:
			d = g.images[f]
			transindex = g.transindex
	else:
		d = g
	i = PILImage.new('RGBA', (len(d[0]),len(d)))
	data = []
	pal = []
	if draw_function == None:
		draw_function = rle_normal
	pal = map(lambda i,p=p,e=draw_info: draw_function(p,i,e), xrange(len(p)))
	pal[transindex] = (0,0,0,0)
	if size:
		image = [None,-1,-1,-1,-1]
		for y,yd in enumerate(d):
			if yd.count(transindex) != g.width:
				if image[3] == -1:
					image[3] = y
				image[4] = y + 1
				line = yd
				if flipHor:
					line = reversed(line)
				for x,xd in enumerate(line):
					if xd != transindex:
						if image[1] == -1 or x < image[1]:
							image[1] = x
						if x >= image[2]:
							image[2] = x + 1
					data.append(pal[xd])
			else:
				data.extend([(0,0,0,0) for _ in range(g.width)])
		i.putdata(data)
		image[0] = ImageTk.PhotoImage(i)
		return image
	else:
		if flipHor:
			d = map(reversed, d)
		data = itertools.chain.from_iterable(d)
		data = map(pal.__getitem__, data)
		i.putdata(data)
		return ImageTk.PhotoImage(i)

class RLE:
	TRANSPARENT_FLAG = (1 << 7)
	TRANSPARENT_MAX_LENGTH = TRANSPARENT_FLAG - 1
	REPEAT_FLAG = (1 << 6)
	REPEAT_MAX_LENGTH = REPEAT_FLAG - 1
	STATIC_MAX_LENGTH = REPEAT_FLAG - 1

	@staticmethod
	def encode_transparent(count): # type: (int) -> str
		encoded = ''
		while count > 0:
			encoded += struct.pack('<B', RLE.TRANSPARENT_FLAG | min(RLE.TRANSPARENT_MAX_LENGTH, count))
			count -= RLE.TRANSPARENT_MAX_LENGTH
		return encoded

	@staticmethod
	def encode_repeat(index, count): # type: (int, int) -> str
		encoded = ''
		while count > 0:
			encoded += struct.pack('<BB', RLE.REPEAT_FLAG | min(RLE.REPEAT_MAX_LENGTH, count), index)
			count -= RLE.REPEAT_MAX_LENGTH
		return encoded

	@staticmethod
	def encode_static(line): # type: (list[int]) -> str
		encoded = ''
		for x in range(0, len(line), RLE.STATIC_MAX_LENGTH):
			run = line[x:x+RLE.STATIC_MAX_LENGTH]
			encoded += struct.pack('<%dB' % (1 + len(run)), len(run), *run)
		return encoded

	@staticmethod
	def compress_line(line, transparent_index): # type: (list[int], int) -> str
		last_index = line[0]
		repeat_count = 0
		static_len = 0
		compressed = ''
		for (x,index) in enumerate(line):
			if index == last_index:
				repeat_count += 1
			else:
				if last_index == transparent_index:
					compressed += RLE.encode_transparent(repeat_count)
				elif repeat_count > 1 and static_len < 2:
					compressed += RLE.encode_repeat(last_index, repeat_count)
				repeat_count =  1
			if repeat_count > 2 or index == transparent_index:
				if static_len > repeat_count-1:
					compressed += RLE.encode_static(line[x-static_len:x-repeat_count+1])
				static_len = 0
			else:
				static_len += 1
			last_index = index
		if last_index == transparent_index:
			compressed += RLE.encode_transparent(repeat_count)
		elif static_len and static_len > repeat_count:
			compressed += RLE.encode_static(line[-static_len:])
		elif repeat_count:
			compressed += RLE.encode_repeat(last_index, repeat_count)
		return compressed

class CacheGRP:
	def __init__(self, palette=[[0,0,0]]*256):
		self.frames = 0
		self.width = 0
		self.height = 0
		self.palette = palette
		self.imagebuffer = []
		self.images = {}
		self.image_frames = {}
		self.databuffer = ''
		self.uncompressed = None

	def load_file(self, file, palette=None, restrict=None, uncompressed=None):
		data = load_file(file, 'GRP')
		try:
			frames, width, height = struct.unpack('<3H',data[:6])
			if frames < 1 or frames > 2400 or width < 1 or width > 256 or height < 1 or height > 256:
				raise
			if restrict:
				frames = restrict
			images = []
			for frame in range(frames):
				xoffset, yoffset, linewidth, lines, framedata = struct.unpack('<4BL', data[6+8*frame:14+8*frame])
				d = [xoffset,yoffset,linewidth,lines,[]]
				for line in range(lines):
					d[4].append(framedata+struct.unpack('<H',data[framedata+2*line:framedata+2+2*line])[0])
				images.append(d)
		except:
			raise PyMSError('Load',"Unsupported GRP file '%s', could possibly be corrupt or an uncompressed GRP" % file,exception=sys.exc_info())
		self.frames = frames
		self.width = width
		self.height = height
		if palette:
			self.palette = list(palette)
		self.imagebuffer = images
		self.images = {}
		self.databuffer = data
		self.uncompressed = uncompressed

	def __getitem__(self, frame):
		if not frame in self.images:
			image = []
			xoffset, yoffset, linewidth, lines, offsets = self.imagebuffer[frame]
			if xoffset + linewidth > self.width:
				linewidth = self.width - xoffset
			if yoffset + lines > self.height:
				lines = self.height - yoffset
			image.extend([[0] * self.width for _ in xrange(yoffset)])
			if not self.uncompressed:
				try:
					for offset in offsets:
						linedata = []
						if xoffset > 0:
							linedata = [0] * xoffset
						while len(linedata)-xoffset < linewidth:
							o = ord(self.databuffer[offset])
							if o & 0x80:
								linedata.extend([0] * (o - 0x80))
								offset += 1
							elif o & 0x40:
								linedata.extend([ord(self.databuffer[offset+1])] * (o - 0x40))
								offset += 2
							else:
								linedata.extend(map(ord, self.databuffer[offset+1:offset+1+o]))
								offset += o + 1
						image.append(linedata[:xoffset+linewidth] + [0] * (self.width-linewidth-xoffset))
					if self.uncompressed == None:
						self.uncompressed = False
				except:
					if self.uncompressed == None:
						self.uncompressed = True
					else:
						raise PyMSError('Decompile','Could not decompile frame %s, GRP could be corrupt.' % frame)
			if self.uncompressed:
				try:
					for offset in offsets:
						linedata = []
						if xoffset > 0:
							linedata = [0] * xoffset
						linedata.extend([ord(index) for index in self.databuffer[offset:offset+linewidth]])
						image.append(linedata + [0] * (self.width-linewidth-xoffset))
				except:
					raise PyMSError('Decompile','Could not decompile frame %s, GRP could be corrupt.' % frame)
			if len(image) < self.height:
				image.extend([[0] * self.width for _ in range(self.height - len(image))])
			self.images[frame] = image[:self.height]
			self.image_frames[frame] = (xoffset,yoffset,linewidth,lines)
		return self.images[frame]

class GRP:
	def __init__(self, palette=[[0,0,0]]*256, uncompressed=None, transindex=0):
		self.frames = 0
		self.width = 0
		self.height = 0
		self.palette = palette
		self.images = []
		self.images_bounds = []
		self.uncompressed = uncompressed
		self.transindex = transindex

	def load_file(self, file, palette=None, transindex=0, uncompressed=None):
		data = load_file(file, 'GRP')
		try:
			frames, width, height = struct.unpack('<3H',data[:6])
			if frames < 1 or frames > 2400 or width < 1 or width > 256 or height < 1 or height > 256:
				raise
			retries = 2
			while retries:
				retries -= 1
				images = []
				images_bounds = []
				for frame in range(frames):
					image = []
					xoffset, yoffset, linewidth, lines, framedata = struct.unpack('<4BL', data[6+8*frame:14+8*frame])
					# ignore extra bytes
					if xoffset + linewidth > width:
						linewidth = width - xoffset
					if yoffset + lines > height:
						lines = height - yoffset
					# print frames,width,height,xoffset,yoffset,linewidth,lines,framedata
					image.extend([[0] * width for _ in range(yoffset)])
					if uncompressed:
						for line in range(lines):
							linedata = []
							if xoffset > 0:
								linedata = [transindex] * xoffset
							linedata.extend([ord(index) for index in data[framedata:framedata+linewidth]])
							image.append(linedata + [transindex] * (width-linewidth-xoffset))
							framedata += linewidth
					else:
						try:
							for line in range(lines):
								linedata = []
								if xoffset > 0:
									linedata = [transindex] * xoffset
								offset = framedata+struct.unpack('<H',data[framedata+2*line:framedata+2+2*line])[0]
								while len(linedata)-xoffset < linewidth:
									o = ord(data[offset])
									if o & 0x80:
										linedata.extend([transindex] * (o - 0x80))
										offset += 1
									elif o & 0x40:
										linedata.extend([ord(data[offset+1])] * (o - 0x40))
										offset += 2
									else:
										linedata.extend([ord(c) for c in data[offset+1:offset+1+o]])
										offset += o + 1
								image.append(linedata[:xoffset+linewidth] + [transindex] * (width-linewidth-xoffset))
						except:
							if uncompressed == None:
								uncompressed = True
								break
							raise
					if len(image) < height:
						image.extend([[transindex] * width for _ in range(height - len(image))])
					images.append(image[:height])
					images_bounds.append((xoffset,yoffset,xoffset+linewidth,yoffset+lines))
		except:
			raise PyMSError('Load',"Unsupported GRP file '%s', could possibly be corrupt" % file,exception=sys.exc_info())
		self.frames = frames
		self.width = width
		self.height = height
		self.uncompressed = uncompressed
		if palette:
			self.palette = list(palette)
		self.images = images
		self.images_bounds = images_bounds
		self.transindex = transindex

	def load_data(self, image, palette=None, transindex=0):
		self.frames = 1
		self.height = len(image)
		self.width = len(image[0])
		if palette:
			self.palette = list(palette)
		self.images = [list(image)]
		self.images_bounds = [image_bounds(image, transindex)]
		self.transindex = transindex

	def save_file(self, file, uncompressed=None):
		if isstr(file):
			try:
				f = AtomicWriter(file, 'wb')
			except:
				raise PyMSError('Save',"Could not save the GRP to '%s'" % file)
		else:
			f = file
		if uncompressed == None:
			uncompressed = self.uncompressed
		f.write(struct.pack('<3H', self.frames, self.width, self.height))
		image_data = ''
		offset = 6 + 8 * self.frames
		frame_history = {}
		for z,frame in enumerate(self.images):
			x_min, y_min, x_max, y_max = self.images_bounds[z]
			if uncompressed:
				data = ''.join(''.join(chr(i) for i in l[x_min:x_max]) for l in frame[y_min:y_max])
				if data in frame_history:
					f.write(frame_history[data])
				else:
					frame_data = struct.pack('<4BL', x_min, y_min, x_max - x_min, y_max - y_min, offset)
					f.write(frame_data)
					frame_history[data] = frame_data
					image_data += data
					offset += len(data)
			else:
				frame_hash = (x_min, x_max, y_min, y_max) + tuple(tuple(l[x_min:x_max]) for l in frame[y_min:y_max])
				# If there is a duplicate frame, just point to it
				if frame_hash in frame_history:
					f.write(frame_history[frame_hash])
				else:
					frame_data = struct.pack('<4BL', x_min, y_min, x_max - x_min, y_max - y_min, offset)
					frame_history[frame_hash] = frame_data
					f.write(frame_data)
					line_data = ''
					line_offset = 2 * (y_max - y_min)
					line_offsets = []
					line_history = {}
					for y,line in enumerate(frame[y_min:y_max]):
						line_hash = tuple(line)
						# If there is a duplicate line is this frame, just point to it
						if line_hash in line_history:
							line_offsets.append(line_history[line_hash])
						else:
							data = RLE.compress_line(line[x_min:x_max], self.transindex)s
							line_data += data
							if line_offset > 65535:
								raise PyMSError('Save','The image has too much pixel data to compile')
							line_offsets.append(struct.pack('<H', line_offset))
							line_history[line_hash] = line_offsets[-1]
							line_offset += len(data)
					line_data = ''.join(line_offsets) + line_data
					image_data += line_data
					offset += len(line_data)
		f.write(image_data)
		f.close()
