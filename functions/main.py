"""Backend do Vamos Colorir — checkout, portal do cliente e entitlement premium.

Os nomes das funções são minúsculos e sem underscore de propósito: o SDK Python
usa o nome da função Python literalmente como id implantado, e ids de funções
de 2ª geração não aceitam underscore.

    criarcheckout   -> callable
    portalcliente   -> callable
    stripewebhook   -> HTTP
"""

import stripe
from firebase_admin import initialize_app
from firebase_functions import https_fn, logger

from colorir.clientes import obter_ou_criar_cliente
from colorir.config import (
    APP_URL,
    REGIAO,
    STRIPE_PRICE_ID,
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
)
from colorir.eventos import liberar_evento, marcar_evento, tratar_evento
from colorir.stripe_client import obter_stripe

initialize_app()


@https_fn.on_call(region=REGIAO, secrets=[STRIPE_SECRET_KEY])
def criarcheckout(req: https_fn.CallableRequest) -> dict:
    """Cria a sessão de checkout da assinatura e devolve a URL.

    Não concede nada: quem libera o premium é o webhook, depois que a Stripe
    confirmar. Chamar isto à mão não vira assinatura.
    """
    if req.auth is None:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.UNAUTHENTICATED,
            "Faça login para assinar o premium.",
        )

    uid = req.auth.uid
    email = (req.auth.token or {}).get("email")

    customer_id = obter_ou_criar_cliente(uid, email)
    base = APP_URL.value.rstrip("/")

    sessao = obter_stripe().v1.checkout.sessions.create(
        params={
            "mode": "subscription",
            "customer": customer_id,
            "client_reference_id": uid,
            "line_items": [{"price": STRIPE_PRICE_ID.value, "quantity": 1}],
            "success_url": f"{base}/#/premium/sucesso?session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{base}/#/premium/cancelado",
            "allow_promotion_codes": True,
        }
    )

    return {"url": sessao.url}


@https_fn.on_call(region=REGIAO, secrets=[STRIPE_SECRET_KEY])
def portalcliente(req: https_fn.CallableRequest) -> dict:
    """Abre o Customer Portal da Stripe — cancelar, trocar cartão, ver faturas.

    Assinatura sem saída vira problema de suporte e, dependendo do país, de
    direito do consumidor.
    """
    if req.auth is None:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.UNAUTHENTICATED,
            "Faça login para gerenciar a assinatura.",
        )

    from firebase_admin import firestore

    snap = firestore.client().collection("usuarios").document(req.auth.uid).get()
    customer_id = snap.to_dict().get("stripeCustomerId") if snap.exists else None

    if not customer_id:
        raise https_fn.HttpsError(
            https_fn.FunctionsErrorCode.FAILED_PRECONDITION,
            "Nenhuma assinatura encontrada para esta conta.",
        )

    base = APP_URL.value.rstrip("/")
    sessao = obter_stripe().v1.billing_portal.sessions.create(
        params={"customer": customer_id, "return_url": f"{base}/#/premium"}
    )

    return {"url": sessao.url}


@https_fn.on_request(region=REGIAO, secrets=[STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET])
def stripewebhook(req: https_fn.Request) -> https_fn.Response:
    """Recebe os eventos da Stripe. É a ÚNICA coisa que concede premium.

    Registrar a URL no dashboard da Stripe após o primeiro deploy e guardar o
    signing secret em STRIPE_WEBHOOK_SECRET.
    """
    assinatura = req.headers.get("stripe-signature", "")

    try:
        # Precisa ser o corpo cru. O corpo já parseado muda os bytes e a
        # validação falha — sem ela, qualquer um vira premium com um curl.
        evento = stripe.Webhook.construct_event(
            req.get_data(),
            assinatura,
            STRIPE_WEBHOOK_SECRET.value,
        )
    except (ValueError, stripe.SignatureVerificationError) as erro:
        logger.warn(f"Webhook com assinatura inválida: {erro}")
        return https_fn.Response("assinatura inválida", status=400)

    evento_id = evento["id"]
    tipo = evento["type"]

    if not marcar_evento(evento_id, tipo):
        logger.info(f"Evento já processado, ignorando: {evento_id} ({tipo})")
        return https_fn.Response("ok", status=200)

    try:
        tratar_evento(evento)
    except Exception as erro:  # noqa: BLE001 - devolver 500 faz a Stripe tentar de novo
        liberar_evento(evento_id)
        logger.error(f"Falha ao tratar {evento_id} ({tipo}): {erro}")
        return https_fn.Response("erro ao processar", status=500)

    return https_fn.Response("ok", status=200)
