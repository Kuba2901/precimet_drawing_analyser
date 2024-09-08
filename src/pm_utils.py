from colorama import Fore, Style, Back
import ezdxf
from .pm_entities import PMLineSegment, PMEntity

class PMAnalyserUtils:
	def __init__(self, pm_analyser):
		self.pm_analyser = pm_analyser

	def polyline_to_line_segments(self, polyline: ezdxf.entities.DXFEntity) -> []:
		points = PMLineSegment.get_poly_points(polyline)
		if points is not None:
			return PMLineSegment.poly_points_to_line_segments(points, polyline.is_closed)
		return []

	def print_err(self, *args, **kwargs) -> None:
		import sys
		print(Fore.RED, *args, file=sys.stderr, **kwargs)
		print(Style.RESET_ALL, end='')

	def print_info(self, *args, **kwargs) -> None:
		print(Fore.CYAN, *args, **kwargs)
		print(Style.RESET_ALL, end='')

	def print_warn(self, *args, **kwargs) -> None:
		print(Fore.YELLOW, *args, **kwargs)
		print(Style.RESET_ALL, end='')

	def print_debug(self, *args, **kwargs) -> None:
		print(Fore.YELLOW, *args, **kwargs)
		print(Style.RESET_ALL, end='')

	def print_success(self, *args, **kwargs) -> None:
		print(Fore.GREEN, *args, **kwargs)
		print(Style.RESET_ALL, end='')

	def print_entities(self) -> None:
		for entity in self.pm_analyser.entities:
			print(entity)

	def print_entities_types(self) -> None:
		types = {}
		for entity in self.pm_analyser.entities:
			print(entity.type)
		print(types)

	def __get_total_entities_count(self) -> int:
		return len(self.pm_analyser.entities)

	def get_total_cutting_length(self) -> float:
		total_length = 0
		for entity in self.pm_analyser.entities:
			total_length += entity.get_length()
		return round(total_length, 3)

	def get_entities(self) -> [PMEntity]:
		entities = []
		for entity in self.pm_analyser.msp:
			if entity.dxftype() == 'LWPOLYLINE' or entity.dxftype() == 'POLYLINE':
				line_segments = self.polyline_to_line_segments(entity)
				entities.extend(line_segments)
			else:
				instance, count = PMEntity.get_instance(entity)
				if instance is not None:
					if count == 1:
						entities.append(instance)
					else:
						entities.extend(instance)
		return (entities)

	def create_entity_adjacency_matrix(self) -> []:
		entities = self.pm_analyser.entities
		matrix = []
		for i in range(len(entities)):
			row = []
			for j in range(len(entities)):
				row.append(0)
			matrix.append(row)
		for i in range(len(entities)):
			matrix[i][i] = 1
			for j in range(i + 1, len(entities)):
				entity1, entity2 = entities[i], entities[j]
				connected = 1 if entity1.connectable and entity2.connectable and entity1.is_connected(entity2) else 0
				matrix[i][j] = connected
				matrix[j][i] = connected
		return matrix

	def print_entity_adjacency_matrix(self) -> None:
		print(Fore.MAGENTA, end='')
		matrix = self.pm_analyser.adj_matrix
		for row in matrix:
			print(row)
		print(Style.RESET_ALL, end='')

	def get_cut_ins_count(self) -> int:
		"""
		Count the number of cut-ins in the drawing.
		A cut-in is a point where the cutting is lowered and starts cutting again.
		"""
		return self.__get_element_groups_count()

	def __get_element_groups_count(self) -> int:
		analyser = self.pm_analyser
		adj_matrix = analyser.adj_matrix
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
