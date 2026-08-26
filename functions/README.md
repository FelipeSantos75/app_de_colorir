# Backend — Vamos Colorir

Cloud Functions em **Python 3.13** (2ª geração) do projeto Firebase
`colorir-448119`. Cria o checkout da assinatura e é a **única** coisa que
concede premium. Ver [PLANO.md](../PLANO.md), item 2.

## Funções

| Função | Tipo | Papel |
| --- | --- | --- |
| `criarcheckout` | callable | Cria a Checkout Session da assinatura e devolve a URL. Exige usuário autenticado. Não concede nada. |
| `portalcliente` | callable | Abre o Customer Portal da Stripe: cancelar, trocar cartão, ver faturas. |
| `stripewebhook` | HTTP | Recebe os eventos da Stripe, valida a assinatura e grava a claim `premium`. |

Os nomes são minúsculos e sem underscore **de propósito**: o SDK Python usa o
nome da função Python literalmente como id implantado (verificado rodando a
descoberta do SDK), e ids de funções de 2ª geração não aceitam underscore.

Região: `southamerica-east1`. O app precisa usar a mesma:

```dart
FirebaseFunctions.instanceFor(region: 'southamerica-east1')
```

## Estrutura

```
main.py                  as 3 funções decoradas (finas)
colorir/config.py        região, segredos e parâmetros
colorir/stripe_client.py client da Stripe (lazy — o segredo só existe em runtime)
colorir/clientes.py      mapa customer <-> uid
colorir/entitlement.py   única função que concede/tira premium
colorir/eventos.py       idempotência e roteamento dos eventos
tests/test_webhook.py    testes sem rede
```

## Modelo de dados

Escrito só pelo backend via Admin SDK. O app **não** lê nada disso — é por
isso que ele não precisa da dependência `cloud_firestore`.

```
usuarios/{uid}                -> stripeCustomerId, premium, statusAssinatura,
                                 assinaturaId, fimPeriodoAtual
stripe_clientes/{customerId}  -> uid
stripe_eventos/{eventId}      -> tipo, em        (guarda de idempotência)
```

A fonte de verdade que o app lê é a **custom claim `premium`** no ID token,
não estes documentos.

## Ambiente local

O venv já está criado com as dependências instaladas. Para refazer do zero:

```bash
python -m venv functions/venv
```

```bash
functions/venv/Scripts/python.exe -m pip install -r functions/requirements.txt
```

## Testes

Rodam offline, sem Firebase e sem deploy — assinatura real via HMAC e
Firestore/Auth substituídos:

```bash
functions/venv/Scripts/python.exe functions/tests/test_webhook.py
```

## Configuração

Ainda pendente (precisa da Firebase CLI e do plano Blaze):

```bash
firebase functions:secrets:set STRIPE_SECRET_KEY
```

```bash
firebase functions:secrets:set STRIPE_WEBHOOK_SECRET
```

`STRIPE_PRICE_ID` e `APP_URL` não são segredos — a CLI pergunta no primeiro
deploy e guarda em `.env.colorir-448119`.

## Deploy

```bash
firebase deploy --only functions
```

Depois do primeiro deploy, pegue a URL de `stripewebhook`, cadastre no
dashboard da Stripe (eventos `checkout.session.completed`,
`customer.subscription.*` e `invoice.payment_failed`) e guarde o signing
secret gerado em `STRIPE_WEBHOOK_SECRET`.

## Desenvolvimento local

```bash
firebase emulators:start --only functions
```

O emulador do Firestore sobe na porta **8081**, não na 8080 — a 8080 é do
`flutter run -d chrome --web-port 8080`.

Para testar o webhook de ponta a ponta, use a Stripe CLI encaminhando para o
emulador:

```bash
stripe listen --forward-to http://localhost:5001/colorir-448119/southamerica-east1/stripewebhook
```

## Pontos que já mordem

- **`req.get_data()`** — a validação da assinatura precisa do corpo cru. Corpo
  já parseado falha, e sem validação qualquer um vira premium com um `curl`.
- **`set_custom_user_claims` substitui todas as claims**, não faz merge. O
  código lê as existentes antes de gravar; manter assim.
- **`param.value` é propriedade, não método** no SDK Python (no Node é
  `.value()`).
- **Nunca criar um módulo chamado `stripe.py`** aqui — sombrearia o pacote
  instalado.
- **Eventos são reentregues.** A coleção `stripe_eventos` existe para isso.
- **O ID token vive ~1h.** Quem cancela segue premium até o token renovar.
