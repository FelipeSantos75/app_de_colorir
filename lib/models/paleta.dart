import 'package:flutter/material.dart';
import 'brush_type.dart';

class BrushPalette extends StatelessWidget {
  final BrushType selectedBrush;
  final String? selectedTexture;
  final Function(String) onTextureSelected;

  const BrushPalette({
    Key? key,
    required this.selectedBrush,
    this.selectedTexture,
    required this.onTextureSelected,
  }) : super(key: key);

  // Get textures based on brush type
  List<String> _getTexturesForBrush(BrushType brush) {
    switch (brush) {
      case BrushType.basic:
        return [
          'assets/textures/basic/red.png',
          'assets/textures/basic/blue.png',
          'assets/textures/basic/green.png',
          'assets/textures/basic/yellow.png',
          'assets/textures/basic/purple.png',
          'assets/textures/basic/orange.png',
          'assets/textures/basic/brown.png',
          'assets/textures/basic/black.png',
          'assets/textures/basic/white.png',
        ];
      case BrushType.pencil:
        return [
          'assets/textures/pencil/redpencil.png',
          'assets/textures/pencil/bluepencil.png',
          'assets/textures/pencil/greenpencil.png',
          'assets/textures/pencil/yellowpencil.png',
          'assets/textures/pencil/purplepencil.png',
          'assets/textures/pencil/orangepencil.png',
        ];
      case BrushType.chalk:
        return [
          'assets/textures/giz/indigogiz.png',
          'assets/textures/giz/violetgiz.png',

        ];
    }
  }

  @override
  Widget build(BuildContext context) {
    final textures = _getTexturesForBrush(selectedBrush);

    return Container(
      height: 100,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${selectedBrush.name} - Texturas',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: textures.length,
              itemBuilder: (context, index) {
                final texture = textures[index];
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: _TextureOption(
                    texture: texture,
                    isSelected: selectedTexture == texture,
                    onSelected: onTextureSelected,
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _TextureOption extends StatelessWidget {
  final String texture;
  final bool isSelected;
  final Function(String) onSelected;

  const _TextureOption({
    required this.texture,
    required this.isSelected,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => onSelected(texture),
      child: Container(
        width: 60,
        margin: const EdgeInsets.symmetric(vertical: 4),
        decoration: BoxDecoration(
          border: isSelected 
            ? Border.all(color: Colors.purple, width: 2)
            : Border.all(color: Colors.grey.shade300),
          borderRadius: BorderRadius.circular(8),
          image: DecorationImage(
            image: AssetImage(texture),
            fit: BoxFit.cover,
          ),
        ),
      ),
    );
  }
}