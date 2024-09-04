import ezdxf
import math

doc = ezdxf.readfile("ex.dxf")
msp = doc.modelspace()
total_length = 0.0

# Process LINE entities
for line in msp.query('LINE'):
	start_point = line.dxf.start
	end_point = line.dxf.end
	line_len = start_point.distance(end_point)
	print(f"Line from {start_point} to {end_point}, len: {line_len}")
	total_length += line_len

# Process ARC entities
for arc in msp.query('ARC'):
	start_point = arc.start_point
	end_point = arc.end_point
	center = arc.dxf.center
	radius = arc.dxf.radius
	start_angle = arc.dxf.start_angle
	end_angle = arc.dxf.end_angle

	import math
	if (end_angle - start_angle) < 0:
		end_angle += 360
	arc_length = radius * math.radians(abs(end_angle - start_angle))
	print(f"Arc found at {center}, Radius: {radius}, Arc Length: {arc_length}, start_point: {start_point}, end_point: {end_point}")
	total_length += arc_length

# Compose the polyline from the vertices
for polyline in msp.query('POLYLINE'):
	print(f"Polyline found with {len(polyline)} vertices")
	poly_len = 0
	first_vertex = polyline.vertices[0].dxf.location
	last_vertex = polyline.vertices[-1].dxf.location
	for i in range(len(polyline)):
		if i == 0:
			continue
		vertex = polyline.vertices[i]
		print(f"Vertex at {vertex.dxf.location}")
		poly_len += polyline.vertices[i].dxf.location.distance(polyline.vertices[i-1].dxf.location)
	print(f"Polyline length: {poly_len}")
	total_length += poly_len


# Get a list of all unique DXF entity types in the file
entities = set(entity.dxftype() for entity in msp)

print("Entities found in the DXF file:")
for entity in entities:
    print(entity)


# Print the total length of the outer border
print(f"Total length of the outer border: {total_length:.2f} units")