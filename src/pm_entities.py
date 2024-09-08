from enum import Enum
from abc import ABC, abstractmethod
import math
import ezdxf

class PMEntityType(Enum):
	CIRCLE = 1
	ARC = 2
	LINE = 3
	POLY = 4
	SPLINE = 5
	LINE_SEGMENT = 6

class PMPoint:
	def __init__(self, x: float, y: float):
		self.x = x
		self.y = y

	def __eq__(self, other):
		return (self.x == other.x and self.y == other.y) or (self.__is_close(other))

	def __is_close(self, other):
		return (math.isclose(self.x, other.x) and math.isclose(self.y, other.y))

	def __str__(self):
		return f"({self.x}, {self.y})"

	def __gt__(self, other):
		return (self.x > other.x and self.y > other.y)

class PMEntity(ABC):
	def __init__(self, entity: ezdxf.entities.DXFEntity = None, start_point: PMPoint = None, end_point: PMPoint = None):
		self.entity = entity
		self.points = None
		self.type = None
		self.radius = None
		self.center = None
		self.start_point = start_point
		self.end_point = end_point
		self.is_curvy = False
		self.connectable = True


	@abstractmethod
	def __eq__(self, other):
		pass

	@abstractmethod
	def get_length(self) -> float:
		pass

	def is_connected(self, entity) -> bool:
		if self.start_point is None or self.end_point is None:
			return (False)
		if entity.start_point is None or entity.end_point is None:
			return (False)
		if self.start_point == entity.start_point or self.start_point == entity.end_point:
			return (True)
		elif self.end_point == entity.start_point or self.end_point == entity.end_point:
			return (True)
		return (False)

	@staticmethod
	def get_instance(entity: ezdxf.entities.DXFEntity) -> tuple:
		if entity.dxftype() == 'LINE':
			start_point = PMPoint(entity.dxf.start.x, entity.dxf.start.y)
			end_point = PMPoint(entity.dxf.end.x, entity.dxf.end.y)
			return (PMLineSegment(start_point=start_point, end_point=end_point), 1)
		elif entity.dxftype() == 'CIRCLE':
			return (PMCircle(entity), 1)
		elif entity.dxftype() == 'ARC':
			return (PMArc(entity), 1)
		elif entity.dxftype() == 'SPLINE':
			return (PMSpline(entity), 1)
		else:
			return (None, 0)

class PMLineSegment(PMEntity):
	def __init__(self, start_point: PMPoint, end_point: PMPoint):
		super().__init__(start_point=start_point, end_point=end_point)
		self.length = self.get_length()
		self.type = PMEntityType.LINE_SEGMENT

	def get_length(self) -> float:
		return math.dist([self.start_point.x, self.start_point.y], [self.end_point.x, self.end_point.y])

	def __str__(self):
		return f"[Entity][PMLineSegment] Start: {self.start_point}, end: {self.end_point}, length: {self.length}"

	@staticmethod
	def poly_points_to_line_segments(points: [PMPoint], is_closed: bool) -> []:
		line_segments = []
		for i in range(len(points) - 1):
			line_segments.append(PMLineSegment(points[i], points[i + 1]))
		if is_closed and len(points) > 1 and points[-1] != points[0]:
			line_segments.append(PMLineSegment(points[-1], points[0]))
		return line_segments

	@staticmethod
	def get_poly_points(entity: ezdxf.entities.DXFEntity):
		points = None
		if entity.dxftype() == 'POLYLINE':
			points = [PMPoint(point.dxf.location.x, point.dxf.location.y) for point in entity.vertices]
		elif entity.dxftype() == 'LWPOLYLINE':
			points = [PMPoint(point[0], point[1]) for point in entity.vertices()]
		if points is not None:
			points = PMLineSegment.__remove_duplicate_points(points)
		return points

	@staticmethod
	def __remove_duplicate_points(points: [PMPoint]) -> [PMPoint]:
		for i in range(len(points) - 1):
			if points[i] == points[i + 1]:
				points.pop(i)
		return points

	def __eq__(self, other):
		if (other.type != PMEntityType.LINE_SEGMENT):
			return (False)
		return (self.start_point == other.start_point and self.end_point == other.end_point) \
				or (self.start_point == other.end_point and self.end_point == other.start_point)

class PMCircle(PMEntity):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		super().__init__(entity)
		self.center = PMPoint(self.entity.dxf.center.x, self.entity.dxf.center.y)
		self.radius = self.entity.dxf.radius
		self.type = PMEntityType.CIRCLE
		self.is_curvy = True
		self.connectable = False

	def get_length(self) -> float:
		return (math.pi * 2 * self.radius)

	def is_connected(self, entity) -> bool:
		return (False)

	def __str__(self) -> str:
		return f"Circle with center: {self.center} and radius: {self.radius} and length: {self.get_length()}"

	def __eq__(self, other):
		if (other.type != PMEntityType.CIRCLE):
			return (False)
		return (self.center == other.center and self.radius == other.radius)

class PMLine(PMEntity):
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		super().__init__(entity)
		self.start_point = PMPoint(self.entity.dxf.start.x, self.entity.dxf.start.y)
		self.end_point = PMPoint(self.entity.dxf.end.x, self.entity.dxf.end.y)
		self.type = PMEntityType.LINE
		self.is_curvy = False

	def	get_length(self) -> float:
		line: ezdxf.entities.Line = self.entity
		return line.dxf.start.distance(line.dxf.end)

	def __str__(self) -> str:
		return f"Line with start_point: {self.start_point}, end_point: {self.end_point} and length: {self.get_length()}"

	def __eq__(self, other):
		if (other.type != PMEntityType.LINE):
			return (False)
		return (self.start_point == other.start_point and self.end_point == other.end_point) \
				or (self.start_point == other.end_point and self.end_point == other.start_point)

class PMSpline(PMEntity):
	def __init__(self, entity: ezdxf.entities.Spline):
		super().__init__(entity)
		self.points = [PMPoint(float(point[0]), float(point[1])) for point in self.entity.control_points]
		self.type = PMEntityType.SPLINE
		self.is_curvy = True
		self.start_point = PMPoint(self.points[0].x, self.points[0].y)
		self.end_point = PMPoint(self.points[-1].x, self.points[-1].y)

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
		return f"[Entity][Spline] Start: {self.start_point}, end: {self.end_point} and length: {self.get_length()}"

	def is_connected(self, entity) -> bool:
		for p in self.points:
			if p == entity.start_point or p == entity.end_point:
				return (True)

	def __eq__(self, other):
		if (other.type != PMEntityType.SPLINE):
			return (False)
		if (len(self.points) != len(other.points)):
			return (False)
		self_start, self_end = PMPoint(round(self.points[0].x), round(self.points[0].y)), PMPoint(round(self.points[-1].x), round(self.points[-1].y))
		other_start, other_end = PMPoint(round(other.points[0].x), round(other.points[0].y)), PMPoint(round(other.points[-1].x), round(other.points[-1].y))
		same = (self_start == other_start and self_end == other_end) or (self_start == other_end and self_end == other_start)
		return same

class PMArc(PMEntity):
	def __init__(self, entity: ezdxf.entities.Arc):
		super().__init__(entity)
		self.center = PMPoint(self.entity.dxf.center.x, self.entity.dxf.center.y)
		self.radius = self.entity.dxf.radius
		self.start_angle = self.entity.dxf.start_angle
		self.end_angle = self.entity.dxf.end_angle
		self.type = PMEntityType.ARC
		self.is_curvy = True
		self.start_point = PMPoint(self.entity.start_point.x, self.entity.start_point.y)
		self.end_point = PMPoint(self.entity.end_point.x, self.entity.end_point.y)

	def get_length(self) -> float:
		start_angle = self.start_angle
		end_angle = self.end_angle
		if (end_angle - start_angle) < 0:
			end_angle += 360
		arc_length = self.radius * math.radians(abs(end_angle - start_angle))
		return (arc_length)

	def __str__(self) -> str:
		return f"Arc with center: {self.center}, radius: {self.radius}, start_angle: {self.start_angle}, end_angle: {self.end_angle} and length: {self.get_length()}"

	def is_connected(self, entity) -> bool:
		return (self.start_point == entity.start_point or self.start_point == entity.end_point or self.end_point == entity.start_point or self.end_point == entity.end_point)

	def __eq__(self, other):
		if (other.type != PMEntityType.ARC):
			return (False)
		return (self.center == other.center and self.radius == other.radius and self.start_angle == other.start_angle and self.end_angle == other.end_angle)