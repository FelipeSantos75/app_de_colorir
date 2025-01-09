import 'shape.dart';

class Drawing {
  final String id; // Identificador único do desenho
  final String title; // Título/nome do desenho
  final List<Shape> shapes; // Lista de formas que compõem o desenho
  final List<String> tags; // Tags para busca e categorização
  final bool isPremium; // Flag para indicar se é um desenho premium
  final String? thumbnailPath; // Caminho para uma miniatura do desenho (opcional)
  final String category; // Categoria do desenho (ex: "Animais", "Mandalas", etc)
  
  const Drawing({
    required this.id,
    required this.title,
    required this.shapes,
    required this.tags,
    required this.category,
    this.isPremium = false,
    this.thumbnailPath,
  });

  
}