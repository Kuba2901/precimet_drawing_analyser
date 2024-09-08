import ezdxf
from .pm_utils import PMAnalyserUtils
from .pm_entities import *

class PMAnalyser:
	def __init__(self, file_name) -> None:
		self.file_name = file_name
		self.utils = PMAnalyserUtils(self)
		import sys
		try:
			if not file_name.endswith('.dxf'):
				self.utils.print_err("File is not a DXF file")
				sys.exit(1)
			doc = ezdxf.readfile(file_name)
			self.doc = doc
			self.msp = doc.modelspace()
			self.entities = self.utils.get_entities()
			self.adj_matrix = self.utils.create_entity_adjacency_matrix()
			self.total_cutting_length = self.utils.get_total_cutting_length()
			self.cut_ins_count = self.utils.get_cut_ins_count()
			self.turns_count = self.utils.get_turns_count()
		except Exception as e:
			print(f"Error: {e}")
			sys.exit(1)

	def __str__(self) -> str:
		return f"""
Analyser for {self.file_name}
Total cutting length: {self.total_cutting_length}
Cut-ins count: {self.cut_ins_count}
Turns count: {self.turns_count}
Entities count: {len(self.entities)}
		"""