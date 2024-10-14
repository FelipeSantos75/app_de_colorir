import 'package:flutter/material.dart';
import '../control/canvas.dart';
import '../models/shape.dart';
import '../control/shapes_library.dart';
import 'dart:math';

class ShapesPageGrid extends StatefulWidget {
  
  const ShapesPageGrid({super.key});
  
  @override
  _ShapesPageGridState createState() => _ShapesPageGridState();
}

class _ShapesPageGridState extends State<ShapesPageGrid> {
  late List<MapEntry<String, List<Shape>>> allShapeEntries;

  @override
  void initState() {
    super.initState();
    // Coleta todas as entradas do library (cada uma é um par chave-valor)
    allShapeEntries = library.entries.toList();
  }

  @override
  Widget build(BuildContext context) {
    const double canvasSize = 300;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text("Vamos Colorir"),
      ),
      body: GridView.builder(
        padding: const EdgeInsets.all(8),
        itemCount: allShapeEntries.length,
        gridDelegate:const  SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2, // Número de colunas no grid
          crossAxisSpacing: 8,
          mainAxisSpacing: 8,
          childAspectRatio: 1, // Mantém os itens quadrados
        ),
        itemBuilder: (context, index) {
          final entry = allShapeEntries[index];
          final objectName = entry.key;
          final shapes = entry.value;
          return GestureDetector(
            onTap: () {
// Navega para a ColorableShapesPage passando a lista de shapes correspondente
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => ColorableShapesPage(
                    
                    shapes: shapes,
                  ),
                ),
              );    
        },
            child: Column(
              children: [
                Expanded(
                  child: CustomPaint(
                    size: Size(canvasSize, canvasSize),
                    painter: MultiShapePainter(shapes),
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  objectName,
                  style: TextStyle(fontSize: 16),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}


// Atualização do MultiShapePainter para ajustar escala e posição
class MultiShapePainter extends CustomPainter {
  final List<Shape> shapes;

  MultiShapePainter(this.shapes);

  @override
  void paint(Canvas canvas, Size size) {
    // Calcula os limites combinados dos shapes
    final Rect bounds = _calculateShapesBounds(shapes);

    // Calcula a escala para ajustar os shapes ao tamanho do canvas
    final double scaleX = size.width / bounds.width;
    final double scaleY = size.height / bounds.height;
    final double scale = min(scaleX, scaleY);

    // Centraliza os shapes no canvas
    final double dx = (size.width - bounds.width * scale) / 2 - bounds.left * scale;
    final double dy = (size.height - bounds.height * scale) / 2 - bounds.top * scale;

    canvas.translate(dx, dy);
    canvas.scale(scale);

    for (var shape in shapes) {
      final fillPaint = Paint()
        ..color = shape.color
        ..style = PaintingStyle.fill;

      Paint strokePaint = Paint()
        ..color = Colors.black
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0 / scale; // Ajusta a espessura do traço

      canvas.drawPath(shape.path, fillPaint);
      if (shape.hasStroke) {
        canvas.drawPath(shape.path, strokePaint);
      }
    }
  }

  // Método para calcular os limites combinados dos shapes
  Rect _calculateShapesBounds(List<Shape> shapes) {
    Rect bounds = shapes.first.path.getBounds();
    for (var shape in shapes.skip(1)) {
      bounds = bounds.expandToInclude(shape.path.getBounds());
    }
    return bounds;
  }

  @override
  bool shouldRepaint(covariant MultiShapePainter oldDelegate) {
    return false;
  }
}
