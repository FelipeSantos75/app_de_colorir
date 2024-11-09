
import 'package:flutter/material.dart';


// Paleta de Cores
class ColorPalette extends StatelessWidget {
  final Function(Color) onColorSelected;
  final Color selectedColor;
  final Function(dynamic)? onItemSelected;
  final dynamic selectedItem;

  ColorPalette({required this.onColorSelected, required this.selectedColor,  this.onItemSelected,  this.selectedItem});

  final List<Color> colors = [
    Colors.black,
    Colors.brown,
    Colors.grey,
    Colors.red,
    Colors.blue,
    Colors.green,
    Colors.yellow,
    Colors.orange,
    Colors.purple,
    Colors.pink,
  ];

  

  // Função para gerar tons mais claros e escuros da cor
  List<Color> getShades(Color color) {
    return color != Colors.black ? [
      lighten(color, 0.4),
      lighten(color, 0.35),
      lighten(color, 0.3),
      lighten(color, 0.15),
      color,
      darken(color, 0.15),
      darken(color, 0.3),
      darken(color, 0.45),
      
    ] : [color];
  }



  // Função para clarear a cor
  Color lighten(Color color, double amount) {
    final hsl = HSLColor.fromColor(color);
    final hslLight = hsl.withLightness(
      (hsl.lightness + amount).clamp(0.0, 1.0),
    );
    return hslLight.toColor();
  }

  // Função para escurecer a cor
  Color darken(Color color, double amount) {
    final hsl = HSLColor.fromColor(color);
    final hslDark = hsl.withLightness(
      (hsl.lightness - amount).clamp(0.0, 1.0),
    );
    return hslDark.toColor();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 70,
      color: Colors.grey,
      child: ListView(
        scrollDirection: Axis.horizontal,
        children:       
      colors.map((Color color) {
          return ColorTile(
            color: color,
            isSelected: selectedColor == color,
            selectedColor: selectedColor,
            onColorSelected: onColorSelected,
            getShades: getShades,
          );
        }).toList(),
        
      ),
    );
  }  
}

class TexturePalette extends StatelessWidget {
  
  late final Function(String) onStringSelected;
  late final dynamic selectedItem;
  final List<String> textures = [
  'assets/textures/basic/borracha.png',
  'assets/textures/basic/blue.png',
  'assets/textures/basic/green.png',
  'assets/textures/basic/orange.png',
  'assets/textures/basic/indigo.png',
  'assets/textures/basic/violet.png',
  'assets/textures/giz/indigogiz.png',
  'assets/textures/giz/violetgiz.png',
  // 'assets/textures/giz/yellowgiz.png',
  // 'assets/textures/giz/pinkgiz.png',
  // 'assets/textures/giz/redgiz.png',
  // 'assets/textures/giz/bluegiz.png',
  'assets/textures/pencil/bluepencil.png',
'assets/textures/pencil/borrachapencil.png',
'assets/textures/pencil/greenpencil.png',
'assets/textures/pencil/indigopencil.png',
'assets/textures/pencil/orangepencil.png',
'assets/textures/pencil/redpencil.png',
'assets/textures/pencil/violetpencil.png',
];
  TexturePalette({ required this.onStringSelected, required this.selectedItem});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 70,
      color: Colors.grey,
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: 
        textureList.map((String texture) {
  return TextureTile(
    texture: texture,
    isSelected: selectedItem == texture,
    selectedItem: selectedItem,
    onStringSelected: onStringSelected,
  );
}).toList(),
        
      ),
    );
  }

  List<String> get textureList => textures;
}


class TextureTile extends StatelessWidget {
  final String texture;
  final bool isSelected;
  final dynamic selectedItem;
  final Function(String)? onStringSelected;

  TextureTile({
    required this.texture,
    required this.isSelected,
    required this.selectedItem,
    this.onStringSelected,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => onStringSelected!(texture),
      child: Container(
        width: 50,
        margin: EdgeInsets.all(1),
        decoration: BoxDecoration(
          image: DecorationImage(
            image: AssetImage(texture),
            fit: BoxFit.cover,
          ),
          border: isSelected ? Border.all(width: 3, color: Colors.white) : null,
        ),
      ),
    );
  }
}


class ColorTile extends StatelessWidget {
  final Color color;
  final bool isSelected;
  final Color selectedColor; // Adicionado
  final Function(Color) onColorSelected;
  final List<Color> Function(Color) getShades;

  ColorTile({
    required this.color,
    required this.isSelected,
    required this.selectedColor, // Adicionado
    required this.onColorSelected,
    required this.getShades,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => onColorSelected(color),
      child: Container(
        width: 60,
        
        decoration: BoxDecoration(
          border: isSelected ? Border.all(width: 3, color: Colors.white) : null,
          color: color,
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            
            Positioned(
              bottom: 0,
              right: 0,
              child: IconButton(
                icon: Icon(Icons.arrow_drop_down, color: Colors.white),
                onPressed: () {
                  // Mostrar tons
                  showModalBottomSheet(
                    context: context,
                    builder: (context) {
                      final shades = getShades(color);
                      return Container(
                        height: 100,
                        color: Colors.grey[200],
                        child: ListView(
                          scrollDirection: Axis.horizontal,
                          children: shades.map((shade) {
                            return GestureDetector(
                              onTap: () {
                                onColorSelected(shade);
                                Navigator.pop(context);
                              },
                              child: Container(
                                width: 60,
                                decoration: BoxDecoration(
                                  border: isSelected ? Border.all(width: 3, color: Colors.white) : null,
                                  color: shade,
                                ),
                                
                              ),
                            );
                          }).toList(),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
