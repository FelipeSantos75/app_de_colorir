import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'views/splash.dart';
import 'firebase_options.dart';
import 'services/stripe_service.dart'; // Import Stripe Service
import 'dart:ui'; // Import dart:ui for PointerDeviceKind

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Firebase
  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
    debugPrint('Firebase inicializado com sucesso');
  } catch (e) {
    debugPrint('Erro ao inicializar Firebase: $e');
    // Consider how to handle Firebase init errors in production
  }

  // Initialize Stripe
  // TODO: Certifique-se de que suas chaves Stripe e URL de backend estão configuradas em stripe_service.dart
  try {
    await StripeService.initializeStripe();
    debugPrint('Stripe Service inicializado com sucesso.');
  } catch (e) {
    debugPrint('Erro ao inicializar Stripe Service: $e');
    // Handle Stripe init errors (e.g., show an error message or disable payments)
  }

  runApp(const ColorableShapesApp());
}

// Custom Scroll Behavior to enable mouse dragging for scrolling on web
class MyCustomScrollBehavior extends MaterialScrollBehavior {
  // Override behavior methods and getters like dragDevices
  @override
  Set<PointerDeviceKind> get dragDevices => {
        PointerDeviceKind.touch,
        PointerDeviceKind.mouse,
        // Add other device kinds as needed
      };
}

class ColorableShapesApp extends StatelessWidget {
  const ColorableShapesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      // Apply the custom scroll behavior
      scrollBehavior: MyCustomScrollBehavior(),
      debugShowCheckedModeBanner: false,
      title: 'Vamos Colorir',
      theme: ThemeData( // Add a basic theme
        primarySwatch: Colors.purple,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: const SplashScreen(),
      // Define routes if needed for navigation (e.g., for registration)
      routes: {
        // '/register': (context) => const RegisterPage(), // Example route
        // '/login': (context) => const LoginPage(), // Example route
      },
    );
  }
}

