import re
import pyperclip
import math

def svg_to_dart(svg_content):
    shapes = []

    # Regular expressions to find SVG elements
    path_regex = re.compile(r'<path[^>]*d="([^"]+)"[^>]*>')
    circle_regex = re.compile(r'<circle[^>]*cx="([^"]+)"[^>]*cy="([^"]+)"[^>]*r="([^"]+)"[^>]*>')
    rect_regex = re.compile(r'<rect[^>]*>')
    ellipse_regex = re.compile(r'<ellipse[^>]*cx="([^"]+)"[^>]*cy="([^"]+)"[^>]*rx="([^"]+)"[^>]*ry="([^"]+)"[^>]*>')

    # Handle <path> elements
    paths = path_regex.findall(svg_content)
    for d in paths:
        # Clean up the path data
        d_clean = ' '.join(d.strip().split())
        # Convert arcs to cubic Bezier curves
        d_converted = convert_arcs_to_beziers(d_clean)
        shape = f"""Shape(
          path: parseSvgPathData(
            '{d_converted}',
          ),
          color: Colors.white,
        ),"""
        shapes.append(shape)

    # Handle <circle> elements
    circles = circle_regex.findall(svg_content)
    for cx, cy, r in circles:
        path_data = circle_to_path(float(cx), float(cy), float(r))
        shape = f"""Shape(
          path: parseSvgPathData(
            '{path_data}',
          ),
          color: Colors.white,
        ),"""
        shapes.append(shape)

    # Handle <rect> elements
    rects = rect_regex.findall(svg_content)
    for rect in rects:
        attributes = extract_attributes(rect)
        x = float(attributes.get('x', '0'))
        y = float(attributes.get('y', '0'))
        width = float(attributes.get('width', '0'))
        height = float(attributes.get('height', '0'))
        rx = float(attributes.get('rx', '0'))
        ry = float(attributes.get('ry', '0'))

        path_data = rect_to_path(x, y, width, height, rx, ry)
        shape = f"""Shape(
          path: parseSvgPathData(
            '{path_data}',
          ),
          color: Colors.white,
        ),"""
        shapes.append(shape)

    # Handle <ellipse> elements
    ellipses = ellipse_regex.findall(svg_content)
    for cx, cy, rx, ry in ellipses:
        path_data = ellipse_to_path(float(cx), float(cy), float(rx), float(ry))
        shape = f"""Shape(
          path: parseSvgPathData(
            '{path_data}',
          ),
          color: Colors.white,
        ),"""
        shapes.append(shape)

    return '\n\n'.join(shapes)

def extract_attributes(element_str):
    """Extract attributes from an SVG element string."""
    attributes = {}
    attr_regex = re.compile(r'(\w+)="([^"]+)"')
    for attr, value in attr_regex.findall(element_str):
        attributes[attr] = value
    return attributes

def circle_to_path(cx, cy, r):
    """Convert a circle to path data using cubic Bezier curves."""
    # Same implementation as before
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
    # This is a simplified implementation; for production code, consider using a proper SVG path parser.
    # Regular expression to match arc commands
    arc_regex = re.compile(r'([a-df-zA-DF-Z])|(\-?\d*\.?\d+(?:e[\-+]?\d+)?)')
    tokens = arc_regex.findall(path_data)
    tokens = [t[0] if t[0] else t[1] for t in tokens]

    new_tokens = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.upper() == 'A':
            # Arc command found, extract parameters
            is_relative = token.islower()
            rx = float(tokens[i + 1])
            ry = float(tokens[i + 2])
            x_axis_rotation = float(tokens[i + 3])
            large_arc_flag = int(tokens[i + 4])
            sweep_flag = int(tokens[i + 5])
            x = float(tokens[i + 6])
            y = float(tokens[i + 7])
            # Approximate the arc with cubic Bezier curves
            # For simplicity, we'll use a placeholder function here
            beziers = arc_to_bezier(rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y)
            new_tokens.extend(beziers)
            i += 8
        else:
            new_tokens.append(token)
            i += 1

    return ' '.join(new_tokens)

def arc_to_bezier(rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y):
    """Approximate an arc with cubic Bezier curves."""
    # Placeholder implementation; in practice, you'd calculate control points here
    # For the sake of this example, we'll return a straight line to the endpoint
    return [f'L{x},{y}']


# Exemplo de uso:
if __name__ == "__main__":
    svg_file_path = 'assets/49266001_9226009.svg' #input("Digite o caminho para o arquivo SVG: ")
    try:
        with open(svg_file_path, 'r', encoding='utf-8') as svg_file:
            svg_content = svg_file.read()
        dart_code = svg_to_dart(svg_content)
        pyperclip.copy(dart_code)
        print("O código Dart foi copiado para a área de transferência.")
    except FileNotFoundError:
        print("Arquivo SVG não encontrado. Verifique o caminho e tente novamente.")
