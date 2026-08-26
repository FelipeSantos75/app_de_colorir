"""Mapa entre o usuário do Firebase e o customer da Stripe.

Escrito só pelo backend, via Admin SDK. O app nunca lê estas coleções — é por
isso que ele não precisa da dependência cloud_firestore.

    usuarios/{uid}                 -> stripeCustomerId, premium, statusAssinatura, ...
    stripe_clientes/{customerId}   -> uid
    stripe_eventos/{eventId}       -> tipo, em   (guarda de idempotência)
"""

from firebase_admin import firestore

from .stripe_client import obter_stripe


def obter_ou_criar_cliente(uid: str, email: str | None) -> str:
    db = firestore.client()
    ref = db.collection("usuarios").document(uid)
    snap = ref.get()

    if snap.exists:
        existente = snap.to_dict().get("stripeCustomerId")
        if existente:
            return existente

    cliente = obter_stripe().v1.customers.create(
        params={
            "email": email or None,
            "metadata": {"firebaseUid": uid},
        }
    )

    ref.set({"stripeCustomerId": cliente.id}, merge=True)
    db.collection("stripe_clientes").document(cliente.id).set({"uid": uid})

    return cliente.id


def uid_do_cliente(customer_id: str) -> str | None:
    """Caminho inverso, usado pelo webhook: o evento traz o customer, não o uid."""
    snap = firestore.client().collection("stripe_clientes").document(customer_id).get()
    if not snap.exists:
        return None
    return snap.to_dict().get("uid")


def vincular_cliente(uid: str | None, customer_id: str | None) -> None:
    """Rede de segurança: se o customer nasceu fora do fluxo normal, o
    checkout.session.completed ainda traz o uid em client_reference_id."""
    if not uid or not customer_id:
        return
    db = firestore.client()
    db.collection("stripe_clientes").document(customer_id).set({"uid": uid}, merge=True)
    db.collection("usuarios").document(uid).set({"stripeCustomerId": customer_id}, merge=True)
