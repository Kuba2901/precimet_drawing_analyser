import ezdxf
import math
from .drawing_analyser_utils import DrawingAnalyserUtils
from .drawing_custom_entity import *
import ezdxf.addons.odafc

class DrawingAnalyser:
	def __init__(self, name, file_name) -> None:
		self.name = name
		self.file_name = file_name
		import sys
		try:
			# if file_name.endswith('.dwg'):
			# 	print("Converting DWG to DXF")
			# 	converter = drawing_converter.DrawingConverter(r"/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter")
			# 	file_name = converter.convert_dwg_to_dxf(file_name)
			doc = ezdxf.readfile(file_name)
		except Exception as e:
			print(f"Error: {e}")
			sys.exit(1)
		self.doc = doc
		self.msp = doc.modelspace()
		self.entities = self.__get_entities()
		# for e in self.entities:
		# 	print(str(e))

	def get_total_length(self) -> float:
		total_length = 0.0
		for entity in self.entities:
			total_length += entity.get_length()
		return total_length

	def __get_entities(self) -> [CustomEntity]:
		entities = []
		for entity in self.msp:
			ent = CustomEntity.get_instance(entity)
			if ent is not None:
				entities.append(ent)
		return entities

	def get_cut_ins_count(self) -> int:
		return self.get_element_groups_count()

	# def __visualize_included_entities(self) -> None:
	# 	from pathlib import Path
	# 	Path("output").mkdir(parents=True, exist_ok=True)
	# 	output_file_name = f"output/{Path(self.file_name).name.replace(".dxf", "_filtered.dxf")}"
	# 	new_doc = ezdxf.new(dxfversion=self.doc.dxfversion)
	# 	new_msp = new_doc.modelspace()
	# 	all_entities = self.__get_analysed_entities()
	# 	for entity, is_included in all_entities:
	# 		if entity.dxftype() == 'LINE':
	# 			new_msp.add_line(entity.dxf.start, entity.dxf.end, dxfattribs={'color': entity.dxf.color})
	# 		elif entity.dxftype() == 'ARC':
	# 			new_msp.add_arc(
	# 				center=entity.dxf.center,
	# 				radius=entity.dxf.radius,
	# 				start_angle=entity.dxf.start_angle,
	# 				end_angle=entity.dxf.end_angle,
	# 				dxfattribs={'color': entity.dxf.color}
	# 			)
	# 		elif entity.dxftype() == 'POLYLINE':
	# 			new_msp.add_polyline2d(entity.points(), dxfattribs={'color': entity.dxf.color})		
	# 		elif entity.dxftype() == 'CIRCLE':
	# 			new_msp.add_circle(entity.dxf.center, entity.dxf.radius, dxfattribs={'color': entity.dxf.color})
	# 	new_doc.saveas(output_file_name)
	# 	self.__clear_included_entities()
	# 	print(f"Filtered entities saved to {output_file_name}")

	# def	analyse(self) -> None:
	# 	self.__visualize_included_entities()
	# 	groups_count = self.get_element_groups_count()
	# 	print(f"Liczba wpaleń: {groups_count}")

	def get_element_groups_count(self) -> int:
		"""
		Count the number of separate components (connected elements) in the adjacency matrix.

		:param adj_matrix: 2D adjacency matrix (list of lists), where adj_matrix[i][j] == 1
						indicates a connection between entity i and entity j.
		:return: Number of separate connected components.
		"""
		adj_matrix = self.__create_entity_adjacency_matrix()
		num_entities = len(adj_matrix)
		visited = [False] * num_entities
		components_count = 0

		def dfs(entity):
			"""Perform DFS to mark all reachable entities from the current entity."""
			visited[entity] = True
			for adjacent_entity, is_connected in enumerate(adj_matrix[entity]):
				if is_connected and not visited[adjacent_entity]:
					dfs(adjacent_entity)
		for entity in range(num_entities):
			if not visited[entity]:
				components_count += 1
				dfs(entity)
		return components_count

	def __create_entity_adjacency_matrix(self) -> []:
		entities = self.entities
		matrix = []
		for i in range(len(entities)):
			row = []
			for j in range(len(entities)):
				row.append(0) # TODO: Verify if not 1
			matrix.append(row)
		for i in range(len(entities)):
			matrix[i][i] = 1
			for j in range(i + 1, len(entities)):
				entity1, entity2 = entities[i], entities[j]
				connected = 1 if entity1.is_connected(entity2) else 0
				matrix[i][j] = connected
				matrix[j][i] = connected
		# for line in matrix:
		# 	print(line)
		return matrix
		
	def __str__(self) -> str:
		return f"""
DETAILS OF {self.file_name.upper()}
Total laser cut length: {self.get_total_length()}
Number of cut-ins: {self.get_cut_ins_count()}
		""" 
