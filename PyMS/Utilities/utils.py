
from PyMSError import PyMSError

from tkMessageBox import askquestion, OK

from textwrap import wrap
from thread import start_new_thread
import os, sys, platform, re, tempfile, errno, codecs

WIN_REG_AVAILABLE = True
try:
	from _winreg import *
except:
	WIN_REG_AVAILABLE = False

if hasattr(sys, 'frozen'):
	BASE_DIR = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))
else:
	BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))))

import json
with open(os.path.join(BASE_DIR, 'PyMS', 'versions.json'), 'r') as f:
	VERSIONS = json.load(f)

couriernew = ('Courier', -12, 'normal')
couriersmall = ('Courier', -8, 'normal')
ARROW = None
TRANS_FIX = None

def is_windows():
	return (platform.system().lower() == 'windows')
def is_mac():
	return (platform.system().lower() == 'darwin')

def startup(toplevel):
	toplevel.lift()
	toplevel.call('wm', 'attributes', '.', '-topmost', True)
	toplevel.after_idle(toplevel.call, 'wm', 'attributes', '.', '-topmost', False)
	toplevel.focus_force()
	try:
		from Cocoa import NSRunningApplication, NSApplicationActivateIgnoringOtherApps

		app = NSRunningApplication.runningApplicationWithProcessIdentifier_(os.getpid())
		app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
	except:
		pass
	toplevel.mainloop()

# Decorator
def debug_func_log(should_log_call=None):
	def decorator(func):
		def do_log(*args, **kwargs):
			import uuid
			ref = uuid.uuid4().hex
			log = not should_log_call or should_log_call(func, args, kwargs)
			if log:
				print "Func  : %s (%s)" % (func.__name__, ref)
				print "\tArgs  : %s" % (args,)
				print "\tkwargs: %s" % kwargs
			result = func(*args, **kwargs)
			if log:
				print "Func  : %s (%s)" % (func.__name__, ref)
				print "\tResult: %s" % (result,)
			return result
		return do_log
	return decorator
def debug_state(states, history=[]):
	n = len(history)
	print '##### %d: %s' % (n, states[n] if n < len(states) else 'Unknown')
	history.append(None)

def parse_geometry(geometry):
	match = re.match(r'(?:(\d+)x(\d+))?\+(-?\d+)\+(-?\d+)(\^)?',geometry)
	return tuple(None if v == None else int(v) for v in match.groups()[:-1]) + (True if match.group(5) else False,)

def parse_scrollregion(scrollregion):
	return tuple(int(v) for v in scrollregion.split(' '))

def isstr(s):
	return isinstance(s,str) or isinstance(s,unicode)

def nearest_multiple(v, m, r=round):
	return m * int(r(v / float(m)))

def register_registry(prog,type,filetype,progpath,icon):
	if not WIN_REG_AVAILABLE:
		raise PyMSError('Registry', 'You can currently only set as the default program on Windows machines.')
	def delkey(key,sub_key):
		try:
			h = OpenKey(key,sub_key)
		except WindowsError, e:
			if e.errno == 2:
				return
			raise
		except:
			raise
		try:
			while True:
				n = EnumKey(h,0)
				delkey(h,n)
		except EnvironmentError:
			pass
		h.Close()
		DeleteKey(key,sub_key)

	key = '%s:%s' % (prog,filetype)
	try:
		delkey(HKEY_CLASSES_ROOT, '.' + filetype)
		delkey(HKEY_CLASSES_ROOT, key)
		SetValue(HKEY_CLASSES_ROOT, '.' + filetype, REG_SZ, key)
		SetValue(HKEY_CLASSES_ROOT, key, REG_SZ, 'StarCraft %s *.%s file (%s)' % (type,filetype,prog))
		SetValue(HKEY_CLASSES_ROOT, key + '\\DefaultIcon', REG_SZ, icon)
		SetValue(HKEY_CLASSES_ROOT, key + '\\Shell', REG_SZ, 'open')
		SetValue(HKEY_CLASSES_ROOT, key + '\\Shell\\open\\command', REG_SZ, '"%s" "%s" --gui "%%1"' % (sys.executable.replace('python.exe','pythonw.exe'),progpath))
	except:
		raise PyMSError('Registry', 'Could not complete file association.',exception=sys.exc_info())
	askquestion(title='Success!', message='The file association was set.', type=OK)

def flags(value, length):
	if isstr(value):
		if len(value) != length or value.replace('0','').replace('1',''):
			raise PyMSError('Flags', 'Invalid flags')
		return sum(int(x)*(2**n) for n,x in enumerate(reversed(value)))
	return ''.join(reversed([str(value/(2**n)%2) for n in range(length)]))

def ccopy(lst):
	r = []
	for item in lst:
		if isinstance(item, list):
			r.append(ccopy(item))
		else:
			r.append(item)
	return r

def fit(label, text, width=80, end=False, indent=0):
	r = label
	if not indent:
		s = len(r)
	else:
		s = indent
	indent = False
	for p in text.split('\n'):
		if p:
			for l in wrap(p, width - s):
				if indent:
					r += ' ' * s
				else:
					indent = True
				r += l
				r += '\n'
			r += '\n'
	return r.rstrip('\n') + '\n' if end else ''

def removedir(path):
	if os.path.exists(path):
		for r,ds,fs in os.walk(path, topdown=False):
			for f in fs:
				os.remove(os.path.join(r, f))
			for d in ds:
				p = os.path.join(r, d)
				removedir(p)
				os.rmdir(p)
		os.rmdir(path)

class odict:
	def __init__(self, d=None, k=None):
		self.keynames = []
		self.dict = {}
		if d:
			if k:
				self.keynames = list(k)
				self.dict = dict(d)
			else:
				self.keynames = list(d.keynames)
				self.dict = dict(d.dict)

	def __delitem__(self, key):
		del self.dict[key]
		self.keynames.remove(key)

	def __setitem__(self, key, item):
		self.dict[key] = item
		if key not in self.keynames:
			self.keynames.append(key)

	def __getitem__(self, key):
		return self.dict[key]

	def __contains__(self, key):
		if key in self.keynames:
			return True
		return False

	def __len__(self):
		return len(self.keynames)

	def iteritems(self):
		iter = []
		for k in self.keynames:
			iter.append((k,self.dict[k]))
		return iter

	def iterkeys(self):
		return list(self.keynames)

	def peek(self):
		return (self.keynames[0],self.dict[self.keynames[0]])

	def keys(self):
		return list(self.keynames)

	def index(self, key):
		return self.keynames.index(key)

	def get(self, key, default=None):
		if not key in self.keynames:
			return default
		return self.dict[key]

	def getkey(self, n):
		return self.keynames[n]

	def getitem(self, n):
		return self.dict[self.keynames[n]]

	def remove(self, n):
		self.keynames.remove(n)
		del self.dict[n]

	def __repr__(self):
		return '%s@%s' % (self.keynames,self.dict)

	def copy(self):
		return odict(self)

	def sort(self):
		self.keynames.sort()

def get_umask():
	umask = os.umask(0)
	os.umask(umask)
	return umask

def create_temp_file(name, createmode=None):
	directory, filename = os.path.split(name)
	handle, temp_file = tempfile.mkstemp(prefix=".%s-" % filename, dir=directory)
	os.close(handle)

	try:
		mode = os.lstat(name).st_mode & 0o777
	except OSError as e:
		if e.errno != errno.ENOENT:
			raise
		mode = createmode
		if mode == None:
			mode = ~get_umask()
		mode &= 0o666
	os.chmod(temp_file, mode)

	return temp_file

def apply_cursor(widget, cursors):
	for cursor in reversed(cursors):
		try:
			widget.config(cursor=cursor)
			return cursor
		except:
			pass

play_sound = None
try:
	from winsound import PlaySound, SND_MEMORY
	def win_play(raw_audio):
		start_new_thread(PlaySound, (raw_audio, SND_MEMORY))
	play_sound = win_play
except:
	import subprocess
	def osx_play(raw_audio):
		def do_play(path):
			try:
				subprocess.call(["afplay", temp_file])
			except:
				pass
			try:
				os.remove(path)
			except:
				pass
		temp_file = create_temp_file('audio')
		handle = open(temp_file, 'wb')
		handle.write(raw_audio)
		handle.flush()
		os.fsync(handle.fileno())
		handle.close()
		start_new_thread(do_play, (temp_file,))
	play_sound = osx_play

class FFile:
	def __init__(self):
		self.data = ''

	def read(self):
		return self.data

	def write(self, data):
		self.data += data

	def close(self):
		pass
