import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:ui' as ui;

import '../models/brush_selector.dart';
import '../models/brush_type.dart';
import '../models/paleta.dart';
import '../models/shape.dart';

class ColorableShapesPage extends StatefulWidget {
  final List<Shape> shapes;
  final bool isPremiumUser; // Premium status parameter

  const ColorableShapesPage({
    super.key,
    required this.shapes,
    this.isPremiumUser = false, // Default to false
  });

  @override
  _ColorableShapesPageState createState() => _ColorableShapesPageState();
}

class _ColorableShapesPageState extends State<ColorableShapesPage> {
  Color selectedColor = Colors.red;
  String? selectedTexture;
  BrushType selectedBrush = BrushType.basic; // Default to basic brush

  @override
  void initState() {
    super.initState();
    _loadTextures();
  }

  Future<void> _loadTextures() async {
    for (var shape in widget.shapes) {
      if (shape.textureAsset != null) {
        try {
          final ByteData data = await rootBundle.load(shape.textureAsset!);
          final ui.Codec codec =
              await ui.instantiateImageCodec(data.buffer.asUint8List());
          final ui.FrameInfo frameInfo = await codec.getNextFrame();
          shape.texture = frameInfo.image;
        } catch (e) {
          print('Error loading texture for ${shape.textureAsset}: $e');
        }
      }
    }
    if (mounted) {
      setState(() {});
    }
  }

  @override
  void dispose() {
    for (var shape in widget.shapes) {
      shape.texture?.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const double canvasWidth = double.infinity;
    const double canvasHeight = 500;
    // Espaco de coordenadas em que todos os desenhos da biblioteca sao escritos.
    const double drawingSide = 500;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Colorindo'),
        backgroundColor: Colors.purple,
      ),
      body: Column(
        children: [
          // Área de desenho
          SizedBox(
            width: canvasWidth,
            height: canvasHeight,
            // Os shapes vivem num espaco de 500x500. O FittedBox encaixa esse
            // quadrado na area disponivel — e, como o GestureDetector fica
            // dentro dele, o Flutter ja' devolve o toque nas coordenadas do
            // desenho, sem conta nenhuma aqui.
            child: FittedBox(
              fit: BoxFit.contain,
              child: SizedBox(
                width: drawingSide,
                height: drawingSide,
                child: GestureDetector(
                  onTapDown: (TapDownDetails details) {
                    Offset localPosition = details.localPosition;
                    for (var shape in widget.shapes.reversed) {
                      if (!shape.colorable) continue;
                      if (shape.path.contains(localPosition)) {
                        setState(() {
                          // Removendo a atribuição de cor direta, pois agora usamos apenas texturas
                          // shape.color = selectedColor;
                          shape.textureAsset = selectedTexture;
                          _loadTextures();
                          if (shape.id != null) {
                            debugPrint('Tapped shape ID: ${shape.id}');
                          }
                        });
                        break;
                      }
                    }
                  },
                  child: CustomPaint(
                    size: const Size(drawingSide, drawingSide),
                    painter: MultiShapePainter(widget.shapes),
                  ),
                ),
              ),
            ),
          ),

          const Spacer(),

          // Seletor de Pincéis
          BrushSelector(
            selectedBrush: selectedBrush,
            onBrushSelected: (brush) {
              setState(() {
                selectedBrush = brush;
                // Reset texture when changing brush
                selectedTexture = null;
              });
            },
            isPremiumUser:
                widget.isPremiumUser, // Use the actual premium status
          ),

          // Paleta de texturas específica do pincel
          BrushPalette(
            selectedBrush: selectedBrush,
            selectedTexture: selectedTexture,
            selectedColor: selectedColor, // Mantido para compatibilidade
            onTextureSelected: (texture) {
              setState(() {
                selectedTexture = texture;
                _loadTextures();
              });
            },
            isPremiumUser:
                widget.isPremiumUser, // Pass premium status to palette
          ),
        ],
      ),
    );
  }
}
