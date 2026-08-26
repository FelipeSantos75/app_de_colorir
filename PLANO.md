# Plano de trabalho — Vamos Colorir

> **O que falta para ir ao ar: [CHECKLIST-PRODUCAO.md](CHECKLIST-PRODUCAO.md).**
>
> Funcionalidades futuras, planejadas à parte:
> [PLANO-UPLOAD-SVG.md](PLANO-UPLOAD-SVG.md) — usuários enviando SVG e recebendo desenhos pintáveis.
> [PLANO-SALVAR-DESENHO.md](PLANO-SALVAR-DESENHO.md) — usuários salvando e exportando o que pintaram.
> As duas dependem do mesmo pré-requisito: separar o desenho da pintura, hoje impedido pela mutação in-place.

Consolidação dos pendentes levantados na análise do código (agosto/2026). Contexto: **web é a única plataforma alvo**; o Firebase (projeto `colorir-448119`) já inicializa em runtime.

Ordem sugerida: **3 → 1 → 2 → 4**. O item 3 é barato e destrava o clone; o 1 precisa vir antes do 2, porque o checkout só faz sentido depois que existir uma fonte de verdade para a entitlement.

---

## 1. Unificar o gating premium em `AuthService`

**Problema.** Hoje há duas fontes de verdade que se contradizem:

- [shape_grid.dart:42](lib/views/shape_grid.dart:42) marca `_isPremiumUser = true` para **qualquer** usuário logado (com `TODO`), e propaga esse bool para [canvas.dart:12](lib/views/canvas.dart:12), que decide se os pincéis lápis/giz destravam (`BrushType.isPremium`, [brush_type.dart:39](lib/models/brush_type.dart:39)).
- [AuthService.isPremiumUser()](lib/services/auth_service.dart:19) sempre retorna `false` (`TODO: verificar no Firestore`) e **nunca é chamado**.

Resultado: basta criar uma conta gratuita para ganhar todos os recursos pagos.

**Proposta.** Uma fonte de verdade só, gravada pelo backend, lida pelo cliente:

- **Recomendado — custom claim no ID token.** O backend (webhook do Stripe, item 2) grava `premium: true` no token via Admin SDK. O cliente lê com `user.getIdTokenResult()`, sem adicionar nenhuma dependência nova. Depois de uma compra é preciso forçar `user.getIdToken(true)` para o token novo carregar a claim.
- **Alternativa — documento `users/{uid}` no Firestore.** Mais fácil de inspecionar e alterar à mão, mas exige adicionar `cloud_firestore` ao `pubspec.yaml` (hoje não é dependência) e escrever regras de segurança que impeçam o cliente de editar o próprio campo.

**Passos.**

1. Implementar `AuthService.isPremiumUser()` de verdade e remover o `TODO`.
2. Em `shape_grid.dart`, apagar o `_isPremiumUser = true` e passar a consumir `AuthService` (o método é assíncrono — resolver no `initState` guardando em estado, ou com `FutureBuilder`).
3. Manter a assinatura `isPremiumUser` que já desce para `ColorableShapesPage` e `BrushSelector`; nada muda ali.
4. Reagir a `authStateChanges` para não deixar o status obsoleto após logout/troca de conta.

**Critério de aceite.** Conta gratuita recém-criada: pincéis lápis/giz aparecem bloqueados e desenhos `isPremium` seguem cadeados. Conta com a claim/documento premium: tudo destrava sem precisar reinstalar nada.

**Atenção — isso é UX, não segurança.** Todo o gating roda no cliente, e no build web *todos* os assets (desenhos e texturas premium) vão no bundle e são baixáveis por qualquer visitante. Se proteger o conteúdo pago importa de fato, os assets premium precisam sair do bundle e ser servidos atrás de autenticação (Firebase Storage com regras + URL assinada). É uma decisão de produto, não uma consequência automática deste item.

---

## 2. Trocar `flutter_stripe` por Stripe Checkout

**Problema.** `flutter_stripe` 11.5 não tem implementação web: [main.dart:25](lib/main.dart:25) chama `StripeService.initializeStripe()` no boot e o console registra `Unsupported operation: Platform._operatingSystem` a cada carga. Sendo web-only, a `StripeService` inteira (payment sheet) é código morto. Somando a isso:

- [stripe_service.dart:9-11](lib/services/stripe_service.dart:9) tem `YOUR_BACKEND_URL` / `YOUR_STRIPE_PUBLISHABLE_KEY` como placeholders;
- [premium_page.dart:263](lib/views/premium_page.dart:263) concede o premium a partir do retorno do cliente (`initiatePayment`), o que é falsificável;
- nada no app navega para `PremiumPage` — o fluxo de upgrade é inalcançável hoje.

**Decidido.** Stripe, **assinatura mensal**, checkout por redirect, backend em Cloud Functions no projeto `colorir-448119` (exige plano Blaze). O cliente nunca decide quem é premium — quem grava é o webhook.

**Duas Cloud Functions.**

`criarSessaoCheckout` — callable, exige usuário autenticado:

1. Rejeita chamada sem `request.auth`.
2. Busca ou cria o Stripe Customer do usuário, guardando o mapa `customerId ↔ uid` no Firestore via Admin SDK (só o backend escreve; o cliente nunca lê isso, então **não precisa** adicionar `cloud_firestore` ao app).
3. Cria a Checkout Session com `mode: 'subscription'`, o `price` da assinatura, `client_reference_id: uid`, `success_url` e `cancel_url` apontando de volta para o app.
4. Devolve `session.url`.

`stripeWebhook` — HTTP, público por natureza:

1. Valida a assinatura com `stripe.webhooks.constructEvent(req.rawBody, sig, WEBHOOK_SECRET)` — **precisa do `rawBody`**, o corpo já parseado não serve. Sem essa validação, qualquer um concede premium com um `curl`.
2. Trata os eventos do ciclo de vida da assinatura: `customer.subscription.created`, `.updated`, `.deleted` e `invoice.payment_failed`.
3. Resolve o `uid` a partir do customer e grava `admin.auth().setCustomUserClaims(uid, {premium: <ativo>})`, onde `<ativo>` é `status ∈ {active, trialing}`.
4. Espelha status e `current_period_end` em `users/{uid}` — só para inspeção e suporte, não como fonte de verdade do cliente.

**No app.** `PremiumPage` chama a callable, recebe a URL e redireciona a aba (`url_launcher` com `webOnlyWindowName: '_self'`). Na volta pela `success_url`, força `user.getIdToken(true)` e reavalia.

**Dois detalhes de timing que costumam morder:**

- O webhook pode chegar *depois* do redirect de volta. Sem `cloud_firestore` no cliente para escutar em tempo real, a saída é tentar o refresh do token algumas vezes ao longo de ~10s antes de desistir e pedir para o usuário recarregar.
- O ID token vive ~1h. Quem cancelar segue premium até o token expirar ou ser renovado à força. Aceitável aqui; se não for, o cliente precisa observar o Firestore.

**Cancelamento.** Assinatura exige uma saída: uma terceira callable criando uma sessão do Customer Portal da Stripe resolve cancelamento e troca de cartão sem UI própria.

**Segredos.** `STRIPE_SECRET_KEY` e `STRIPE_WEBHOOK_SECRET` via `defineSecret` (Secret Manager), nunca no cliente. A publicável não é usada neste desenho — o redirect dispensa Stripe.js.

**Descartado — a extensão do Firebase.** A extensão *Run Payments with Stripe* (`firestore-stripe-payments`) faria tudo isso sem backend próprio: o cliente escreve em `customers/{uid}/checkout_sessions`, a extensão devolve a `url` da sessão, e o webhook dela grava o custom claim `stripeRole`. Não dá para adotar:

- **A plataforma de Extensions do Firebase foi descontinuada e desliga em 31/03/2027** — depois disso não é possível instalar, atualizar, reconfigurar nem desinstalar pelo console/CLI, e a limpeza dos recursos (Cloud Functions, secrets, filas, service accounts) vira manual no Google Cloud. Ferramentas de migração prometidas para setembro/2026.
- A Stripe transferiu a extensão para a Invertase; a versão `stripe/firestore-stripe-payments` está sem manutenção desde junho/2026.

Ainda assim ela é open source e implementa exatamente o desenho abaixo — vale copiar a abordagem em vez de inventar.

**Passos.**

1. Criar produto e `price` recorrente mensal no dashboard da Stripe, em **modo teste** primeiro.
2. ~~Criar `functions/` (Python 3.13, 2ª geração)~~ — **feito**, ver [functions/README.md](functions/README.md). Venv instalado. Falta a Firebase CLI nesta máquina e subir o projeto para o plano Blaze.
3. ~~Escrever as três funções~~ — **feito e testado offline**: a descoberta do SDK reconhece as 3 funções com região e secrets corretos, e `functions/tests/test_webhook.py` cobre assinatura e roteamento (15 testes). Falta registrar a URL do webhook na Stripe e guardar o signing secret.
4. Remover `flutter_stripe` do `pubspec.yaml`, apagar `stripe_service.dart` e a chamada em `main()` (`main.dart:25`) — o erro de boot na web some junto. `package:http` sai com ele.
5. Criar um `CheckoutService` enxuto no app (chamada callable + redirect).
6. Reescrever `PremiumPage` sobre o novo fluxo, apagando o `TODO` de `premium_page.dart:263`.
7. Tornar `PremiumPage` alcançável: botão no `AppBar` do grid e no diálogo de recurso bloqueado do `BrushSelector`.
8. Adicionar rota/tratamento para o retorno de `success_url` e `cancel_url`.

**Critério de aceite.**

- Assinatura de teste com `4242 4242 4242 4242` conclui e, na volta ao app, os pincéis premium destravam sem novo login.
- Cancelar no meio do checkout não concede nada.
- Cancelar pelo Customer Portal derruba o premium após a renovação do token.
- `invoice.payment_failed` tira o premium.
- Chamar a callable à mão, sem pagar, não concede nada; `POST` no webhook com corpo forjado e assinatura inválida é rejeitado.

---

## 3. Versionar a plataforma web

**Problema.** O [.gitignore](.gitignore:52) ignora `/web` (linha 52) e `web/index.html` (linha 55) — ou seja, a única plataforma que importa não está versionada. Um clone novo perde o `index.html` com o meta tag `google-signin-client_id`, sem o qual o login Google quebra. Idem para `/lib/firebase_options.dart` (linha 47), sem o qual o projeto **nem compila** (foi o que travou este PC; o arquivo foi recuperado de dentro do `lib.zip`).

**Passos.**

1. Remover as linhas `/web` e `web/index.html` do `.gitignore` e commitar `web/`.
2. Decidir sobre `lib/firebase_options.dart` — ver "decisões pendentes".
3. Validar clonando em uma pasta limpa: `flutter pub get` + `flutter build web` devem funcionar sem nenhum passo manual.
4. Opcional: remover `lib.zip` do repositório depois disso — ele só existia como backup improvisado e já cumpriu o papel.

**Critério de aceite.** Clone limpo → `pub get` → `build web` → app sobe com Firebase inicializando e login Google funcionando.

---

## 4. Limpezas de baixo risco

- `touchable` e `flutter_svg` estão declarados no `pubspec.yaml` e **nunca são importados** — remover.
- `package:http` é usado em `stripe_service.dart` mas é apenas dependência transitiva — some junto se o item 2 apagar o arquivo; caso contrário, declarar.
- [loginpage.dart](lib/views/loginpage.dart) reimplementa login por e-mail e Google direto no `FirebaseAuth`/`GoogleSignIn` em vez de usar `AuthService`, e cerca de metade do arquivo é uma cópia comentada da versão antiga (mesmo padrão em `shape.dart` e `auth_service.dart`). Apagar as cópias e passar a chamar `AuthService`.
- `flutter analyze` reporta 39 avisos/infos: `print` em produção (trocar por `debugPrint`), `withOpacity` depreciado (`withValues`), variáveis e imports não usados. Nenhum erro.

---

## Decisões tomadas

1. **Plataforma:** web only. Android/iOS/desktop não são mantidos.
2. **Backend:** Cloud Functions escritas à mão no projeto `colorir-448119`, plano Blaze. A extensão do Firebase está fora (ver item 2).
3. **PSP:** Stripe.
4. **Modelo de cobrança:** assinatura mensal.
5. **Entitlement:** custom claim `premium` no ID token, gravada só pelo webhook. O Firestore entra apenas do lado do backend (mapa customer ↔ uid e espelho de status), então o app **não** ganha a dependência `cloud_firestore`.

**Cobrar "pela própria Google" foi avaliado e descartado** — não substitui o PSP:

   - **Google Pay** é carteira e tokenização, não processador — exige um gateway atrás (a integração "Direct" só existe para quem é PCI DSS validado por QSA). Ele monta em cima de qualquer PSP escolhido; é ganho de conversão no checkout, não alternativa.
   - **Google Play Billing** é a Google cobrando de fato, mas só dentro da Play Store. Para um app web significa empacotar a PWA como TWA e usar a Digital Goods API — que só funciona no Chrome dentro de um TWA (Android/ChromeOS). Quem abrir no desktop ou no iOS fica sem como pagar. Some-se a comissão de 15–30%, a exigência da Play Billing Library 7+ (desde 31/08/2025), a volta da pasta `android/` que hoje não existe, e a validação da compra no servidor, que continua obrigatória. Só faz sentido se a decisão "web-only" for reaberta — é escolha de distribuição, não de pagamento.
---

## Decisões pendentes (precisam de você)

1. **Assets premium no bundle:** aceitar que são baixáveis, ou movê-los para trás de autenticação? Não bloqueia nada — dá para decidir depois que a cobrança estiver de pé.
2. **Versionar `lib/firebase_options.dart`?** Não são segredos (as chaves já aparecem no bundle JS público e dentro do `lib.zip` commitado), e versionar simplifica o clone. Bloqueia o passo 2 do item 3.
3. **Preço da assinatura.** Precisa estar definido antes de criar o `price` na Stripe (passo 1 do item 2).
