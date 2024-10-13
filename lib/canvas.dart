import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:ui' as ui;

import 'paleta.dart';
import 'shape.dart';


class ColorableShapesPage extends StatefulWidget {
  final List<Shape> shapes;

  const ColorableShapesPage({super.key, required this.shapes}); //= library['dino']!;
  @override
  _ColorableShapesPageState createState() => _ColorableShapesPageState();
}

class _ColorableShapesPageState extends State<ColorableShapesPage> {
  Color selectedColor = Colors.red;
  String selectedTexture = ""; 
  bool istexture = false;

  // Definimos três diferentes Paths para formas que se sobrepõem
  
  _ColorableShapesPageState();
   @override
  void initState() {
    super.initState();
    _loadTextures();
  }

  Future<void> _loadTextures() async {
  for (var shape in widget.shapes) {
    if (shape.textureAsset != null) {
      try {
        // Load image data from assets
        final ByteData data = await rootBundle.load(shape.textureAsset!);
        // Decode image data to get a ui.Image
        final ui.Codec codec = await ui.instantiateImageCodec(data. buffer.asUint8List());
        final ui.FrameInfo frameInfo = await codec.getNextFrame();
        shape.texture = frameInfo.image;
      } catch (e) {
        print('Error loading texture for ${shape.textureAsset}: $e');
      }
    }
  }
  // After loading all textures, trigger a repaint
  setState(() {});
}

  @override
  void dispose() {
    // Dispose of images when done
    for (var shape in widget.shapes) {
      shape.texture?.dispose();
    }
    super.dispose();
  } 

  @override
  Widget build(BuildContext context) {
    // Definimos um tamanho fixo para a área de desenho
    const double canvasWidth = double.infinity;
    const double canvasHeight = 600;

    return Scaffold(
      appBar: AppBar(
        title:const  Text('Aplicativo de Colorir Formas'),
      ),
      body: SizedBox(
        width: double.infinity,
        height: double.infinity,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Container(
              width: canvasWidth,
              height: canvasHeight,
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
                         shape.textureAsset = selectedTexture;
                         _loadTextures();
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
            const Spacer(),
            Row(
              children: [
                
                TexturePalette(
                  selectedItem: selectedTexture,
                  onStringSelected: (String path) {
                    setState(() {
                      selectedTexture = path;
                    });
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
