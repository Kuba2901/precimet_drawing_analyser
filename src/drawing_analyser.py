import ezdxf
import math
from src import drawing_converter
import ezdxf.addons.odafc

class DrawingAnalyser:
	def __init__(self, name, file_name) -> None:
		self.name = name
		self.file_name = file_name
		import sys
		try:
			if file_name.endswith('.dwg'):
				print("Converting DWG to DXF")
				converter = drawing_converter.DrawingConverter(r"/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter")
				file_name = converter.convert_dwg_to_dxf(file_name)
			doc = ezdxf.readfile(file_name)
		except Exception as e:
			print(f"Error: {e}")
			sys.exit(1)
		self.doc = doc
		self.msp = doc.modelspace()
		self.included_entities = []

	def	get_holes(self) -> [ezdxf.entities.circle.Circle]:
		hole_centers = []
		for entity in self.msp:
			if entity.dxftype() == 'CIRCLE':
				hole_centers.append(entity)
		return hole_centers

	def	get_holes_count(self) -> int:
		return len(self.get_holes())
	
	def get_entities_types(self) -> [str]:
		print(f"Getting entities in {self.name}")
		return [entity.dxftype() for entity in self.msp]

	def get_entities(self) -> []:
		entities = []
		for entity in self.msp:
			entities.append(entity)
		return entities

	def	get_total_cut_length(self) -> float:
		print("Getting the total length of laser cutting")
		total_length = 0.0
		total_length += self.get_total_polylines_length()
		total_length += self.get_total_lines_length()
		total_length += self.get_total_arcs_length()
		return total_length

	def	get_total_polylines_length(self) -> float:
		print("Getting the total length of polylines")
		total_length = 0.0
		for polyline in self.msp.query('POLYLINE'):
			self.__add_to_included_entities(polyline)
			total_length += self.get_polyline_length(polyline)
		return total_length

	def	get_total_lines_length(self) -> float:
		print("Getting the total length of lines")
		total_length = 0.0
		for line in self.msp.query('LINE'):
			self.__add_to_included_entities(line)
			total_length += self.get_line_length(line)
		return total_length

	def	get_total_arcs_length(self) -> float:
		print("Getting the total length of arcs")
		total_length = 0.0
		for arc in self.msp.query('ARC'):
			self.__add_to_included_entities(arc)
			total_length += self.get_arc_length(arc)
		return total_length
		
	def	get_polyline_length(self, polyline: ezdxf.entities.Polyline) -> float:
		poly_len = 0
		for i in range(len(polyline)):
			if i == 0:
				continue
			vertex = polyline.vertices[i]
			poly_len += polyline.vertices[i].dxf.location.distance(polyline.vertices[i-1].dxf.location)
		return poly_len

	def	get_line_length(self, line: ezdxf.entities.Line) -> float:
		start_point = line.dxf.start
		end_point = line.dxf.end
		return start_point.distance(end_point)

	def	get_arc_length(self, arc: ezdxf.entities.Arc) -> float:
		start_point = arc.start_point
		end_point = arc.end_point
		center = arc.dxf.center
		radius = arc.dxf.radius
		start_angle = arc.dxf.start_angle
		end_angle = arc.dxf.end_angle
		if (end_angle - start_angle) < 0:
			end_angle += 360
		arc_length = radius * math.radians(abs(end_angle - start_angle))
		return arc_length

	def	__clear_included_entities(self) -> None:
		self.included_entities = []

	def	__add_to_included_entities(self, entity) -> None:
		self.included_entities.append(entity)

	def __get_analysed_entities(self):
		self.__clear_included_entities()
		self.get_total_cut_length()
		included = self.included_entities
		all_entities = self.get_entities()
		ret = []
		for	entity in all_entities:
			print(f"Entity: {entity}")
			if not entity in included:
				ret.append((entity, False))
			else:
				ret.append((entity, True))
		return (ret)

	def __visualize_included_entities(self) -> None:
		output_file_name = f"indicated_{self.file_name}"
		new_doc = ezdxf.new(dxfversion=self.doc.dxfversion)
		new_msp = new_doc.modelspace()
		all_entities = self.__get_analysed_entities()
		for entity, is_included in all_entities:
			print(f"Entity: {entity}, {is_included}")
			if is_included:
				entity.dxf.color = 4
			if entity.dxftype() == 'LINE':
				new_msp.add_line(entity.dxf.start, entity.dxf.end, dxfattribs={'color': entity.dxf.color})
			elif entity.dxftype() == 'ARC':
				new_msp.add_arc(
					center=entity.dxf.center,
					radius=entity.dxf.radius,
					start_angle=entity.dxf.start_angle,
					end_angle=entity.dxf.end_angle,
					dxfattribs={'color': entity.dxf.color}
				)
			elif entity.dxftype() == 'POLYLINE':
				new_msp.add_polyline2d(entity.points(), dxfattribs={'color': entity.dxf.color})		
			elif entity.dxftype() == 'CIRCLE':
				new_msp.add_circle(entity.dxf.center, entity.dxf.radius, dxfattribs={'color': entity.dxf.color})
		new_doc.saveas(output_file_name)
		self.__clear_included_entities()
		print(f"Filtered entities saved to {output_file_name}")

	def	analyse(self) -> None:
		self.__visualize_included_entities()
		print(self)

	def find_connected_elements(self) -> []:
		entities = self.get_entities()
		

	def __str__(self) -> str:
		return f"""
DETAILS OF {self.file_name.upper()}
Holes count: {self.get_holes_count()}
Total laser cut length: {self.get_total_cut_length()}
		"""
