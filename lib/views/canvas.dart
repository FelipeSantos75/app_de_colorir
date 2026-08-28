import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:ui' as ui;

import '../models/brush_selector.dart';
import '../models/brush_type.dart';
import '../models/paleta.dart';
import '../models/shape.dart';

class ColorableShapesPage extends StatefulWidget {
  final List<Shape> shapes;
  final String title; // Nome do desenho, exibido na AppBar
  final bool isPremiumUser; // Premium status parameter

  const ColorableShapesPage({
    super.key,
    required this.shapes,
    this.title = 'Colorindo',
    this.isPremiumUser = false, // Default to false
  });

  @override
  _ColorableShapesPageState createState() => _ColorableShapesPageState();
}

class _ColorableShapesPageState extends State<ColorableShapesPage> {
  Color selectedColor = Colors.red;
  String? selectedTexture;
  BrushType selectedBrush = BrushType.basic; // Default to basic brush

  // Os Shapes sao mutados no lugar e a lista e' compartilhada com a grade, entao
  // guardamos a textura original de cada um para poder desfazer tudo na saida.
  late final List<String?> _texturasOriginais;
  bool _pintou = false;

  // Uma ui.Image por asset. Os shapes so' apontam para as imagens daqui, e este
  // mapa e' o unico dono delas: antes cada toque redecodificava a textura de
  // todos os shapes e sobrescrevia a anterior sem dispose, vazando uma imagem
  // por shape por toque.
  final Map<String, ui.Image> _cacheTexturas = {};

  @override
  void initState() {
    super.initState();
    _texturasOriginais =
        widget.shapes.map((shape) => shape.textureAsset).toList();
    _loadTextures();
  }

  Future<ui.Image?> _decodificarTextura(String asset) async {
    try {
      final ByteData data = await rootBundle.load(asset);
      final ui.Codec codec =
          await ui.instantiateImageCodec(data.buffer.asUint8List());
      final ui.FrameInfo frameInfo = await codec.getNextFrame();
      final ui.Image imagem = frameInfo.image;

      // Enquanto esperavamos, a pagina pode ter saido ou outra chamada pode ter
      // decodificado o mesmo asset. Nos dois casos esta copia sobra.
      if (!mounted) {
        imagem.dispose();
        return null;
      }
      final jaNoCache = _cacheTexturas[asset];
      if (jaNoCache != null) {
        imagem.dispose();
        return jaNoCache;
      }

      _cacheTexturas[asset] = imagem;
      return imagem;
    } catch (e) {
      debugPrint('Erro ao carregar a textura $asset: $e');
      return null;
    }
  }

  Future<void> _loadTextures() async {
    for (var shape in widget.shapes) {
      final asset = shape.textureAsset;
      if (asset == null) {
        // O toque com nenhuma textura escolhida limpa o shape; sem isto ele
        // continuava pintado com a imagem anterior.
        shape.texture = null;
        continue;
      }

      final emCache = _cacheTexturas[asset];
      if (emCache != null) {
        shape.texture = emCache;
        continue;
      }

      final imagem = await _decodificarTextura(asset);
      if (!mounted) return;
      shape.texture = imagem;
    }
    if (mounted) {
      setState(() {});
    }
  }

  // Devolve cada shape ao estado em que estava quando o desenho foi aberto.
  void _resetarPintura() {
    for (var i = 0; i < widget.shapes.length; i++) {
      final shape = widget.shapes[i];
      // A imagem pertence a _cacheTexturas, que da' o dispose no fim da pagina;
      // aqui so' se solta a referencia.
      shape.texture = null;
      shape.textureAsset = _texturasOriginais[i];
    }
    _pintou = false;
  }

  Future<bool> _confirmarSaida() async {
    if (!_pintou) return true;

    final sair = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Sair do desenho?'),
        content: const Text(
            'Sua pintura vai ser apagada e o desenho volta ao normal. Quer sair mesmo assim?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Continuar pintando'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Sair'),
          ),
        ],
      ),
    );

    return sair ?? false;
  }

  @override
  void dispose() {
    _resetarPintura();
    for (final imagem in _cacheTexturas.values) {
      imagem.dispose();
    }
    _cacheTexturas.clear();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const double canvasWidth = double.infinity;
    const double canvasHeight = 500;
    // Espaco de coordenadas em que todos os desenhos da biblioteca sao escritos.
    const double drawingSide = 500;

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        // Guardado antes do await: depois dele o context pode nao valer mais.
        final navegador = Navigator.of(context);
        final sair = await _confirmarSaida();
        if (sair && mounted) {
          // Antes do pop de proposito: o Future do Navigator.push da grade
          // completa no inicio da animacao de saida, bem antes do dispose
          // desta pagina, e a miniatura repintaria ainda colorida.
          _resetarPintura();
          navegador.pop();
        }
      },
      child: Scaffold(
        appBar: AppBar(
          title: Text(
            widget.title,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          backgroundColor: Colors.purple,
          elevation: 0,
          iconTheme: const IconThemeData(color: Colors.white),
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
                            _pintou = true;
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
      ),
    );
  }
}
