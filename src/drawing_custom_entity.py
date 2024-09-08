import ezdxf
import ezdxf.math
from abc import ABC, abstractmethod
import math
from enum import Enum

class CustomEntityType(Enum):
	CIRCLE = 1
	ARC = 2
	LINE = 3
	POLY = 4
	SPLINE = 5

class CustomPoint:
	def __init__(self, x: float, y: float):
		self.x = x
		self.y = y

	def __eq__(self, other):
		return (self.x == other.x and self.y == other.y) or (self.__is_close(other))

	def __is_close(self, other):
		return (math.isclose(self.x, other.x) and math.isclose(self.y, other.y))

	def __str__(self):
		return f"({self.x}, {self.y})"

class CustomLineSegment:
	def __init__(self, start_point: CustomPoint, end_point: CustomPoint):
		self.start_point = start_point
		self.end_point = end_point
		self.length = self.__get_length()

	def __get_common_point(self, other):
		if self.start_point == other.start_point or self.start_point == other.end_point:
			return (self.start_point)
		elif self.end_point == other.start_point or self.end_point == other.end_point:
			return (self.end_point)
		return (None)

	def __get_angle(self, other):
		common_point = self.__get_common_point(other)
		if common_point is None:
			return None
		
		# Vector for this line segment
		v1x = self.end_point.x - self.start_point.x
		v1y = self.end_point.y - self.start_point.y
		
		# Vector for the other line segment
		if other.start_point == common_point:
			v2x = other.end_point.x - other.start_point.x
			v2y = other.end_point.y - other.start_point.y
		else:
			v2x = other.start_point.x - other.end_point.x
			v2y = other.start_point.y - other.end_point.y
		
		# Calculate the angle using dot product and cross product
		dot_product = v1x * v2x + v1y * v2y
		cross_product = v1x * v2y - v1y * v2x
		
		angle = math.atan2(cross_product, dot_product)
		
		# Convert to degrees if needed
		angle_degrees = math.degrees(angle)
		
		return angle_degrees


	def __get_length(self):
		return math.dist((self.start_point.x, self.start_point.y), (self.end_point.x, self.end_point.y))

	def __str__(self):
		return f"Start: {self.start_point}, End: {self.end_point}"

class CustomEntity(ABC):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		self.entity: ezdxf.entities.DXFEntity = entity
		self.start_point: CustomPoint = None
		self.end_point: CustomPoint = None
		self.center: CustomPoint = None
		self.radius: float = None
		self.points: [CustomPoint] = None
		self.type = None
		
	def _point_to_tuple(self, point) -> tuple:
		return (point.x, point.y)

	def _is_point_connected(self, point: tuple) -> bool:
		for p in self.points:
			is_close: bool = math.isclose(p[0], point[0]) and math.isclose(p[1], point[1])
			if is_close:
				return (True)
		return (False)

	def _remove_duplicated_points(self) -> None:
		for i in range(len(self.points) - 1, -1, -1):
			p1 = self.points[i]
			for j in range (i - 1, 0):
				p2 = self.points[j]
				if (p1[0] == p2[0] and p1[1] == p2[1]):
					self.points.pop(i)

	def get_turns_count(self) -> int:
		return (0)

	@abstractmethod
	def is_curvy_type(self) -> bool:
		pass

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

	def find_common_point(self, entity):
		for idx, p1 in enumerate(self.points):
			if entity._is_point_connected(p1):
				return (p1, idx)
		return (None)

class CustomCircle(CustomEntity):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		super().__init__(entity)
		self.center = self._point_to_tuple(self.entity.dxf.center)
		self.radius = self.entity.dxf.radius
		self.points = [self.center]
		self.type = CustomEntityType.CIRCLE
		self._remove_duplicated_points()

	def get_length(self) -> float:
		return (math.pi * 2 * self.radius)

	def is_connected(self, entity) -> bool:
		return (False)

	def is_curvy_type(self) -> bool:
		return (True)
	
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
		self.type = CustomEntityType.ARC
		self._remove_duplicated_points()

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
	
	def is_curvy_type(self) -> bool:
		return (True)

class CustomLine(CustomEntity):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		super().__init__(entity)
		start_point = self._point_to_tuple(self.entity.dxf.start)
		end_point = self._point_to_tuple(self.entity.dxf.end)
		self.points = [start_point, end_point]
		self.type = CustomEntityType.LINE
		self._remove_duplicated_points()

	def	get_length(self) -> float:
		line: ezdxf.entities.Line = self.entity
		return line.dxf.start.distance(line.dxf.end)

	def is_curvy_type(self) -> bool:
		return (False)

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
		self.type = CustomEntityType.POLY
		self._remove_duplicated_points()

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

	def __str__(self) -> str:
		return f"Polyline with points: {self.points} and length: {self._format_number(self.get_length())}"

	def is_curvy_type(self) -> bool:
		return (False)

	def get_turns_count(self) -> int:
		turns_count = len(self.points) - 1
		if self.is_closed:
			turns_count += 1
		return (turns_count)

	def to_custom_line_segments(self) -> [CustomLineSegment]:
		line_segments = []
		for i in range(len(self.points) - 1):
			start_point = CustomPoint(self.points[i][0], self.points[i][1])
			end_point = CustomPoint(self.points[i + 1][0], self.points[i + 1][1])
			line_segments.append(CustomLineSegment(start_point, end_point))
		if self.is_closed:
			start_point = CustomPoint(self.points[-1][0], self.points[-1][1])
			end_point = CustomPoint(self.points[0][0], self.points[0][1])
			line_segments.append(CustomLineSegment(start_point, end_point))
		return line_segments

class CustomSpline(CustomEntity):
	def __init__(self, entity: ezdxf.entities.Spline):
		super().__init__(entity)
		self.points = [(float(point[0]), float(point[1]), float(point[2])) for point in self.entity.control_points]
		self.type = CustomEntityType.SPLINE
		self._remove_duplicated_points()

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

	def is_curvy_type(self) -> bool:
		return (True)

	def __str__(self) -> str:
		return f"Spline with control points: {self.points} and length: {self._format_number(self.get_length())}"