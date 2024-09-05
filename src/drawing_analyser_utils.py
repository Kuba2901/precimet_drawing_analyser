import ezdxf
import math

class DrawingAnalyserUtils:
	def __init__(self, msp: ezdxf.layouts.Modelspace):
		self.msp = msp
		self.included_entities = []

	def __is_connected_lines(self, line1: ezdxf.entities.Line, line2: ezdxf.entities.Line) -> bool:
		return line1.dxf.end == line2.dxf.start or line1.dxf.start == line2.dxf.end

	def __is_connected_polylines(self, polyline1: ezdxf.entities.Polyline, polyline2: ezdxf.entities.Polyline) -> bool:
		return polyline1.vertices[-1].dxf.location == polyline2.vertices[0].dxf.location or polyline1.vertices[0].dxf.location == polyline2.vertices[-1].dxf.location	

	def __is_connected_arc_line(self, arc: ezdxf.entities.Arc, line: ezdxf.entities.Line) -> bool:
		return arc.end_point == line.dxf.start or arc.start_point == line.dxf.end

	def __is_connected_arc_polyline(self, arc: ezdxf.entities.Arc, polyline: ezdxf.entities.Polyline) -> bool:
		return self.__compare_points(arc.end_point, polyline.vertices[0].dxf.location) or self.__compare_points(arc.start_point, polyline.vertices[-1].dxf.location)

	def __is_connected_arc_arc(self, arc1: ezdxf.entities.Arc, arc2: ezdxf.entities.Arc) -> bool:
		return self.__compare_points(arc1.end_point, arc2.start_point) or self.__compare_points(arc1.start_point, arc2.end_point)

	# 2D drawings only
	def __compare_points(self, point1: ezdxf.math.Vec2, point2: ezdxf.math.Vec2) -> bool:
		return math.isclose(point1.x, point2.x) and math.isclose(point1.y, point2.y)

	def __is_connected_line_polyline(self, line: ezdxf.entities.Line, polyline: ezdxf.entities.Polyline) -> bool:
		return line.dxf.end == polyline.vertices[0].dxf.location or line.dxf.start == polyline.vertices[-1].dxf.location

	def check_entities_connected(self, entity1: ezdxf.entities.dxfentity.DXFEntity, entity2: ezdxf.entities.dxfentity.DXFEntity) -> bool:
		if (entity1.dxftype() == "CIRCLE" or entity2.dxftype() == "CIRCLE"):
			return False
		print("Entities received: ", entity1, entity2)
		if entity1.dxftype() == 'LINE' and entity2.dxftype() == 'LINE':
			if entity2.dxftype() == 'LINE':
				return self.__is_connected_lines(entity1, entity2)
			elif entity2.dxftype() == 'POLYLINE':
				return self.__is_connected_line_polyline(entity1, entity2)
			elif entity2.dxftype() == 'ARC':
				return self.__is_connected_arc_line(entity2, entity1)
		elif entity1.dxftype() == 'POLYLINE':
			if entity2.dxftype() == 'LINE':
				return self.__is_connected_line_polyline(entity2, entity1)
			elif entity2.dxftype() == 'POLYLINE':
				return self.__is_connected_polylines(entity1, entity2)
			elif entity2.dxftype() == 'ARC':
				return self.__is_connected_arc_polyline(entity2, entity1)
		elif entity1.dxftype() == 'ARC':
			if entity2.dxftype() == 'LINE':
				return self.__is_connected_arc_line(entity1, entity2)
			elif entity2.dxftype() == 'POLYLINE':
				return self.__is_connected_arc_polyline(entity1, entity2)
			elif entity2.dxftype() == 'ARC':
				return self.__is_connected_arc_arc(entity1, entity2)
		else:
			return False

	# def is_point_included_in_line_segment(self, point_x: float, point_y: float, start_x: float, start_y: float, end_x: float, end_y: float) -> bool:
	# 	start_x, end_x = line.dxf.start.x, line.dxf.end.x
	# 	start_y, end_y = line.dxf.start.y, line.dxf.end.y
	# 	if ((point_y - start_y) * (end_x - start_x) - (point_x - start_x) * (end_y - start_y)) != 0:
	# 		return False
	# 	return False
	
	# def is_point_on_polyline(self, polyline, point, tolerance=1e-6):
	# 	for i in range(len(polyline)):
	# 		if i == 0:
	# 			continue
	# 		p1 = polyline.vertices[i-1].dxf.location
	# 		p2 = polyline.vertices[i].dxf.location
	# 		if self.is_point_included_in_line_segment(point.x, point.y, p1.x, p1.y, p2.x, p2.y) < tolerance:
	# 			return True
	# 	return False

	# # TODO: Test this method
	# def is_point_on_arc(self, point: ezdxf.math.Vec2, arc: ezdxf.entities.Arc) -> bool:
	# 	# Calculate the distance between the point and the center of the arc
	# 	distance = math.sqrt((point_x - center_x)**2 + (point_y - center_y)**2)
		
	# 	# Check if the point is on the circle (within a small tolerance)
	# 	tolerance = 1e-6
	# 	if abs(distance - radius) > tolerance:
	# 		return False

	# 	point_x, point_y = point.x, point.y
	# 	center_x, center_y = arc.dxf.center.x, arc.dxf.center.y
	# 	point_angle = math.atan2(point_y - center_y, point_x - center_x)
		
	# 	# Convert angle to degrees and ensure it's positive
	# 	point_angle = math.degrees(point_angle)
	# 	if point_angle < 0:
	# 		point_angle += 360
		
	# 	# Normalize start and end angles to be between 0 and 360
	# 	start_angle = start_angle % 360
	# 	end_angle = end_angle % 360
		
	# 	# Check if the point's angle is within the arc's range
	# 	if start_angle <= end_angle:
	# 		return start_angle <= point_angle <= end_angle
	# 	else:  # Arc crosses the 0/360 degree line
	# 		return point_angle >= start_angle or point_angle <= end_angle
