import ezdxf
from enum import Enum

DrawingCustomEntityType = Enum('DrawingCustomEntityType', ["LINE", "POLYLINE", "ARC", "CIRCLE"])

class DrawingCustomEntity:
	def __init__(self, entity: ezdxf.entities.DXFEntity):
		self.entity = entity
		self.start_point = None
		self.end_point = None
		self.center = None
		self.radius = None
		self.__set_entity_points()
		self.entity_type = self.__get_entity_type()

	def __contains_point(self, point):
		if self.entity_type == DrawingCustomEntityType.LINE:
			return self.start_point == point or self.end_point == point
		elif self.entity_type == DrawingCustomEntityType.ARC:
			return self.start_point == point or self.end_point == point or self.center == point
		elif self.entity_type == DrawingCustomEntityType.CIRCLE:
			return self.center == point

	def __get_entity_type(self):
		if self.entity.dxftype() == 'LINE':
			return DrawingCustomEntityType.LINE
		elif self.entity.dxftype() == 'ARC':
			return DrawingCustomEntityType.ARC
		elif self.entity.dxftype() == 'CIRCLE':
			return DrawingCustomEntityType.CIRCLE
		else:
			return DrawingCustomEntityType.POLYLINE

	def __set_entity_points(self):
		if self.entity_type == DrawingCustomEntityType.LINE:
			self.start_point = self.entity.dxf.start
			self.end_point = self.entity.dxf.end
		elif self.entity_type == DrawingCustomEntityType.ARC:
			self.start_point = self.entity.start_point
			self.end_point = self.entity.end_point
			self.center = self.entity.dxf.center
			self.radius = self.entity.dxf.radius
		elif self.entity_type == DrawingCustomEntityType.CIRCLE:
			self.center = self.entity.dxf.center
			self.radius = self.entity.dxf.radius