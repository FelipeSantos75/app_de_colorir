import 'package:flutter/material.dart';
import 'views/shape_grid.dart';
void main() {
  runApp(const ColorableShapesApp());
}

class ColorableShapesApp extends StatelessWidget {
  const ColorableShapesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      title: 'Vamos Colorir',
      home: ShapesPageGrid(),
    );
  }
}


