# -*- coding: utf-8 -*-
"""Gera o workflow do ComfyUI (formato da interface, nao o formato de API).

O `build_workflow()` de geradesehmo.py devolve o formato que o endpoint
/prompt aceita, e esse formato NAO abre na tela do ComfyUI: falta posicao,
tamanho, ordem e a lista de links. Este script emite o formato da interface,
com os nos de comfyui_colorir/ no fim da linha.

    python comfyui_colorir/gerar_workflow.py [--instalar]

Sem argumento grava so' em comfyui_colorir/workflow_colorir.json.
Com --instalar copia tambem para a pasta de workflows do ComfyUI, onde ele
aparece na barra lateral.

Regerar depois de mexer em geradesehmo.py: os valores dos widgets (modelo,
steps, sampler, limites, textos de estilo) sao lidos de la'.
"""

import json
import os
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import geradesehmo as G  # noqa: E402

DESTINO_COMFY = os.path.join(
    os.environ.get("LOCALAPPDATA", ""),
    "Comfy-Desktop", "ComfyUI-Installs", "ComfyUI", "ComfyUI",
    "user", "default", "workflows",
)


class Grafo:
    """Montador enxuto do formato litegraph que o ComfyUI usa (version 0.4)."""

    def __init__(self):
        self.nos = []
        self.links = []
        self._proximo_no = 1
        self._proximo_link = 1

    def no(self, tipo, pos, tamanho, entradas=(), widgets=(), saidas=(),
           entradas_extra=(), titulo=None):
        """entradas: [(nome, tipo)] ligadas por cabo, sempre antes dos widgets.

        widgets: [(nome, valor, aceita_cabo)] — na ordem posicional em que o
        ComfyUI le' `widgets_values`.
        saidas:  [(nome, tipo)]
        """
        ident = self._proximo_no
        self._proximo_no += 1
        entradas_json = [
            {"name": nome, "type": tipo_e, "link": None} for nome, tipo_e in entradas
        ]
        for nome, _valor, aceita_cabo in widgets:
            if aceita_cabo:
                entradas_json.append(
                    {"name": nome, "type": "STRING", "widget": {"name": nome}, "link": None}
                )
        entradas_json += [
            {"name": nome, "type": tipo_x, "link": None, "shape": 7}
            for nome, tipo_x in entradas_extra
        ]
        no = {
            "id": ident,
            "type": tipo,
            "pos": list(pos),
            "size": list(tamanho),
            "flags": {},
            "order": ident,
            "mode": 0,
            "inputs": entradas_json,
            "outputs": [
                {"name": nome, "type": tipo_s, "slot_index": i, "links": []}
                for i, (nome, tipo_s) in enumerate(saidas)
            ],
            "properties": {"Node name for S&R": tipo},
            "widgets_values": [valor for _n, valor, _c in widgets],
        }
        if titulo:
            no["title"] = titulo
        self.nos.append(no)
        return ident

    def nota(self, pos, tamanho, texto):
        return self.no("MarkdownNote", pos, tamanho, widgets=[("texto", texto, False)],
                       titulo="Como usar")

    def ligar(self, origem, saida, destino, entrada):
        """`saida` e' indice na lista de saidas; `entrada` e' o NOME da entrada."""
        no_origem = next(n for n in self.nos if n["id"] == origem)
        no_destino = next(n for n in self.nos if n["id"] == destino)
        slot = next(i for i, e in enumerate(no_destino["inputs"]) if e["name"] == entrada)
        tipo = no_origem["outputs"][saida]["type"]

        ident = self._proximo_link
        self._proximo_link += 1
        no_origem["outputs"][saida]["links"].append(ident)
        no_destino["inputs"][slot]["link"] = ident
        self.links.append([ident, origem, saida, destino, slot, tipo])
        return ident

    def json(self):
        return {
            "id": "colorir-pipeline",
            "revision": 0,
            "last_node_id": self._proximo_no - 1,
            "last_link_id": self._proximo_link - 1,
            "nodes": self.nos,
            "links": self.links,
            "groups": [],
            "config": {},
            "extra": {"ds": {"scale": 0.55, "offset": [120, 260]}},
            "version": 0.4,
        }


NOTA = """## Página de colorir — pipeline completo

Mesmo caminho que `geradesehmo.py` roda no batch, aberto em nós:

1. **Cena pronta** → escolhe uma das cenas já escritas (`ANIMALS`).
2. **Montar prompt** → prefixo + cena + composição + sufixo. Os três blocos
   de estilo estão editáveis: são eles que carregam as restrições
   (contorno fechado, moldura, subdivisão). Ver `CLAUDE.md`.
3. **KSampler** → Z-Image-Turbo, `cfg=1` com `ConditioningZeroOut`:
   **não existe prompt negativo**, tudo tem que ser dito de forma afirmativa.
4. **Limpar e abrir manchas** → preto e branco puro, e esvazia preenchimento
   sólido (pata preta vira contorno, e portanto área pintável).
5. **Diagnóstico** → as seis checagens. Liga no `PreviewAny` pra ler o laudo.
6. **Vetorizar SVG** → grava em `output_coloring_pages/`, que é a pasta que
   `conversor_linhas.py` varre depois.

O batch faz uma coisa que a tela não faz: **re-rolar a seed** quando o
diagnóstico reprova. Aqui você lê o laudo e clica de novo — para gerar as 11
páginas de uma vez continua valendo `python geradesehmo.py`.
"""


def construir():
    g = Grafo()

    g.nota((-560, 40), (470, 560), NOTA)

    clip = g.no("CLIPLoader", (-60, 40), (380, 106),
                widgets=[("clip_name", G.CLIP_NAME, False),
                         ("type", G.CLIP_TYPE, False),
                         ("device", "default", False)],
                saidas=[("CLIP", "CLIP")])

    unet = g.no("UNETLoader", (-60, 200), (380, 82),
                widgets=[("unet_name", G.UNET_NAME, False),
                         ("weight_dtype", "default", False)],
                saidas=[("MODEL", "MODEL")])

    vae = g.no("VAELoader", (-60, 330), (380, 58),
               widgets=[("vae_name", G.VAE_NAME, False)],
               saidas=[("VAE", "VAE")])

    cena = g.no("ColorirCena", (-60, 440), (380, 78),
                widgets=[("cena", G.ANIMALS[0]["name"], False)],
                saidas=[("descricao", "STRING"), ("nome", "STRING")])

    prompt = g.no("ColorirPrompt", (380, 40), (460, 620),
                  widgets=[("descricao", "", True),
                           ("prefixo", G.STYLE_PREFIX, False),
                           ("composicao", G.STYLE_COMPOSICAO, False),
                           ("sufixo", G.STYLE_SUFFIX, False)],
                  saidas=[("prompt", "STRING")])

    texto = g.no("CLIPTextEncode", (900, 40), (420, 200),
                 entradas=[("clip", "CLIP")],
                 widgets=[("text", "", True)],
                 saidas=[("CONDITIONING", "CONDITIONING")])

    zero = g.no("ConditioningZeroOut", (900, 290), (300, 30),
                entradas=[("conditioning", "CONDITIONING")],
                saidas=[("CONDITIONING", "CONDITIONING")],
                titulo="ConditioningZeroOut (o \"negativo\" do turbo)")

    latente = g.no("EmptySD3LatentImage", (900, 380), (300, 106),
                   widgets=[("width", G.WIDTH, False),
                            ("height", G.HEIGHT, False),
                            ("batch_size", 1, False)],
                   saidas=[("LATENT", "LATENT")])

    sampling = g.no("ModelSamplingAuraFlow", (900, 530), (300, 58),
                    entradas=[("model", "MODEL")],
                    widgets=[("shift", G.MODEL_SAMPLING_SHIFT, False)],
                    saidas=[("MODEL", "MODEL")])

    sampler = g.no("KSampler", (1380, 40), (320, 262),
                   entradas=[("model", "MODEL"), ("positive", "CONDITIONING"),
                             ("negative", "CONDITIONING"), ("latent_image", "LATENT")],
                   widgets=[("seed", abs(G.SEED_BASE), False),
                            ("control_after_generate", "randomize", False),
                            ("steps", G.STEPS, False),
                            ("cfg", G.CFG, False),
                            ("sampler_name", G.SAMPLER, False),
                            ("scheduler", G.SCHEDULER, False),
                            ("denoise", 1, False)],
                   saidas=[("LATENT", "LATENT")])

    decode = g.no("VAEDecode", (1380, 350), (240, 46),
                  entradas=[("samples", "LATENT"), ("vae", "VAE")],
                  saidas=[("IMAGE", "IMAGE")])

    limpar = g.no("ColorirLimpar", (1380, 440), (330, 154),
                  entradas=[("imagem", "IMAGE")],
                  widgets=[("limiar", G.BW_THRESHOLD, False),
                           ("abrir_manchas", G.ABRIR_MANCHAS, False),
                           ("erosao", G.EROSAO_TRACO, False),
                           ("nucleo_min", G.NUCLEO_MIN, False)],
                  saidas=[("imagem", "IMAGE"), ("manchas_abertas", "INT")])

    diag = g.no("ColorirDiagnostico", (1780, 40), (340, 202),
                entradas=[("imagem", "IMAGE")],
                widgets=[("limite_fora", G.LIMITE_FORA, False),
                         ("limite_abrangencia", G.LIMITE_ABRANGENCIA, False),
                         ("limite_tinta", G.LIMITE_TINTA, False),
                         ("limite_maior", G.LIMITE_MAIOR, False),
                         ("limite_areas", G.LIMITE_AREAS, False)],
                saidas=[("aprovado", "BOOLEAN"), ("relatorio", "STRING"),
                        ("fora", "FLOAT"), ("maior", "FLOAT"), ("tinta", "FLOAT"),
                        ("areas", "INT"), ("macico", "FLOAT")])

    laudo = g.no("PreviewAny", (1780, 300), (340, 88),
                 entradas=[("source", "*")], titulo="Laudo")

    vetor = g.no("ColorirVetorizar", (1780, 430), (340, 130),
                 entradas=[("imagem", "IMAGE")],
                 entradas_extra=[("aprovado", "BOOLEAN")],
                 widgets=[("nome", "pagina", True),
                          ("pasta", os.path.join(RAIZ, G.OUTPUT_DIR), False),
                          ("salvar_png", True, False),
                          ("sobrescrever", False, False)],
                 saidas=[("caminho_svg", "STRING")])

    previa = g.no("PreviewImage", (2180, 40), (400, 420),
                  entradas=[("images", "IMAGE")], titulo="Página")

    g.ligar(clip, 0, texto, "clip")
    g.ligar(cena, 0, prompt, "descricao")
    g.ligar(cena, 1, vetor, "nome")
    g.ligar(prompt, 0, texto, "text")
    g.ligar(texto, 0, sampler, "positive")
    g.ligar(texto, 0, zero, "conditioning")
    g.ligar(zero, 0, sampler, "negative")
    g.ligar(unet, 0, sampling, "model")
    g.ligar(sampling, 0, sampler, "model")
    g.ligar(latente, 0, sampler, "latent_image")
    g.ligar(sampler, 0, decode, "samples")
    g.ligar(vae, 0, decode, "vae")
    g.ligar(decode, 0, limpar, "imagem")
    g.ligar(limpar, 0, diag, "imagem")
    g.ligar(limpar, 0, vetor, "imagem")
    g.ligar(limpar, 0, previa, "images")
    g.ligar(diag, 0, vetor, "aprovado")
    g.ligar(diag, 1, laudo, "source")

    return g.json()


NOTA_ILL = """## Illustrious XL v2.0 + KidsIllustration — line art

**Line art é PEDIDO ao modelo, não extraído de imagem colorida depois.**
Custou várias voltas chegar aqui, e o caminho errado parecia estar dando
certo: vetorizar a ilustração colorida e classificar as regiões por
luminância rendia 218 regiões com a maior em 10% da página. Números bons de
uma página horrível — luminância não separa traço escuro de *preenchimento*
escuro, e a água azul virava mancha preta sólida.

As tags que resolvem estão em `ILL_POSITIVO`: `lineart, monochrome,
greyscale, white background, no shading` devolve desenho a tinta já em preto
e branco (saturação média 1,6 de 255 na saída crua). Sem cor para tirar, não
há o que classificar errado.

`solo` e `centered composition` são o que centraliza a personagem; sem elas
ela sai num canto com meia página vazia. E `very thick bold black outlines`
não entra — foi o que quebrou todas as tentativas anteriores.

### Diferenças de arquitetura em relação ao `colorir_pipeline`

- **`CheckpointLoaderSimple`** entrega modelo, CLIP e VAE juntos (é SDXL).
- **Existe prompt negativo** (`cfg=6`), e ele ataca cor e degradê.
- **É modelo de tag (booru)**, não de prosa. Colar o `STYLE_PREFIX` do outro
  workflow aqui devolve uma grade 3x3 de adesivos.
- **Clip skip 2** — é como a LoRA foi treinada.

Daqui para a frente o caminho é o mesmo do Z-Image: limpar, diagnosticar,
vetorizar, e `conversor_linhas.py` depois. Medido em três seeds: 67, 82 e 83
áreas; a de 83 passa em tudo, com a maior região em 16% da página.
"""


def construir_illustrious():
    g = Grafo()

    g.nota((-560, 40), (470, 700), NOTA_ILL)

    ckpt = g.no("CheckpointLoaderSimple", (-60, 40), (400, 98),
                widgets=[("ckpt_name", G.ILL_CKPT, False)],
                saidas=[("MODEL", "MODEL"), ("CLIP", "CLIP"), ("VAE", "VAE")])

    lora = g.no("LoraLoader", (-60, 190), (400, 126),
                entradas=[("model", "MODEL"), ("clip", "CLIP")],
                widgets=[("lora_name", G.ILL_LORA, False),
                         ("strength_model", G.ILL_LORA_FORCA, False),
                         ("strength_clip", G.ILL_LORA_FORCA, False)],
                saidas=[("MODEL", "MODEL"), ("CLIP", "CLIP")])

    skip = g.no("CLIPSetLastLayer", (-60, 360), (400, 58),
                entradas=[("clip", "CLIP")],
                widgets=[("stop_at_clip_layer", G.ILL_CLIP_SKIP, False)],
                saidas=[("CLIP", "CLIP")],
                titulo="Clip skip 2 (como a LoRA foi treinada)")

    pos = g.no("CLIPTextEncode", (420, 40), (460, 340),
               entradas=[("clip", "CLIP")],
               widgets=[("text", G.ILL_POSITIVO, False)],
               saidas=[("CONDITIONING", "CONDITIONING")],
               titulo="Positivo (tags)")

    neg = g.no("CLIPTextEncode", (420, 420), (460, 300),
               entradas=[("clip", "CLIP")],
               widgets=[("text", G.ILL_NEGATIVO, False)],
               saidas=[("CONDITIONING", "CONDITIONING")],
               titulo="Negativo — o que o Z-Image não tinha")

    latente = g.no("EmptyLatentImage", (960, 420), (300, 106),
                   widgets=[("width", G.ILL_LADO, False),
                            ("height", G.ILL_LADO, False),
                            ("batch_size", 1, False)],
                   saidas=[("LATENT", "LATENT")])

    sampler = g.no("KSampler", (960, 40), (320, 262),
                   entradas=[("model", "MODEL"), ("positive", "CONDITIONING"),
                             ("negative", "CONDITIONING"), ("latent_image", "LATENT")],
                   widgets=[("seed", abs(G.SEED_BASE), False),
                            ("control_after_generate", "randomize", False),
                            ("steps", G.ILL_STEPS, False),
                            ("cfg", G.ILL_CFG, False),
                            ("sampler_name", G.ILL_SAMPLER, False),
                            ("scheduler", G.ILL_SCHEDULER, False),
                            ("denoise", 1, False)],
                   saidas=[("LATENT", "LATENT")])

    decode = g.no("VAEDecode", (1360, 40), (240, 46),
                  entradas=[("samples", "LATENT"), ("vae", "VAE")],
                  saidas=[("IMAGE", "IMAGE")])

    limpar = g.no("ColorirLimpar", (1360, 130), (330, 154),
                  entradas=[("imagem", "IMAGE")],
                  widgets=[("limiar", G.BW_THRESHOLD, False),
                           ("abrir_manchas", G.ABRIR_MANCHAS, False),
                           ("erosao", G.EROSAO_TRACO, False),
                           ("nucleo_min", G.NUCLEO_MIN, False)],
                  saidas=[("imagem", "IMAGE"), ("manchas_abertas", "INT")])

    diag = g.no("ColorirDiagnostico", (1360, 330), (340, 202),
                entradas=[("imagem", "IMAGE")],
                widgets=[("limite_fora", G.LIMITE_FORA, False),
                         ("limite_abrangencia", G.LIMITE_ABRANGENCIA, False),
                         ("limite_tinta", G.LIMITE_TINTA, False),
                         ("limite_maior", G.LIMITE_MAIOR, False),
                         ("limite_areas", G.LIMITE_AREAS, False)],
                saidas=[("aprovado", "BOOLEAN"), ("relatorio", "STRING"),
                        ("fora", "FLOAT"), ("maior", "FLOAT"), ("tinta", "FLOAT"),
                        ("areas", "INT"), ("macico", "FLOAT")])

    laudo = g.no("PreviewAny", (1360, 580), (340, 88),
                 entradas=[("source", "*")], titulo="Laudo")

    vetor = g.no("ColorirVetorizar", (1360, 700), (340, 154),
                 entradas=[("imagem", "IMAGE")],
                 entradas_extra=[("aprovado", "BOOLEAN")],
                 widgets=[("nome", "illustrious", False),
                          ("pasta", os.path.join(RAIZ, G.OUTPUT_DIR), False),
                          ("salvar_png", True, False),
                          ("sobrescrever", False, False)],
                 saidas=[("caminho_svg", "STRING")])

    previa = g.no("PreviewImage", (1760, 40), (400, 420),
                  entradas=[("images", "IMAGE")], titulo="Página")

    g.ligar(ckpt, 0, lora, "model")
    g.ligar(ckpt, 1, lora, "clip")
    g.ligar(lora, 1, skip, "clip")
    g.ligar(skip, 0, pos, "clip")
    g.ligar(skip, 0, neg, "clip")
    g.ligar(lora, 0, sampler, "model")
    g.ligar(pos, 0, sampler, "positive")
    g.ligar(neg, 0, sampler, "negative")
    g.ligar(latente, 0, sampler, "latent_image")
    g.ligar(sampler, 0, decode, "samples")
    g.ligar(ckpt, 2, decode, "vae")
    g.ligar(decode, 0, limpar, "imagem")
    g.ligar(limpar, 0, diag, "imagem")
    g.ligar(limpar, 0, vetor, "imagem")
    g.ligar(limpar, 0, previa, "images")
    g.ligar(diag, 0, vetor, "aprovado")
    g.ligar(diag, 1, laudo, "source")

    return g.json()


WORKFLOWS = [
    ("workflow_colorir.json", "colorir_pipeline.json", construir),
    ("workflow_colorir_illustrious.json", "colorir_illustrious.json",
     construir_illustrious),
]


def main():
    aqui = os.path.dirname(os.path.abspath(__file__))
    instalar = "--instalar" in sys.argv
    if instalar and not os.path.isdir(DESTINO_COMFY):
        print(f"!! pasta de workflows do ComfyUI não encontrada: {DESTINO_COMFY}")
        instalar = False

    for local, nome_comfy, construtor in WORKFLOWS:
        destino = os.path.join(aqui, local)
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(construtor(), f, ensure_ascii=False, indent=1)
        print(f"-> {destino}")
        if instalar:
            copia = os.path.join(DESTINO_COMFY, nome_comfy)
            shutil.copy(destino, copia)
            print(f"-> {copia}")


if __name__ == "__main__":
    main()
