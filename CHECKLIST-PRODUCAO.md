# Checklist de produção — Vamos Colorir

Tudo que falta para o projeto ir ao ar. Itens marcados **(verificado)** foram
conferidos no código ou no build desta máquina em 12/08/2026; o resto é
trabalho conhecido, ainda não feito.

Funcionalidades futuras ficam fora desta lista: veja
[PLANO-UPLOAD-SVG.md](PLANO-UPLOAD-SVG.md) e
[PLANO-SALVAR-DESENHO.md](PLANO-SALVAR-DESENHO.md).

---

## Dois lançamentos possíveis

Vale enxergar que existem duas metas, e a primeira é muito mais perto:

- **No ar de graça** — precisa só das seções 1, 3 (parte), 5 e 6. Dá para
  chegar lá sem Stripe, sem Blaze e sem backend.
- **No ar cobrando** — soma as seções 2 e 4. É onde mora a maior parte do
  esforço e todo o risco jurídico.

Se a ideia é validar o produto antes de investir na cobrança, lançar grátis
primeiro encurta muito o caminho.

---

## 1. Bloqueadores — não dá para publicar assim

- [ ] **Não existe hospedagem configurada.** O `firebase.json` não tem seção
      `hosting` **(verificado)**. Decidir onde o app é servido — Firebase
      Hosting é o caminho natural, já que o projeto Firebase existe.
- [ ] **O app se apresenta como projeto de exemplo (verificado).** Título
      `app_de_colorir`, descrição "A new Flutter project.", `manifest.json` com
      o mesmo nome, e os ícones ainda são **a logo do Flutter**. Quem instalar
      como PWA hoje recebe isso.
- [ ] **`/web` está no `.gitignore` (verificado).** A única plataforma alvo não
      está versionada, e o `web/index.html` carrega o meta tag
      `google-signin-client_id` sem o qual o login Google quebra. Item 3 do
      [PLANO.md](PLANO.md).
- [ ] **`lib/firebase_options.dart` também está ignorado.** Sem ele o projeto
      nem compila num clone limpo.
- [ ] **Domínio de produção não está autorizado em lugar nenhum.** Precisa
      entrar nos *authorized domains* do Firebase Auth e nas *origens
      JavaScript autorizadas* do cliente OAuth do Google. Hoje só
      `localhost:8080` funciona.
- [ ] **Erro no console a cada carregamento.** `flutter_stripe` não tem
      implementação web e o `main()` registra
      `Unsupported operation: Platform._operatingSystem` no boot. Sai junto com
      a troca por Stripe Checkout.
- [ ] **Qualquer conta gratuita vira premium.** `shape_grid.dart:42` marca
      `_isPremiumUser = true` para todo usuário logado. Se lançar cobrando com
      isso, ninguém precisa pagar.

---

## 2. Cobrança — necessário só se for lançar pago

**Infraestrutura**

- [ ] Subir o projeto Firebase para o **plano Blaze** (Cloud Functions não roda
      no Spark).
- [ ] Instalar **Node** e a **Firebase CLI** nesta máquina — hoje nenhum dos
      dois existe aqui **(verificado)**. O backend é Python, mas a ferramenta
      de deploy é Node.
- [ ] Definir os segredos `STRIPE_SECRET_KEY` e `STRIPE_WEBHOOK_SECRET`.
- [ ] Definir `STRIPE_PRICE_ID` e `APP_URL` — a `APP_URL` precisa ser o domínio
      de produção, não `localhost`.
- [ ] Fazer o primeiro deploy das três funções.
- [ ] Registrar a URL do `stripewebhook` no dashboard da Stripe e guardar o
      signing secret.

**Stripe**

- [ ] Definir o **preço da assinatura** (ainda não decidido).
- [ ] Criar produto e `price` recorrente em **modo teste**.
- [ ] **Ativar a conta Stripe**: dados da empresa/pessoa, conta bancária,
      configuração fiscal. Sem isso não se recebe dinheiro de verdade.
- [ ] Depois de tudo validado, migrar para **chaves live** e criar o webhook de
      produção (o signing secret é outro).

**No app**

- [ ] `AuthService.isPremiumUser()` lendo a custom claim de verdade — hoje
      sempre retorna `false` e nunca é chamado.
- [ ] Remover o `_isPremiumUser = true` do `shape_grid.dart`.
- [ ] Criar o `CheckoutService` (chamada callable + redirect).
- [ ] Reescrever a `PremiumPage` sobre o novo fluxo e **torná-la alcançável** —
      hoje nada navega até ela.
- [ ] Tratar o retorno de `success_url` / `cancel_url` e forçar
      `getIdToken(true)`, com nova tentativa por alguns segundos (o webhook
      pode chegar depois do redirect).
- [ ] Remover `flutter_stripe`, `stripe_service.dart` e a chamada no `main()`.

**Testes**

- [ ] Assinatura de teste ponta a ponta com `4242 4242 4242 4242`.
- [ ] Cancelar pelo Customer Portal e confirmar que o premium cai.
- [ ] Falha de pagamento derrubando o premium.
- [ ] Tentar virar premium sem pagar (chamar a callable à mão, forjar webhook)
      e confirmar que não funciona.

---

## 3. Segurança

- [ ] **Não existem regras do Firestore (verificado).** Não há
      `firestore.rules` no repositório. O backend escreve em `usuarios/`,
      `stripe_clientes/` e `stripe_eventos/`, e nenhuma dessas coleções tem
      regra escrita. Precisa negar acesso do cliente a todas elas — o app não
      lê Firestore, então a regra pode ser restritiva de verdade.
- [ ] Conferir que a chave secreta da Stripe **nunca** aparece no bundle web.
      As chaves do Firebase no `firebase_options.dart` são públicas por design;
      a da Stripe não é.
- [ ] **Alertas de orçamento** no Blaze. Sem teto, um laço de requisição vira
      fatura.
- [ ] Backup do Firestore (ou point-in-time recovery) antes de haver assinante
      pagante — perder o vínculo `customer ↔ uid` significa perder quem pagou.
- [ ] `storage.rules` — só se o upload de SVG existir um dia.

---

## 4. Jurídico — obrigatório antes de cobrar

- [ ] **Termos de uso e política de privacidade** publicados e acessíveis pelo
      app. A Stripe exige que estejam no ar para ativar a conta.
- [ ] **Política de cancelamento e reembolso** clara. O Customer Portal já
      resolve o cancelamento em si.
- [ ] **LGPD, com o agravante de ser app infantil.** Dado de criança tem regime
      próprio e exige consentimento de um responsável. Vale deixar explícito no
      fluxo que a conta e a assinatura são contratadas por um adulto.
- [ ] Se houver público fora do Brasil, COPPA (EUA) e GDPR-K (Europa) entram na
      conta.

> Não sou advogado e isto não é aconselhamento jurídico — é a lista do que
> costuma ser exigido. Para um app infantil que cobra assinatura, vale uma
> revisão profissional antes do lançamento pago.

---

## 5. Qualidade e desempenho (tudo verificado)

- [ ] **Primeira carga pesada.** `main.dart.js` tem **2,9 MB** e o runtime WASM
      entre **3,5 MB e 6,9 MB**, conforme o navegador. Para pais em rede móvel
      isso é muito. Vale medir o tempo real de primeira abertura antes de
      decidir se precisa de ação.
- [ ] **Texturas de giz somam 9,8 MB** em cerca de 60 arquivos (~160 KB cada).
      Cada cor que o usuário escolhe baixa um desses. Comprimir vale a pena.
- [ ] **2,6 MB de peso morto no repositório**: `gizazul.png` (1,1 MB) e
      `gizverde.png` (1,5 MB) não são referenciados por nenhum código e nem
      entram no bundle, porque a pasta deles não está declarada no
      `pubspec.yaml`. Podem ser apagados.
- [ ] **`_loadTextures()` redecodifica a textura de todas as formas a cada
      toque** no canvas. Com desenhos maiores, trava.
- [ ] **Pintar suja a miniatura.** As formas são mutadas na lista compartilhada,
      então colorir um desenho vaza para a grade e persiste na sessão.
- [ ] **Layout em celular nunca foi testado.** O canvas tem altura fixa de 500
      com um `Spacer()` abaixo. Sendo web-only, boa parte do público vai chegar
      pelo navegador do celular — isso precisa ser verificado antes de lançar.
- [ ] **39 avisos do `flutter analyze`** (nenhum erro): `print` em produção,
      `withOpacity` depreciado, variáveis e imports não usados.
- [ ] **O app Flutter não tem nenhum teste.** Os únicos testes do projeto são
      os do webhook, no backend.

---

## 6. Limpeza do repositório

- [ ] `lib.zip` — snapshot antigo do `lib/`, commitado. Já cumpriu o papel de
      recuperar o `firebase_options.dart`.
- [ ] `android/app/google-services.json` commitado, sendo que a pasta `android/`
      nem existe mais.
- [ ] `touchable` e `flutter_svg` declarados no `pubspec.yaml` e nunca
      importados **(verificado)**.
- [ ] `loginpage.dart` reimplementa login em vez de usar o `AuthService`, e
      metade do arquivo é cópia comentada da versão antiga. Mesmo padrão em
      `shape.dart` e `auth_service.dart`.
- [ ] `README.md` ainda é o boilerplate do `flutter create`.

---

## 7. Operação — depois de no ar

- [ ] **Nenhum relatório de erro.** Se quebrar no navegador de um usuário, você
      não fica sabendo. Vale um serviço de captura de erro para web.
- [ ] **Nenhuma analytics.** Sem isso não dá para saber quantos chegam à tela de
      premium e desistem.
- [ ] **Alerta de falha no webhook.** Webhook falhando em silêncio significa
      gente pagando e não recebendo o premium — o pior tipo de bug.
- [ ] **Falha de inicialização do Firebase é só um `debugPrint`.** Em produção,
      o usuário vê um app que simplesmente não funciona, sem explicação.
- [ ] Plano para atualizar o app: quem tiver a página aberta continua no build
      antigo até recarregar.

---

## Caminho mínimo para lançar grátis

Se a meta for só colocar no ar, sem cobrar, o conjunto encolhe bastante:

1. Versionar `web/` e o `firebase_options.dart` (seção 1).
2. Trocar nome, descrição e ícones (seção 1).
3. Configurar hospedagem e autorizar o domínio no Auth e no OAuth (seção 1).
4. Testar no navegador do celular (seção 5).
5. Apagar o peso morto e comprimir as texturas de giz (seções 5 e 6).
6. Escrever as regras do Firestore, mesmo sem usar ainda (seção 3).
7. Publicar política de privacidade — mesmo sem cobrar, há login e dado
      pessoal (seção 4).

O erro de boot do Stripe e o premium liberado para todos deixam de ser
bloqueadores nesse cenário: sem cobrança, o pior que acontece é todo mundo ter
acesso a tudo — o que pode até ser o desejado numa validação inicial.
