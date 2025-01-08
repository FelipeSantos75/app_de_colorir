import 'package:flutter/material.dart';
import 'views/splash.dart';
void main() {
  runApp(const ColorableShapesApp());
}

class ColorableShapesApp extends StatelessWidget {
  const ColorableShapesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Vamos Colorir',
      home: SplashScreen(),
    );
  }
}


