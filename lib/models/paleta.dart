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
          "assets/textures/basic/FFFFFF.png",
          "assets/textures/basic/000000.png",
          "assets/textures/basic/FF00FF.png",
          "assets/textures/basic/00FFFF.png",
          "assets/textures/basic/FFDFC4.png",
          "assets/textures/basic/F0C8A0.png",
          "assets/textures/basic/DEB887.png",
          "assets/textures/basic/D2956B.png",
          "assets/textures/basic/C68642.png",
          "assets/textures/basic/8D5524.png",
          "assets/textures/basic/73452E.png",
          "assets/textures/basic/4C3024.png",
          "assets/textures/basic/B07C6D.png",
          "assets/textures/basic/AA7B6C.png",
          "assets/textures/basic/8B4513.png",
          "assets/textures/basic/6B4423.png",
          "assets/textures/basic/000080.png",
          "assets/textures/basic/0000FF.png",
          "assets/textures/basic/1E90FF.png",
          "assets/textures/basic/87CEEB.png",
          "assets/textures/basic/8B0000.png",
          "assets/textures/basic/FF0000.png",
          "assets/textures/basic/DC143C.png",
          "assets/textures/basic/FA8072.png",
          "assets/textures/basic/FFD700.png",
          "assets/textures/basic/FFFF00.png",
          "assets/textures/basic/F0E68C.png",
          "assets/textures/basic/FFFACD.png",
          "assets/textures/basic/C0C0C0.png",
          "assets/textures/basic/A9A9A9.png",
          "assets/textures/basic/D3D3D3.png",
          "assets/textures/basic/DCDCDC.png",
          "assets/textures/basic/FFD700.png",
          "assets/textures/basic/DAA520.png",
          "assets/textures/basic/B8860B.png",
          "assets/textures/basic/CD853F.png",
          "assets/textures/basic/8B0000.png",
          "assets/textures/basic/B22222.png",
          "assets/textures/basic/CD5C5C.png",
          "assets/textures/basic/FF6347.png",
          "assets/textures/basic/FF4500.png",
          "assets/textures/basic/FF8C00.png",
          "assets/textures/basic/FFA500.png",
          "assets/textures/basic/FFB347.png",
          "assets/textures/basic/FFD700.png",
          "assets/textures/basic/FFFF00.png",
          "assets/textures/basic/FFFFE0.png",
          "assets/textures/basic/FFFACD.png",
          "assets/textures/basic/006400.png",
          "assets/textures/basic/008000.png",
          "assets/textures/basic/32CD32.png",
          "assets/textures/basic/90EE90.png",
          "assets/textures/basic/00008B.png",
          "assets/textures/basic/0000FF.png",
          "assets/textures/basic/1E90FF.png",
          "assets/textures/basic/87CEEB.png",
          "assets/textures/basic/191970.png",
          "assets/textures/basic/4169E1.png",
          "assets/textures/basic/6495ED.png",
          "assets/textures/basic/B0C4DE.png",
          "assets/textures/basic/4B0082.png",
          "assets/textures/basic/8A2BE2.png",
          "assets/textures/basic/9370DB.png",
          "assets/textures/basic/DDA0DD.png",
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
