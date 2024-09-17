

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class SvgPainter extends CustomPainter {
  final DrawableRoot svgRoot;
  final Map<String, Color> partColors;
  final Function(String) onPartTapped;
  List<_SvgPart> svgParts = [];

  SvgPainter({
    required this.svgRoot,
    required this.partColors,
    required this.onPartTapped,
  });

  @override
  void paint(Canvas canvas, Size size) {
    svgParts.clear();
    svgRoot.children.forEach((Drawable drawable) {
      if (drawable is DrawableShape) {
        String? id = drawable.id;
        if (id != null) {
          Color color = partColors[id] ?? Colors.white;
          Paint paint = Paint()..color = color;
          canvas.drawPath(drawable.path, paint);

          // Armazena o caminho para detecção de toque
          svgParts.add(_SvgPart(id: id, path: drawable.path));
        }
      }
    });
  }

  @override
  bool hitTest(Offset position) {
    for (var part in svgParts) {
      if (part.path.contains(position)) {
        onPartTapped(part.id);
        return true;
      }
    }
    return false;
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => true;
}

class _SvgPart {
  final String id;
  final Path path;

  _SvgPart({required this.id, required this.path});
}
