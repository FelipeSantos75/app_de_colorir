# Plano — upload de SVG pelos usuários

Funcionalidade futura: o usuário envia um SVG e recebe de volta um desenho
pintável dentro do app. Documento de planejamento; nenhum código foi escrito.

Contexto: web only, backend Python em Cloud Functions, Stripe/assinatura
(ver [PLANO.md](PLANO.md)). Compartilha o pré-requisito da fase 0 com o
[PLANO-SALVAR-DESENHO.md](PLANO-SALVAR-DESENHO.md).

---

## O bloqueio de fundo

**Desenhos hoje são código-fonte Dart, não dados.**

[shapes_library.dart](lib/control/shapes_library.dart) tem ~4700 linhas de
`var dino = [Shape(id: ..., path: parseSvgPathData('M0.0,0.0 h500.0 ...'))]`,
mais uma lista `library` de `Drawing`. Tudo isso é **compilado dentro do app**.
O fluxo atual é: rodar o conversor na sua máquina, colar o resultado no
arquivo, recompilar, publicar.

Um upload em runtime não tem como acrescentar código Dart a um app já
compilado. Então nenhuma quantidade de trabalho no upload resolve isto — a
representação dos desenhos precisa deixar de ser código e virar dado carregado
em runtime. **Essa é a fase 0, e ela é pré-requisito de tudo o mais.**

---

## Fase 0 — tirar os desenhos do código

Pré-requisito. Entregável sozinho, sem nenhum upload envolvido, o que a torna
uma boa fase para validar antes de investir no resto.

**Formato.** Um JSON por desenho, com metadados e a lista de formas, cada uma
com seu `id` e a string `d` do path. É exatamente o que o `Shape` já precisa: o
app faz `parseSvgPathData(d)` ao carregar. A conversão pesada (varrer a árvore
do SVG, gerar ids, normalizar) acontece uma vez, fora do app.

**Repositório de desenhos.** Uma camada que entrega `Drawing`s vindos de duas
origens — os embutidos (que continuam no bundle, funcionando offline e sem
login) e os do usuário (baixados). A `shape_grid` passa a consumir essa camada
em vez de filtrar a lista `library` direto.

**Migração.** Converter os desenhos atuais para o novo formato e apagar o
`shapes_library.dart`. Vale manter os dois caminhos vivos por um tempo, para
comparar o resultado visual antes de descartar o antigo.

**Ganho colateral.** Hoje `widget.shapes` aponta para a lista compartilhada e
as formas são mutadas no lugar — pintar um desenho suja a miniatura da grade e
persiste pela sessão. Carregando de dado, cada abertura do canvas ganha sua
própria cópia e o bug morre de graça.

---

## Fase 1 — upload e conversão

**Fluxo.** App envia o SVG para o Firebase Storage num caminho por usuário →
uma função disparada por Storage converte → grava o JSON resultante e um
documento de metadados no Firestore → o app lê e o desenho aparece na grade.

**Por que a conversão vai para o backend.** Já existe um backend Python em
Cloud Functions, e o conversor já é Python. É a peça que melhor se encaixa no
que foi construído: o `coversor3.py` vira o núcleo de uma função, deixando de
emitir texto Dart e passando a emitir JSON.

**Assíncrono por natureza.** A conversão não é instantânea e pode falhar. O
documento de metadados precisa de estado (`enviado`, `convertendo`, `pronto`,
`falhou`, com motivo), e o app precisa mostrar esse estado em vez de fingir que
foi imediato.

**Limites, desde o primeiro dia.** Tamanho máximo do arquivo, número máximo de
desenhos por usuário, e limite de uploads por período. Sem isso, o endpoint é
um vetor de custo — Storage e Functions são cobrados, e um laço de upload numa
conta gratuita vira fatura.

**Regras de segurança.** O usuário escreve só na própria pasta de upload; o
JSON convertido é escrito apenas pelo backend e é somente-leitura para o
cliente. Vale a mesma disciplina da entitlement: o cliente nunca escreve o que
o cliente consome como verdade.

---

## Fase 2 — o conversor atual não serve para SVG arbitrário

Ele foi feito para os SVGs específicos que você já usou, e funciona neles. Para
arquivo de estranho, tem buracos concretos. Confirmei lendo o código:

- **`transform` é ignorado.** O `traverse_svg` lê `id`, `d` e atributos de
  geometria — nunca `transform`. Qualquer SVG que posicione grupos com
  `translate`/`rotate`/`scale`, que é a maioria do que sai de Illustrator,
  Inkscape ou Figma, produz formas na posição errada. **É o maior dos
  problemas** e provavelmente o que mais vai gerar "meu desenho ficou
  embaralhado".
- **`viewBox` é ignorado.** Não há normalização de escala. Os desenhos atuais
  vivem num espaço 0–500 porque os SVGs de origem eram assim; um arquivo com
  outro viewBox entra fora de escala.
- **`<defs>`, `<clipPath>`, `<mask>`, `<symbol>` viram desenho.** A recursão
  genérica desce em qualquer elemento desconhecido, então formas que existem só
  como definição ou recorte são emitidas como se fossem partes visíveis.
- **Elementos não suportados somem em silêncio:** `polygon`, `polyline`,
  `line`, `text`, `image`, `use`. O usuário não recebe aviso — só um desenho
  incompleto.
- **Arcos passam crus.** O `convert_arcs_to_beziers` devolve o path
  inalterado. Isso **não é bug hoje**, porque o `parseSvgPathData` do lado Dart
  entende arcos; só vira problema se alguém reescrever a função achando que
  deveria converter.

Nada disso é difícil isoladamente. O ponto é que "aceitar SVG de usuário"
significa reescrever o conversor com uma noção real de árvore SVG — matriz de
transformação acumulada, normalização por viewBox, lista explícita de elementos
suportados e ignorados — e não reaproveitar o script como está.

---

## Fase 3 — o SVG que simplesmente não dá para pintar

Mesmo com um conversor correto, muitos SVGs não viram livro de colorir. A
interação depende de `path.contains(ponto)` acertar **regiões fechadas**. Casos
que quebram isso:

- arte só de traço, sem nenhuma região fechada — não há o que tocar;
- um path único gigante com furos em even-odd — tocar em qualquer lugar pinta o
  desenho inteiro;
- fotos vetorizadas com milhares de formas minúsculas — pintável na teoria,
  insuportável na prática;
- ausência do retângulo de fundo que os desenhos atuais têm (`BACKGROUND_path1`
  cobrindo a tela), do qual o comportamento de toque depende hoje.

**A saída é não salvar às cegas.** Converter, medir e mostrar ao usuário antes
de guardar: quantas regiões pintáveis saíram, uma prévia renderizada, e a
opção de confirmar ou descartar. Um aviso honesto de "este arquivo virou 2
regiões, provavelmente não vai ficar bom" custa pouco e evita a maior fonte de
frustração da funcionalidade.

Vale também um teto de formas por desenho, por desempenho: o
`MultiShapePainter` repinta a lista inteira a cada toque, e o
`_loadTextures()` do canvas hoje redecodifica a textura de **todas** as formas
a cada toque — com centenas de formas isso trava.

---

## Fase 4 — compartilhar (opcional, e cara)

Tudo acima presume **desenho privado, visível só para quem enviou**. Se em
algum momento um usuário puder publicar para os outros, o projeto muda de
categoria:

- fila de moderação antes de publicar;
- denúncia, remoção e bloqueio de quem reincide;
- registro de quem enviou o quê, para responder a takedown.

Este é um app infantil. Conteúdo enviado por desconhecidos aparecendo para
crianças não é um detalhe de produto — é responsabilidade legal. **A
recomendação é não fazer a fase 4**, ou fazê-la só com curadoria manual, você
aprovando um a um.

---

## Segurança

**SVG é um formato de ataque, não um formato de imagem.** Ele carrega script,
referências a entidades externas (XXE), referências remotas em `<image>` e
estruturas que explodem em memória ao serem expandidas.

Duas defesas, que se reforçam:

1. **O app nunca renderiza o SVG enviado.** Ele só recebe strings de path já
   normalizadas em JSON. Isso elimina de saída quase toda a superfície — script
   e recurso remoto não sobrevivem à conversão.
2. **O parser do backend precisa ser endurecido.** Parsear XML não confiável
   com a biblioteca padrão exige cuidado com expansão de entidades; existe
   biblioteca específica para isso. Somar limites de tamanho, de profundidade
   da árvore e de número de elementos, além de timeout na função.

Também tratar como questão de segurança: **cota e custo**. Conversão é CPU paga
por invocação, e armazenamento é cobrado por mês.

---

## O que isso mexe no que já existe

| Área | Impacto |
| --- | --- |
| `shapes_library.dart` | Deixa de existir na forma atual; vira dado. |
| `shape_grid.dart` | Passa a consumir o repositório, com carregamento assíncrono e estados de erro. |
| `canvas.dart` | Recebe cópia das formas, não a lista compartilhada; precisa de teto de formas e do conserto do `_loadTextures()`. |
| `Drawing` / `Shape` | Ganham serialização e origem (embutido vs. do usuário). |
| `functions/` | Nova função disparada por Storage; conversor reescrito. |
| `functions/ferramentas/coversor3.py` | Vira base do conversor do backend, ou é aposentado por ele. |
| Regras do Storage e Firestore | Novas, por usuário. |

---

## Dependências

- **Fase 0 não depende de nada** e pode começar quando quiser.
- **Fase 1 em diante depende** do backend estar de pé: plano Blaze, Cloud
  Functions publicadas, Storage habilitado — ou seja, do item 2 do
  [PLANO.md](PLANO.md).
- Se o upload for recurso pago, depende também da entitlement do item 1.

---

## Decisões pendentes

1. **Upload é recurso premium ou grátis?** Se for premium, resolve boa parte do
   problema de abuso e de custo por tabela.
2. **Privado ou compartilhado?** A recomendação é privado. Compartilhado é a
   fase 4 e muda a natureza do projeto.
3. **Quantos desenhos por usuário, e de que tamanho?** Precisa de número antes
   de escrever regra de Storage.
4. **O que fazer com conversão parcial?** Salvar o que deu, avisando o que foi
   perdido, ou recusar o arquivo inteiro. Afeta bastante a percepção de
   qualidade.
5. **Miniatura no cliente ou no servidor?** Hoje a grade repinta cada desenho
   com o `MultiShapePainter`. Com muitos desenhos do usuário isso fica caro, e
   gerar um PNG no backend passa a valer a pena.
