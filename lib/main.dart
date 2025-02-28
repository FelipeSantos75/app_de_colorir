import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'views/splash.dart';
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    await Firebase.initializeApp();
    print('Firebase inicializado com sucesso');
  } catch (e) {
    print('Erro ao inicializar Firebase: $e');
    // Continue mesmo em caso de erro para permitir o desenvolvimento
  }
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


