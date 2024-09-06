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
		self.__set_entity_points()

	def __set_entity_points(self) -> None:
		if self.entity.dxftype() == 'LINE':
			self.start_point = self.__point_to_tuple(self.entity.dxf.start)
			self.end_point = self.__point_to_tuple(self.entity.dxf.end)
		elif self.entity.dxftype() == 'ARC':
			self.start_point = self.__point_to_tuple(self.entity.start_point)
			self.end_point = self.__point_to_tuple(self.entity.end_point)
			self.center = self.__point_to_tuple(self.entity.dxf.center)
			self.radius = self.entity.dxf.radius
		elif self.entity.dxftype() == 'CIRCLE':
			self.center = self.__point_to_tuple(self.entity.dxf.center)
			self.start_point = self.__point_to_tuple(self.entity.dxf.center)
			self.end_point = self.__point_to_tuple(self.entity.dxf.center)
			self.radius = self.entity.dxf.radius
		elif self.entity.dxftype() == 'POLYLINE':
			self.points = [self.__point_to_tuple(point.dxf.location) for point in self.entity.vertices()]
		elif self.entity.dxftype() == 'LWPOLYLINE':
			self.points = [(point[0], point[1]) for point in self.entity.vertices()]

	def __point_to_tuple(self, point) -> tuple:
		return (point.x, point.y)

	def _is_point_connected(self, point: tuple) -> bool:
		start: bool = math.isclose(self.start_point[0], point[0]) and math.isclose(self.start_point[1], point[1])
		end: bool = math.isclose(self.end_point[0], point[0]) and math.isclose(self.end_point[1], point[1])
		return (start or end)

	@abstractmethod
	def get_length(self) -> float:
		pass

	@abstractmethod
	def is_connected(self, entity: CustomEntity) -> bool:
		pass

class CustomCircle(CustomEntity):
	def get_length(self) -> float:
		return (math.pi * 2 * self.radius)

	def is_connected(self, entity) -> bool:
		return (False)

class CustomArc(CustomEntity):
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

	def is_connected(self, entity: CustomEntity) -> bool:
		return (self._is_point_connected(entity.start_point) \
				or self._is_point_connected(entity.end_point))

class CustomLine(CustomEntity):
	def	get_length(self) -> float:
		line: ezdxf.entities.Line = self.entity
		return line.start_point.distance(self.end_point)

	def is_connected(self, entity: CustomEntity) -> bool:
		return self._is_point_connected(entity.start_point) or self._is_point_connected(entity.end_point)

class CustomPoly(CustomEntity):
	def get_length(self) -> float:
		total = 0.0
		for i in range(len(self.points)):
			for j in range(i + 1, len(self.points)):
				x1, y1 = self.points[i][0], self.points[i][1]
				x2, y2 = self.points[j][0], self.points[j][1]
				p = [x1, y1]
				q = [x2, y2]
				total += math.dist(p, q)
		return (total)

	def is_connected(self, entity: CustomEntity) -> bool:
		for point in self.points:
			if self.__compare_points(point, entity.start_point) or self.__compare_points(point, entity.end_point):
				return (True)
		return (False)

	def __compare_points(self, p: tuple, q: tuple) -> bool:
		start: bool = math.isclose(self.p[0], q[0]) and math.isclose(self.p[1], q[1])
		return (start)
