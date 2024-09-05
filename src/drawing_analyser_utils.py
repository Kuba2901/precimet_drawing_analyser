import ezdxf
import math

class DrawingAnalyserUtils:
	def __init__(self, msp: ezdxf.layouts.Modelspace):
		self.msp = msp
		self.included_entities = []

	def __is_connected_lines(self, line1: ezdxf.entities.Line, line2: ezdxf.entities.Line) -> bool:
		return self.__compare_points(point1=line1.dxf.end, point2=line2.dxf.start) or self.__compare_points(point1=line2.dxf.end, point2=line1.dxf.start)

	def __is_connected_polylines(self, polyline1: ezdxf.entities.Polyline, polyline2: ezdxf.entities.Polyline) -> bool:
		return self.__compare_points(point1=polyline1.vertices[-1].dxf.location, point2=polyline2.vertices[0].dxf.location) or self.__compare_points(point1=polyline1.vertices[0].dxf.location, point2=polyline2.vertices[-1].dxf.location)

	def __is_connected_lwpolylines(self, lwpolyline1: ezdxf.entities.LWPolyline, lwpolyline2: ezdxf.entities.LWPolyline) -> bool:
		return self.__compare_points(p1=lwpolyline1[-1], p2=lwpolyline2[0]) or self.__compare_points(p1=lwpolyline1[0], p2=lwpolyline2[-1])
	
	def __is_connected_lwpolyline_polyline(self, lwpolyline: ezdxf.entities.LWPolyline, polyline: ezdxf.entities.Polyline) -> bool:	
		return self.__compare_points(p1=lwpolyline[-1], point2=polyline.vertices[0].dxf.location) or self.__compare_points(p1=lwpolyline[0], point2=polyline.vertices[-1].dxf.location)

	def __is_connected_arc_line(self, arc: ezdxf.entities.Arc, line: ezdxf.entities.Line) -> bool:
		return self.__compare_points(point1=arc.end_point, point2=line.dxf.start) or self.__compare_points(point1=arc.start_point, point2=line.dxf.end)
		
	def __is_connected_arc_polyline(self, arc: ezdxf.entities.Arc, polyline: ezdxf.entities.Polyline) -> bool:
		return self.__compare_points(point1=arc.end_point, p2=polyline.vertices[0].dxf.location) or self.__compare_points(point1=arc.start_point, p2=polyline.vertices[-1].dxf.location)

	def __is_connected_arc_arc(self, arc1: ezdxf.entities.Arc, arc2: ezdxf.entities.Arc) -> bool:
		return self.__compare_points(point1=arc1.end_point, point2=arc2.start_point) or self.__compare_points(point1=arc1.start_point, point2=arc2.end_point)

	def __is_connected_arc_lwpolyline(self, arc: ezdxf.entities.Arc, lwpolyline: ezdxf.entities.LWPolyline) -> bool:
		arc_start_x, arc_start_y = arc.start_point.x, arc.start_point.y
		arc_end_x, arc_end_y = arc.end_point.x, arc.end_point.y
		lwpolyline_start_x, lwpolyline_start_y = lwpolyline[0][0], lwpolyline[0][1]
		lwpolyline_end_x, lwpolyline_end_y = lwpolyline[-1][0], lwpolyline[-1][1]
		print(f"arc_start: ({arc_start_x}, {arc_start_y}), arc_end: ({arc_end_x}, {arc_end_y})")
		print(f"lwpolyline_start: ({lwpolyline_start_x}, {lwpolyline_start_y}), lwpolyline_end: ({lwpolyline_end_x}, {lwpolyline_end_y})\n\n")
		return self.__compare_points(point1=arc.end_point, p2=lwpolyline[0]) or self.__compare_points(point1=arc.start_point, p2=lwpolyline[-1])

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
			elif entity2.dxftype() == 'POLYLINE':
				return self.__is_connected_line_polyline(entity1, entity2)
			elif entity2.dxftype() == 'ARC':
				return self.__is_connected_arc_line(entity2, entity1)
			elif entity2.dxftype() == 'LWPOLYLINE':
				return self.__is_connected_line_lwpolyline(entity1, entity2)
		elif entity1.dxftype() == 'POLYLINE':
			if entity2.dxftype() == 'LINE':
				return self.__is_connected_line_polyline(entity2, entity1)
			elif entity2.dxftype() == 'POLYLINE':
				return self.__is_connected_polylines(entity1, entity2)
			elif entity2.dxftype() == 'ARC':
				return self.__is_connected_arc_polyline(entity2, entity1)
			elif entity2.dxftype() == 'LWPOLYLINE':
				return self.__is_connected_lwpolyline_polyline(entity2, entity1)
		elif entity1.dxftype() == 'ARC':
			if entity2.dxftype() == 'LINE':
				return self.__is_connected_arc_line(entity1, entity2)
			elif entity2.dxftype() == 'POLYLINE':
				return self.__is_connected_arc_polyline(entity1, entity2)
			elif entity2.dxftype() == 'ARC':
				return self.__is_connected_arc_arc(entity1, entity2)
			elif entity2.dxftype() == 'LWPOLYLINE':
				return self.__is_connected_arc_lwpolyline(entity1, entity2)
		elif entity1.dxftype() == 'LWPOLYLINE':
			if entity2.dxftype() == 'LINE':
				return self.__is_connected_line_lwpolyline(entity2, entity1)
			elif entity2.dxftype() == 'POLYLINE':
				return self.__is_connected_lwpolyline_polyline(entity1, entity2)
			elif entity2.dxftype() == 'ARC':
				return self.__is_connected_arc_lwpolyline(entity2, entity1)
			elif entity2.dxftype() == 'LWPOLYLINE':
				return self.__is_connected_lwpolylines(entity1, entity2)
		else:
			return False

	def __is_connected_line_polyline(self, line: ezdxf.entities.Line, polyline: ezdxf.entities.Polyline) -> bool:
		return self.__compare_points(point1=line.dxf.end, point2=polyline.vertices[0].dxf.location) or self.__compare_points(point1=line.dxf.start, point2=polyline.vertices[-1].dxf.location)

	def __is_connected_line_lwpolyline(self, line: ezdxf.entities.Line, lwpolyline: ezdxf.entities.LWPolyline) -> bool:
		return self.__compare_points(point1=line.dxf.end, p2=lwpolyline[0]) or self.__compare_points(point1=line.dxf.start, p2=lwpolyline[-1])
