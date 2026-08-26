"""Tratamento dos eventos da Stripe e guarda de idempotência."""

from firebase_admin import firestore
from firebase_functions import logger

from .clientes import uid_do_cliente, vincular_cliente
from .config import STATUS_ATIVOS
from .entitlement import definir_premium


def marcar_evento(evento_id: str, tipo: str) -> bool:
    """Devolve True se o evento é inédito e deve ser processado.

    A Stripe reentrega eventos. Sem guarda, um retry reprocessa algo já
    tratado, e um evento antigo fora de ordem pode reverter estado mais novo.
    """
    db = firestore.client()
    ref = db.collection("stripe_eventos").document(evento_id)

    @firestore.transactional
    def _marcar(transacao):
        snap = ref.get(transaction=transacao)
        if snap.exists:
            return False
        transacao.set(ref, {"tipo": tipo, "em": firestore.SERVER_TIMESTAMP})
        return True

    return _marcar(db.transaction())


def liberar_evento(evento_id: str) -> None:
    """Solta a marca para o retry da Stripe poder reprocessar após uma falha."""
    try:
        firestore.client().collection("stripe_eventos").document(evento_id).delete()
    except Exception as erro:  # noqa: BLE001 - melhor engolir do que mascarar o erro original
        logger.warn(f"Não consegui liberar o evento {evento_id}: {erro}")


def tratar_evento(evento) -> None:
    tipo = evento["type"]
    objeto = evento["data"]["object"]

    if tipo == "checkout.session.completed":
        vincular_cliente(objeto.get("client_reference_id"), objeto.get("customer"))
        return

    if tipo in (
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    ):
        uid = uid_do_cliente(objeto.get("customer"))
        if not uid:
            logger.error(
                f"Assinatura sem uid vinculado: customer={objeto.get('customer')} "
                f"assinatura={objeto.get('id')}"
            )
            return

        ativo = (
            tipo != "customer.subscription.deleted"
            and objeto.get("status") in STATUS_ATIVOS
        )

        definir_premium(
            uid,
            ativo,
            statusAssinatura=objeto.get("status"),
            assinaturaId=objeto.get("id"),
            fimPeriodoAtual=fim_do_periodo(objeto),
        )
        return

    if tipo == "invoice.payment_failed":
        # O status da assinatura muda junto e chega em customer.subscription.updated,
        # que é quem de fato derruba o premium. Aqui só registramos.
        logger.warn(f"Falha de pagamento: customer={objeto.get('customer')}")
        return

    logger.debug(f"Evento ignorado: {tipo}")


def fim_do_periodo(assinatura) -> int | None:
    """current_period_end saiu do objeto da assinatura e passou para os items
    em versões recentes da API. Lê dos dois lugares."""
    direto = assinatura.get("current_period_end")
    if direto:
        return direto
    items = (assinatura.get("items") or {}).get("data") or []
    if items:
        return items[0].get("current_period_end")
    return None
