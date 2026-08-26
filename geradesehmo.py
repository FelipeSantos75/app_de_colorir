"""
Batch generator para imagens de colorir (line art) usando a API do ComfyUI
+ vetorização automática para SVG usando vtracer.

Requisitos:
    pip install requests vtracer pillow

Workflow: Z-Image-Turbo (UNETLoader + CLIPLoader + VAELoader + ModelSamplingAuraFlow),
espelhando o workflow exportado do ComfyUI.

Uso:
    1. Confirme os nomes de modelo na seção CONFIGURAÇÕES abaixo rodando:
           python comfyui_batch_coloring.py --list-models
    2. Certifique-se de que o ComfyUI esteja rodando
       (padrão local: http://127.0.0.1:8188)
    3. Rode: python comfyui_batch_coloring.py
"""

import time
import uuid
import os
import requests
from PIL import Image

# vtracer so' e' preciso na vetorizacao, e o pacote de nos do ComfyUI
# (comfyui_colorir/) importa este modulo de dentro da venv do ComfyUI, onde
# ele pode nao estar instalado. Import tardio para nao derrubar o resto.

# ============ CONFIGURAÇÕES ============
COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = "output_coloring_pages"

# Modelo: Z-Image-Turbo (carregado em partes, como no seu workflow exportado)
UNET_NAME = "z_image_turbo_bf16.safetensors"
CLIP_NAME = "qwen_3_4b.safetensors"
CLIP_TYPE = "lumina2"
VAE_NAME = "ae.safetensors"
MODEL_SAMPLING_SHIFT = 3

WIDTH = 1024
HEIGHT = 1024
STEPS = 8                # Z-Image-Turbo usa poucos steps (é um modelo "turbo"/destilado)
CFG = 1                  # modelos turbo geralmente usam cfg=1; negative prompt não se aplica
SAMPLER = "res_multistep"
SCHEDULER = "simple"
SEED_BASE = 42          # -1 para seed aleatória a cada imagem
TENTATIVAS = 3          # quantas seeds tentar antes de aceitar uma página com problema
BW_THRESHOLD = 200      # quanto menor, mais linhas "sobrevivem" no preto e branco puro

# Nota: esse workflow não usa um prompt negativo de texto — o "negativo" é a
# própria conditioning positiva zerada (nó ConditioningZeroOut), como no
# workflow que você exportou. É o padrão para modelos turbo/destilados.

# IMPORTANTE — este workflow roda com cfg=1 e ConditioningZeroOut: nao existe
# prompt negativo. Tudo precisa ser dito de forma AFIRMATIVA. "no gaps" tende a
# ser ignorado (ou a virar o proprio conceito); "continuous closed outline"
# funciona. Por isso os textos abaixo descrevem o que a imagem DEVE ter.
#
# O objetivo de cada restricao e' topologico: toda area branca precisa estar
# cercada por preto. O app pinta regiao a regiao, entao um contorno aberto faz
# duas areas virarem uma so' — e um toque pinta as duas. Ver a secao
# "Adding a drawing" no CLAUDE.md.

STYLE_PREFIX = (
    # "coloring book style" na frente e' convencao difundida para este tipo de
    # imagem. Medido em tres cenas do Krea2, mesmas seeds: 78,0 areas sem ele
    # contra 77,7 com — diferenca dentro do ruido, e a imagem sai igual. Nao
    # rende porque a linha seguinte ja' diz "coloring book page". Fica porque
    # nao custa nada e e' o vocabulario que a maioria dos modelos espera.
    "coloring book style, "
    "black and white line art, coloring book page for young children, "
    "clean bold black outlines of uniform thickness, pure white inside every shape, "
    # "closed silhouette" fazia o modelo desenhar o bicho de costas, sem rosto.
    # A ideia e' contorno fechado, nao silhueta - e o rosto precisa ser pedido.
    "every object drawn with one continuous outline that closes back on itself, "
    "each animal seen from the front with a friendly face, two round eyes and a smile, "
    "each outline joins neighbouring outlines so every white area is fully sealed by black lines, "
    "outlines only, everything white except the outlines, no shading, no hatching, "
    "no solid black filled areas, no grey, "
    # O modelo preenche de preto o que e' preto no mundo real (a asa do
    # pinguim, o peito da raposa) e aquela area deixa de ser pintavel.
    "every animal is left blank white inside its outline whatever its real colour, "
    "markings and patches are drawn as outlined shapes rather than filled in, "
    # As partes que o modelo enche de preto sao sempre as mesmas: pata, dentro
    # da orelha, pinta, listra, ponta do rabo. Nomear cada uma custa pouco e
    # foi o que sobrou de mancha macica na leva rica (raposinha, girafa).
    "paws, ear insides, spots and stripes are outlined shapes left white inside "
    "like the rest of the animal, "
    # RIQUEZA - o que separava as nossas paginas de uma pagina comercial nao
    # era o traco, era a subdivisao. Medido contra a referencia
    # (assets/image.svg, sereia): ela tem 60 areas pintaveis e a maior ocupa
    # 20% da pagina; a primeira leva nossa tinha 11-23 areas e a maior chegava
    # a 53%. Uma superficie grande e vazia e' UMA area: a crianca da' um toque
    # e um terco da pagina acabou. Estas tres linhas sozinhas levaram a mesma
    # cena de sereia de 24 para 55 areas, com a mesma seed.
    "every large surface is subdivided by extra outlines into several smaller sections, "
    "hair is drawn as separate curved strands each closed by its own outline, "
    "scales, petals, feathers and leaves are drawn as rows of small outlined shapes, "
)

# A composicao e' a outra metade da riqueza: elenco nos cantos, fundo em
# faixas sobrepostas e miudezas preenchendo os vaos. Sem isso o bicho fica
# sozinho boiando num ceu vazio, que era o retrato da primeira leva.
STYLE_COMPOSICAO = (
    ", rich composition that fills the page without crowding it, "
    "the main character is large and centered and fills most of the height of the page, "
    "two smaller companion creatures, each with its own friendly smiling face, "
    "are placed around it near the corners, "
    "the background is built from two or three overlapping rounded hills or banks, "
    "each one a closed outlined shape, so the background is never one single empty area, "
    "a few small round closed shapes rest in the larger gaps, "
    "leaving calm empty space between the objects, "
    "objects may overlap, the scene continues behind the main character"
)

# O sufixo cuida do fundo, que era o pior vazamento: sem um limite fechado, o
# ceu, o chao e o vao entre os objetos viram uma unica regiao gigante.
# A referencia comercial nao tem moldura e sangra ate a borda - por isso o
# `fora` dela e' 28,9%, contra 17%-19% das paginas ricas nossas. A moldura fica.
STYLE_SUFFIX = (
    ", the entire scene is enclosed by a plain thin rectangular border drawn on the page, "
    "a single continuous ground line spans the full width and touches that border on the left "
    "and on the right, so the sky above and the ground below are each one separate sealed area, "
    "every object sits completely inside the border with a small margin, nothing touches or "
    "crosses the edge of the page, "
    # NADA FLUTUA. Sem isto o modelo entende "one owl on a branch, at the
    # corner" como um galho solto boiando no canto, e espalha pinha e folha no
    # ar. Cada adereco precisa de um lugar onde se apoia.
    "nothing floats in the air, every object rests on the ground, grows out of the "
    "ground, or is attached to something visible in the scene, "
    "any branch is part of a tree that is drawn in the scene, "
    "the leaves match the tree they came from, "
    "each decorative element is a small closed shape resting on the ground or attached to an object, "
    "cartoon style, minimalistic, high contrast, crisp vector-like lines, centered composition"
)

# Cada cena foi reescrita para nao pedir nada que so' exista como traco solto:
# tufos de grama, juncos, flocos em risquinho, linhas de movimento e faiscas
# viram formas fechadas (arbustos arredondados, bolinhas, folhas inteiras).
# Onde o bicho e' preto no mundo real (pinguim), o pedido diz explicitamente
# que ele e' branco com contorno - senao o modelo preenche a asa de preto e
# aquela area deixa de ser pintavel.
#
# Cada cena tambem nomeia o elenco secundario e a QUANTIDADE das miudezas.
# Pedir "garden scene" devolve um coelho sozinho num campo vazio; pedir cinco
# flores, tres cogumelos, dois passaros e duas joaninhas devolve a pagina
# cheia. O numero importa mais que o adjetivo.
ANIMALS = [
    # As contagens abaixo levaram um corte de ~30% (media de 17,3 itens
    # contados por cena para ~12). A leva anterior ficava caotica: elemento
    # demais competindo por espaco, e o desenho perdia respiro. O elenco de
    # dois coadjuvantes fica — e' o que segura a riqueza e o que evita a
    # criatura hibrida (ver "Richness" no CLAUDE.md); quem sai e' miudeza.
    {"name": "sereia_fundo_mar", "subject": "cute smiling mermaid girl floating in the middle of the page, her long wavy hair drawn as several separate curved strands, her fish tail covered in rows of outlined scales, a shell top drawn as two outlined shells, two round smiling jellyfish with outlined tentacles in the upper corners, two small smiling crabs with outlined claws on the sea floor in the lower corners, one smiling starfish resting on the sand, six round bubbles of different sizes floating in the water, three broad closed seaweed leaves growing from the sea floor, a rounded sand dune making the sea floor, underwater scene"},
    {"name": "coelhinho_jardim", "subject": "cute smiling baby rabbit sitting in the middle of the page, its ears and chest divided by thin outlines into separate sections, one smiling bird standing on the ground in a corner and one smiling ladybug resting on a flower petal, four large round flowers with rows of outlined petals on outlined stems rooted in the ground, two rounded mushrooms with outlined dots on their caps growing from the ground, one rounded bush made of several outlined lobes growing from the ground, garden scene"},
    {"name": "ursinho_floresta", "subject": "cute smiling baby bear hugging a wide tree trunk with outlined bark sections, the trunk standing on the ground line and its round crown divided into several outlined leaf clusters, one smiling owl perched on a thick branch of that same tree and one smiling squirrel sitting on the ground at the foot of the trunk, three closed pinecone shapes lying on the ground beside the trunk, two rounded bushes made of several outlined lobes growing from the ground, three whole rounded leaves lying on the ground, matching the leaves of the crown, forest scene"},
    {"name": "passarinho_galho", "subject": "cute smiling little bird with rows of outlined feathers on its wing, perched on one thick branch that crosses the scene and meets the border on both sides, a closed round nest woven from outlined strands with two round eggs inside, one smiling butterfly and one smiling ladybug at the corners, five whole rounded leaves growing from that same branch, two round flowers with outlined petals rooted in the ground below, small round clouds divided into outlined lobes in the sky"},
    {"name": "peixinho_mar", "subject": "cute smiling fish with a rounded body, rows of outlined scales and outlined fins, in the middle of the page, one smiling seahorse and one smiling octopus with outlined tentacles at the corners, three broad closed seaweed leaves growing from the sea floor, one rounded coral divided into outlined branches, five round bubbles of different sizes, one smiling starfish and two closed shells with outlined ridges resting on the sand, the sea floor made of two overlapping rounded mounds, underwater scene"},
    {"name": "elefantinho_savana", "subject": "cute smiling baby elephant standing in the middle of the page, its ears and blanket divided by thin outlines into outlined sections, one smiling giraffe whose spots are small outlined patches left white inside and one smiling zebra whose stripes are outlined bands left white inside at the corners, a round striped ball resting on the ground beside the elephant, one smiling little bird perched on a rounded rock that sits on the ground, three rounded closed clouds divided into lobes in the sky, three flat topped acacia trees with outlined leaf clusters standing on the ground line, four low rounded bushes made of outlined lobes growing from the ground, savanna scene"},
    {"name": "gatinho_janela", "subject": "cute smiling kitten sitting inside a rectangular window frame divided into outlined panes, its chest and paws marked with thin outlines, two curtains hanging as closed shapes with rows of outlined folds, a flower pot resting on the window sill with two round flowers with outlined petals growing out of it, one smiling bird perched on the window sill outside, a round moon and three round stars in the sky outside, cozy scene"},
    {"name": "pinguim_neve", "subject": "cute smiling baby penguin standing in the middle of the page, the penguin's body and wings blank white inside with only a thin outline around them and a thin outlined belly patch, one smiling baby seal and one smiling snowy owl at the corners, a closed dome igloo built from rows of outlined blocks with a rounded arch doorway, two rounded snow hills behind, four round snowballs resting on the snow, two closed cloud shapes in the sky, winter scene"},
    {"name": "esquilinho_outono", "subject": "cute smiling squirrel holding a round acorn, its tail divided into rows of outlined fur sections, sitting on one thick branch with outlined bark that meets the border on both sides, in the bottom left corner one smiling hedgehog with outlined spines, alone, and in the bottom right corner one smiling little bird perched on a stone, alone, six whole rounded autumn leaves of different shapes, some resting on the branch and the rest lying on the ground below, two more round acorns with outlined caps lying on the ground"},
    {"name": "sapinho_lagoa", "subject": "cute smiling little frog sitting on a round lily pad with outlined veins, floating on a closed oval pond, its belly marked with a thin outlined patch, one smiling dragonfly with outlined rounded wing patterns and one smiling snail with an outlined spiral shell at the corners, three more round lily pads and two round water lily flowers with rows of outlined petals, four broad closed leaves at the pond edge, pond scene"},
    {"name": "raposinha_campo", "subject": "cute smiling baby fox sitting in the middle of the page, the whole fox is blank white inside, its four paws, the insides of its ears and the tip of its tail are outlined shapes left white inside exactly like the rest of its body, in the bottom left corner one smiling little bird standing on a stone, alone, and in the bottom right corner one smiling hedgehog with outlined spines, alone, four round wildflowers with rows of outlined petals on outlined stems rooted in the ground, two rounded bushes made of several outlined lobes growing from the ground, one closed tree with a round crown divided into outlined leaf clusters standing on the ground line, two rounded clouds divided into lobes in the sky, meadow scene"},
]


# NENHUM limite acima detecta DEFORMIDADE, e deformidade e' o unico defeito
# que nao tem tolerancia. Um esquilo que virou borrao com cara de sapo passa
# em `fora`, em `maior`, em `preto` e em `areas` sem tocar em nada — as quatro
# medidas sao topologicas e estatisticas, e nao sabem o que e' um esquilo.
# A defesa e' anterior: escolher modelo e prompt que desenhem o bicho certo, e
# OLHAR a pagina antes de aceita-la. Nao existe numero para isso aqui.

# ============ LoRA DE TRACO NA TRILHA Z-IMAGE ============
# LineDrawing03_CE, treinada com ai-toolkit em cima do Z-Image Turbo. Ao
# contrario da KidsIllustration (que era SDXL e teve 2958 de 2958 chaves
# recusadas), esta aplica inteira: 0 recusas no log. O ComfyUI remapeia o
# `attention.qkv` fundido do modelo para os `to_q/to_k/to_v` da LoRA.
#
# So' tem pesos de difusao, entao carrega com LoraLoaderModelOnly — o CLIP
# nao e' tocado.
# Segunda LoRA de Z-Image, treinada especificamente em livro de colorir
# (ai-toolkit, 1000 passos). Chaves identicas as da LineDrawing, entao aplica
# inteira: 0 recusas. Nao serve no Krea2 — la' as chaves casam 0%, porque a
# arquitetura e' outra (`blocks` contra `layers`).
#
# Medido em raposinha/gatinho/elefantinho, forca 1,0 contra 0,8: 1,0 vence nas
# tres em numero de areas. O ganho principal e' tinta, 12%-15% contra os 22%
# do Krea2 — traco fino e uniforme sem perder area.
REDMOND_LORA = "[ZImage.Turbo]ColoringBook_Redmond.safetensors"
REDMOND_FORCA = 1.0
REDMOND_GATILHO = "Coloring Book. ColoringBookAF, "

ZIMG_LORA = "LineDrawing03_CE_ZIMGT_AIT5k.safetensors"
ZIMG_LORA_FORCA = 1.0
# Palavra-gatilho da LoRA, do metadata de treino (pasta 1_lndrwngCE_style).
ZIMG_LORA_GATILHO = "lndrwngCE_style, "


# ============ TRILHA KREA 2 TURBO ============
# SOBRE PROMPT NEGATIVO: nao existe util aqui, e nao e' por falta de tentar.
# Em cfg=1 o negativo e' matematicamente ignorado (cfg=1 significa
# condicional puro), entao qualquer texto no slot negativo nao faz nada — o
# ConditioningZeroOut esta' la' so' para preencher a entrada. Subir o cfg faz
# o negativo passar a valer e o modelo turbo desandar. Medido na raposinha,
# mesma seed, com um negativo de livro de colorir:
#
#   cfg 1,0   73 areas  23% tinta   (identico a sem negativo: ele nao age)
#   cfg 1,5   76 areas  24% tinta   OK, sem ganho mensuravel
#   cfg 2,5   34 areas  35% tinta   patas pretas de volta, traco pesado
#   cfg 4,0    6 areas  fora=65%    desmonta
#
# Ou seja: as restricoes continuam tendo que ser afirmativas no positivo,
# como na trilha Z-Image.
# Terceiro modelo. Como o Z-Image e' carregado em partes (UNET + CLIP + VAE
# separados) e roda em cfg=1 com ConditioningZeroOut — nao existe prompt
# negativo. Mas o text encoder e' outro: Qwen3-VL-4B, e o Krea2 consome um
# empilhamento de 12 camadas dele (12 x 2560 = 30720 features). Passar o
# Qwen3 puro do Z-Image da' erro explicito de dimensao; tem que ser o VL.
#
# E' modelo de PROSA: o template do encoder pede "describe the image by
# detailing the color, shape, size, texture, quantity, spatial relationships".
# Os mesmos ANIMALS da trilha Z-Image servem sem reescrever nada.
#
# Parametros do template oficial do ComfyUI (image_krea2_turbo_t2i.json).
KREA_UNET = "krea2Turbo_v10.safetensors"
KREA_CLIP = "qwen3vl_4b_fp8_scaled.safetensors"
KREA_CLIP_TIPO = "krea2"
KREA_VAE = "qwen_image_vae.safetensors"
KREA_STEPS = 8
KREA_CFG = 1.0
KREA_SAMPLER = "euler"
KREA_SCHEDULER = "simple"
KREA_LADO = 1024

# A LoRA LineDrawing de Krea2 existe e aplica inteira (0 recusas), mas NAO
# entra por padrao: ela desenha pelo e sombreado a lapis, 19,9% da pagina
# vira cinza, e o pelo e' traco solto que nao cerca nada. Medido na mesma
# cena e seed: sem ela 54 areas, com ela 7. Baixar o limiar ate' 60 nao
# recupera — nao e' o limiar, e' que nao ha' regiao fechada para achar.
KREA_LORA = "LineDrawing03_CE_Krea2_AIT4k.safetensors"
KREA_LORA_FORCA = 0.0

# ============ TRILHA ILLUSTRIOUS (SDXL) — experimental ============
# Nada abaixo e' usado pelo batch: `main()` continua no Z-Image-Turbo, que e'
# o que produziu as 11 paginas aprovadas em output_coloring_pages/. Estas
# constantes alimentam o segundo workflow do ComfyUI
# (comfyui_colorir/workflow_colorir_illustrious.json).
#
# Illustrious XL v2.0 e' SDXL, e muda tres coisas de uma vez:
#
#  1. CheckpointLoaderSimple no lugar de UNET+CLIP+VAE separados.
#  2. cfg de verdade (6, nao 1), entao EXISTE PROMPT NEGATIVO. Toda a
#     ginastica de dizer as coisas de forma afirmativa deixa de ser
#     necessaria nesta trilha — "solid black fill" vai no negativo.
#  3. E' modelo de tag (booru), nao de prosa. Isto nao e' detalhe de estilo:
#     jogar o STYLE_PREFIX inteiro nele devolveu uma GRADE 3x3 de adesivos,
#     nao uma pagina. As tags abaixo sao a reescrita das mesmas restricoes.
#
# A LoRA KidsIllustration e' SDXL 1.0, dim/alpha 32, treinada em 68 imagens
# com tags de anthro (bicho vestido) e clip skip 2 — dai ILL_CLIP_SKIP.
#
# MEDIDO (cena da sereia, seed 4242, sempre com abrir_manchas depois):
#
#   prompt de tag, LoRA 0.8         fora=85%  maior=1%   areas=26  lindo e inutil
#   idem, sem LoRA                  fora=29%  maior=32%  areas=24
#   nosso STYLE_PREFIX em prosa     fora=1%   maior=42%  areas=14  virou grade
#   tag + traco grosso + anti-detalhe  fora=2%   maior=46%  areas=60  <- ILL_POSITIVO
#   idem + faixas de fundo          fora=0%   maior=24%  areas=59  fecha, mas feio
#
# O compromisso e' direto e ainda nao esta' resolvido: solto o modelo desenha
# coral, peixe e moldura decorativa muito acima do Z-Image, e a pagina fica
# 85% aberta (um toque pinta tudo). Apertado o bastante para fechar, o
# negativo anti-detalhe leva junto a beleza que motivou a troca. O padrao
# abaixo e' o melhor equilibrio medido, e ainda reprova no diagnostico por
# excesso de tinta e por uma unica area de agua atravessando a cena.
ILL_CKPT = "illustriousXLV20_v20Stable.safetensors"
ILL_LORA = "KidsIllustration.safetensors"
ILL_LORA_FORCA = 0.8
ILL_CLIP_SKIP = -2      # a LoRA foi treinada em clip skip 2
ILL_STEPS = 28
ILL_CFG = 6.0
ILL_SAMPLER = "euler_ancestral"
ILL_SCHEDULER = "normal"
ILL_LADO = 1024

# PEDIR line art, nao descolorir depois. Custou varias voltas chegar aqui.
#
# O que nao funciona: gerar a ilustracao colorida e reduzir para preto e
# branco. Nem por limiar de luminancia (o pastel vira preto junto com o
# contorno) nem por classificacao das regioes vetorizadas — e essa segunda
# falha e' instrutiva, porque *parecia* boa: 218 regioes, maior com 10% da
# pagina. Sao numeros bons de uma pagina horrivel. Luminancia nao distingue
# traco escuro de PREENCHIMENTO escuro: a agua azul (luminancia 69) e a rocha
# (135) foram classificadas como tinta e viraram mancha preta solida. A
# informacao para separar as duas coisas nao esta' na cor.
#
# O que funciona: as tags de line art do booru. 'lineart, monochrome,
# greyscale, white background, no shading' devolve desenho a tinta ja' em
# preto e branco — saturacao media 1,6 de 255 na saida crua. Sem cor para
# tirar, o problema de classificacao deixa de existir.
#
# Duas tags fazem a composicao: 'solo' e 'centered composition'. Sem elas a
# sereia sai jogada num canto com meia pagina vazia.
#
# E 'very thick bold black outlines' NAO entra. Foi o que quebrou todas as
# tentativas anteriores — empurrado forte, o modelo para de desenhar e
# devolve manchas.
# PEDIR line art, nao descolorir depois. Custou varias voltas chegar aqui.
#
# O que nao funciona: gerar a ilustracao colorida e reduzir para preto e
# branco. Nem por limiar de luminancia (o pastel vira preto junto com o
# contorno) nem por classificacao das regioes vetorizadas — e essa segunda
# falha e' instrutiva, porque *parecia* boa: 218 regioes, maior com 10% da
# pagina. Sao numeros bons de uma pagina horrivel. Luminancia nao distingue
# traco escuro de PREENCHIMENTO escuro: a agua azul (luminancia 69) e a rocha
# (135) foram classificadas como tinta e viraram mancha preta solida.
#
# O que funciona: as tags de line art do booru. Saida crua com saturacao
# media 1,6 de 255 — ja' vem em preto e branco, sem cor para tirar.
#
# 'solo' e 'centered composition' sao o que centraliza a personagem; sem elas
# ela sai num canto com meia pagina vazia. E 'very thick bold black outlines'
# NAO entra: empurrado forte, o modelo para de desenhar e devolve manchas.
ILL_ESTILO = (
    "coloring book page, lineart, monochrome, greyscale, white background, "
    "black and white, no shading, no screentone, clean even lines, no fill, "
    "solo, centered composition, large in the middle of the frame, "
    "full body, facing viewer, smile, "
)

# O sufixo faz o mesmo servico que o STYLE_SUFFIX faz na trilha do Z-Image:
# fecha o fundo. Sem a moldura e a linha de chao, ceu e chao viram uma regiao
# unica que um toque resolve.
ILL_SUFIXO = (
    ", rounded hills across the bottom touching the frame on both sides, "
    "decorative rectangular border frame around the whole page"
)

ILL_NEGATIVO = (
    "color, colored, colorful, gradient, soft shading, shadow, screentone, hatching, "
    "grey fill, painted, airbrush, blurry, glow, photo, realistic, 3d, "
    "text, watermark, signature, multiple views, cropped, off-center"
)

# As mesmas 11 cenas do ANIMALS, reescritas em tag. Os nomes batem de
# proposito: o resto do pipeline (conversor, registro no library) nao precisa
# saber por qual modelo a pagina passou. O elenco e as quantidades continuam
# nomeados, que e' o que enche a pagina — ver "Richness" no CLAUDE.md.
ILL_CENAS = [
    # Nome de ESPECIE, tirado de functions/ferramentas/prompts_bichos/. "chibi
    # baby bear" e' um conceito difuso; "black bear" e' um conceito que o
    # modelo tem. Peixe e sapo nao estao no pacote (ele e' mamifero, ave, gato
    # e cachorro), entao ali a especie foi escolhida a mao.
    {"name": "sereia_fundo_mar", "subject": "chibi mermaid girl, long wavy hair, fish tail with scales, shell top, underwater, two jellyfish, two crabs, starfish, seashells, round bubbles, coral and seaweed along the bottom edge"},
    {"name": "coelhinho_jardim", "subject": "common rabbit in a meadow, five round flowers, three mushrooms, two round bushes, one house wren, one ladybug, one butterfly, round pebbles on the ground"},
    {"name": "ursinho_floresta", "subject": "black bear cub in a forest, hugging a tree trunk, one tawny owl, one gray squirrel, four pinecones, three round bushes, five rounded leaves, round berries on the ground"},
    {"name": "passarinho_galho", "subject": "house wren perched on a thick branch crossing the frame, round nest with two eggs, one butterfly, one ladybug, eight rounded leaves, three round flowers, rounded clouds"},
    {"name": "peixinho_mar", "subject": "clownfish underwater, one seahorse, one octopus, five broad seaweed leaves, two corals, eight round bubbles, two starfish, three seashells on the sand"},
    {"name": "elefantinho_savana", "subject": "african elephant calf in the savanna, one giraffe, one plains zebra, one small bird on a rock, four rounded clouds, three acacia trees, five round bushes, six round stones"},
    {"name": "gatinho_janela", "subject": "british shorthair kitten sitting in a rectangular window frame, two curtains with folds, flower pot with three round flowers, one house wren outside, round moon and five stars, rooftops in the distance"},
    {"name": "pinguim_neve", "subject": "emperor penguin chick on the snow, one baby harp seal, one snowy owl, dome igloo with an arch doorway, two pine trees, six round snowballs, three rounded clouds"},
    {"name": "esquilinho_outono", "subject": "eurasian red squirrel on a thick branch crossing the frame, holding an acorn, one european hedgehog in the bottom left corner, one house wren in the bottom right corner, eight rounded autumn leaves, three acorns, two round bushes"},
    {"name": "sapinho_lagoa", "subject": "green tree frog on a round lily pad, oval pond, one dragonfly, one garden snail with a spiral shell, four lily pads, three water lily flowers, five broad leaves at the pond edge, round pebbles"},
    {"name": "raposinha_campo", "subject": "red fox cub in a meadow, one house wren in the bottom left corner, one european hedgehog in the bottom right corner, one butterfly, six round wildflowers, three round bushes, two round trees, three rounded clouds"},
]

# NENHUM limite acima detecta DEFORMIDADE, e deformidade e' o unico defeito
# que nao tem tolerancia. Um esquilo que virou borrao com cara de sapo passa
# em `fora`, em `maior`, em `preto` e em `areas` sem tocar em nada — as quatro
# medidas sao topologicas e estatisticas, e nao sabem o que e' um esquilo.
# A defesa e' anterior: escolher modelo e prompt que desenhem o bicho certo, e
# OLHAR a pagina antes de aceita-la. Nao existe numero para isso aqui.

ILL_POSITIVO = ILL_ESTILO + ILL_CENAS[0]["subject"] + ILL_SUFIXO

# ============ WORKFLOW (formato API do ComfyUI, espelhando o export do Z-Image-Turbo) ============
def build_workflow(positive_prompt, seed):
    return {
        "clip_loader": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": CLIP_NAME,
                "type": CLIP_TYPE,
                "device": "default",
            },
        },
        "vae_loader": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": VAE_NAME},
        },
        "unet_loader": {
            "class_type": "UNETLoader",
            "inputs": {"unet_name": UNET_NAME, "weight_dtype": "default"},
        },
        "model_sampling": {
            "class_type": "ModelSamplingAuraFlow",
            "inputs": {"shift": MODEL_SAMPLING_SHIFT, "model": ["unet_loader", 0]},
        },
        "positive_prompt": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": positive_prompt, "clip": ["clip_loader", 0]},
        },
        "negative_zero": {
            "class_type": "ConditioningZeroOut",
            "inputs": {"conditioning": ["positive_prompt", 0]},
        },
        "empty_latent": {
            "class_type": "EmptySD3LatentImage",
            "inputs": {"width": WIDTH, "height": HEIGHT, "batch_size": 1},
        },
        "sampler": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": STEPS,
                "cfg": CFG,
                "sampler_name": SAMPLER,
                "scheduler": SCHEDULER,
                "denoise": 1,
                "model": ["model_sampling", 0],
                "positive": ["positive_prompt", 0],
                "negative": ["negative_zero", 0],
                "latent_image": ["empty_latent", 0],
            },
        },
        "vae_decode": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["sampler", 0], "vae": ["vae_loader", 0]},
        },
        "save_image": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "coloring", "images": ["vae_decode", 0]},
        },
    }


# ============ FUNÇÕES DE COMUNICAÇÃO COM O COMFYUI ============
def queue_prompt(workflow):
    client_id = str(uuid.uuid4())
    payload = {"prompt": workflow, "client_id": client_id}
    resp = requests.post(f"{COMFYUI_URL}/prompt", json=payload)
    if resp.status_code != 200:
        # O ComfyUI manda o motivo exato do erro no corpo da resposta
        # (node_errors indica qual nó/campo reprovou na validação).
        try:
            print("Resposta de erro do ComfyUI:")
            print(resp.json())
        except ValueError:
            print("Resposta de erro do ComfyUI (texto bruto):", resp.text)
        resp.raise_for_status()
    return resp.json()["prompt_id"]


def list_available_models():
    """Consulta o ComfyUI e mostra os nomes exatos de UNET/CLIP/VAE disponíveis."""
    checks = [
        ("UNETLoader", "unet_name", UNET_NAME),
        ("CLIPLoader", "clip_name", CLIP_NAME),
        ("VAELoader", "vae_name", VAE_NAME),
    ]
    for node_type, field, configured in checks:
        resp = requests.get(f"{COMFYUI_URL}/object_info/{node_type}")
        resp.raise_for_status()
        options = resp.json()[node_type]["input"]["required"][field][0]
        marker = "OK" if configured in options else "NÃO ENCONTRADO"
        print(f"\n{node_type} ({field}) — configurado: '{configured}' [{marker}]")
        for name in options:
            print(" -", name)


def wait_for_completion(prompt_id, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
        history = resp.json()
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(2)
    raise TimeoutError(f"Geração {prompt_id} não terminou a tempo")


def download_image(filename, subfolder, folder_type):
    params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    resp = requests.get(f"{COMFYUI_URL}/view", params=params)
    resp.raise_for_status()
    return resp.content


# ============ PÓS-PROCESSAMENTO ============
def preprocess_bw(png_path, threshold=BW_THRESHOLD):
    """Converte para preto e branco puro (sem tons de cinza) antes de vetorizar.
    Isso deixa a vetorização muito mais limpa mesmo se o modelo gerar leves
    tons de cinza nas bordas."""
    img = Image.open(png_path).convert("L")
    bw = img.point(lambda p: 255 if p > threshold else 0)
    bw.convert("RGB").save(png_path)


def abrir_manchas(png_path):
    """Esvazia manchas pretas macicas, deixando so' o contorno delas.

    O modelo tem prior visual mais forte que o prompt em algumas partes: a
    raposa sai de meia preta e ponta de orelha preta em toda seed que se
    tente, a asa do pinguim idem. Preto macico nao e' pintavel — a crianca
    toca e nada acontece.

    Erodir o preto derruba o traco (~7px) e deixa so' o miolo das manchas;
    pintar esse miolo de branco converte a mancha num anel de ~4px, que e'
    exatamente o contorno fechado que o conversor precisa. A area vira
    pintavel em vez de morta.

    Devolve quantas manchas foram abertas.
    """
    from PIL import ImageDraw, ImageFilter

    img = Image.open(png_path).convert("L").point(lambda v: 0 if v < 128 else 255)
    nucleo = img.filter(ImageFilter.MaxFilter(EROSAO_TRACO))
    # nucleo: 255 onde sobrou preto depois da erosao
    mapa = nucleo.point(lambda v: 255 if v < 128 else 0).convert("P")
    largura, altura = mapa.size
    pixels = mapa.load()

    grandes = []
    marca = 1
    restante = mapa.histogram()[255]
    for y in range(altura):
        for x in range(largura):
            if pixels[x, y] == 255:
                ImageDraw.floodfill(mapa, (x, y), marca)
                agora = mapa.histogram()[255]
                if restante - agora >= NUCLEO_MIN:
                    grandes.append(marca)
                restante = agora
                marca += 1
                if marca > 250:
                    break
        if marca > 250:
            break

    if not grandes:
        return 0

    vazar = mapa.point(lambda v: 255 if v in grandes else 0).convert("L")
    img.paste(255, mask=vazar)
    img.convert("RGB").save(png_path)
    return len(grandes)


# A regiao "de fora" e' a que se alcanca a partir do canto da pagina sem
# cruzar nenhuma linha. Com a moldura fechada ela e' so' a margem (12%-25%
# medidos); sem moldura ela engole ceu, chao e o miolo dos objetos (58%-62%
# na primeira leva). E' esse numero que diz se um toque pinta a pagina toda.
LIMITE_FORA = 0.30

# Uma regiao interna legitima pode ser grande — o ceu sozinho da' uns 45%.
# O que denuncia fusao e' ela cobrir a cena inteira nos dois eixos.
LIMITE_ABRANGENCIA = 0.88

# Um bloco preto grande demais nao e' contorno, e' area preenchida: aquele
# pedaco do desenho deixa de ser pintavel (as asas do pinguim da primeira leva).
LIMITE_TINTA = 0.25

# RIQUEZA — os dois limites abaixo nao falam de vazamento, falam de pagina
# pobre. Uma pagina pode estar perfeitamente fechada e ainda assim ser chata
# de pintar: um bicho sozinho no meio de um ceu vazio.
#
# Referencia medida (assets/image.svg, a sereia comercial): 60 areas, maior
# ocupando 20% da pagina. Primeira leva nossa: 11-23 areas, maior de 17% a
# 53%. Leva rica, mesma seed: 55-64 areas, maior de 18% a 25%.
#
# Se a maior area passa de ~28% da pagina, sobrou um vazio grande demais —
# um toque so' resolve um quarto do desenho.
LIMITE_MAIOR = 0.35

# Menos de 35 areas nao e' uma cena, e' um bicho recortado. Todas as paginas
# da primeira leva reprovariam aqui, e e' exatamente esse o ponto.
LIMITE_AREAS = 15

# Mancha preta macica NAO e' defeito, e por isso nao ha' LIMITE_MACICO: a
# pata da raposa, a pinta da girafa e a asa do pinguim sao tinta, do mesmo
# jeito que o contorno e' tinta. O `canvas.dart` ja' trata isso — shape com
# `colorable: false` deixa o toque passar para a regiao debaixo, entao area
# preta nao e' area perdida, e' desenho.
#
# `medir_macico` continua existindo porque o numero e' informativo (aparece no
# print de cada pagina) e porque `abrir_manchas` precisa do mesmo calculo.
# Erodindo o preto com raio 9 o traco (uns 7px a 1024) some e so' sobra o que
# e' macico. Para referencia: paginas sem preenchimento ficam entre 0,04% e
# 0,46%; a raposinha, com as quatro patas pretas, deu 1,37%.
EROSAO_TRACO = 9

# `abrir_manchas` esvazia mancha, nao olho. Medido nos nucleos (o que sobra
# depois de erodir com EROSAO_TRACO): as patas pretas da raposa dao 2724 a
# 6161 px; o maior olho legitimo da leva inteira, o do pinguim, da 512. O piso
# no meio dessa folga pega pata, asa e pinta sem tocar em olho nem focinho.
#
# 1200 ainda esvaziava o olho grande do sapo (nucleo ~1300). Olho preto e'
# desejavel, entao o piso fica acima do maior olho visto e bem abaixo da
# menor pata: nada entre 512 e 2724 aparece na leva atual.
NUCLEO_MIN = 2000

# Desligado por padrao: abrir a mancha apaga justamente a parte preta que o
# desenho deve ter. Vale ligar num caso so' — quando o modelo preenche um
# bicho INTEIRO de preto e nao sobra regiao nenhuma ali. Nesse caso suba
# tambem o NUCLEO_MIN, para pegar o corpo e nao a pata.
ABRIR_MANCHAS = False


def medir_vazamento(png_path):
    """Diagnostica se as areas do desenho estao fechadas.

    Devolve (fora, maior_interna, abrangencia, tinta, n_areas), todos em
    fracao da pagina, exceto n_areas:

      fora          — regiao alcancavel do canto; grande = contorno aberto
      maior_interna — maior area fechada; grande sozinho e' aceitavel
      abrangencia   — quanto da cena a maior area interna cobre nos dois
                      eixos; perto de 1 significa que ela fundiu tudo
      tinta         — fracao preta da pagina; alta = preenchimento solido
    """
    from PIL import ImageDraw

    img = Image.open(png_path).convert("L")
    img = img.point(lambda p: 255 if p > 128 else 0).convert("P")
    largura, altura = img.size
    total = largura * altura
    pixels = img.load()

    tinta = img.histogram()[0] / total

    # 1 marca tudo que se alcanca a partir do canto sem cruzar uma linha preta.
    ImageDraw.floodfill(img, (0, 0), 1)
    fora = img.histogram()[1] / total

    # O que sobrou de branco sao as areas realmente fechadas.
    marcas = []
    marca = 10
    for y in range(altura):
        for x in range(largura):
            if pixels[x, y] == 255:
                ImageDraw.floodfill(img, (x, y), marca)
                marcas.append(marca)
                marca += 1
                if marca > 240:
                    break
        if marca > 240:
            break

    hist = img.histogram()
    internas = [m for m in marcas if hist[m] > total * 0.0004]
    if not internas:
        return fora, 0.0, 0.0, tinta, 0

    maior = max(internas, key=lambda m: hist[m])
    caixa = img.point(lambda v, m=maior: 255 if v == m else 0).convert("L").getbbox()
    abrangencia = min(
        (caixa[2] - caixa[0]) / largura,
        (caixa[3] - caixa[1]) / altura,
    )
    return fora, hist[maior] / total, abrangencia, tinta, len(internas)


def medir_macico(png_path):
    """Fracao da pagina que e' preto solido, e nao traco.

    Erode o preto: o contorno desaparece, o preenchimento sobrevive.
    """
    from PIL import ImageFilter

    img = Image.open(png_path).convert("L").point(lambda v: 0 if v < 128 else 255)
    largura, altura = img.size
    # MaxFilter num canal onde preto=0 dilata o branco, ou seja, erode o preto.
    erodida = img.filter(ImageFilter.MaxFilter(EROSAO_TRACO))
    return erodida.histogram()[0] / (largura * altura)


def diagnosticar(png_path):
    """Devolve (metricas, lista_de_problemas) para uma pagina gerada."""
    fora, maior, abrangencia, tinta, n = medir_vazamento(png_path)
    problemas = []
    if fora > LIMITE_FORA:
        problemas.append(f"fundo aberto ({fora:.0%} da página num toque só)")
    if abrangencia > LIMITE_ABRANGENCIA:
        problemas.append(f"uma área cobre a cena inteira ({abrangencia:.0%})")
    if tinta > LIMITE_TINTA:
        problemas.append(f"preenchimento sólido demais ({tinta:.0%} de preto)")
    if maior > LIMITE_MAIOR:
        problemas.append(f"vazio grande demais (maior área = {maior:.0%} da página)")
    if n < LIMITE_AREAS:
        problemas.append(f"página pobre: só {n} áreas para colorir")
    return (fora, maior, abrangencia, tinta, n), problemas


def vectorize_to_svg(png_path, svg_path):
    import vtracer

    vtracer.convert_image_to_svg_py(
        png_path,
        svg_path,
        colormode="binary",     # preto e branco
        hierarchical="stacked",
        mode="spline",
        filter_speckle=4,
        color_precision=1,
        corner_threshold=60,
        length_threshold=4.0,
        max_iterations=10,
        splice_threshold=45,
        path_precision=3,
    )


# ============ LOOP PRINCIPAL ============
def main():
    """Batch padrao: Krea 2 Turbo.

    Foi o Z-Image-Turbo por toda a fase inicial, e a troca tem motivo medido.
    Nas 11 cenas, mesmas seeds: Krea2 63,8 areas de media contra 48,9 do
    Z-Image, com `maior` em 18,0% contra 22,8%. E, o que decidiu, ele desenha o
    bicho que foi pedido — as duas falhas classicas do Z-Image (criatura
    hibrida no canto e pata preta macica) nao aparecem nele.
    O Z-Image continua acessivel em `--zimage`.
    """
    return main_krea2()


def main_zimage():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    vazando = []

    for i, animal in enumerate(ANIMALS):
        prompt = f"{STYLE_PREFIX}{animal['subject']}{STYLE_COMPOSICAO}{STYLE_SUFFIX}"
        png_path = os.path.join(OUTPUT_DIR, f"{animal['name']}.png")
        svg_path = os.path.join(OUTPUT_DIR, f"{animal['name']}.svg")

        print(f"[{i + 1}/{len(ANIMALS)}] Gerando: {animal['name']}...")

        # O modelo erra o fechamento de vez em quando. Como o diagnostico e'
        # barato e objetivo, vale re-rolar a seed em vez de aceitar a pagina.
        problemas = []
        for tentativa in range(TENTATIVAS):
            seed = -1 if SEED_BASE == -1 else SEED_BASE + i + 1000 * tentativa

            result = wait_for_completion(queue_prompt(build_workflow(prompt, seed)))
            imagens = [
                img
                for node_output in result["outputs"].values()
                for img in node_output.get("images", [])
            ]
            if not imagens:
                raise RuntimeError(f"ComfyUI não devolveu imagem para {animal['name']}")

            img = imagens[0]
            with open(png_path, "wb") as f:
                f.write(download_image(img["filename"], img["subfolder"], img["type"]))
            preprocess_bw(png_path)
            if ABRIR_MANCHAS:
                abertas = abrir_manchas(png_path)
                if abertas:
                    print(f"       {abertas} mancha(s) maciça(s) esvaziada(s)")

            (fora, maior, _, tinta, n), problemas = diagnosticar(png_path)
            sufixo = "" if tentativa == 0 else f" (tentativa {tentativa + 1})"
            print(f"       fora={fora:.0%} maior={maior:.0%} preto={tinta:.0%} "
                  f"maciço={medir_macico(png_path):.1%} áreas={n}{sufixo}")
            for problema in problemas:
                print(f"       !! {problema}")
            if not problemas:
                break

        if problemas:
            vazando.append((animal["name"], problemas))

        vectorize_to_svg(png_path, svg_path)
        print(f"    -> {png_path}")
        print(f"    -> {svg_path}")

    print(f"\nConcluído! Imagens e SVGs salvos em: {OUTPUT_DIR}")
    if vazando:
        print("\nEstes desenhos têm problema de fechamento — no app um toque "
              "vai pintar mais do que devia. Vale regerar com outra seed "
              "antes de converter para Dart:")
        for nome, problemas in vazando:
            print(f" - {nome}: {'; '.join(problemas)}")


def build_workflow_krea2(prompt, seed, forca_lora=None):
    """Krea 2 Turbo: UNET + CLIP(krea2) + VAE separados, cfg=1 sem negativo."""
    forca = KREA_LORA_FORCA if forca_lora is None else forca_lora
    fonte = ["lora", 0] if forca else ["unet", 0]
    g = {
        "clip": {"class_type": "CLIPLoader",
                 "inputs": {"clip_name": KREA_CLIP, "type": KREA_CLIP_TIPO,
                            "device": "default"}},
        "vae": {"class_type": "VAELoader", "inputs": {"vae_name": KREA_VAE}},
        "unet": {"class_type": "UNETLoader",
                 "inputs": {"unet_name": KREA_UNET, "weight_dtype": "default"}},
        "pos": {"class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["clip", 0]}},
        "zero": {"class_type": "ConditioningZeroOut",
                 "inputs": {"conditioning": ["pos", 0]}},
        "latente": {"class_type": "EmptyLatentImage",
                    "inputs": {"width": KREA_LADO, "height": KREA_LADO,
                               "batch_size": 1}},
        "ks": {"class_type": "KSampler",
               "inputs": {"model": fonte, "positive": ["pos", 0],
                          "negative": ["zero", 0], "latent_image": ["latente", 0],
                          "seed": seed, "steps": KREA_STEPS, "cfg": KREA_CFG,
                          "sampler_name": KREA_SAMPLER,
                          "scheduler": KREA_SCHEDULER, "denoise": 1.0}},
        "decode": {"class_type": "VAEDecode",
                   "inputs": {"samples": ["ks", 0], "vae": ["vae", 0]}},
        "save": {"class_type": "SaveImage",
                 "inputs": {"filename_prefix": "colorir_krea",
                            "images": ["decode", 0]}},
    }
    if forca:
        g["lora"] = {"class_type": "LoraLoaderModelOnly",
                     "inputs": {"model": ["unet", 0], "lora_name": KREA_LORA,
                                "strength_model": forca}}
    return g


def build_workflow_illustrious(positivo, negativo, seed, forca_lora=None):
    """Grafo SDXL: checkpoint + LoRA + clip skip, positivo e negativo de verdade."""
    forca = ILL_LORA_FORCA if forca_lora is None else forca_lora
    # forca 0 tira o no' inteiro em vez de carregar a LoRA para nada
    fonte_modelo = ["lora", 0] if forca else ["ckpt", 0]
    fonte_clip = ["lora", 1] if forca else ["ckpt", 1]

    grafo = {
        "ckpt": {"class_type": "CheckpointLoaderSimple",
                 "inputs": {"ckpt_name": ILL_CKPT}},
        "skip": {"class_type": "CLIPSetLastLayer",
                 "inputs": {"clip": fonte_clip, "stop_at_clip_layer": ILL_CLIP_SKIP}},
        "pos": {"class_type": "CLIPTextEncode",
                "inputs": {"text": positivo, "clip": ["skip", 0]}},
        "neg": {"class_type": "CLIPTextEncode",
                "inputs": {"text": negativo, "clip": ["skip", 0]}},
        "latente": {"class_type": "EmptyLatentImage",
                    "inputs": {"width": ILL_LADO, "height": ILL_LADO, "batch_size": 1}},
        "ks": {"class_type": "KSampler",
               "inputs": {"model": fonte_modelo, "positive": ["pos", 0],
                          "negative": ["neg", 0], "latent_image": ["latente", 0],
                          "seed": seed, "steps": ILL_STEPS, "cfg": ILL_CFG,
                          "sampler_name": ILL_SAMPLER, "scheduler": ILL_SCHEDULER,
                          "denoise": 1.0}},
        "decode": {"class_type": "VAEDecode",
                   "inputs": {"samples": ["ks", 0], "vae": ["ckpt", 2]}},
        "save": {"class_type": "SaveImage",
                 "inputs": {"filename_prefix": "colorir_ill", "images": ["decode", 0]}},
    }
    if forca:
        grafo["lora"] = {"class_type": "LoraLoader",
                         "inputs": {"model": ["ckpt", 0], "clip": ["ckpt", 1],
                                    "lora_name": ILL_LORA,
                                    "strength_model": forca, "strength_clip": forca}}
    return grafo


def rodar_lote(nome_trilha, monta_grafo, pasta, cenas=None):
    """Loop comum das trilhas: gera, diagnostica, re-rola a seed, vetoriza."""
    cenas = cenas or ANIMALS
    os.makedirs(pasta, exist_ok=True)
    reprovadas = []

    for i, cena in enumerate(cenas):
        prompt = f"{STYLE_PREFIX}{cena['subject']}{STYLE_COMPOSICAO}{STYLE_SUFFIX}"
        png_path = os.path.join(pasta, f"{cena['name']}.png")
        svg_path = os.path.join(pasta, f"{cena['name']}.svg")
        print(f"[{i + 1}/{len(cenas)}] {nome_trilha}: {cena['name']}...")

        problemas = []
        for tentativa in range(TENTATIVAS):
            seed = -1 if SEED_BASE == -1 else SEED_BASE + i + 1000 * tentativa
            resultado = wait_for_completion(
                queue_prompt(monta_grafo(prompt, seed)), timeout=900)
            imagens = [img for no in resultado["outputs"].values()
                       for img in no.get("images", [])]
            if not imagens:
                raise RuntimeError(f"ComfyUI não devolveu imagem para {cena['name']}")
            img = imagens[0]
            with open(png_path, "wb") as f:
                f.write(download_image(img["filename"], img["subfolder"], img["type"]))
            preprocess_bw(png_path)
            if ABRIR_MANCHAS:
                abrir_manchas(png_path)

            (fora, maior, _, tinta, n), problemas = diagnosticar(png_path)
            sufixo = "" if tentativa == 0 else f" (tentativa {tentativa + 1})"
            print(f"       fora={fora:.0%} maior={maior:.0%} preto={tinta:.0%} "
                  f"áreas={n}{sufixo}")
            for problema in problemas:
                print(f"       !! {problema}")
            if not problemas:
                break

        if problemas:
            reprovadas.append((cena["name"], problemas))
        vectorize_to_svg(png_path, svg_path)

    print(f"\n{nome_trilha}: {len(cenas) - len(reprovadas)}/{len(cenas)} aprovadas — {pasta}")
    for nome, problemas in reprovadas:
        print(f" - {nome}: {'; '.join(problemas)}")
    return reprovadas


def main_krea2(pasta=None):
    rodar_lote("Krea2", build_workflow_krea2, pasta or OUTPUT_DIR)


def main_zimg_lora():
    def monta(prompt, seed):
        w = build_workflow(ZIMG_LORA_GATILHO + prompt, seed)
        w["lora"] = {"class_type": "LoraLoaderModelOnly",
                     "inputs": {"model": ["unet_loader", 0],
                                "lora_name": ZIMG_LORA,
                                "strength_model": ZIMG_LORA_FORCA}}
        w["model_sampling"]["inputs"]["model"] = ["lora", 0]
        return w
    rodar_lote("Z-Image+ZIMGT", monta, os.path.join(OUTPUT_DIR, "zimgt"))


def main_redmond():
    def monta(prompt, seed):
        w = build_workflow(REDMOND_GATILHO + prompt, seed)
        w["lora"] = {"class_type": "LoraLoaderModelOnly",
                     "inputs": {"model": ["unet_loader", 0],
                                "lora_name": REDMOND_LORA,
                                "strength_model": REDMOND_FORCA}}
        w["model_sampling"]["inputs"]["model"] = ["lora", 0]
        return w
    rodar_lote("Z-Image+Redmond", monta, os.path.join(OUTPUT_DIR, "redmond"))


def main_illustrious(forca_lora=None, pasta=None):
    """Mesmo loop de `main()`, na trilha Illustrious.

    `pasta` existe para nao sobrescrever a leva boa: uma rodada de teste
    escreve numa subpasta, que `conversor_linhas.py` nao varre.
    """
    pasta = pasta or OUTPUT_DIR
    os.makedirs(pasta, exist_ok=True)
    reprovadas = []

    for i, cena in enumerate(ILL_CENAS):
        positivo = ILL_ESTILO + cena["subject"] + ILL_SUFIXO
        png_path = os.path.join(pasta, f"{cena['name']}.png")
        svg_path = os.path.join(pasta, f"{cena['name']}.svg")
        print(f"[{i + 1}/{len(ILL_CENAS)}] Gerando: {cena['name']}...")

        problemas = []
        for tentativa in range(TENTATIVAS):
            seed = -1 if SEED_BASE == -1 else SEED_BASE + i + 1000 * tentativa
            result = wait_for_completion(
                queue_prompt(build_workflow_illustrious(
                    positivo, ILL_NEGATIVO, seed, forca_lora)))
            imagens = [img for node in result["outputs"].values()
                       for img in node.get("images", [])]
            if not imagens:
                raise RuntimeError(f"ComfyUI não devolveu imagem para {cena['name']}")
            img = imagens[0]
            with open(png_path, "wb") as f:
                f.write(download_image(img["filename"], img["subfolder"], img["type"]))
            preprocess_bw(png_path)
            if ABRIR_MANCHAS:
                abrir_manchas(png_path)

            (fora, maior, _, tinta, n), problemas = diagnosticar(png_path)
            sufixo = "" if tentativa == 0 else f" (tentativa {tentativa + 1})"
            print(f"       fora={fora:.0%} maior={maior:.0%} preto={tinta:.0%} "
                  f"áreas={n}{sufixo}")
            for problema in problemas:
                print(f"       !! {problema}")
            if not problemas:
                break

        if problemas:
            reprovadas.append((cena["name"], problemas))
        vectorize_to_svg(png_path, svg_path)
        print(f"    -> {png_path}")

    print(f"\nConcluído! Imagens e SVGs salvos em: {pasta}")
    if reprovadas:
        print("\nEstas reprovaram no diagnóstico e não devem ser convertidas:")
        for nome, problemas in reprovadas:
            print(f" - {nome}: {'; '.join(problemas)}")


if __name__ == "__main__":
    import sys

    if "--list-models" in sys.argv:
        list_available_models()
    elif "--zimage" in sys.argv:
        main_zimage()
    elif "--krea2" in sys.argv:
        main_krea2()
    elif "--redmond" in sys.argv:
        main_redmond()
    elif "--zimgt" in sys.argv:
        main_zimg_lora()
    elif "--illustrious" in sys.argv:
        sem_lora = "--sem-lora" in sys.argv
        main_illustrious(
            forca_lora=0.0 if sem_lora else None,
            pasta=os.path.join(OUTPUT_DIR, "sem_lora") if sem_lora else None,
        )
    else:
        main()