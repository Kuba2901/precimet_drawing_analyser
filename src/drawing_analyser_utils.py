import ezdxf
import math

class DrawingAnalyserUtils:
	def __init__(self, msp: ezdxf.layouts.Modelspace):
		self.msp = msp
		self.included_entities = []

	def __is_connected_lines(self, line1: ezdxf.entities.Line, line2: ezdxf.entities.Line) -> bool:
		return self.__compare_points(point1=line1.dxf.end, point2=line2.dxf.start) or self.__compare_points(point1=line2.dxf.end, point2=line1.dxf.start)
	
	def __is_connected_arc_line(self, arc: ezdxf.entities.Arc, line: ezdxf.entities.Line) -> bool:
		return self.__compare_points(point1=arc.end_point, point2=line.dxf.start) or self.__compare_points(point1=arc.start_point, point2=line.dxf.end)
		
	def __is_connected_arc_arc(self, arc1: ezdxf.entities.Arc, arc2: ezdxf.entities.Arc) -> bool:
		return self.__compare_points(point1=arc1.end_point, point2=arc2.start_point) or self.__compare_points(point1=arc1.start_point, point2=arc2.end_point)

	# 2D drawings only
	def __compare_points(self, point1 = None, point2 = None, p1 = None, p2 = None) -> bool:
		if (point1 is None and p1 is None) or (point2 is None and p2 is None):
			raise ValueError("The values cannot be None")
		if p1 is not None:
			x1, y1 = p1[0], p1[1]
		else:
			x1, y1 = point1.x, point1.y
		if p2 is not None:
			x2, y2 = p2[0], p2[1]
		else:
			x2, y2 = point2.x, point2.y
		return math.isclose(x1, x2) and math.isclose(y1, y2)
		 
	def check_entities_connected(self, entity1: ezdxf.entities.dxfentity.DXFEntity, entity2: ezdxf.entities.dxfentity.DXFEntity) -> bool:
		if (entity1.dxftype() == "CIRCLE" or entity2.dxftype() == "CIRCLE"):
			return False
		if entity1.dxftype() == 'LINE':
			if entity2.dxftype() == 'LINE':
				return self.__is_connected_lines(entity1, entity2)
			elif entity2.dxftype() == 'POLYLINE' or entity2.dxftype() == 'LWPOLYLINE':
				return self.__is_connected_to_polyline(entity1, entity2)
			elif entity2.dxftype() == 'ARC':
				return self.__is_connected_arc_line(entity2, entity1)
		elif entity1.dxftype() == 'POLYLINE' or entity1.dxftype() == 'LWPOLYLINE':
			if entity2.dxftype() == 'LINE':
				return self.__is_connected_to_polyline(entity2, entity1)
			elif entity2.dxftype() == 'POLYLINE' or entity2.dxftype() == 'LWPOLYLINE':
				return self.__is_connected_to_polyline(entity2, entity1)
			elif entity2.dxftype() == 'ARC':
				return self.__is_connected_to_polyline(entity2, entity1)
		elif entity1.dxftype() == 'ARC':
			if entity2.dxftype() == 'LINE':
				return self.__is_connected_arc_line(entity1, entity2)
			elif entity2.dxftype() == 'POLYLINE' or entity2.dxftype() == 'LWPOLYLINE':
				return self.__is_connected_to_polyline(entity1, entity2)
			elif entity2.dxftype() == 'ARC':
				return self.__is_connected_arc_arc(entity1, entity2)
		else:
			return False

	def __is_connected_to_polyline(self, entity: ezdxf.entities.dxfentity.DXFEntity, polyline: ezdxf.entities.Polyline) -> bool:
		poli = self.__lwpolyline_to_list(polyline)
		if entity.dxftype() == 'LINE':
			start = self.__location_to_tuple(entity.dxf.start)
			end = self.__location_to_tuple(entity.dxf.end)
			return self.__contains_point(start, poli) or self.__contains_point(end, poli)
		elif entity.dxftype() == 'ARC':
			start = self.__location_to_tuple(entity.start_point)
			end = self.__location_to_tuple(entity.end_point)
			return self.__contains_point(start, poli) or self.__contains_point(end, poli)
		elif entity.dxftype() == 'POLYLINE':
			for vertex in entity.vertices:
				if self.__contains_point(self.__location_to_tuple(vertex.dxf.location), poli):
					return True
			return False
		elif entity.dxftype() == 'LWPOLYLINE':
			for vertex in entity:
				if self.__contains_point(vertex, poli):
					return True
			return False
		else:
			return False

	def __location_to_tuple(self, location) -> tuple:
		return (location.x, location.y)

	def __polyline_to_list(self, polyline: ezdxf.entities.Polyline) -> list:
		ret = []
		for vertex in polyline.vertices:
			pt = vertex.dxf.location
			ret.append((pt.x, pt.y))
		return ret
	
	def __lwpolyline_to_list(self, lwpolyline: ezdxf.entities.LWPolyline) -> list:
		ret = []
		for vertex in lwpolyline:
			ret.append((vertex[0], vertex[1]))
		return ret

	def __contains_point(self, point: tuple, polyline: list) -> bool:
		for vertex in polyline:
			if self.__compare_points(p1=vertex, p2=point):
				return True
		return False
