import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import '../services/stripe_service.dart';

class PremiumPage extends StatefulWidget {
  const PremiumPage({super.key});

  @override
  State<PremiumPage> createState() => _PremiumPageState();
}

class _PremiumPageState extends State<PremiumPage> {
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Upgrade para Premium'),
        backgroundColor: Colors.purple,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Cabeçalho com gradiente
            Container(
              padding: const EdgeInsets.all(24),
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Colors.purple, Colors.purpleAccent],
                ),
              ),
              child: Column(
                children: [
                  const Icon(
                    Icons.star,
                    size: 80,
                    color: Colors.amber,
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Vamos Colorir Premium',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Desbloqueie todos os recursos e desenhos premium!',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.white,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 12,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.amber,
                      borderRadius: BorderRadius.circular(30),
                    ),
                    child: const Text(
                      'R\$ 9,90 / mês',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Lista de benefícios
            Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Benefícios Premium:',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildBenefitItem(
                    icon: Icons.lock_open,
                    title: 'Acesso a todos os desenhos',
                    description:
                        'Desbloqueie todos os desenhos premium da biblioteca.',
                  ),
                  _buildBenefitItem(
                    icon: Icons.brush,
                    title: 'Pincéis exclusivos',
                    description:
                        'Use pincéis especiais com efeitos e texturas únicas.',
                  ),
                  _buildBenefitItem(
                    icon: Icons.palette,
                    title: 'Paleta de cores expandida',
                    description: 'Acesse uma paleta com mais de 100 cores.',
                  ),
                  _buildBenefitItem(
                    icon: Icons.cloud_upload,
                    title: 'Salve seus desenhos na nuvem',
                    description:
                        'Acesse seus desenhos de qualquer dispositivo.',
                  ),
                  _buildBenefitItem(
                    icon: Icons.ad_units_outlined,
                    title: 'Sem anúncios',
                    description: 'Experiência sem interrupções.',
                  ),
                ],
              ),
            ),

            // Botão de assinatura
            Padding(
              padding: const EdgeInsets.all(24),
              child: ElevatedButton(
                onPressed: _isLoading ? null : _handleSubscription,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.purple,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(30),
                  ),
                ),
                child: _isLoading
                    ? const SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor:
                              AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Text(
                        'Assinar Premium',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
              ),
            ),

            // Termos e condições
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 24, vertical: 8),
              child: Text(
                'Ao assinar, você concorda com nossos termos de serviço e política de privacidade. A assinatura será renovada automaticamente e pode ser cancelada a qualquer momento.',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey,
                ),
                textAlign: TextAlign.center,
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildBenefitItem({
    required IconData icon,
    required String title,
    required String description,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.purple.shade50,
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              color: Colors.purple,
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade700,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _handleSubscription() async {
    // Verificar se o usuário está logado
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Você precisa estar logado para assinar o Premium.'),
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      // Iniciar o fluxo de pagamento
      // 'premium_monthly' é um identificador para o plano mensal
      final success = await StripeService.initiatePayment(
        context,
        user.uid,
        'premium_monthly',
      );

      if (success) {
        // Atualizar o status premium do usuário no Firebase
        // Isso geralmente seria feito pelo backend após confirmação do webhook do Stripe
        // Aqui estamos apenas simulando para fins de demonstração
        
        // TODO: Implementar a atualização do status premium no Firebase
        // Exemplo: await FirebaseFirestore.instance.collection('users').doc(user.uid).update({'isPremium': true});
        
        // Navegar de volta para a tela principal ou mostrar uma tela de sucesso
        if (mounted) {
          Navigator.pop(context, true); // Retorna true para indicar sucesso
        }
      }
    } catch (e) {
      debugPrint('Erro ao processar assinatura: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erro ao processar assinatura: ${e.toString()}'),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }
}
