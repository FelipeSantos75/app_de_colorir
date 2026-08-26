"""Testes do webhook — sem rede, sem Firebase, sem deploy.

Cobre as duas partes que, se quebrarem, viram furo de segurança ou premium
fantasma: a validação da assinatura da Stripe e o roteamento dos eventos.

    functions/venv/Scripts/python.exe functions/tests/test_webhook.py
"""

import hashlib
import hmac
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import stripe  # noqa: E402
from colorir import eventos  # noqa: E402

SEGREDO = "whsec_teste_1234567890"
falhas = []


def assinar(payload: str, segredo: str = SEGREDO, t: int | None = None) -> str:
    """Reproduz o esquema de assinatura da Stripe: t=<ts>,v1=<hmac sha256>."""
    t = t or int(time.time())
    sig = hmac.new(segredo.encode(), f"{t}.{payload}".encode(), hashlib.sha256).hexdigest()
    return f"t={t},v1={sig}"


def checar(nome, condicao, detalhe=""):
    print(("  OK   " if condicao else "  FALHA") + f"  {nome}" + (f"  [{detalhe}]" if detalhe and not condicao else ""))
    if not condicao:
        falhas.append(nome)


print("== validacao de assinatura ==")

corpo = json.dumps({"id": "evt_1", "type": "ping", "data": {"object": {}}})

ev = stripe.Webhook.construct_event(corpo, assinar(corpo), SEGREDO)
checar("assinatura valida e aceita", ev["id"] == "evt_1")

try:
    stripe.Webhook.construct_event(corpo, assinar(corpo, "whsec_outro"), SEGREDO)
    checar("assinatura de outro segredo e rejeitada", False)
except stripe.SignatureVerificationError:
    checar("assinatura de outro segredo e rejeitada", True)

try:
    adulterado = json.dumps({"id": "evt_1", "type": "ping", "data": {"object": {"hack": 1}}})
    stripe.Webhook.construct_event(adulterado, assinar(corpo), SEGREDO)
    checar("corpo adulterado e rejeitado", False)
except stripe.SignatureVerificationError:
    checar("corpo adulterado e rejeitado", True)

try:
    stripe.Webhook.construct_event(corpo, assinar(corpo, t=int(time.time()) - 4000), SEGREDO)
    checar("timestamp velho e rejeitado (replay)", False)
except stripe.SignatureVerificationError:
    checar("timestamp velho e rejeitado (replay)", True)

try:
    stripe.Webhook.construct_event(corpo, "", SEGREDO)
    checar("header vazio e rejeitado", False)
except (stripe.SignatureVerificationError, ValueError):
    checar("header vazio e rejeitado", True)


print()
print("== roteamento de eventos ==")

# Substitui as dependencias que falariam com Firestore/Auth.
chamadas = []
eventos.definir_premium = lambda uid, ativo, **kw: chamadas.append(("premium", uid, ativo, kw))
eventos.uid_do_cliente = lambda cid: "uid_teste" if cid == "cus_ok" else None
eventos.vincular_cliente = lambda uid, cid: chamadas.append(("vincular", uid, cid))


def rodar(tipo, objeto):
    chamadas.clear()
    eventos.tratar_evento({"id": "evt_x", "type": tipo, "data": {"object": objeto}})
    return list(chamadas)


r = rodar("customer.subscription.created", {"customer": "cus_ok", "status": "active", "id": "sub_1", "current_period_end": 111})
checar(
    "subscription active concede premium",
    r == [("premium", "uid_teste", True, {"statusAssinatura": "active", "assinaturaId": "sub_1", "fimPeriodoAtual": 111})],
    str(r),
)

r = rodar("customer.subscription.updated", {"customer": "cus_ok", "status": "past_due", "id": "sub_1"})
checar("status past_due tira premium", bool(r) and r[0][2] is False, str(r))

r = rodar("customer.subscription.updated", {"customer": "cus_ok", "status": "trialing", "id": "sub_1"})
checar("status trialing mantem premium", bool(r) and r[0][2] is True, str(r))

r = rodar("customer.subscription.deleted", {"customer": "cus_ok", "status": "active", "id": "sub_1"})
checar("deleted tira premium mesmo com status active", bool(r) and r[0][2] is False, str(r))

r = rodar("customer.subscription.updated", {"customer": "cus_desconhecido", "status": "active", "id": "sub_1"})
checar("customer sem uid nao concede nada", r == [], str(r))

r = rodar("checkout.session.completed", {"client_reference_id": "uid_teste", "customer": "cus_ok"})
checar("checkout.completed vincula customer ao uid", r == [("vincular", "uid_teste", "cus_ok")], str(r))

r = rodar("invoice.payment_failed", {"customer": "cus_ok"})
checar("payment_failed nao mexe na claim direto", r == [], str(r))

r = rodar("customer.updated", {"customer": "cus_ok"})
checar("evento irrelevante e ignorado", r == [], str(r))


print()
print("== current_period_end nos dois formatos ==")

checar("formato antigo (no objeto)", eventos.fim_do_periodo({"current_period_end": 999}) == 999)
checar("formato novo (nos items)", eventos.fim_do_periodo({"items": {"data": [{"current_period_end": 555}]}}) == 555)
checar("ausente vira None", eventos.fim_do_periodo({}) is None)

print()
print("RESULTADO: " + ("TODOS OS TESTES PASSARAM" if not falhas else f"{len(falhas)} FALHA(S): " + ", ".join(falhas)))
sys.exit(1 if falhas else 0)
