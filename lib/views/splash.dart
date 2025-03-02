import 'package:flutter/material.dart';
import 'loginpage.dart';
import 'dart:math' as math;

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotateAnimation;
  late Animation<double> _opacityAnimation;
  
  // Flag para controlar o início da animação de transição
  bool _startTransition = false;

  @override
  void initState() {
    super.initState();
    
    _controller = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.7, curve: Curves.elasticOut),
      ),
    );

    _rotateAnimation = Tween<double>(
      begin: -2 * math.pi,
      end: 0,
    ).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.7, curve: Curves.elasticOut),
      ),
    );

    _opacityAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.5, 1.0, curve: Curves.easeIn),
      ),
    );

    _controller.forward();

    // Inicia a animação de transição após a animação inicial completar
    Future.delayed(const Duration(milliseconds: 2500), () {
      if (mounted) {
        setState(() {
          _startTransition = true;
        });
        
        // Dá tempo para a animação de transição ocorrer antes de navegar
        Future.delayed(const Duration(milliseconds: 800), () {
          if (mounted) {
            Navigator.of(context).pushReplacement(
              PageRouteBuilder(
                transitionDuration: const Duration(milliseconds: 500),
                pageBuilder: (context, animation, secondaryAnimation) => const LoginPage(),
                transitionsBuilder: (context, animation, secondaryAnimation, child) {
                  return FadeTransition(
                    opacity: animation,
                    child: child,
                  );
                },
              ),
            );
          }
        });
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Determina a posição vertical final do logo
    // Na splash screen, está centralizado, mas na tela de login estará mais acima
    final double startPosition = MediaQuery.of(context).size.height / 2 - 75; // Centralizado
    final double endPosition = MediaQuery.of(context).size.height * 0.2; // Aproximadamente 20% do topo da tela
    
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFFF3E5F5), Color(0xFFFCE4EC)],
          ),
        ),
        child: Stack(
          children: [
            // Animated Logo with Hero tag for smooth transition
            AnimatedPositioned(
              duration: const Duration(milliseconds: 800),
              curve: Curves.easeInOut,
              top: _startTransition ? endPosition : startPosition,
              left: 0,
              right: 0,
              child: Center(
                child: Hero(
                  tag: 'app_logo',
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 800),
                    curve: Curves.easeInOut,
                    width: _startTransition ? 120 : 150,
                    height: _startTransition ? 120 : 150,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.2),
                          blurRadius: 10,
                          offset: const Offset(0, 5),
                        ),
                      ],
                    ),
                    child: AnimatedBuilder(
                      animation: _controller,
                      builder: (context, child) {
                        return Transform.scale(
                          scale: _scaleAnimation.value,
                          child: Transform.rotate(
                            angle: _rotateAnimation.value,
                            child: CustomPaint(
                              painter: PalettePainter(
                                opacity: _opacityAnimation.value,
                              ),
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                ),
              ),
            ),

            // Animated Title with fade out during transition
            AnimatedPositioned(
              duration: const Duration(milliseconds: 800),
              curve: Curves.easeInOut,
              top: _startTransition ? endPosition + 160 : startPosition + 170, // Abaixo do logo
              left: 0,
              right: 0,
              child: AnimatedOpacity(
                opacity: _startTransition ? 0.0 : 1.0,
                duration: const Duration(milliseconds: 500),
                child: AnimatedBuilder(
                  animation: _opacityAnimation,
                  builder: (context, child) {
                    return Opacity(
                      opacity: _opacityAnimation.value,
                      child: Center(
                        child: ShaderMask(
                          shaderCallback: (bounds) => const LinearGradient(
                            colors: [Color(0xFF9C27B0), Color(0xFFE91E63)],
                          ).createShader(bounds),
                          child: const Text(
                            'Vamos Colorir',
                            style: TextStyle(
                              fontSize: 36,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Custom Painter para desenhar a paleta
class PalettePainter extends CustomPainter {
  final double opacity;

  PalettePainter({required this.opacity});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..style = PaintingStyle.fill
      ..color = const Color(0xFF9C27B0).withOpacity(opacity);

    // Desenha a base da paleta
    final center = Offset(size.width / 2, size.height / 2);
    canvas.drawCircle(center, size.width * 0.4, paint);

    // Desenha as manchas de tinta
    final colors = [
      Colors.red,
      Colors.yellow,
      Colors.green,
      Colors.blue,
      Colors.pink[100],
    ];

    final random = math.Random(0); // Seed fixo para consistência
    for (var i = 0; i < colors.length; i++) {
      final angle = (i * math.pi * 2) / colors.length;
      final x = center.dx + math.cos(angle) * size.width * 0.25;
      final y = center.dy + math.sin(angle) * size.width * 0.25;
      
      paint.color = colors[i]!.withOpacity(opacity);
      canvas.drawCircle(
        Offset(x, y),
        size.width * 0.1,
        paint,
      );
    }

    // Desenha o buraco do polegar
    paint.color = const Color(0xFF7B1FA2).withOpacity(opacity);
    canvas.drawCircle(
      Offset(center.dx - size.width * 0.2, center.dy + size.width * 0.15),
      size.width * 0.12,
      paint,
    );
  }

  @override
  bool shouldRepaint(PalettePainter oldDelegate) {
    return opacity != oldDelegate.opacity;
  }
}