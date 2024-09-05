from enum import Enum

DrawingCustomEntityType = Enum('DrawingCustomEntityType', ["LINE", "POLYLINE", "ARC", "CIRCLE"])

class DrawingCustomEntity:
	def __init__(self, entity, entity_type: DrawingCustomEntityType):
		self.entity = entity
		self.entity_type = entity_type
		self.start_point = None
		self.end_point = None
		self.center = None
		self.radius = None
		self.__set_entity_points()

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