import ezdxf
import math

class DrawingAnalyserUtils:
	def __init__(self, msp: ezdxf.layouts.modelspace):
		self.msp = msp
		self.included_entities = []

	def is_point_included_in_line_segment(self, point: ezdxf.math.Vec2, line: ezdxf.entities.Line) -> bool:
		start_point: ezdxf.math.Vec2 = line.dxf.start
		end_point: ezdxf.math.Vec2 = line.dxf.end
		if ((point.y - start_point.y) * (end_point.x - start_point.x) - (point.x - start_point.x) * (end_point.y - start_point.y)) != 0:
			return False
		return False
	
	def is_point_on_polyline(polyline, point, tolerance=1e-6):
		"""
		Check if a point is on a polyline within a given tolerance.
		
		:param polyline: List of (x, y) tuples representing the vertices of the polyline
		:param point: Tuple (x, y) representing the point to check
		:param tolerance: Distance tolerance (default is 1e-6)
		:return: True if the point is on the polyline, False otherwise
		"""
		# Check each line segment in the polyline
		for i in range(len(polyline) - 1):
			start = polyline[i]
			end = polyline[i + 1]
			
			# If the point is within tolerance distance of the line segment, it's on the polyline
			if self.__distance_point_to_line(start, end, point) <= tolerance:
				return True
		
		return False

	# TODO: Test this method
	def __distance_point_to_line(p1, p2, point):
		"""Calculate the distance from a point to a line segment."""
		x1, y1 = p1
		x2, y2 = p2
		x, y = point
		
		# Vector from p1 to p2
		dx = x2 - x1
		dy = y2 - y1
		
		# If the line segment is just a point, return distance to that point
		if dx == 0 and dy == 0:
			return math.sqrt((x - x1)**2 + (y - y1)**2)
		
		# Calculate the t that minimizes the distance
		t = ((x - x1) * dx + (y - y1) * dy) / (dx**2 + dy**2)
		
		# See if this represents one of the segment's endpoints or a point in the middle
		if t < 0:
			dx = x - x1
			dy = y - y1
		elif t > 1:
			dx = x - x2
			dy = y - y2
		else:
			near_x = x1 + t * dx
			near_y = y1 + t * dy
			dx = x - near_x
			dy = y - near_y
		return math.sqrt(dx**2 + dy**2)

	# TODO: Test this method
	def is_point_on_arc(self, point: ezdxf.math.Vec2, arc: ezdxf.entities.Arc) -> bool:
		# Calculate the distance between the point and the center of the arc
		distance = math.sqrt((point_x - center_x)**2 + (point_y - center_y)**2)
		
		# Check if the point is on the circle (within a small tolerance)
		tolerance = 1e-6
		if abs(distance - radius) > tolerance:
			return False

		point_x, point_y = point.x, point.y
		center_x, center_y = arc.dxf.center.x, arc.dxf.center.y
		point_angle = math.atan2(point_y - center_y, point_x - center_x)
		
		# Convert angle to degrees and ensure it's positive
		point_angle = math.degrees(point_angle)
		if point_angle < 0:
			point_angle += 360
		
		# Normalize start and end angles to be between 0 and 360
		start_angle = start_angle % 360
		end_angle = end_angle % 360
		
		# Check if the point's angle is within the arc's range
		if start_angle <= end_angle:
			return start_angle <= point_angle <= end_angle
		else:  # Arc crosses the 0/360 degree line
			return point_angle >= start_angle or point_angle <= end_angle
