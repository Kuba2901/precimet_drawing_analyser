import ezdxf
import ezdxf.math
from abc import ABC, abstractmethod
import math

class CustomEntity(ABC):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		self.entity: ezdxf.entities.DXFEntity = entity
		self.start_point: tuple = None
		self.end_point: tuple = None
		self.center: tuple = None
		self.radius: tuple = None
		self.points = None
		
	def _point_to_tuple(self, point) -> tuple:
		return (point.x, point.y)

	def _is_point_connected(self, point: tuple) -> bool:
		for p in self.points:
			is_close: bool = math.isclose(p[0], point[0]) and math.isclose(p[1], point[1])
			if is_close:
				return (True)
		return (False)

	@staticmethod
	def get_instance(entity : ezdxf.entities.DXFEntity):
		if entity.dxftype() == "CIRCLE":
			return CustomCircle(entity)
		elif entity.dxftype() == "ARC":
			return CustomArc(entity)
		elif entity.dxftype() == "LINE":
			return CustomLine(entity)
		elif entity.dxftype() == "POLYLINE" or entity.dxftype() == "LWPOLYLINE":
			return CustomPoly(entity)
		elif entity.dxftype() == "SPLINE":
			return CustomSpline(entity)

	@abstractmethod
	def get_length(self) -> float:
		pass

	# @abstractmethod
	def is_connected(self, entity) -> bool:
		for p in entity.points:
			if self._is_point_connected(p):
				return (True)
		return (False)

	@abstractmethod
	def __str__(self) -> str:
		pass

	def _format_number(self, number: float) -> float:
		return round(number, 3)

class CustomCircle(CustomEntity):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		super().__init__(entity)
		self.center = self._point_to_tuple(self.entity.dxf.center)
		self.radius = self.entity.dxf.radius
		self.points = [self.center]

	def get_length(self) -> float:
		return (math.pi * 2 * self.radius)

	def is_connected(self, entity) -> bool:
		return (False)
	
	def __str__(self) -> str:
		return f"Circle with center: {self.center} and radius: {self.radius} and length: {self._format_number(self.get_length())}"

class CustomArc(CustomEntity):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		super().__init__(entity)
		self.center = self._point_to_tuple(self.entity.dxf.center)
		self.radius = self.entity.dxf.radius
		start_point = self._point_to_tuple(self.entity.start_point)
		end_point = self._point_to_tuple(self.entity.end_point)
		self.points = [start_point, end_point]

	def get_length(self) -> float:
		arc: ezdxf.entities.Arc = self.entity
		start_point = arc.start_point
		end_point = arc.end_point
		start_angle = arc.dxf.start_angle
		end_angle = arc.dxf.end_angle
		if (end_angle - start_angle) < 0:
			end_angle += 360
		arc_length = self.radius * math.radians(abs(end_angle - start_angle))
		return (arc_length)

	def __str__(self) -> str:
		return f"Arc with center: {self.center}, radius: {self._format_number(self.radius)}, start_point: {self.start_point}, end_point: {self.end_point} and length: {self._format_number(self.get_length())}"

class CustomLine(CustomEntity):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		super().__init__(entity)
		start_point = self._point_to_tuple(self.entity.dxf.start)
		end_point = self._point_to_tuple(self.entity.dxf.end)
		self.points = [start_point, end_point]

	def	get_length(self) -> float:
		line: ezdxf.entities.Line = self.entity
		return line.dxf.start.distance(line.dxf.end)

	# def is_connected(self, entity: CustomEntity) -> bool:
	# 	return self._is_point_connected(entity.start_point) or self._is_point_connected(entity.end_point)

	def __str__(self) -> str:
		return f"Line with start_point: {self.start_point}, end_point: {self.end_point} and length: {self._format_number(self.get_length())}"

class CustomPoly(CustomEntity):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		super().__init__(entity)
		if self.entity.dxftype() == 'POLYLINE':
			self.points = [self._point_to_tuple(point.dxf.location) for point in self.entity.vertices]
		elif self.entity.dxftype() == 'LWPOLYLINE':
			self.points = [(point[0], point[1]) for point in self.entity.vertices()]
		self.is_closed = self.entity.is_closed

	def get_length(self) -> float:
		total = 0.0
		for i in range(len(self.points) - 1):
			j = i + 1
			x1, y1 = self.points[i][0], self.points[i][1]
			x2, y2 = self.points[j][0], self.points[j][1]
			p = [x1, y1]
			q = [x2, y2]
			total += math.dist(p, q)
		if self.is_closed:
			x1, y1 = self.points[0][0], self.points[0][1]
			x2, y2 = self.points[-1][0], self.points[-1][1]
			p = [x1, y1]
			q = [x2, y2]
			total += math.dist(p, q)
		return (total)

	# def is_connected(self, entity: CustomEntity) -> bool:
	# 	for point in self.points:
	# 		if self.__compare_points(point, entity.start_point) or self.__compare_points(point, entity.end_point):
	# 			return (True)
	# 	return (False)

	# def __compare_points(self, p: tuple, q: tuple) -> bool:
	# 	start: bool = math.isclose(p[0], q[0]) and math.isclose(p[1], q[1])
	# 	return (start)

	def __str__(self) -> str:
		return f"Polyline with points: {self.points} and length: {self._format_number(self.get_length())}"

class CustomSpline(CustomEntity):
	def __init__(self, entity: ezdxf.entities.Spline):
		super().__init__(entity)
		self.points = [(float(point[0]), float(point[1]), float(point[2])) for point in self.entity.control_points]

	def get_length(self) -> float:
		total = 0.0
		points = self.points
		for i in range(len(points) - 1):
			x1, y1, z1 = points[i][0], points[i][1], points[i][2]
			x2, y2, z2 = points[i + 1][0], points[i + 1][1], points[i + 1][2]
			ds = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
			# ds = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
			total = total + ds
		return (total)

	# def is_connected(self, entity: CustomEntity) -> bool:
	# 	print("IS_CONNECTED")
	# 	for point in self.points:
	# 		if isinstance(entity, CustomSpline):
	# 			for entity_point in entity.points:
	# 				if self.__compare_points(point, entity_point):
	# 					return (True)
	# 		elif self.__compare_points(point, entity.start_point) or self.__compare_points(point, entity.end_point):
	# 			return (True)
	# 	return (False)

	def __str__(self) -> str:
		return f"Spline with control points: {self.points} and length: {self._format_number(self.get_length())}"