# Plano — salvar o desenho pintado

Funcionalidade futura: o usuário pinta e o trabalho dele não se perde.
Documento de planejamento; nenhum código foi escrito.

Contexto: web only, backend Python em Cloud Functions (ver [PLANO.md](PLANO.md)).
Compartilha um pré-requisito com o [PLANO-UPLOAD-SVG.md](PLANO-UPLOAD-SVG.md).

---

## Duas funcionalidades diferentes debaixo do mesmo pedido

"Salvar o desenho" quase sempre quer dizer duas coisas, com custos bem
distintos. Vale separar, porque uma é barata e a outra não:

- **Guardar o progresso** — fechar o app e voltar depois com o desenho como
  estava, numa lista de "meus desenhos".
- **Exportar uma imagem** — baixar um PNG para mandar para a avó, imprimir ou
  usar de papel de parede.

A segunda é bem mais barata e provavelmente vale mais por esforço. Elas são
independentes: dá para entregar exportação sem nunca implementar
armazenamento.

---

## O que se perde hoje

[canvas.dart](lib/views/canvas.dart) faz `shape.textureAsset = selectedTexture`
direto na lista de formas. Só que essa lista é a mesma do
`shapes_library.dart` — `widget.shapes` aponta para o objeto compartilhado.

Duas consequências:

1. **Pintar suja a fonte.** A miniatura na grade passa a mostrar o desenho
   pintado, e o desenho "em branco" deixa de existir enquanto o app estiver
   aberto.
2. **Nada é gravado.** Ao recarregar a página, tudo volta ao branco.

Ou seja: hoje o app não consegue distinguir "o desenho" de "a minha pintura do
desenho". Enquanto isso for verdade, não há o que salvar.

---

## Fase A — separar o desenho da pintura

Pré-requisito de tudo o que envolve guardar progresso.

O canvas precisa trabalhar sobre uma **cópia** das formas, e a pintura precisa
existir como um objeto próprio, separado do desenho de origem.

**A pintura é minúscula.** Não é imagem, não são paths: é só um mapa de
`id da forma` → `caminho da textura`. Cada forma já tem id estável
(`OBJECTS_g1_path4`), gerado pelo conversor. Uma pintura inteira cabe em
poucas centenas de bytes de JSON — o que torna barato guardar, sincronizar e
versionar.

**Dois cuidados com os ids:**

- `Shape.id` é opcional no modelo (`String? id`). Forma sem id não tem como
  ser referenciada numa pintura salva. Passa a ser obrigatório.
- Se um desenho for reconvertido no futuro, os ids podem mudar de posição e a
  pintura salva passa a colorir as regiões erradas. A pintura precisa guardar
  qual versão do desenho ela pintou, e o app precisa recusar com elegância
  quando não baterem — melhor abrir em branco avisando do que abrir errado.

Esta fase é a **mesma** exigida pela fase 0 do plano de upload. Fazer uma
resolve boa parte da outra.

---

## Fase B — exportar imagem

A mais barata, e independente das outras. Pode ser a primeira a sair.

**Reaproveita o que já existe.** O `MultiShapePainter` que desenha a tela é o
mesmo que desenharia a imagem exportada — o mesmo painter que já serve a
miniatura e o canvas. Não há motor de renderização novo.

**Pontos de atenção concretos:**

- **Resolução.** A tela é 500 pontos de altura. Exportar nesse tamanho dá uma
  imagem pequena demais para imprimir. Precisa renderizar numa escala maior.
- **A textura não escala junto.** O preenchimento usa `ImageShader` com escala
  **fixa em 0.5** ([shape.dart](lib/models/shape.dart)). Renderizando em outra
  resolução, o padrão da textura muda de tamanho relativo e a imagem exportada
  não fica igual à tela. Precisa compensar, ou o resultado surpreende o
  usuário.
- **Baixar arquivo na web** é mecanismo do navegador, não do Flutter. É pouco
  código, mas é código específico de web.
- **Fundo.** Os desenhos têm um retângulo branco de fundo; convém confirmar
  que a exportação não sai com fundo transparente por acidente.

**Decisão de produto embutida:** com ou sem marca d'água / nome do app. Para
app infantil, uma marca discreta costuma ser bem aceita e ajuda a divulgar —
mas é escolha sua.

---

## Fase C — guardar o progresso localmente

Funciona para **todo mundo**, inclusive visitante sem login, e não custa nada
de backend. Casa com a decisão já tomada de deixar o app usável sem conta.

**Onde.** Armazenamento local do navegador. O projeto hoje não tem nenhuma
dependência de persistência no `pubspec.yaml`, então entra uma.

**Quando gravar.** Localmente pode ser a cada toque, sem problema.

**Limitações a comunicar ao usuário**, não esconder: some se ele limpar os
dados do navegador, não acompanha para outro aparelho, e não sobrevive a uma
troca de computador. Se a pessoa acha que está "salvo na conta" e perde tudo,
o problema não é técnico, é de confiança.

---

## Fase D — galeria "meus desenhos"

Onde as pinturas salvas aparecem. A grade atual já pinta cada item com o
`MultiShapePainter`, e uma pintura salva é o mesmo desenho com o mapa de
cores aplicado — **as miniaturas saem de graça**, sem gerar imagem nenhuma.

Precisa resolver: renomear, apagar, e o que acontece ao abrir de novo um
desenho já pintado (continua por cima ou começa outro).

**Uma pintura por desenho, ou várias?** O caminho simples é uma só — "continuar
de onde parei". Várias versões do mesmo desenho é bem mais interface: lista,
nomes, duplicar. Recomendo começar com uma, e só abrir para várias se os
usuários pedirem.

---

## Fase E — sincronizar na nuvem

Só para usuário logado. É o que permite pintar no computador e ver no celular.

**Custo escondido: contradiz uma decisão já tomada.** O plano principal decidiu
que a entitlement vem por *custom claim* justamente para o app **não** precisar
de `cloud_firestore`. Sincronizar pintura traz essa dependência de volta para o
cliente — mais peso no bundle web e mais superfície de regras de segurança.

A alternativa é salvar e carregar por Cloud Function, o que evita a
dependência, mas fica desajeitado para escrita frequente. Se a sincronização
for mesmo desejada, o honesto é aceitar o `cloud_firestore` e reabrir aquela
decisão conscientemente, em vez de contorná-la.

**Gravação precisa ser espaçada.** Uma escrita por toque na tela vira uma
escrita por toque cobrada. Agrupar as alterações e gravar ao sair do canvas,
ou em intervalos.

**Conflito entre aparelhos.** Pintou no celular e no computador sem conexão —
alguém perde. Para este app, "o último a gravar vence" é resposta aceitável,
desde que seja escolha e não acidente.

---

## Ordem sugerida

**A → B → C → D → E**, com uma observação: a **fase B (exportar) não depende da
fase A** e é a mais barata de todas. Se quiser um ganho visível rápido, ela sai
primeiro, sozinha.

As fases C, D e E não fazem sentido sem a A.

---

## O que isso mexe no que já existe

| Área | Impacto |
| --- | --- |
| `canvas.dart` | Passa a trabalhar sobre cópia das formas; ganha o conceito de pintura em andamento e o gatilho de gravação. |
| `shape.dart` | `id` deixa de ser opcional; o painter passa a ser reutilizado para exportar. |
| `shape_grid.dart` | Ganha a aba/filtro de "meus desenhos". |
| `pubspec.yaml` | Nova dependência de persistência local; e `cloud_firestore` se a fase E acontecer. |
| Regras do Firestore | Só na fase E: cada um lê e escreve apenas as próprias pinturas. |
| `functions/` | Nada, a menos que a fase E use função em vez de acesso direto. |

---

## Decisões pendentes

1. **Guardar progresso, exportar imagem, ou os dois?** São funcionalidades
   separadas; exportar é bem mais barato.
2. **Uma pintura por desenho ou várias versões?** Recomendo uma, para começar.
3. **Visitante sem login também salva?** Localmente dá, e é coerente com o app
   já ser usável sem conta.
4. **Sincronizar na nuvem vale trazer `cloud_firestore` para o app?** Reabre
   uma decisão do plano principal.
5. **Marca d'água na imagem exportada?**
6. **Limite de pinturas salvas por usuário?** Local quase não importa; na
   nuvem, importa.
