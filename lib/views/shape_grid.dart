
import 'package:flutter/material.dart';
import '../control/canvas.dart';
import '../control/shapes_library.dart';
import '../models/shape.dart';


class ShapesPageGrid extends StatefulWidget {
  const ShapesPageGrid({super.key});

  @override
  State<ShapesPageGrid> createState() => _ShapesPageGridState();
}

class _ShapesPageGridState extends State<ShapesPageGrid> {
  // Filtros e categorias
  final List<String> categories = ['Todos', 'Animais', 'Plantas', 'Mandalas', 'Paisagens'];
  String selectedCategory = 'Todos';

  // Controller para busca
  final TextEditingController _searchController = TextEditingController();
  String searchQuery = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Vamos Colorir',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        backgroundColor: Colors.purple,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.color_lens, color: Colors.white),
            onPressed: () {
              // TODO: Implementar página de temas/configurações
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Barra de busca
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.purple.shade50,
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(20),
                bottomRight: Radius.circular(20),
              ),
            ),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Buscar desenhos...',
                prefixIcon: const Icon(Icons.search),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(30),
                  borderSide: BorderSide.none,
                ),
                contentPadding: const EdgeInsets.symmetric(horizontal: 20),
              ),
              onChanged: (value) {
                setState(() {
                  searchQuery = value;
                });
              },
            ),
          ),

          // Categorias horizontais
          Container(
            height: 50,
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: categories.length,
              itemBuilder: (context, index) {
                final category = categories[index];
                final isSelected = category == selectedCategory;
                
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: FilterChip(
                    label: Text(
                      category,
                      style: TextStyle(
                        color: isSelected ? Colors.white : Colors.purple,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                    selected: isSelected,
                    onSelected: (bool selected) {
                      setState(() {
                        selectedCategory = category;
                      });
                    },
                    selectedColor: Colors.purple,
                    backgroundColor: Colors.purple.shade50,
                    checkmarkColor: Colors.white,
                  ),
                );
              },
            ),
          ),

          // Grid de desenhos
          Expanded(
            child: GridView.builder(
              padding: const EdgeInsets.all(16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 1.0,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
              ),
              itemCount: library.length,
              itemBuilder: (context, index) {
                final entry = library.entries.elementAt(index);
                return _buildGridItem(entry.key, entry.value);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGridItem(String title, List<Shape> shapes) {
    // Calcular porcentagem de conclusão (shapes coloridos vs total)
    int coloredShapes = shapes.where((shape) => shape.color != Colors.white).length;
    double progress = coloredShapes / shapes.length;

    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ColorableShapesPage(shapes: shapes),
          ),
        );
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(15),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withOpacity(0.2),
              spreadRadius: 2,
              blurRadius: 5,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Miniatura do desenho
            Expanded(
              child: ClipRRect(
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(15),
                  topRight: Radius.circular(15),
                ),
                child: Container(
                  color: Colors.grey.shade100,
                  child: CustomPaint(
                    painter: MultiShapePainter(shapes),
                  ),
                ),
              ),
            ),

            // Informações do desenho
            Container(
              padding: const EdgeInsets.all(8),
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.only(
                  bottomLeft: Radius.circular(15),
                  bottomRight: Radius.circular(15),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  LinearProgressIndicator(
                    value: progress,
                    backgroundColor: Colors.grey.shade200,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      progress == 1.0 ? Colors.green : Colors.purple,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}



// import 'package:flutter/material.dart';
// import '../control/canvas.dart';
// import '../models/shape.dart';
// import '../control/shapes_library.dart';
// import 'dart:math';

// class ShapesPageGrid extends StatefulWidget {
  
//   const ShapesPageGrid({super.key});
  
//   @override
//   _ShapesPageGridState createState() => _ShapesPageGridState();
// }

// class _ShapesPageGridState extends State<ShapesPageGrid> {
//   late List<MapEntry<String, List<Shape>>> allShapeEntries;

//   @override
//   void initState() {
//     super.initState();
//     // Coleta todas as entradas do library (cada uma é um par chave-valor)
//     allShapeEntries = library.entries.toList();
//   }

//   @override
//   Widget build(BuildContext context) {
//     const double canvasSize = 300;
    
//     return Scaffold(
//       appBar: AppBar(
//         title: const Text("Vamos Colorir"),
//       ),
//       body: GridView.builder(
//         padding: const EdgeInsets.all(8),
//         itemCount: allShapeEntries.length,
//         gridDelegate:const  SliverGridDelegateWithFixedCrossAxisCount(
//           crossAxisCount: 2, // Número de colunas no grid
//           crossAxisSpacing: 8,
//           mainAxisSpacing: 8,
//           childAspectRatio: 1, // Mantém os itens quadrados
//         ),
//         itemBuilder: (context, index) {
//           final entry = allShapeEntries[index];
//           final objectName = entry.key;
//           final shapes = entry.value;
//           return GestureDetector(
//             onTap: () {
// // Navega para a ColorableShapesPage passando a lista de shapes correspondente
//               Navigator.push(
//                 context,
//                 MaterialPageRoute(
//                   builder: (context) => ColorableShapesPage(
                    
//                     shapes: shapes,
//                   ),
//                 ),
//               );    
//         },
//             child: Column(
//               children: [
//                 Expanded(
//                   child: CustomPaint(
//                     size: Size(canvasSize, canvasSize),
//                     painter: MultiShapePainter(shapes),
//                   ),
//                 ),
//                 SizedBox(height: 8),
//                 Text(
//                   objectName,
//                   style: TextStyle(fontSize: 16),
//                 ),
//               ],
//             ),
//           );
//         },
//       ),
//     );
//   }
// }


// // Atualização do MultiShapePainter para ajustar escala e posição
// class MultiShapePainter extends CustomPainter {
//   final List<Shape> shapes;

//   MultiShapePainter(this.shapes);

//   @override
//   void paint(Canvas canvas, Size size) {
//     // Calcula os limites combinados dos shapes
//     final Rect bounds = _calculateShapesBounds(shapes);

//     // Calcula a escala para ajustar os shapes ao tamanho do canvas
//     final double scaleX = size.width / bounds.width;
//     final double scaleY = size.height / bounds.height;
//     final double scale = min(scaleX, scaleY);

//     // Centraliza os shapes no canvas
//     final double dx = (size.width - bounds.width * scale) / 2 - bounds.left * scale;
//     final double dy = (size.height - bounds.height * scale) / 2 - bounds.top * scale;

//     canvas.translate(dx, dy);
//     canvas.scale(scale);

//     for (var shape in shapes) {
//       final fillPaint = Paint()
//         ..color = shape.color
//         ..style = PaintingStyle.fill;

//       Paint strokePaint = Paint()
//         ..color = Colors.black
//         ..style = PaintingStyle.stroke
//         ..strokeWidth = 2.0 / scale; // Ajusta a espessura do traço

//       canvas.drawPath(shape.path, fillPaint);
//       if (shape.hasStroke) {
//         canvas.drawPath(shape.path, strokePaint);
//       }
//     }
//   }

//   // Método para calcular os limites combinados dos shapes
//   Rect _calculateShapesBounds(List<Shape> shapes) {
//     Rect bounds = shapes.first.path.getBounds();
//     for (var shape in shapes.skip(1)) {
//       bounds = bounds.expandToInclude(shape.path.getBounds());
//     }
//     return bounds;
//   }

//   @override
//   bool shouldRepaint(covariant MultiShapePainter oldDelegate) {
//     return false;
//   }
// }
