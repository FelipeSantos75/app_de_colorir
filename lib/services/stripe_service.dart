
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import 'package:http/http.dart' as http;

class StripeService {
  // TODO: Substitua pela sua URL de backend
  static const String _backendUrl = 'YOUR_BACKEND_URL'; 
  // TODO: Substitua pela sua chave publicável do Stripe (Publishable Key)
  static const String _stripePublishableKey = 'YOUR_STRIPE_PUBLISHABLE_KEY'; 

  // Inicializa o Stripe
  static Future<void> initializeStripe() async {
    Stripe.publishableKey = _stripePublishableKey;
    // Configurações adicionais, como merchantIdentifier para Apple Pay, podem ser adicionadas aqui
    await Stripe.instance.applySettings();
    debugPrint('Stripe inicializado com a chave: $_stripePublishableKey');
  }

  // Função para criar uma intenção de pagamento no backend
  static Future<Map<String, dynamic>> _createPaymentIntent(String userId, String productId) async {
    // TODO: Implemente a chamada ao seu backend
    // O backend deve criar uma PaymentIntent no Stripe e retornar o client_secret
    // Exemplo de chamada HTTP POST (adapte conforme sua API de backend)
    try {
      final response = await http.post(
        Uri.parse('$_backendUrl/create-payment-intent'), // Endpoint do seu backend
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'userId': userId, // Identificador do usuário
          'productId': productId, // Identificador do produto/plano premium
          // Adicione outros dados necessários, como moeda, valor, etc.
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body); // Espera-se que retorne { 'clientSecret': '...' }
      } else {
        debugPrint('Erro ao criar PaymentIntent: ${response.body}');
        throw Exception('Falha ao criar intenção de pagamento no backend.');
      }
    } catch (e) {
      debugPrint('Erro na chamada HTTP para criar PaymentIntent: $e');
      throw Exception('Erro de comunicação com o backend.');
    }
    
    // --- Exemplo de retorno Fixo (REMOVER EM PRODUÇÃO) ---
    // Apenas para simulação sem backend. Substitua pela chamada real.
    // await Future.delayed(const Duration(seconds: 1));
    // return {'clientSecret': 'pi_test_secret_12345'};
    // --- Fim do exemplo fixo ---
  }

  // Função para iniciar o fluxo de pagamento no app
  static Future<bool> initiatePayment(BuildContext context, String userId, String productId) async {
    try {
      // 1. Criar Payment Intent no backend
      debugPrint('Criando Payment Intent para usuário: $userId, produto: $productId');
      final paymentIntentData = await _createPaymentIntent(userId, productId);
      final clientSecret = paymentIntentData['clientSecret'];

      if (clientSecret == null) {
        throw Exception('Client secret não recebido do backend.');
      }
      debugPrint('Client Secret recebido: $clientSecret');

      // 2. Apresentar a folha de pagamento do Stripe
      debugPrint('Apresentando folha de pagamento do Stripe...');
      await Stripe.instance.initPaymentSheet(
        paymentSheetParameters: SetupPaymentSheetParameters(
          paymentIntentClientSecret: clientSecret,
          merchantDisplayName: 'Vamos Colorir Premium', // Nome que aparece na folha de pagamento
          // customerId: customerId, // Opcional: ID do cliente Stripe
          // customerEphemeralKeySecret: ephemeralKey, // Opcional: Chave efêmera do cliente
          // setupIntentClientSecret: setupIntentClientSecret, // Para salvar métodos de pagamento
          style: ThemeMode.system, // Adapta ao tema do sistema
        ),
      );

      await Stripe.instance.presentPaymentSheet();
      debugPrint('Folha de pagamento apresentada e fechada.');

      // 3. Verificar o status do pagamento (o backend geralmente confirma via webhooks)
      // Aqui, podemos apenas assumir sucesso se não houver exceção.
      // O ideal é que o backend atualize o status premium do usuário após confirmação via webhook.
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Pagamento concluído com sucesso! Bem-vindo ao Premium!')),
      );
      return true; // Indica sucesso (simplificado)

    } on StripeException catch (e) {
      debugPrint('Erro Stripe durante o pagamento: ${e.error.localizedMessage}');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro no pagamento: ${e.error.localizedMessage ?? e.toString()}')),
      );
      return false; // Indica falha
    } catch (e) {
      debugPrint('Erro inesperado durante o pagamento: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro inesperado: ${e.toString()}')),
      );
      return false; // Indica falha
    }
  }
}

