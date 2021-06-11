
import AbstractDAT
import DATFormat

class Sound(AbstractDAT.AbstractDATEntry):
	class Property:
		sound_file = 'sound_file'
		priority = 'priority'
		flags = 'flags'
		portrait_length_adjust = 'portrait_length_adjust'
		minimum_volume = 'minimum_volume'

	class Flag:
		preload       = 1 << 0
		unit_speech   = 1 << 1
		one_at_a_time = 1 << 4
		never_preempt = 1 << 5

		ALL_FLAGS = (preload | unit_speech | one_at_a_time | never_preempt)

	def __init__(self):
		self.sound_file = 0
		self.priority = 0
		self.flags = 0
		self.portrait_length_adjust = 0
		self.minimum_volume = 0

	def load_values(self, values):
		self.sound_file,\
		self.priority,\
		self.flags,\
		self.portrait_length_adjust,\
		self.minimum_volume\
			= values

	def save_values(self):
		return (
			self.sound_file,
			self.priority,
			self.flags,
			self.portrait_length_adjust,
			self.minimum_volume
		)

	EXPORT_NAME = 'Sound'
	def _export(self, export_properties, export_type, data):
		self._export_property_value(export_properties, Sound.Property.sound_file, self.sound_file, export_type, data)
		self._export_property_value(export_properties, Sound.Property.priority, self.priority, export_type, data)
		self._export_property_value(export_properties, Sound.Property.flags, self.flags, export_type, data)
		self._export_property_value(export_properties, Sound.Property.portrait_length_adjust, self.portrait_length_adjust, export_type, data)
		self._export_property_value(export_properties, Sound.Property.minimum_volume, self.minimum_volume, export_type, data)

# sfxdata.dat file handler
class SoundsDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 1144,
			"expanded_max_entries": 65536,
			"properties": [
				{
					"name": "sound_file", # Pointer to sfxdata.tbl
					"type": "long"
				},
				{
					"name": "priority",
					"type": "byte"
				},
				{
					"name": "flags",
					"type": "byte"
				},
				{
					"name": "portrait_length_adjust",
					"type": "short"
				},
				{
					"name": "minimum_volume",
					"type": "byte"
				}
			]
		})
	ENTRY_STRUCT = Sound
	FILE_NAME = "sfxdata.dat"