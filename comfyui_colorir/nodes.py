# -*- coding: utf-8 -*-
"""Os nos.

Nada de algoritmo aqui: tudo e' delegado para geradesehmo.py, que continua
sendo a fonte de verdade do pipeline (prompts, limites, medicoes). Este
arquivo so' embrulha aquilo em nos do ComfyUI, converte tensor <-> PIL e
escreve arquivo temporario, porque as funcoes de la' trabalham em cima de um
caminho de PNG.

Mexer nos textos ou nos limites: mexa em geradesehmo.py. Os widgets abaixo
apenas nascem com os valores de la' como padrao, e podem ser sobrescritos na
tela sem alterar o script.
"""

import os
import sys
import tempfile

import numpy as np
import torch
from PIL import Image

# geradesehmo.py mora na raiz do projeto, um nivel acima desta pasta.
# realpath, e nao abspath: o ComfyUI carrega esta pasta atraves de um junction
# em custom_nodes, e abspath devolveria o caminho de la' — onde nao existe
# geradesehmo.py nenhum. COLORIR_RAIZ permite apontar a mao se preciso.
RAIZ = os.environ.get("COLORIR_RAIZ") or os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))
)
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import geradesehmo as G  # noqa: E402

CATEGORIA = "colorir"


# ============ tensor <-> PIL ============
def _para_pil(imagem):
    """IMAGE do ComfyUI (tensor [B,H,W,C] em 0..1) -> PIL da primeira imagem."""
    arr = (imagem[0].cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def _para_tensor(pil):
    arr = np.array(pil.convert("RGB")).astype(np.float32) / 255.0
    return torch.from_numpy(arr).unsqueeze(0)


class _Temporario:
    """As funcoes de geradesehmo.py operam sobre um PNG em disco."""

    def __init__(self, pil):
        self.pil = pil

    def __enter__(self):
        fd, self.caminho = tempfile.mkstemp(suffix=".png", prefix="colorir_")
        os.close(fd)
        self.pil.save(self.caminho)
        return self.caminho

    def __exit__(self, *_):
        try:
            os.remove(self.caminho)
        except OSError:
            pass


# ============ 1. cena ============
class ColorirCena:
    """Devolve o texto de uma das cenas ja' escritas em geradesehmo.ANIMALS."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"cena": ([a["name"] for a in G.ANIMALS],)}}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("descricao", "nome")
    FUNCTION = "escolher"
    CATEGORY = CATEGORIA

    def escolher(self, cena):
        for animal in G.ANIMALS:
            if animal["name"] == cena:
                return (animal["subject"], animal["name"])
        raise ValueError(f"cena desconhecida: {cena}")


# ============ 2. prompt ============
class ColorirPrompt:
    """Monta prefixo + cena + composicao + sufixo, na ordem que o batch usa.

    Os tres blocos de estilo aparecem como campos editaveis de proposito: sao
    eles que carregam as restricoes topologicas (contorno fechado, moldura,
    subdivisao) e a ideia e' poder testar variacoes sem editar o script.
    """

    @classmethod
    def INPUT_TYPES(cls):
        multi = {"multiline": True}
        return {
            "required": {
                "descricao": ("STRING", dict(multi, default="", forceInput=False)),
                "prefixo": ("STRING", dict(multi, default=G.STYLE_PREFIX)),
                "composicao": ("STRING", dict(multi, default=G.STYLE_COMPOSICAO)),
                "sufixo": ("STRING", dict(multi, default=G.STYLE_SUFFIX)),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "montar"
    CATEGORY = CATEGORIA

    def montar(self, descricao, prefixo, composicao, sufixo):
        return (f"{prefixo}{descricao}{composicao}{sufixo}",)


# ============ 3. limpeza ============
class ColorirLimpar:
    """Preto e branco puro + esvaziamento das manchas macicas.

    Mesma dupla que o batch roda antes de diagnosticar: `preprocess_bw` tira o
    cinza das bordas. `abrir_manchas` vem DESLIGADO: mancha preta e' tinta, nao
    defeito, e abri-la apaga a parte preta que o desenho deve ter. Ligue so'
    quando o modelo encher um bicho inteiro de preto — e ai' suba o nucleo_min
    junto, para pegar o corpo e nao a pata. Ver o CLAUDE.md.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "imagem": ("IMAGE",),
                "limiar": ("INT", {"default": G.BW_THRESHOLD, "min": 1, "max": 254}),
                "abrir_manchas": ("BOOLEAN", {"default": G.ABRIR_MANCHAS}),
                "erosao": ("INT", {"default": G.EROSAO_TRACO, "min": 3, "max": 31, "step": 2}),
                "nucleo_min": ("INT", {"default": G.NUCLEO_MIN, "min": 0, "max": 50000, "step": 100}),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("imagem", "manchas_abertas")
    FUNCTION = "limpar"
    CATEGORY = CATEGORIA

    def limpar(self, imagem, limiar, abrir_manchas, erosao, nucleo_min):
        with _Temporario(_para_pil(imagem)) as caminho:
            G.preprocess_bw(caminho, threshold=limiar)
            abertas = 0
            if abrir_manchas:
                # geradesehmo le' os dois valores de constantes de modulo;
                # trocar na tela nao deve vazar para o batch, entao restaura.
                erosao_antiga, nucleo_antigo = G.EROSAO_TRACO, G.NUCLEO_MIN
                G.EROSAO_TRACO, G.NUCLEO_MIN = erosao, nucleo_min
                try:
                    abertas = G.abrir_manchas(caminho)
                finally:
                    G.EROSAO_TRACO, G.NUCLEO_MIN = erosao_antiga, nucleo_antigo
            return (_para_tensor(Image.open(caminho)), abertas)


# ============ 4. diagnostico ============
class ColorirDiagnostico:
    """Roda as mesmas checagens do batch e devolve o veredito.

    `aprovado` sai como BOOLEAN para poder alimentar um no de decisao; o
    relatorio sai como texto para ligar num PreviewAny e ler na tela.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "imagem": ("IMAGE",),
                "limite_fora": ("FLOAT", {"default": G.LIMITE_FORA, "min": 0.0, "max": 1.0, "step": 0.01}),
                "limite_abrangencia": ("FLOAT", {"default": G.LIMITE_ABRANGENCIA, "min": 0.0, "max": 1.0, "step": 0.01}),
                "limite_tinta": ("FLOAT", {"default": G.LIMITE_TINTA, "min": 0.0, "max": 1.0, "step": 0.01}),
                "limite_maior": ("FLOAT", {"default": G.LIMITE_MAIOR, "min": 0.0, "max": 1.0, "step": 0.01}),
                "limite_areas": ("INT", {"default": G.LIMITE_AREAS, "min": 0, "max": 500}),
            }
        }

    RETURN_TYPES = ("BOOLEAN", "STRING", "FLOAT", "FLOAT", "FLOAT", "INT", "FLOAT")
    RETURN_NAMES = ("aprovado", "relatorio", "fora", "maior", "tinta", "areas", "macico")
    FUNCTION = "diagnosticar"
    CATEGORY = CATEGORIA
    OUTPUT_NODE = True

    _LIMITES = (
        ("LIMITE_FORA", "limite_fora"),
        ("LIMITE_ABRANGENCIA", "limite_abrangencia"),
        ("LIMITE_TINTA", "limite_tinta"),
        ("LIMITE_MAIOR", "limite_maior"),
        ("LIMITE_AREAS", "limite_areas"),
    )

    def diagnosticar(self, imagem, **limites):
        antigos = {nome: getattr(G, nome) for nome, _ in self._LIMITES}
        for nome, chave in self._LIMITES:
            setattr(G, nome, limites[chave])
        try:
            with _Temporario(_para_pil(imagem)) as caminho:
                (fora, maior, abrangencia, tinta, n), problemas = G.diagnosticar(caminho)
                macico = G.medir_macico(caminho)
        finally:
            for nome, valor in antigos.items():
                setattr(G, nome, valor)

        relatorio = (
            f"fora={fora:.0%}  maior={maior:.0%}  abrangência={abrangencia:.2f}\n"
            f"preto={tinta:.0%}  maciço={macico:.2%}  áreas={n}\n"
        )
        relatorio += "APROVADA\n" if not problemas else "REPROVADA\n" + "".join(
            f"  !! {p}\n" for p in problemas
        )
        print(f"[colorir] {relatorio}")
        return {
            "ui": {"text": [relatorio]},
            "result": (not problemas, relatorio, float(fora), float(maior),
                       float(tinta), int(n), float(macico)),
        }


# ============ 5. vetorizacao ============
class ColorirVetorizar:
    """Grava o SVG que o conversor de linhas consome depois.

    Escreve direto em output_coloring_pages/ do projeto por padrao, que e' a
    pasta que conversor_linhas.py varre. Justamente por escrever na pasta boa,
    tem duas travas:

    - `aprovado` vem do no de diagnostico. Reprovou, nao grava — o batch
      tambem so' converte o que passou, e uma pagina reprovada nao deve virar
      Dart.
    - `sobrescrever` desligado por padrao: com a cena vinda do no "Cena
      pronta" o nome bate com um arquivo que ja' existe, e uma rodada de
      teste apagaria a pagina boa. Sem ele, numera: nome_2, nome_3.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "imagem": ("IMAGE",),
                "nome": ("STRING", {"default": "pagina"}),
                "pasta": ("STRING", {"default": os.path.join(RAIZ, G.OUTPUT_DIR)}),
                "salvar_png": ("BOOLEAN", {"default": True}),
                "sobrescrever": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "aprovado": ("BOOLEAN", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("caminho_svg",)
    FUNCTION = "vetorizar"
    CATEGORY = CATEGORIA
    OUTPUT_NODE = True

    def vetorizar(self, imagem, nome, pasta, salvar_png, sobrescrever, aprovado=None):
        if aprovado is False:
            aviso = "[colorir] página reprovada no diagnóstico — SVG não gravado"
            print(aviso)
            return {"ui": {"text": [aviso]}, "result": ("",)}

        os.makedirs(pasta, exist_ok=True)
        if not sobrescrever:
            base, n = nome, 2
            while os.path.exists(os.path.join(pasta, f"{nome}.svg")):
                nome = f"{base}_{n}"
                n += 1
        png = os.path.join(pasta, f"{nome}.png")
        svg = os.path.join(pasta, f"{nome}.svg")
        _para_pil(imagem).save(png)
        try:
            G.vectorize_to_svg(png, svg)
        except ImportError as erro:
            raise RuntimeError(
                "vtracer não está instalado na venv do ComfyUI. Instale com:\n"
                '  "<ComfyUI>\\ComfyUI\\.venv\\Scripts\\python.exe" -m pip install vtracer'
            ) from erro
        if not salvar_png:
            os.remove(png)
        print(f"[colorir] SVG gravado em {svg}")
        return {"ui": {"text": [svg]}, "result": (svg,)}


NODE_CLASS_MAPPINGS = {
    "ColorirCena": ColorirCena,
    "ColorirPrompt": ColorirPrompt,
    "ColorirLimpar": ColorirLimpar,
    "ColorirDiagnostico": ColorirDiagnostico,
    "ColorirVetorizar": ColorirVetorizar,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ColorirCena": "Colorir · Cena pronta",
    "ColorirPrompt": "Colorir · Montar prompt",
    "ColorirLimpar": "Colorir · Limpar e abrir manchas",
    "ColorirDiagnostico": "Colorir · Diagnóstico",
    "ColorirVetorizar": "Colorir · Vetorizar SVG",
}
