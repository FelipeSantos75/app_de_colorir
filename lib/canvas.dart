import 'package:flutter/material.dart';

import 'paleta.dart';
import 'shape.dart';
import 'shapes_library.dart';

class ColorableShapesPage extends StatefulWidget {
  @override
  _ColorableShapesPageState createState() => _ColorableShapesPageState();
}

class _ColorableShapesPageState extends State<ColorableShapesPage> {
  Color selectedColor = Colors.red;

  // Definimos três diferentes Paths para formas que se sobrepõem
  final List<Shape> shapes = library['marmeid2']!;

  _ColorableShapesPageState();
   

  @override
  Widget build(BuildContext context) {
    // Definimos um tamanho fixo para a área de desenho
    final double canvasWidth = 400;
    final double canvasHeight = 400;

    return Scaffold(
      appBar: AppBar(
        title: Text('Aplicativo de Colorir Formas'),
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Container(
            width: double.infinity,
            height: canvasHeight- (canvasHeight*0.2),
            child: GestureDetector(
              onTapDown: (TapDownDetails details) {
                RenderBox box = context.findRenderObject() as RenderBox;
          
                // Posição local relativa ao GestureDetector/CustomPaint
                Offset localPosition = details.localPosition;
          
                // Verifica as formas na ordem inversa, da última para a primeira
                for (var shape in shapes.reversed) {
                  if (shape.path.contains(localPosition)) {
                    setState(() {
                      shape.color = selectedColor;
                    });
                    break;
                  }
                }
              },
              child: CustomPaint(
                size: Size(canvasWidth, canvasHeight),
                painter: MultiShapePainter(shapes),
              ),
            ),
          ),
          Spacer(),
          ColorPalette(
            selectedColor: selectedColor,
            onColorSelected: (Color color) {
              setState(() {
                selectedColor = color;
              });
            },
          ),
        ],
      ),
    );
  }
}
