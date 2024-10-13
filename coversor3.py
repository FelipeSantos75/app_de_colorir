import re
import pyperclip
import math
import xml.etree.ElementTree as ET

def svg_to_dart(svg_content):
    shapes = []
    root = ET.fromstring(svg_content)
    # Define the SVG namespace
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    shapes = traverse_svg(root, ns)
    return '\n\n'.join(shapes)

def traverse_svg(element, ns, id_prefix='', shapes=None, group_counters=None, path_counters=None):
    if shapes is None:
        shapes = []
    if group_counters is None:
        group_counters = {}
    if path_counters is None:
        path_counters = {}

    # Handle the element
    tag = element.tag
    if '}' in tag:
        tag = tag.split('}', 1)[1]  # Remove namespace

    if tag == 'g':
        # Get group ID
        group_id = element.attrib.get('id')
        if group_id:
            new_id_prefix = f"{id_prefix}_{group_id}" if id_prefix else group_id
        else:
            # Assign default group ID
            group_counters.setdefault(id_prefix, 0)
            group_counters[id_prefix] += 1
            group_num = group_counters[id_prefix]
            new_id_prefix = f"{id_prefix}_g{group_num}" if id_prefix else f"g{group_num}"
        # Recurse into children
        for child in element:
            traverse_svg(child, ns, new_id_prefix, shapes, group_counters, path_counters)
    elif tag in ('path', 'circle', 'rect', 'ellipse'):
        # Generate shape ID
        element_id = element.attrib.get('id')
        if element_id:
            shape_id = f"{id_prefix}_{element_id}" if id_prefix else element_id
        else:
            # Assign default shape ID
            path_counters.setdefault(id_prefix, 0)
            path_counters[id_prefix] += 1
            path_num = path_counters[id_prefix]
            shape_id = f"{id_prefix}_path{path_num}" if id_prefix else f"path{path_num}"
        # Process the shape
        if tag == 'path':
            d = element.attrib.get('d')
            if d:
                # Clean and convert path data
                d_clean = ' '.join(d.strip().split())
                d_converted = convert_arcs_to_beziers(d_clean)
                shape = f"""Shape(
  id: '{shape_id}',
  path: parseSvgPathData(
    '{d_converted}',
  ),
  color: Colors.white,
),"""
                shapes.append(shape)
        elif tag == 'circle':
            cx = float(element.attrib.get('cx', '0'))
            cy = float(element.attrib.get('cy', '0'))
            r = float(element.attrib.get('r', '0'))
            path_data = circle_to_path(cx, cy, r)
            shape = f"""Shape(
  id: '{shape_id}',
  path: parseSvgPathData(
    '{path_data}',
  ),
  color: Colors.white,
),"""
            shapes.append(shape)
        elif tag == 'rect':
            x = float(element.attrib.get('x', '0'))
            y = float(element.attrib.get('y', '0'))
            width = float(element.attrib.get('width', '0'))
            height = float(element.attrib.get('height', '0'))
            rx = float(element.attrib.get('rx', '0'))
            ry = float(element.attrib.get('ry', '0'))
            path_data = rect_to_path(x, y, width, height, rx, ry)
            shape = f"""Shape(
  id: '{shape_id}',
  path: parseSvgPathData(
    '{path_data}',
  ),
  color: Colors.white,
),"""
            shapes.append(shape)
        elif tag == 'ellipse':
            cx = float(element.attrib.get('cx', '0'))
            cy = float(element.attrib.get('cy', '0'))
            rx = float(element.attrib.get('rx', '0'))
            ry = float(element.attrib.get('ry', '0'))
            path_data = ellipse_to_path(cx, cy, rx, ry)
            shape = f"""Shape(
  id: '{shape_id}',
  path: parseSvgPathData(
    '{path_data}',
  ),
  color: Colors.white,
),"""
            shapes.append(shape)
    else:
        # Recurse into children for other elements
        for child in element:
            traverse_svg(child, ns, id_prefix, shapes, group_counters, path_counters)
    return shapes

def circle_to_path(cx, cy, r):
    """Convert a circle to path data using cubic Bezier curves."""
    c = r * 0.552284749831
    path_data = (
        f'M{cx - r},{cy} '
        f'C{cx - r},{cy - c} {cx - c},{cy - r} {cx},{cy - r} '
        f'C{cx + c},{cy - r} {cx + r},{cy - c} {cx + r},{cy} '
        f'C{cx + r},{cy + c} {cx + c},{cy + r} {cx},{cy + r} '
        f'C{cx - c},{cy + r} {cx - r},{cy + c} {cx - r},{cy} Z'
    )
    return path_data

def rect_to_path(x, y, width, height, rx, ry):
    """Convert a rectangle (with optional rounded corners) to path data."""
    if rx == 0 and ry == 0:
        # Simple rectangle
        path_data = f'M{x},{y} h{width} v{height} h{-width} Z'
    else:
        # Rectangle with rounded corners
        rx = min(rx, width / 2)
        ry = min(ry, height / 2)
        path_data = (
            f'M{x + rx},{y} '
            f'H{x + width - rx} '
            f'C{x + width},{y} {x + width},{y} {x + width},{y + ry} '
            f'V{y + height - ry} '
            f'C{x + width},{y + height} {x + width},{y + height} {x + width - rx},{y + height} '
            f'H{x + rx} '
            f'C{x},{y + height} {x},{y + height} {x},{y + height - ry} '
            f'V{y + ry} '
            f'C{x},{y} {x},{y} {x + rx},{y} Z'
        )
    return path_data

def ellipse_to_path(cx, cy, rx, ry):
    """Convert an ellipse to path data using cubic Bezier curves."""
    c = 0.552284749831
    dx = rx * c
    dy = ry * c
    path_data = (
        f'M{cx - rx},{cy} '
        f'C{cx - rx},{cy - dy} {cx - dx},{cy - ry} {cx},{cy - ry} '
        f'C{cx + dx},{cy - ry} {cx + rx},{cy - dy} {cx + rx},{cy} '
        f'C{cx + rx},{cy + dy} {cx + dx},{cy + ry} {cx},{cy + ry} '
        f'C{cx - dx},{cy + ry} {cx - rx},{cy + dy} {cx - rx},{cy} Z'
    )
    return path_data

def convert_arcs_to_beziers(path_data):
    """Convert 'A' commands in path data to cubic Bezier curves."""
    # This is a placeholder for actual arc conversion logic.
    # For production code, consider using a proper SVG path parser.
    return path_data  # Returning as is for now

# Example usage:
if __name__ == "__main__":
    svg_file_path = 'assets/32042198_7888840.svg'  # Replace with your SVG file path
    try:
        with open(svg_file_path, 'r', encoding='utf-8') as svg_file:
            svg_content = svg_file.read()
        dart_code = svg_to_dart(svg_content)
        pyperclip.copy(dart_code)
        print("O código Dart foi copiado para a área de transferência.")
    except FileNotFoundError:
        print("Arquivo SVG não encontrado. Verifique o caminho e tente novamente.")
