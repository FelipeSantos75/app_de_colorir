"""Concessão e revogação do premium."""

from firebase_admin import auth, firestore
from firebase_functions import logger


def definir_premium(uid: str, ativo: bool, **extras) -> None:
    """Única função autorizada a conceder ou tirar premium.

    A claim é o que o app lê (via getIdTokenResult). O documento em
    usuarios/{uid} é só espelho para suporte — nunca fonte de verdade.
    """
    # set_custom_user_claims SUBSTITUI todas as claims, não faz merge.
    # Sem ler as existentes antes, qualquer outra claim do usuário some.
    usuario = auth.get_user(uid)
    claims = dict(usuario.custom_claims or {})
    claims["premium"] = ativo
    auth.set_custom_user_claims(uid, claims)

    firestore.client().collection("usuarios").document(uid).set(
        {"premium": ativo, **extras},
        merge=True,
    )

    logger.info(f"Premium atualizado: uid={uid} ativo={ativo} {extras}")
