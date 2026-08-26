"""Cliente da Stripe.

O módulo se chama stripe_client e não stripe de propósito: um módulo local
chamado stripe sombrearia o pacote instalado e nada disto importaria.
"""

import stripe

from .config import STRIPE_SECRET_KEY

_cliente: stripe.StripeClient | None = None


def obter_stripe() -> stripe.StripeClient:
    """O segredo só existe em runtime.

    Ler STRIPE_SECRET_KEY.value no topo do módulo seria avaliado durante a
    descoberta do deploy, quando a variável ainda está vazia.
    """
    global _cliente
    if _cliente is None:
        _cliente = stripe.StripeClient(STRIPE_SECRET_KEY.value)
    return _cliente
