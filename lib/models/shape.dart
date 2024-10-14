
// import 'package:flutter/material.dart';

// // Classe que define cada forma com seu Path e Cor
// class Shape {
//   Path path;
//   Color color;
//   String? id;
//   bool hasStroke;
//   Shape({required this.path, required this.color,  this.id, this.hasStroke = true});
// }

// // Painter para desenhar múltiplas formas
// class MultiShapePainter extends CustomPainter {
//   final List<Shape> shapes;

//   MultiShapePainter(this.shapes);

//   @override
//   void paint(Canvas canvas, Size size) {
//     // Se necessário, podemos ajustar o canvas aqui
    
//     for (var shape in shapes) {
      
//       final fillPaint = Paint()
//         ..color = shape.color
//         ..style = PaintingStyle.fill;
      
//       Paint strokePaint = Paint()
//         ..color = Colors.black
//         ..style = PaintingStyle.stroke
//         ..strokeWidth = 2.0;
      
//       canvas.drawPath(shape.path, fillPaint);      
//       shape.hasStroke ? canvas.drawPath(shape.path, strokePaint): null;
      
  
      
//     }
//   }

//   @override
//   bool shouldRepaint(covariant MultiShapePainter oldDelegate) {
//     return true;
//   }
// }


import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:ui' as ui;

// Classe que define cada forma com seu Path, Cor ou Textura
class Shape {
  Path path;
  Color color; ui.Image? texture; // Holds the loaded image
  String? textureAsset; // Path to the texture in assets // Caminho para a textura nos assets
  String? id;
  bool hasStroke;

  Shape({
    required this.path,
    required this.color,
    this.texture,
    this.id,
    this.hasStroke = true,
  });
}

// Painter para desenhar múltiplas formas
class MultiShapePainter extends CustomPainter {
  final List<Shape> shapes;

  MultiShapePainter(this.shapes);

  @override
  void paint(Canvas canvas, Size size) {
    for (var shape in shapes) {
      if (shape.texture != null) {
        // Use the preloaded texture
        final paint = Paint()
          ..shader = ImageShader(
            shape.texture!,
            TileMode.repeated,
            TileMode.repeated,
            Matrix4.identity().storage,
          )
          ..style = PaintingStyle.fill;

        canvas.drawPath(shape.path, paint);
      } else {
        // Use color
        final fillPaint = Paint()
          ..color = shape.color
          ..style = PaintingStyle.fill;

        canvas.drawPath(shape.path, fillPaint);
      }

      if (shape.hasStroke) {
        Paint strokePaint = Paint()
          ..color = Colors.black
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2.0;

        canvas.drawPath(shape.path, strokePaint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant MultiShapePainter oldDelegate) {
    return true;
  }
}