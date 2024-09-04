import ezdxf
import math

class DrawingAnalyser:
	def __init__(self, name, file_name) -> None:
		self.name = name
		self.file_name = file_name
		import sys
		try:
			doc = ezdxf.readfile(file_name)
		except IOError:
			print(f"Not a DXF file or a generic I/O error.")
			sys.exit(1)
		except ezdxf.DXFStructureError:
			print(f"Invalid or corrupted DXF file.")
			sys.exit(2)
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
	
	def get_entities(self) -> [str]:
		print(f"Getting entities in {self.name}")
		return [entity.dxftype() for entity in self.msp]

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

	def __visualize_included_entities(self) -> None:
		output_file_name = f"indicated_{self.file_name}"
		new_doc = ezdxf.new(dxfversion=self.doc.dxfversion)
		new_msp = new_doc.modelspace()
		
		# Calculate total cut length and populate included_entities
		self.get_total_cut_length()
		print(f"Included entities: {self.included_entities}")
		
		for entity in self.included_entities:
			entity.dxf.color = 1  # Set the entity color to red (AutoCAD color index 1)
			
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
		
		new_doc.saveas(output_file_name)
		self.__clear_included_entities()
		print(f"Filtered entities saved to {output_file_name}")

	def	analyse(self) -> None:
		self.__visualize_included_entities()
		print(self)

	def __str__(self) -> str:
		return f"""
[*] DETAILS OF {self.file_name.upper()}
Holes count: {self.get_holes_count()}
Total laser cut length: {self.get_total_cut_length()}
		"""
