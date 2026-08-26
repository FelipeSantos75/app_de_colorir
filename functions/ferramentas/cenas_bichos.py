# -*- coding: utf-8 -*-
"""Transforma o pacote animalPrompts em cenas no formato de geradesehmo.ANIMALS.

O pacote (prompts_bichos/) traz listas de especie e habitat, uma por linha:

    koala in a tree in the dry forest
    ring tailed lemur on a branch
    red kangaroo in the grassy plains

Isso e' *assunto*, nao prompt. Jogar a linha crua no gerador devolve o bicho
sozinho num campo vazio — exatamente a primeira leva, 11 a 23 areas pintaveis.
O que enche a pagina e' nomear elenco secundario e a QUANTIDADE das miudezas
(ver a secao "Richness" do CLAUDE.md). Este modulo faz esse embrulho: pega a
linha, descobre o bioma pelo lugar, e monta a cena com o elenco e os adereços
daquele bioma.

Uso:

    python functions/ferramentas/cenas_bichos.py --listar 5
    python functions/ferramentas/cenas_bichos.py --bioma neve --listar 3

E de dentro do gerador:

    from functions.ferramentas.cenas_bichos import cenas
    ANIMALS = cenas("mammals_habitats.txt", quantidade=10)
"""

import os
import random
import re
import sys

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts_bichos")

# A linha e' "<bicho> <preposicao> <lugar>". Separar importa: procurar o bioma
# na linha inteira faz "swamp wallaby in the thicket" cair em pantano por causa
# do nome do bicho, nao do lugar.
PREPOSICAO = re.compile(r"^(.*?)\s+\b(in|on|by|at|near|among|over|under)\b\s+(.*)$")

# Ordem importa: 'galho' antes de 'floresta', porque quase todo galho esta' numa
# floresta e o galho manda mais na composicao (ele atravessa a cena).
BIOMAS = [
    ("galho", r"\bbranch\b|\btwig\b"),
    ("neve", r"snow|ice|arctic|tundra|polar|glacier"),
    ("agua", r"underwater|reef|\bsea\b|ocean|coast|river|lake|pond|marsh|swamp|wetland|mangrove"),
    ("monte", r"mountain|rocky|cliff|outcrop|highland|\brock\b"),
    ("deserto", r"desert|arid|\bscrub\b|\bdune\b|semi-desert"),
    ("savana", r"savanna|grassland|plains|prairie|pampas|steppe|meadow|clearing|field"),
    ("ceu", r"sky background|\bflight\b|\bair\b"),
    ("floresta", r"forest|rainforest|woodland|jungle|taiga|thicket|bush|orchard|\btree\b"),
]
BIOMA_PADRAO = "floresta"

# cats_breeds.txt, dogs_breeds.txt e os *_singles trazem so' a especie, sem
# lugar nenhum. Cair no padrao poria um siames no meio do bosque; bicho
# domestico vai para o quintal.
BIOMA_SEM_LUGAR = "quintal"

# Elenco e adereços por bioma. Tudo aqui e' forma fechada de proposito: nada de
# tufo de grama, junco, faisca ou risquinho, que viram traco que nao cerca nada.
# As quantidades sao explicitas porque numero rende mais que adjetivo.
CENARIO = {
    "floresta": {
        "elenco": ["smiling owl", "smiling squirrel", "smiling hedgehog with outlined spines",
                   "smiling little bird", "smiling ladybug"],
        "props": [
            "two closed trees with round crowns divided into outlined leaf clusters",
            "three rounded bushes made of several outlined lobes",
            "five whole rounded leaves of different shapes",
            "four closed mushrooms with outlined dots on their caps",
            "small round berries and pebbles scattered on the ground",
        ],
        "chao": "two overlapping rounded hills behind, forest scene",
    },
    "galho": {
        "elenco": ["smiling butterfly with outlined wing patterns", "smiling ladybug",
                   "smiling little bird", "smiling caterpillar with outlined segments"],
        "props": [
            "one thick branch with outlined bark that crosses the scene and meets the border on both sides",
            "a closed round nest woven from outlined strands with two round eggs inside",
            "eight whole rounded leaves along the branch",
            "three round fruits with outlined stems",
            "small round clouds divided into outlined lobes in the sky",
        ],
        "chao": "two rounded treetops below, seen from above",
    },
    "savana": {
        "elenco": ["smiling little bird", "smiling meerkat", "smiling tortoise with an outlined shell",
                   "smiling butterfly"],
        "props": [
            "three flat topped acacia trees with outlined leaf clusters",
            "five low rounded bushes made of outlined lobes",
            "four rounded closed clouds divided into lobes",
            "six round stones of different sizes on the ground",
            "a closed oval water hole",
        ],
        "chao": "two overlapping rounded hills behind, savanna scene",
    },
    "agua": {
        "elenco": ["smiling fish with rows of outlined scales", "smiling crab with outlined claws",
                   "smiling turtle with an outlined shell", "smiling frog"],
        "props": [
            "five broad closed water plant leaves",
            "eight round bubbles of different sizes",
            "two smiling starfish and three closed shells with outlined ridges",
            "two rounded rocks",
            "small round pebbles resting on the bottom",
        ],
        "chao": "the bottom made of two overlapping rounded mounds, water scene",
    },
    "neve": {
        "elenco": ["smiling baby seal", "smiling snowy owl", "smiling penguin left blank white inside"],
        "props": [
            "two small pine trees with outlined branch layers",
            "six round snowballs of different sizes",
            "three closed cloud shapes",
            "four rounded blocks of ice with outlined edges",
            "small round dots on the snow",
        ],
        "chao": "two rounded snow hills behind, winter scene",
    },
    "monte": {
        "elenco": ["smiling mountain goat", "smiling eagle with rows of outlined feathers",
                   "smiling marmot", "smiling little bird"],
        "props": [
            "four rounded boulders of different sizes with outlined cracks",
            "two small pine trees with outlined branch layers",
            "three rounded closed clouds divided into lobes",
            "five round pebbles on the ground",
            "a closed mountain stream drawn as two curved outlines with round stones in it",
            "three rounded bushes made of several outlined lobes",
        ],
        "chao": "two overlapping rounded mountain ridges behind, mountain scene",
    },
    "deserto": {
        "elenco": ["smiling lizard with rows of outlined scales", "smiling little bird",
                   "smiling tortoise with an outlined shell", "smiling scorpion with outlined segments",
                   "smiling snake coiled into a closed spiral"],
        "props": [
            "three rounded cactus shapes with outlined ribs and round flowers on top",
            "four rounded stones of different sizes",
            "two rounded closed clouds",
            "five small round pebbles on the sand",
            "two closed rock arches with outlined layers",
            "three low rounded desert bushes made of outlined lobes",
            "a round sun with outlined rays drawn as closed triangles",
        ],
        "chao": "two overlapping rounded sand dunes behind, desert scene",
    },
    "quintal": {
        "elenco": ["smiling butterfly with outlined wing patterns", "smiling little bird",
                   "smiling ladybug", "smiling snail with an outlined spiral shell"],
        "props": [
            "five large round flowers with rows of outlined petals on outlined stems",
            "a closed flower pot with outlined rim",
            "two rounded bushes made of several outlined lobes",
            "a closed wooden fence made of rounded outlined planks along the back",
            "four round balls and small round pebbles on the ground",
        ],
        "chao": "a low rounded hill behind the fence, garden scene",
    },
    "ceu": {
        "elenco": ["smiling little bird", "smiling butterfly with outlined wing patterns",
                   "smiling dragonfly with outlined rounded wings", "smiling bee with outlined stripes"],
        "props": [
            "five rounded closed clouds divided into outlined lobes",
            "a round sun with outlined rays drawn as closed triangles",
            "four round balloons with outlined strings",
            "three closed kites with outlined tails",
            "a flock of five small closed bird shapes in the distance",
        ],
        "chao": "rounded hills far below, closing the bottom of the scene",
    },
}


def separar(linha):
    """'koala in a tree in the dry forest' -> ('koala', 'a tree in the dry forest')."""
    m = PREPOSICAO.match(linha.strip())
    if not m:
        return linha.strip(), ""
    return m.group(1), f"{m.group(2)} {m.group(3)}"


def bioma(lugar):
    for nome, padrao in BIOMAS:
        if re.search(padrao, lugar, re.I):
            return nome
    return BIOMA_PADRAO


def slug(bicho):
    return re.sub(r"[^a-z0-9]+", "_", bicho.lower()).strip("_")


def montar(linha, rnd=random):
    """Devolve {'name', 'subject'} no formato que geradesehmo.ANIMALS usa."""
    bicho, lugar = separar(linha)
    chave = bioma(lugar) if lugar else BIOMA_SEM_LUGAR
    cen = CENARIO[chave]

    elenco = rnd.sample(cen["elenco"], min(2, len(cen["elenco"])))
    props = rnd.sample(cen["props"], min(4, len(cen["props"])))

    partes = [
        f"cute smiling {bicho} {lugar}".strip() + ", large in the middle of the page",
        "its body divided by thin outlines into outlined sections, "
        "left blank white inside whatever its real colour",
        f"one {elenco[0]} and one {elenco[1]} at the corners" if len(elenco) > 1
        else f"one {elenco[0]} at the corner",
    ]
    partes += props
    partes.append(cen["chao"])
    return {"name": slug(bicho), "subject": ", ".join(partes), "bioma": chave}


def cenas(arquivos="mammals_habitats.txt", quantidade=None, semente=42,
          filtro_bioma=None):
    """Le um ou mais arquivos do pacote e devolve cenas prontas, sem nome repetido.

    A desduplicacao nao e' zelo: `name` vira o nome do PNG, do SVG e do .dart,
    e o pacote repete especie entre arquivos — `ostrich` esta' em
    birds_singles.txt e em birds_habitats.txt, e sao 688 casos assim. Sem isso,
    gerar de dois arquivos sobrescreve paginas caladamente. Fica a primeira
    ocorrencia, que na ordem dada e' a do arquivo mais especifico que voce
    passou primeiro.
    """
    if isinstance(arquivos, str):
        arquivos = [arquivos]
    rnd = random.Random(semente)

    montadas, vistos = [], set()
    for arquivo in arquivos:
        caminho = os.path.join(PASTA, arquivo)
        for linha in open(caminho, encoding="utf-8"):
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            cena = montar(linha, rnd)
            if cena["name"] in vistos:
                continue
            vistos.add(cena["name"])
            montadas.append(cena)

    if filtro_bioma:
        montadas = [c for c in montadas if c["bioma"] == filtro_bioma]
    if quantidade:
        montadas = rnd.sample(montadas, min(quantidade, len(montadas)))
    return montadas


def _main():
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--arquivo", nargs="+", default=["mammals_habitats.txt"])
    p.add_argument("--listar", type=int, default=3)
    p.add_argument("--bioma", default=None)
    p.add_argument("--semente", type=int, default=42)
    a = p.parse_args()

    for c in cenas(a.arquivo, a.listar, a.semente, a.bioma):
        print(f"\n[{c['bioma']}] {c['name']}")
        print("  " + c["subject"])


if __name__ == "__main__":
    _main()
