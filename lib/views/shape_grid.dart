import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'canvas.dart';
import '../control/shapes_library.dart';
import '../models/desenho.dart';
import '../models/shape.dart';
import 'loginpage.dart'; // Add for navigation
import 'registerpage.dart'; // Add for navigation

class ShapesPageGrid extends StatefulWidget {
  final bool isGuest; // Add isGuest flag

  const ShapesPageGrid({super.key, this.isGuest = false}); // Default to false

  @override
  State<ShapesPageGrid> createState() => _ShapesPageGridState();
}

class _ShapesPageGridState extends State<ShapesPageGrid> {
  // Filtros e categorias
  final List<String> categories = [
    'Todos',
    'Animais',
    'Fantasias',
    'Mandalas',
    'Paisagens'
  ];
  String selectedCategory = 'Todos';

  // Controller para busca
  final TextEditingController _searchController = TextEditingController();
  String searchQuery = '';

  User? _currentUser; // Store current user state
  bool _isPremiumUser = false; // Store premium status (needs implementation)

  @override
  void initState() {
    super.initState();
    _checkUserStatus();
  }

  void _checkUserStatus() {
    if (!widget.isGuest) {
      _currentUser = FirebaseAuth.instance.currentUser;
      // TODO: Implement logic to check if the logged-in user is premium
      // For now, assume logged-in users are premium by default
      _isPremiumUser = true;
    } else {
      _currentUser = null;
      _isPremiumUser = false;
    }
    setState(() {}); // Update UI based on user status
  }

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
          if (widget.isGuest)
            TextButton.icon(
              icon: const Icon(Icons.login, color: Colors.white),
              label: const Text('Login', style: TextStyle(color: Colors.white)),
              onPressed: () {
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(builder: (context) => const LoginPage()),
                );
              },
            )
          else // Logged-in user actions
            IconButton(
              icon: const Icon(Icons.logout, color: Colors.white),
              tooltip: 'Sair',
              onPressed: () async {
                await FirebaseAuth.instance.signOut();
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(builder: (context) => const LoginPage()),
                );
              },
            ),
          // IconButton(
          //   icon: const Icon(Icons.color_lens, color: Colors.white),
          //   onPressed: () {
          //     // TODO: Implementar página de temas/configurações
          //   },
          // ),
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
                        fontWeight:
                            isSelected ? FontWeight.bold : FontWeight.normal,
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

          Expanded(
            child: GridView.builder(
              padding: const EdgeInsets.all(16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 1.0, // Adjust aspect ratio if needed
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
              ),
              itemCount: _getFilteredDrawings().length,
              itemBuilder: (context, index) {
                final drawing = _getFilteredDrawings()[index];
                return _buildGridItem(drawing);
              },
            ),
          ),
        ],
      ),
    );
  }

  List<Drawing> _getFilteredDrawings() {
    return library.where((drawing) {
      // Filter by premium status if user is guest
      if (widget.isGuest && drawing.isPremium) {
        return false;
      }

      // Filter by category
      bool matchesCategory =
          selectedCategory == 'Todos' || drawing.category == selectedCategory;

      // Filter by search query
      bool matchesSearch = searchQuery.isEmpty ||
          drawing.title.toLowerCase().contains(searchQuery.toLowerCase()) ||
          (drawing.tags.any(
              (tag) => tag.toLowerCase().contains(searchQuery.toLowerCase())));

      return matchesCategory && matchesSearch;
    }).toList();
  }

  Widget _buildGridItem(Drawing drawing) {
    bool isLocked =
        drawing.isPremium && widget.isGuest; // Locked if premium and guest

    return GestureDetector(
      onTap: () {
        if (isLocked) {
          _showLoginPrompt(context);
        } else {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => ColorableShapesPage(
                shapes:
                    drawing.shapes.map((shape) => shape.copyWith()).toList(),
                isPremiumUser: _isPremiumUser,
              ),
            ),
          );
        }
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
        child: Stack(
          // Use Stack to overlay lock icon
          children: [
            Column(
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
                        child: LayoutBuilder(
                          builder: (context, constraints) {
                            return CustomPaint(
                              size: Size(
                                  constraints.maxWidth, constraints.maxHeight),
                              painter: MultiShapePainter(drawing.shapes),
                            );
                          },
                        ),
                      )),
                ),

                // Informações do desenho
                Container(
                  padding: const EdgeInsets.all(8),
                  child: Row(
                    // Use Row to place star icon next to title
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          drawing.title,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (drawing.isPremium &&
                          !isLocked) // Show star only if premium and accessible
                        const Icon(Icons.star, color: Colors.amber, size: 16),
                    ],
                  ),
                ),
              ],
            ),
            if (isLocked) // Overlay lock icon if locked
              Container(
                decoration: BoxDecoration(
                  color:
                      Colors.black.withOpacity(0.5), // Semi-transparent overlay
                  borderRadius: BorderRadius.circular(15),
                ),
                child: const Center(
                  child: Icon(
                    Icons.lock,
                    color: Colors.white,
                    size: 40,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  void _showLoginPrompt(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Desenho Premium Bloqueado'),
        content: const Text(
            'Faça login ou crie uma conta para acessar este e outros desenhos premium!'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const LoginPage()),
              );
            },
            child: const Text('Fazer Login'),
          ),
          OutlinedButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const RegisterPage()),
              );
            },
            child: const Text('Criar Conta'),
          )
        ],
      ),
    );
  }
}

// Use the original MultiShapePainter from the Shape class
