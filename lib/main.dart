import 'package:flutter/material.dart';

import 'canvas.dart';

void main() {
  runApp(ColorableShapesApp());
}

class ColorableShapesApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Aplicativo de Colorir Formas',
      home: ColorableShapesPage(),
    );
  }
}


