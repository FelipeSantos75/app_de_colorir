
import 'package:flutter/material.dart';

// Classe que define cada forma com seu Path e Cor
class Shape {
  Path path;
  Color color;

  Shape({required this.path, required this.color});
}

// Painter para desenhar múltiplas formas
class MultiShapePainter extends CustomPainter {
  final List<Shape> shapes;

  MultiShapePainter(this.shapes);

  @override
  void paint(Canvas canvas, Size size) {
    // Se necessário, podemos ajustar o canvas aqui
    for (var shape in shapes) {
      Paint fillPaint = Paint()
        ..color = shape.color
        ..style = PaintingStyle.fill;

      Paint strokePaint = Paint()
        ..color = Colors.black
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0;

      canvas.drawPath(shape.path, fillPaint);
      canvas.drawPath(shape.path, strokePaint);
    }
  }

  @override
  bool shouldRepaint(covariant MultiShapePainter oldDelegate) {
    return true;
  }
}