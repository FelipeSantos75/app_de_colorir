import 'package:flutter/material.dart';
import 'brush_type.dart';

class BrushSelector extends StatelessWidget {
  final BrushType selectedBrush;
  final Function(BrushType) onBrushSelected;
  final bool isPremiumUser;

  const BrushSelector({
    super.key,
    required this.selectedBrush,
    required this.onBrushSelected,
    this.isPremiumUser = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 100,
      padding: const EdgeInsets.symmetric(horizontal: 16),
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
      child: Row(
        children: [
          // Texto "Pincéis"
          const Text(
            'Pincéis',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(width: 16),
          
          // Lista horizontal de pincéis
          Expanded(
            child: ListView(
              scrollDirection: Axis.horizontal,
              children: BrushType.values.map((brush) {
                final isSelected = brush == selectedBrush;
                final isLocked = brush.isPremium && !isPremiumUser;
                
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: _BrushOption(
                    brush: brush,
                    isSelected: isSelected,
                    isLocked: isLocked,
                    onTap: () {
                      if (!isLocked) {
                        onBrushSelected(brush);
                      } else {
                        _showPremiumDialog(context);
                      }
                    },
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  void _showPremiumDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Recurso Premium'),
        content: const Text(
          'Este pincel está disponível apenas para usuários premium. '
          'Que tal fazer um upgrade para acessar todos os pincéis?'
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Depois'),
          ),
          ElevatedButton(
            onPressed: () {
              // TODO: Implementar navegação para tela de upgrade
              Navigator.pop(context);
            },
            child: const Text('Fazer Upgrade'),
          ),
        ],
      ),
    );
  }
}

class _BrushOption extends StatelessWidget {
  final BrushType brush;
  final bool isSelected;
  final bool isLocked;
  final VoidCallback onTap;

  const _BrushOption({
    required this.brush,
    required this.isSelected,
    required this.isLocked,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 80,
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: isSelected ? Colors.purple.shade50 : Colors.white,
          border: Border.all(
            color: isSelected ? Colors.purple : Colors.grey.shade300,
            width: 2,
          ),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Stack(
          children: [
            Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Ícone do pincel
                Image.asset(
                  brush.icon,
                  width: 24,
                  height: 24,
                  color: isSelected ? Colors.purple : Colors.grey.shade600,
                ),
                const SizedBox(height: 4),
                
                // Nome do pincel
                Text(
                  brush.name,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    color: isSelected ? Colors.purple : Colors.black87,
                  ),
                  textAlign: TextAlign.center,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
            
            // Ícone de cadeado para opções premium bloqueadas
            if (isLocked)
              Positioned(
                top: 0,
                right: 0,
                child: Container(
                  padding: const EdgeInsets.all(2),
                  decoration: const BoxDecoration(
                    color: Colors.amber,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.lock,
                    size: 12,
                    color: Colors.white,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}