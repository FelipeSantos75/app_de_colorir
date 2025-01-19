import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:ui' as ui;

import '../models/brush_selector.dart';
import '../models/brush_type.dart';
 // Nova importação
import '../models/paleta.dart';
import '../models/shape.dart';

class ColorableShapesPage extends StatefulWidget {
  final List<Shape> shapes;

  const ColorableShapesPage({super.key, required this.shapes});
  @override
  _ColorableShapesPageState createState() => _ColorableShapesPageState();
}

class _ColorableShapesPageState extends State<ColorableShapesPage> {
  Color selectedColor = Colors.red;
  String? selectedTexture;
  BrushType selectedBrush = BrushType.basic;  // Adicionado estado para o pincel selecionado

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
          final ui.Codec codec = await ui.instantiateImageCodec(data.buffer.asUint8List());
          final ui.FrameInfo frameInfo = await codec.getNextFrame();
          shape.texture = frameInfo.image;
        } catch (e) {
          print('Error loading texture for ${shape.textureAsset}: $e');
        }
      }
    }
    setState(() {});
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

    return Scaffold(
      appBar: AppBar(
        title: const Text('Aplicativo de Colorir Formas'),
      ),
      body: Column(
        children: [
          // Área de desenho
          SizedBox(
            width: canvasWidth,
            height: canvasHeight,
            child: GestureDetector(
              onTapDown: (TapDownDetails details) {
                Offset localPosition = details.localPosition;
                for (var shape in widget.shapes.reversed) {
                  if (shape.path.contains(localPosition)) {
                    setState(() {
                      shape.color = selectedColor;
                      shape.textureAsset = selectedTexture;
                      _loadTextures();
                      if(shape.id != null) {
                        debugPrint(shape.id);
                      }
                    });
                    break;
                  }
                }
              },
              child: CustomPaint(
                size: const Size(canvasWidth, canvasHeight),
                painter: MultiShapePainter(widget.shapes),
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
            isPremiumUser: true,
          ),
          
          // Paleta de cores e texturas específica do pincel
          BrushPalette(
            selectedBrush: selectedBrush,
            selectedTexture: selectedTexture,
            // selectedColor: selectedColor,
            // onColorSelected: (color) {
            //   setState(() {
            //     selectedColor = color;
            //   });
            // },
            onTextureSelected: (texture) {
              setState(() {
                selectedTexture = texture;
                _loadTextures();
              });
            },
          ),
        ],
      ),
    );
  }
}