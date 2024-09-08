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
	LINE_SEGMENT = 6

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

class PMEntity(ABC):
	def __init__(self, entity: ezdxf.entities.DXFEntity = None, start_point: CustomPoint = None, end_point: CustomPoint = None):
		self.entity = entity
		self.points = None
		self.type = None
		self.radius = None
		self.center = None
		self.start_point = start_point
		self.end_point = end_point
		self.is_curvy = False

	@abstractmethod
	def get_length(self) -> float:
		pass

	def is_connected(self, entity) -> bool:
		if self.start_point == entity.start_point or self.start_point == entity.end_point:
			return (True)
		elif self.end_point == entity.start_point or self.end_point == entity.end_point:
			return (True)
		return (False)

class PMLineSegment(PMEntity):
	def __init__(self, start_point: CustomPoint, end_point: CustomPoint):
		super().__init__(entity, start_point, end_point)
		self.length = self.get_length()
		self.type = CustomEntityType.LINE_SEGMENT

	def get_length(self) -> float:
		return math.dist([self.start_point.x, self.start_point.y], [self.end_point.x, self.end_point.y])

	def __str__(self):
		return f"Start: {self.start_point}, End: {self.end_point}"

class PMCircle(PMEntity):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		super().__init__(entity)
		self.center = CustomPoint(self.entity.dxf.center.x, self.entity.dxf.center.y)
		self.radius = self.entity.dxf.radius
		self.type = CustomEntityType.CIRCLE
		self.is_curvy = True

	def get_length(self) -> float:
		return (math.pi * 2 * self.radius)

	def is_connected(self, entity) -> bool:
		return (False)

	def __str__(self) -> str:
		return f"Circle with center: {self.center} and radius: {self.radius} and length: {self.get_length()}"

class PMLine(PMEntity):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		super().__init__(entity)
		self.start_point = CustomPoint(self.entity.dxf.start.x, self.entity.dxf.start.y)
		self.end_point = CustomPoint(self.entity.dxf.end.x, self.entity.dxf.end.y)
		self.type = CustomEntityType.LINE
		self.is_curvy = False

	def	get_length(self) -> float:
		line: ezdxf.entities.Line = self.entity
		return line.dxf.start.distance(line.dxf.end)

	def __str__(self) -> str:
		return f"Line with start_point: {self.start_point}, end_point: {self.end_point} and length: {self.get_length()}"

class PMSpline(PMEntity):
	def __init__(self, entity: ezdxf.entities.Spline):
		super().__init__(entity)
		self.points = [CustomPoint(float(point[0]), float(point[1])) for point in self.entity.control_points]
		self.type = CustomEntityType.SPLINE
		self.is_curvy = True

	def get_length(self) -> float:
		total = 0.0
		points = self.points
		for i in range(len(points) - 1):
			x1, y1 = points[i].x, points[i].y
			x2, y2 = points[i + 1].x, points[i + 1].y
			ds = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
			total = total + ds
		return (total)

	def __str__(self) -> str:
		return f"Spline with control points: {self.points} and length: {self.get_length()}"

class CustomEntity(ABC):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		self.entity: ezdxf.entities.DXFEntity = entity
		self.start_point: CustomPoint = None
		self.end_point: CustomPoint = None
		self.points: [CustomPoint] = None
		self.type = None
		self.radius: float = None
		self.center: CustomPoint = None		

	def _is_point_connected(self, point: CustomPoint) -> bool:
		for p in self.points:
			is_close: bool = math.isclose(p.x, point.x) and math.isclose(p.y, point.y)
			if is_close:
				return (True)
		return (False)

	def _remove_duplicated_points(self) -> None:
		for i in range(len(self.points) - 1, -1, -1):
			p1 = self.points[i]
			for j in range (i - 1, 0):
				p2 = self.points[j]
				if (p1.x == p2.x and p1.y == p2.y):
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

class CustomLineSegment(CustomEntity):
	def __init__(self, entity: ezdxf.entities.DXFEntity, start_point: CustomPoint, end_point: CustomPoint):
		self.start_point = start_point
		self.end_point = end_point
		self.length = self.get_length()
		self.points = [self.start_point, self.end_point]

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


	def get_length(self):
		return math.dist([self.start_point.x, self.start_point.y], [self.end_point.x, self.end_point.y])

	def is_curvy_type(self) -> bool:
		return (False)

	def __str__(self):
		return f"Start: {self.start_point}, End: {self.end_point}"

class CustomCircle(CustomEntity):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		super().__init__(entity)
		self.center = CustomPoint(self.entity.dxf.center.x, self.entity.dxf.center.y)
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
		self.center = CustomPoint(self.entity.dxf.center.x, self.entity.dxf.center.y)
		self.radius = self.entity.dxf.radius
		start_point = CustomPoint(self.entity.start_point.x, self.entity.start_point.y)
		end_point = CustomPoint(self.entity.end_point.x, self.entity.end_point.y)
		self.points = [start_point, end_point]
		self.type = CustomEntityType.ARC
		self._remove_duplicated_points()

	def get_length(self) -> float:
		arc: ezdxf.entities.Arc = self.entity
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
		start_point = CustomPoint(self.entity.dxf.start.x, self.entity.dxf.start.y)
		end_point = CustomPoint(self.entity.dxf.end.x, self.entity.dxf.end.y)
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
			self.points = [CustomPoint(point.dxf.location.x, point.dxf.location.y) for point in self.entity.vertices]
		elif self.entity.dxftype() == 'LWPOLYLINE':
			self.points = [CustomPoint(point[0], point[1]) for point in self.entity.vertices()]
		self.type = CustomEntityType.POLY
		self.is_closed = self.entity.is_closed
		self._remove_duplicated_points()

	def get_length(self) -> float:
		total = 0.0
		for i in range(len(self.points) - 1):
			j = i + 1
			x1, y1 = self.points[i].x, self.points[i].y
			x2, y2 = self.points[j].x, self.points[j].y
			p = [x1, y1]
			q = [x2, y2]
			total += math.dist(p, q)
		if self.is_closed:
			x1, y1 = self.points[0].x, self.points[0].y
			x2, y2 = self.points[-1].x, self.points[-1].y
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
			line_segments.append(CustomLineSegment(self.entity, self.points[i], self.points[i + 1]))
		if self.is_closed:
			line_segments.append(CustomLineSegment(self.entity, self.points[-1], self.points[0]))
		return line_segments

class CustomSpline(CustomEntity):
	def __init__(self, entity: ezdxf.entities.Spline):
		super().__init__(entity)
		self.points = [CustomPoint(float(point[0]), float(point[1])) for point in self.entity.control_points]
		self.type = CustomEntityType.SPLINE
		self._remove_duplicated_points()

	def get_length(self) -> float:
		total = 0.0
		points = self.points
		for i in range(len(points) - 1):
			x1, y1 = points[i].x, points[i].y
			x2, y2 = points[i + 1].x, points[i + 1].y
			ds = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
			total = total + ds
		return (total)

	def is_curvy_type(self) -> bool:
		return (True)

	def __str__(self) -> str:
		return f"Spline with control points: {self.points} and length: {self._format_number(self.get_length())}"