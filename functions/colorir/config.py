"""Região, segredos e parâmetros das funções."""

from firebase_functions.params import SecretParam, StringParam

# São Paulo, para ficar perto do público. O app precisa usar a MESMA região:
# FirebaseFunctions.instanceFor(region: 'southamerica-east1')
REGIAO = "southamerica-east1"

# Segredos — Secret Manager, nunca no repositório nem no cliente.
# Definir com: firebase functions:secrets:set STRIPE_SECRET_KEY
STRIPE_SECRET_KEY = SecretParam("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = SecretParam("STRIPE_WEBHOOK_SECRET")

# Parâmetros não secretos — a CLI pergunta no primeiro deploy e guarda
# em functions/.env.colorir-448119
STRIPE_PRICE_ID = StringParam(
    "STRIPE_PRICE_ID",
    description="ID do price recorrente mensal criado na Stripe (price_...)",
)
APP_URL = StringParam(
    "APP_URL",
    default="http://localhost:8080",
    description="Origem do app web, usada em success_url e cancel_url",
)

# Status de assinatura que valem premium.
STATUS_ATIVOS = frozenset({"active", "trialing"})
