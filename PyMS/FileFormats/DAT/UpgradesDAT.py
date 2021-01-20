
import AbstractDAT
import DATFormat

from collections import OrderedDict
import json

class Upgrade(AbstractDAT.AbstractDATEntry):
	def __init__(self):
		self.mineral_cost_base = 0
		self.mineral_cost_factor = 0
		self.vespene_cost_base = 0
		self.vespene_cost_factor = 0
		self.research_time_base = 0
		self.research_time_factor = 0
		self.requirements = 0
		self.icon = 0
		self.label = 0
		self.staredit_race = 0
		self.max_repeats = 0
		self.broodwar_only = 0

	def load_values(self, values):
		self.mineral_cost_base,\
		self.mineral_cost_factor,\
		self.vespene_cost_base,\
		self.vespene_cost_factor,\
		self.research_time_base,\
		self.research_time_factor,\
		self.requirements,\
		self.icon,\
		self.label,\
		self.staredit_race,\
		self.max_repeats,\
		self.broodwar_only\
			= values

	def save_values(self):
		return (
			self.mineral_cost_base,
			self.mineral_cost_factor,
			self.vespene_cost_base,
			self.vespene_cost_factor,
			self.research_time_base,
			self.research_time_factor,
			self.requirements,
			self.icon,
			self.label,
			self.staredit_race,
			self.max_repeats,
			self.broodwar_only
		)

	def expand(self):
		self.mineral_cost_base = self.mineral_cost_base or 0
		self.mineral_cost_factor = self.mineral_cost_factor or 0
		self.vespene_cost_base = self.vespene_cost_base or 0
		self.vespene_cost_factor = self.vespene_cost_factor or 0
		self.research_time_base = self.research_time_base or 0
		self.research_time_factor = self.research_time_factor or 0
		self.requirements = self.requirements or 0
		self.icon = self.icon or 0
		self.label = self.label or 0
		self.staredit_race = self.staredit_race or 0
		self.max_repeats = self.max_repeats or 0
		self.broodwar_only = self.broodwar_only or 0

	def export_text(self, id):
		return """Upgrade(%d):
	mineral_cost_base %d
	mineral_cost_factor %d
	vespene_cost_base %d
	vespene_cost_factor %d
	research_time_base %d
	research_time_factor %d
	requirements %d
	icon %d
	label %d
	staredit_race %d
	max_repeats %d
	broodwar_only %d""" % (
			id,
			self.mineral_cost_base,
			self.mineral_cost_factor,
			self.vespene_cost_base,
			self.vespene_cost_factor,
			self.research_time_base,
			self.research_time_factor,
			self.requirements,
			self.icon,
			self.label,
			self.staredit_race,
			self.max_repeats,
			self.broodwar_only
		)

	def export_json(self, id, dump=True, indent=4):
		data = OrderedDict()
		data["_type"] = "Upgrade"
		data["_id"] = id
		data["mineral_cost_base"] = self.mineral_cost_base
		data["mineral_cost_factor"] = self.mineral_cost_factor
		data["vespene_cost_base"] = self.vespene_cost_base
		data["vespene_cost_factor"] = self.vespene_cost_factor
		data["research_time_base"] = self.research_time_base
		data["research_time_factor"] = self.research_time_factor
		data["requirements"] = self.requirements
		data["icon"] = self.icon
		data["label"] = self.label
		data["staredit_race"] = self.staredit_race
		data["max_repeats"] = self.max_repeats
		data["broodwar_only"] = self.broodwar_only
		if not dump:
			return data
		return json.dumps(data, indent=indent)

# upgrades.dat file handler
class UpgradesDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 61,
			"properties": [
				{
					"name": "mineral_cost_base",
					"type": "short"
				},
				{
					"name": "mineral_cost_factor",
					"type": "short"
				},
				{
					"name": "vespene_cost_base",
					"type": "short"
				},
				{
					"name": "vespene_cost_factor",
					"type": "short"
				},
				{
					"name": "research_time_base",
					"type": "short"
				},
				{
					"name": "research_time_factor",
					"type": "short"
				},
				{
					"name": "requirements",
					"type": "short"
				},
				{
					"name": "icon",
					"type": "short"
				},
				{
					"name": "label",
					"type": "short"
				},
				{
					"name": "staredit_race",
					"type": "byte"
				},
				{
					"name": "max_repeats",
					"type": "byte"
				},
				{
					"name": "broodwar_only",
					"type": "byte"
				}
			]
		})
	ENTRY_STRUCT = Upgrade
	FILE_NAME = "upgrades.dat"