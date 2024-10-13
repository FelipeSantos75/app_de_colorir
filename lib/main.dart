import 'package:flutter/material.dart';
import 'shape_grid.dart';
void main() {
  runApp(ColorableShapesApp());
}

class ColorableShapesApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Vamos Colorir',
      home: const ShapesPageGrid(),
    );
  }
}


