
class PyMSError(Exception):
	def __init__(self, type, error, line=None, code=None, warnings=[], exception=None):
		self.type = type
		self.error = error
		self.line = line
		if self.line != None:
			self.line += 1
		self.code = code
		self.warnings = warnings
		self.exception = exception

	def repr(self):
		r = '%s Error: %s' % (self.type, self.error)
		if self.line:
			r += '\n    Line %s: %s' % (self.line, self.code)
		return r

	def __repr__(self):
		from utils import fit
		r = fit('%s Error: ' % self.type, self.error)
		if self.line:
			r += fit('    Line %s: ' % self.line, self.code)
		if self.warnings:
			for w in self.warnings:
				r += repr(w)
		return r[:-1]

	def __str__(self):
		return repr(self)