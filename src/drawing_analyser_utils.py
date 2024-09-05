import ezdxf
import math

class DrawingAnalyserUtils:
	def __init__(self, msp: ezdxf.layouts.Modelspace):
		self.msp = msp
		self.included_entities = []

	def __is_connected_lines(self, line1: ezdxf.entities.Line, line2: ezdxf.entities.Line) -> bool:
		return self.__compare_points(line1.dxf.end, line2.dxf.start) or self.__compare_points(line2.dxf.end, line1.dxf.start)

	def __is_connected_polylines(self, polyline1: ezdxf.entities.Polyline, polyline2: ezdxf.entities.Polyline) -> bool:
		return self.__compare_points(polyline1.vertices[-1].dxf.location, polyline2.vertices[0].dxf.location) or self.__compare_points(polyline1.vertices[0].dxf.location, polyline2.vertices[-1].dxf.location)

	def __is_connected_arc_line(self, arc: ezdxf.entities.Arc, line: ezdxf.entities.Line) -> bool:
		return self.__compare_points(arc.end_point, line.dxf.start) or self.__compare_points(arc.start_point, line.dxf.end)
		

	def __is_connected_arc_polyline(self, arc: ezdxf.entities.Arc, polyline: ezdxf.entities.Polyline) -> bool:
		return self.__compare_points(arc.end_point, polyline.vertices[0].dxf.location) or self.__compare_points(arc.start_point, polyline.vertices[-1].dxf.location)

	def __is_connected_arc_arc(self, arc1: ezdxf.entities.Arc, arc2: ezdxf.entities.Arc) -> bool:
		return self.__compare_points(arc1.end_point, arc2.start_point) or self.__compare_points(arc1.start_point, arc2.end_point)

	# 2D drawings only
	def __compare_points(self, point1: ezdxf.math.Vec2, point2: ezdxf.math.Vec2) -> bool:
		return math.isclose(point1.x, point2.x) and math.isclose(point1.y, point2.y)

	def __is_connected_line_polyline(self, line: ezdxf.entities.Line, polyline: ezdxf.entities.Polyline) -> bool:
		return self.__compare_points(line.dxf.end, polyline.vertices[0].dxf.location) or self.__compare_points(line.dxf.start, polyline.vertices[-1].dxf.location)
		 
	def check_entities_connected(self, entity1: ezdxf.entities.dxfentity.DXFEntity, entity2: ezdxf.entities.dxfentity.DXFEntity) -> bool:
		if (entity1.dxftype() == "CIRCLE" or entity2.dxftype() == "CIRCLE"):
			return False
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
