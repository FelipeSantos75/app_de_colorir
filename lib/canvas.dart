import 'package:flutter/material.dart';

import 'paleta.dart';
import 'shape.dart';
import 'shapes_library.dart';

class ColorableShapesPage extends StatefulWidget {
  final List<Shape> shapes;

  const ColorableShapesPage({super.key, required this.shapes}); //= library['dino']!;
  @override
  _ColorableShapesPageState createState() => _ColorableShapesPageState();
}

class _ColorableShapesPageState extends State<ColorableShapesPage> {
  Color selectedColor = Colors.red;

  // Definimos três diferentes Paths para formas que se sobrepõem
  
  _ColorableShapesPageState();
   

  @override
  Widget build(BuildContext context) {
    // Definimos um tamanho fixo para a área de desenho
    const double canvasWidth = double.infinity;
    const double canvasHeight = 800;

    return Scaffold(
      appBar: AppBar(
        title:const  Text('Aplicativo de Colorir Formas'),
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Container(
            width: canvasWidth,
            height: canvasHeight- (canvasHeight*0.2),
            child: GestureDetector(
              onTapDown: (TapDownDetails details) {
          
                // Posição local relativa ao GestureDetector/CustomPaint
                Offset localPosition = details.localPosition;
                
                // Verifica as formas na ordem inversa, da última para a primeira
                for (var shape in widget.shapes.reversed) {
                  if (shape.path.contains(localPosition)) {
                    setState(() {
                      shape.color = selectedColor;
                      debugPrint(localPosition.toString());
                      // Exibimos o ID da forma que foi clicada
                      if(shape.id != null) {
                        debugPrint(shape.id);
                      }
                    });
                    break;
                  }
                }
              },
              child: CustomPaint(
                size: Size(canvasWidth, canvasHeight),
                painter: MultiShapePainter(widget.shapes),
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
