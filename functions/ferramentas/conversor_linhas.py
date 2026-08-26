# -*- coding: utf-8 -*-
"""
Conversor de paginas de colorir (line art) para Shapes do app.

Diferente de `coversor3.py` — que converte SVGs vetoriais ja separados em
regioes coloridas — este script trata SVGs gerados pelo VTracer a partir de
PNGs de contorno preto. Nesses arquivos todo `<path>` e' TINTA preta: o
traco. As areas que a crianca pinta sao os *buracos* desses tracos.

Estrategia:
  1. Cada `<path>` e' quebrado em subpaths (um por comando `M`).
  2. Calcula-se a profundidade de aninhamento de cada subpath (quantos outros
     subpaths o contem).
  3. Profundidade par  -> tinta preta (contorno).
     Profundidade impar -> regiao pintavel.
  4. Os shapes sao emitidos em ordem crescente de profundidade. Como o
     `MultiShapePainter` pinta na ordem da lista, a tinta do nivel 0 e' pintada
     primeiro e as regioes do nivel 1 cobrem o miolo dela, sobrando so' o
     traco. O mesmo se repete nos niveis aninhados.

Uso:
    python functions/ferramentas/conversor_linhas.py
"""

import os
import re
import xml.etree.ElementTree as ET

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENTRADA = os.path.join(RAIZ, 'output_coloring_pages')
SAIDA = os.path.join(RAIZ, 'lib', 'control', 'desenhos')

# O canvas do app trabalha em coordenadas de 500x500 (ver `dino` em
# shapes_library.dart). Os SVGs do VTracer sao 1024x1024.
LADO_DESTINO = 500.0
CASAS = 2

# O VTracer deixa buracos de meio ponto no meio do traco. Como regiao eles nao
# servem para nada — ninguem acerta um alvo de 0.5x1.0 num quadro de 500 — e so'
# incham o Dart. Abaixo desta area em unidades quadradas a regiao e' descartada
# e fica valendo a tinta que estiver embaixo.
AREA_MINIMA_REGIAO = 3.0

NS = '{http://www.w3.org/2000/svg}'


# --------------------------------------------------------------------------
# Leitura do SVG
# --------------------------------------------------------------------------

def ler_paths(caminho_svg):
    """Devolve ([(d, (tx, ty))], (largura, altura)) do arquivo."""
    raiz = ET.parse(caminho_svg).getroot()
    largura = float(raiz.attrib.get('width', '1024'))
    altura = float(raiz.attrib.get('height', '1024'))

    saida = []
    for elemento in raiz.iter(NS + 'path'):
        d = elemento.attrib.get('d')
        if not d:
            continue
        tx, ty = 0.0, 0.0
        casamento = re.search(
            r'translate\(\s*([-\d.eE]+)[ ,]+([-\d.eE]+)\s*\)',
            elemento.attrib.get('transform', ''),
        )
        if casamento:
            tx, ty = float(casamento.group(1)), float(casamento.group(2))
        saida.append((d, (tx, ty)))
    return saida, (largura, altura)


TOKEN = re.compile(r'[MCLZmclz]|[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?')


def quebrar_subpaths(d, deslocamento, escala):
    """Quebra o `d` em subpaths ja' transformados para a escala do app.

    Cada subpath vira um dict com 'segmentos' — tuplas ('M', p), ('L', p) ou
    ('C', c1, c2, p) — e a aproximacao poligonal usada nos testes geometricos.
    """
    tx, ty = deslocamento
    tokens = TOKEN.findall(d)

    def ponto(indice):
        x = (float(tokens[indice]) + tx) * escala
        y = (float(tokens[indice + 1]) + ty) * escala
        return (x, y)

    subpaths = []
    atual = None
    comando = None
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.isalpha():
            comando = token
            i += 1
            if comando in 'Zz':
                if atual:
                    subpaths.append(atual)
                    atual = None
                comando = None
                continue
            if i >= len(tokens):
                break

        if comando in 'Mm':
            if atual:
                subpaths.append(atual)
            atual = {'segmentos': [('M', ponto(i))]}
            i += 2
            comando = 'L'  # repeticao depois de um M e' um lineto implicito
        elif comando in 'Cc':
            atual['segmentos'].append(('C', ponto(i), ponto(i + 2), ponto(i + 4)))
            i += 6
        elif comando in 'Ll':
            atual['segmentos'].append(('L', ponto(i)))
            i += 2
        else:
            raise ValueError('comando inesperado: %r' % comando)

    if atual:
        subpaths.append(atual)

    for subpath in subpaths:
        subpath['poligono'] = achatar(subpath['segmentos'])
        subpath['caixa'] = caixa_delimitadora(subpath['poligono'])
    return [s for s in subpaths if len(s['poligono']) >= 3]


def achatar(segmentos, amostras=4):
    """Aproxima os beziers por segmentos de reta."""
    pontos = []
    atual = None
    for segmento in segmentos:
        if segmento[0] in ('M', 'L'):
            atual = segmento[1]
            pontos.append(atual)
            continue
        _, c1, c2, fim = segmento
        x0, y0 = atual
        for passo in range(1, amostras + 1):
            t = passo / amostras
            u = 1 - t
            pontos.append((
                u * u * u * x0 + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * fim[0],
                u * u * u * y0 + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * fim[1],
            ))
        atual = fim
    return pontos


def caixa_delimitadora(poligono):
    xs = [p[0] for p in poligono]
    ys = [p[1] for p in poligono]
    return (min(xs), min(ys), max(xs), max(ys))


def area_assinada(poligono):
    total = 0.0
    n = len(poligono)
    for i in range(n):
        x1, y1 = poligono[i]
        x2, y2 = poligono[(i + 1) % n]
        total += x1 * y2 - x2 * y1
    return total / 2.0


def dentro(ponto, poligono, caixa):
    """Teste ponto-em-poligono por lancamento de raio."""
    x, y = ponto
    minx, miny, maxx, maxy = caixa
    if x < minx or x > maxx or y < miny or y > maxy:
        return False
    resultado = False
    n = len(poligono)
    j = n - 1
    for i in range(n):
        xi, yi = poligono[i]
        xj, yj = poligono[j]
        if (yi > y) != (yj > y):
            if x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                resultado = not resultado
        j = i
    return resultado


def amostras_da_borda(subpath, quantidade=7):
    """Alguns vertices do proprio contorno, usados para medir o aninhamento.

    O teste precisa ser "curva A dentro da curva B", nao "ponto interno de A
    dentro de B": o centroide de um contorno externo cai dentro do buraco que
    ele envolve, e os dois passariam a se conter mutuamente. Como os subpaths
    do VTracer nunca se cruzam nem se tocam, qualquer vertice da borda de A
    esta' estritamente dentro ou fora de B — varios vertices dao margem contra
    imprecisao do achatamento.
    """
    poligono = subpath['poligono']
    passo = max(1, len(poligono) // quantidade)
    return poligono[::passo][:quantidade]


# --------------------------------------------------------------------------
# Geracao do Dart
# --------------------------------------------------------------------------

def numero(valor):
    texto = ('%.*f' % (CASAS, valor)).rstrip('0').rstrip('.')
    return '0' if texto in ('', '-0') else texto


def dart_path(subpaths):
    """Serializa um ou mais subpaths como um unico atributo `d`."""
    partes = []
    for subpath in subpaths:
        for segmento in subpath['segmentos']:
            if segmento[0] == 'M':
                partes.append('M%s %s' % (numero(segmento[1][0]), numero(segmento[1][1])))
            elif segmento[0] == 'L':
                partes.append('L%s %s' % (numero(segmento[1][0]), numero(segmento[1][1])))
            else:
                _, c1, c2, fim = segmento
                partes.append('C%s %s %s %s %s %s' % (
                    numero(c1[0]), numero(c1[1]),
                    numero(c2[0]), numero(c2[1]),
                    numero(fim[0]), numero(fim[1]),
                ))
        partes.append('Z')
    return ''.join(partes)


def analisar(caminho_svg):
    """Le o SVG e devolve os subpaths anotados com a profundidade."""
    paths, (largura, altura) = ler_paths(caminho_svg)
    escala = LADO_DESTINO / max(largura, altura)

    subpaths = []
    for d, deslocamento in paths:
        subpaths.extend(quebrar_subpaths(d, deslocamento, escala))

    amostras = [amostras_da_borda(s) for s in subpaths]
    for i, subpath in enumerate(subpaths):
        profundidade = 0
        for j, outro in enumerate(subpaths):
            if i == j:
                continue
            votos = sum(dentro(p, outro['poligono'], outro['caixa']) for p in amostras[i])
            if votos * 2 > len(amostras[i]):
                profundidade += 1
        subpath['profundidade'] = profundidade
        subpath['area'] = abs(area_assinada(subpath['poligono']))
    return subpaths


def gerar_dart(caminho_svg, nome_var):
    subpaths = analisar(caminho_svg)
    profundidades = sorted({s['profundidade'] for s in subpaths})

    linhas = [
        '// GERADO POR functions/ferramentas/conversor_linhas.py — nao edite a mao.',
        '// Origem: output_coloring_pages/%s' % os.path.basename(caminho_svg),
        '',
        "import 'package:flutter/material.dart';",
        "import 'package:path_drawing/path_drawing.dart';",
        '',
        "import '../../models/shape.dart';",
        '',
        'var %s = [' % nome_var,
        '  // Fundo pintavel, como nos desenhos ja existentes.',
        '  Shape(',
        "    id: '%s_fundo'," % nome_var,
        "    path: parseSvgPathData('M0 0h%s v%s h-%s Z')," % (
            numero(LADO_DESTINO), numero(LADO_DESTINO), numero(LADO_DESTINO)),
        '    color: Colors.white,',
        '    hasStroke: false,',
        '  ),',
    ]

    regioes = 0
    for profundidade in profundidades:
        nivel = [s for s in subpaths if s['profundidade'] == profundidade]
        if profundidade % 2 == 0:
            # Tinta: um shape por nivel, pintado antes das regioes de dentro.
            linhas += [
                '  Shape(',
                "    id: '%s_traco%d'," % (nome_var, profundidade),
                '    path: parseSvgPathData(',
                "      '%s'," % dart_path(nivel),
                '    ),',
                '    color: Colors.black,',
                '    hasStroke: false,',
                '    colorable: false,',
                '  ),',
            ]
        else:
            # Regioes pintaveis: as maiores primeiro, para que as menores
            # fiquem por cima e recebam o toque.
            for subpath in sorted(nivel, key=lambda s: -s['area']):
                if subpath['area'] < AREA_MINIMA_REGIAO:
                    continue
                regioes += 1
                linhas += [
                    '  Shape(',
                    "    id: '%s_area%d'," % (nome_var, regioes),
                    '    path: parseSvgPathData(',
                    "      '%s'," % dart_path([subpath]),
                    '    ),',
                    '    color: Colors.white,',
                    '    hasStroke: false,',
                    '  ),',
                ]

    linhas += ['];', '']
    return '\n'.join(linhas), regioes


def camel(slug):
    partes = slug.split('_')
    return partes[0] + ''.join(p.capitalize() for p in partes[1:])


if __name__ == '__main__':
    os.makedirs(SAIDA, exist_ok=True)
    for arquivo in sorted(f for f in os.listdir(ENTRADA) if f.endswith('.svg')):
        slug = os.path.splitext(arquivo)[0]
        codigo, regioes = gerar_dart(os.path.join(ENTRADA, arquivo), camel(slug))
        with open(os.path.join(SAIDA, slug + '.dart'), 'w', encoding='utf-8') as saida:
            saida.write(codigo)
        print('%-24s -> %-26s %3d areas %7.1f KB'
              % (arquivo, slug + '.dart', regioes, len(codigo) / 1024))
