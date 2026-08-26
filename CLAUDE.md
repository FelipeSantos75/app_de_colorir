# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

"Vamos Colorir" — a Flutter coloring-book app. Drawings are vector `Path` collections converted from SVG; the user taps a region and it fills with a texture. Free/premium split is enforced client-side (Firebase Auth), with Stripe wired for the premium purchase.

Code, comments and UI strings are in Portuguese. Keep new code consistent with that.

Toolchain: Flutter 3.44 / Dart 3.12 (`environment: sdk: ^3.5.2`).

**Web is the only target platform.** Android/iOS/desktop are not maintained — don't spend effort keeping them buildable, and prefer web-compatible packages when adding dependencies.

## Commands

```bash
flutter pub get
```

```bash
flutter run -d chrome --web-port 8080
```

Pin the port: the Google OAuth client only authorizes specific `http://localhost:<port>` origins, and `flutter run` otherwise picks a random one each launch.

```bash
flutter analyze
```

Build for web (the platform this app has actually been configured for):

```bash
flutter build web
```

There is no `test/` directory (it is gitignored). If tests are added: `flutter test` runs all, `flutter test test/foo_test.dart --plain-name "some test"` runs a single one.

## Required files that are NOT in the repo

A fresh clone does not build. `.gitignore` excludes generated/platform files, and some of them are needed:

- `lib/firebase_options.dart` — imported by [main.dart](lib/main.dart:4) but gitignored, so it is absent in a fresh clone and nothing compiles without it. A valid copy (project `colorir-448119`) is inside the committed `lib.zip`; extract `lib/firebase_options.dart` from it, or regenerate with `flutterfire configure`.
- `web/` is gitignored, so the whole web platform folder — the one target that matters — is absent in a fresh clone. Recreate it with `flutter create --platforms=web .`, then re-add the `google-signin-client_id` meta tag to `web/index.html` (also gitignored, and required for Google sign-in). Consider un-ignoring `web/` to stop losing it.
- `android/` retains only `android/app/google-services.json`; the Gradle project is gone. `windows/`, `linux/`, `macos/`, `ios/` scaffolds exist but are unused — see the web-only note above.

## Architecture

`lib/` is split `models/` (data + palette widgets), `views/` (screens), `control/` (the drawing library), `services/` (Firebase/Stripe). `functions/` is the Cloud Functions backend (Python 3.13, 2nd gen) — see [functions/README.md](functions/README.md). Its venv is installed and `functions/tests/test_webhook.py` passes offline, but nothing has been deployed: that needs the Firebase CLI and the Blaze plan.

**Rendering pipeline.** [Shape](lib/models/shape.dart) holds a `Path`, a fallback `Color`, an optional `textureAsset` path and a decoded `ui.Image`. `MultiShapePainter` (same file) paints every shape in list order: if `texture != null` it fills with an `ImageShader` (tiled, hardcoded 0.5 scale), otherwise with `color`, then optionally strokes black at 2px. The same painter renders both the grid thumbnails and the full canvas.

Every drawing is authored in a 500×500 coordinate space, and the painter draws at those raw coordinates. Both call sites therefore wrap it in `FittedBox` + a 500×500 `SizedBox` to fit the available box; without that the drawing is cropped to whatever fits at 1:1.

**Coloring interaction.** [canvas.dart](lib/views/canvas.dart) hit-tests taps with `shape.path.contains(localPosition)` iterating `shapes.reversed` (topmost first), skipping shapes with `colorable == false` (the black ink of the line-art drawings), and assigns `selectedTexture` to the hit shape, then re-runs `_loadTextures()`, which decodes every shape's texture from the asset bundle again. Direct color assignment is deliberately disabled — the app is texture-only now; `shape.color` survives as the uncolored default.

Note that shapes are mutated in place: `widget.shapes` points at the shared `List<Shape>` in `shapes_library.dart`, so coloring a drawing persists for the session and leaks back into the grid thumbnail.

**Drawing library.** [shapes_library.dart](lib/control/shapes_library.dart) (~4700 lines) is a hand-maintained Dart file: top-level `var dino = [Shape(...), ...]` lists plus a `library` list of [Drawing](lib/models/desenho.dart) entries (id, title, category, tags, `isPremium`). `DrawingLibrary` offers search/filter helpers, but [shape_grid.dart](lib/views/shape_grid.dart:191) filters `library` inline instead of using them.

**Navigation.** `SplashScreen` (animated logo, ~3.3s) → `ShapesPageGrid(isGuest: FirebaseAuth.currentUser == null)` → `ColorableShapesPage`. `LoginPage`/`RegisterPage` are pushed from the grid. `PremiumPage` exists but nothing navigates to it — the paid upgrade flow is unreachable in the current build.

## Adding a drawing

There are two converters, for two different kinds of source SVG. Pick by what the SVG contains.

### Layered SVGs already split into coloured regions

[functions/ferramentas/coversor3.py](functions/ferramentas/coversor3.py) handles these. It walks the SVG tree with ElementTree and emits stable hierarchical ids (`OBJECTS_g1_path4`), matching the ids already in `shapes_library.dart`, then copies the Dart to the clipboard via `pyperclip`. (Two earlier attempts, `conversor.py` and `conversor2.py`, were deleted in favour of it; they are still in git history if ever needed.)

Note the filename typo — `coversor3`, no `n`.

Its `convert_arcs_to_beziers` is a stub that returns the path unchanged, so SVG arc commands (`A`) pass through raw. `parseSvgPathData` on the Dart side does handle arcs, so this is only a problem if a future rewrite starts pre-processing them.

It lives under `functions/` only for tidiness and is listed in the `ignore` array of [firebase.json](firebase.json), so it is never uploaded with the backend. It needs `pyperclip`, which is deliberately *not* in `functions/requirements.txt` — don't add it there, or it ships to the Cloud Functions runtime for nothing. The input SVG is hardcoded in `__main__` and resolved against the repo root via `__file__`, so the script runs from any working directory.

Then paste the generated `Shape(...)` list into `shapes_library.dart` as a new top-level `var`, and register a `Drawing` in `library`.

### Line-art pages traced from a PNG (VTracer)

[functions/ferramentas/conversor_linhas.py](functions/ferramentas/conversor_linhas.py) handles these — the `output_coloring_pages/` set was imported with it. In a VTracer trace of a coloring page *every* path is black ink; the areas a child paints are the **holes** in that ink, so running `coversor3.py` on one would produce shapes that colour the outlines instead of the regions.

It splits each `<path>` into subpaths, counts how many other subpaths contain each one, and reads the parity: even depth is ink, odd depth is a paintable region. Containment is tested with vertices of the subpath's own boundary, not an interior point — a ring's centroid falls inside the hole it encloses, which would make the two contain each other.

Shapes are emitted in ascending depth so the painter's own ordering does the work: level-0 ink is filled solid first, level-1 regions cover its middle and leave only the stroke, and so on for nested levels. Ink shapes carry `colorable: false` so [canvas.dart](lib/views/canvas.dart) lets a tap fall through them to the region underneath. Coordinates are scaled from the 1024² source to the 500² space the library uses.

Unlike `coversor3.py` it writes files rather than the clipboard: run it with no arguments and it regenerates every `lib/control/desenhos/<slug>.dart` from `output_coloring_pages/*.svg`. Those files are generated — re-run the script instead of hand-editing them. Registering the `Drawing` in `library` is still manual.

### Generating those pages (geradesehmo.py)

[geradesehmo.py](geradesehmo.py) drives a local ComfyUI (Z-Image-Turbo) and vectorises the result with VTracer, writing both the PNG and the SVG into `output_coloring_pages/`. Full pipeline: `geradesehmo.py` → `conversor_linhas.py` → register the `Drawing` by hand.

**The property that matters is topological, not aesthetic: every white area must be fully enclosed by black.** The app has no flood fill — regions are precomputed by the converter, so an open outline merges two areas into one shape and a single tap paints both.

The measurement that matters is `fora`: the white area reachable from the page corner without crossing a line. In the first batch that was 58–62% of the page — sky, ground and object interiors had all merged, and on `pinguim_neve` the igloo interior and the sky are literally the same shape. `gatinho_janela` was the one page that behaved, and it is the only one whose scene sits inside a closed frame. That is where the border-and-ground-line wording in `STYLE_SUFFIX` comes from; with it, `fora` drops to 12–25% (just the margin outside the frame).

`fora` alone is not enough, and neither is the largest region on its own. `diagnosticar()` checks `fora` above `LIMITE_FORA`; a single area spanning the whole scene on both axes (`LIMITE_ABRANGENCIA` — real merging, as opposed to a merely large sky); too much solid black overall (`LIMITE_TINTA`); plus the two richness limits below. `main()` prints them per image and re-rolls the seed up to `TENTATIVAS` times when a page is flagged rather than accepting it. Anything still failing after that is listed at the end and should not be converted.

### Richness (`LIMITE_MAIOR`, `LIMITE_AREAS`, `STYLE_COMPOSICAO`)

A page can be perfectly sealed and still be a bad colouring page. Measured against [assets/image.svg](assets/image.svg), a commercial mermaid page kept as the reference: it has **60 colourable areas and its largest is 20% of the page**. The first batch here had 11–23 areas with the largest at 17–53% — one animal alone in an empty sky, where one tap finishes a third of the drawing.

Two prompt blocks close that gap, and both were A/B'd on the same seed (24 → 55 areas on an identical mermaid scene):

- Three lines at the end of `STYLE_PREFIX` ask for **subdivision** — large surfaces broken into outlined sections, hair as separate strands, scales/petals/feathers as rows of small outlined shapes. This is the half that does most of the work.
- `STYLE_COMPOSICAO` supplies the **composition**: a large centred subject, two or three smaller companion creatures with their own faces near the corners, a background built from two or three overlapping rounded banks instead of one sky, and small closed shapes scattered through every gap.

In the subjects, the number is what matters — "garden scene" returns a lone rabbit in an empty field; "five flowers, three mushrooms, two birds, two ladybugs" returns a full page.

Note the earlier advice not to threshold on the largest region no longer holds, and why: it was true only while the background was one undivided sky at 40–50%. Once `STYLE_COMPOSICAO` splits it into bands, the largest area lands at 18–25% and `LIMITE_MAIOR = 0.28` catches genuine emptiness without firing on correct pages. `LIMITE_AREAS = 35` rejects a sparse page outright — every page of the first batch fails it, which is the point.

The reference is *worse* than these pages on closure: it has no border and bleeds to the paper edge, so its `fora` is 28.9% against 17–19% here. Copy its density, not its framing.

Two wordings in `STYLE_PREFIX` were arrived at the hard way and are easy to undo by accident. "Closed silhouette" makes the model draw animals *from behind*, faceless — it has to be "one continuous outline that closes back on itself" plus an explicit request for a front-facing face. And animals that are black in real life get filled solid unless told they are "left blank white inside its outline whatever its real colour", which cost the penguin its wings in the first batch.

### Solid black is ink, not a defect

**A page is allowed to have solid black areas that nobody can colour** — paws, noses, ear insides, giraffe spots, a penguin's wings. This is a product decision, and the app already agrees with it: the converter marks ink shapes `colorable: false` and [canvas.dart](lib/views/canvas.dart) lets a tap fall straight through them to the region underneath. A black paw costs nothing; it is drawing, the same as the outline is drawing. There is no `LIMITE_MACICO`, and `diagnosticar()` does not fail on it.

`medir_macico()` survives as a measurement only — it prints per page, and `abrir_manchas()` shares its arithmetic. It erodes the black mask by `EROSAO_TRACO = 9`, so a ~7px outline disappears and a filled shape survives. For scale: pages with no filled areas measure 0.04–0.46%; the fox with four black paws measured 1.37%.

`abrir_manchas()` hollows those blobs out — erode the black, paint the surviving middle white, and a filled paw becomes a ~4px ring around a paintable region. **It is off by default** (`ABRIR_MANCHAS = False`), because turning it on erases exactly the black the page is supposed to have. Turn it on for the one case it is actually for: the model fills an entire animal solid and there is no region left there at all. Raise `NUCLEO_MIN` with it, so it takes the body and not the paws.

If you do enable it, `NUCLEO_MIN = 2000` is what keeps it away from eyes: the largest legitimate eye core measured across the batch is 512px (the penguin's), the smallest filled paw is 2724px, and nothing lands between. At 1200 it also opened the frog's large eyes into rings.

The workflow runs at `cfg=1` with `ConditioningZeroOut`, so **there is no negative prompt** — every constraint has to be phrased affirmatively in the positive prompt ("one continuous outline that returns to its starting point", not "no gaps"). Subjects avoid asking for anything that only exists as a loose stroke (grass tufts, reeds, sparkles, motion lines); those become ink that encloses nothing. Animals that are black in real life get filled solid unless told "drawn in outline only, white inside". That wording stays in `STYLE_PREFIX` because a mostly-white animal gives a child more to colour — but when it loses, the result is an acceptable page, not a rejected one (see "Solid black is ink" above).

### Scenes from the animal prompt pack

[functions/ferramentas/cenas_bichos.py](functions/ferramentas/cenas_bichos.py) turns the species lists in `prompts_bichos/` (extracted from the downloaded `animalPrompts.zip`; ~690 habitat lines plus cat and dog breeds) into `ANIMALS`-shaped entries.

The pack supplies *subjects*, not prompts — `red kangaroo in the grassy plains` on its own reproduces the first batch exactly: one animal alone in an empty field. The module wraps each line in the recipe that the Richness section above establishes: main character large and subdivided, two named companions with faces, four counted props, a closed ground. Cast and props come from a per-biome table keyed off the *place* half of the line only — matching the whole line puts "swamp wallaby in the thicket" in a wetland because of the animal's name, not the scene's.

Lines with no place at all (`cats_breeds.txt`, `dogs_breeds.txt`, the `*_singles` files) fall to a `quintal` biome rather than the forest default, so a Siamese gets a garden and a fence instead of woodland and mushrooms.

Everything in the biome table is deliberately a closed shape — the same constraint as the hand-written subjects, for the same reason.

Keep each biome's prop list at five or more: `montar()` samples four, so a thin biome hands the model almost the same page every time and `LIMITE_AREAS` rejects it. `deserto`, `monte` and `ceu` shipped thin (3–4 props) and the mountain wallaby failed at 28 areas until the table was filled out, then passed at 36. A sparse *scene* can still fail on top of that — an upright meerkat fills the middle and the model drops the tail of a long prop list, landing at 25–34 areas across three seeds. The diagnostic catches it and the page does not ship; that is the system working, not a bug to tune away.

Measured on six habitat lines, one per biome: five approved (36–47 areas, `fora` 14–20%), one rejected.

### The same pipeline as ComfyUI nodes

[comfyui_colorir/](comfyui_colorir/) exposes the pipeline as five nodes, for trying prompt variations on the canvas instead of editing the script: `ColorirCena` (pick one of `ANIMALS`), `ColorirPrompt` (prefix + scene + composition + suffix, all four editable), `ColorirLimpar` (`preprocess_bw` + `abrir_manchas`), `ColorirDiagnostico` (the six checks, with a `PreviewAny`-readable report), `ColorirVetorizar`.

The nodes hold no algorithms — they import `geradesehmo.py` and call it, so the script stays the single source of truth and the widget defaults are read from its constants. Two consequences: editing a threshold on the canvas does not change the batch (the node saves and restores the module constant around the call), and after changing `geradesehmo.py` you should re-run `python comfyui_colorir/gerar_workflow.py --instalar` so the saved workflow picks the new defaults up.

Installation is a junction from ComfyUI's `custom_nodes` to this folder, so the pack stays versioned with the project — which is why `nodes.py` resolves its root with `os.path.realpath`, not `abspath`: through the junction, `abspath` points back into `custom_nodes`, where there is no `geradesehmo.py`. `COLORIR_RAIZ` overrides it if that ever fails.

`ColorirVetorizar` writes into `output_coloring_pages/`, the folder holding approved pages, so it has two guards: it refuses to write when `aprovado` (wired from the diagnostic) is false, and with `sobrescrever` off it numbers the file rather than replacing one. Both exist because the first test run silently overwrote an approved `sereia_fundo_mar` with a rejected seed.

What the canvas cannot do is the seed re-roll loop — ComfyUI has no conditional retry. Read the report, click Run again. For the whole batch, `python geradesehmo.py` remains the way.

`gerar_workflow.py` emits **two** workflows. The second, `colorir_illustrious`, is a separate experimental track described below; both install with the same `--instalar`.

### The Illustrious track (experimental, not the batch)

Illustrious XL v2.0 + the KidsIllustration LoRA sit in ComfyUI's shared models folder, and the `ILL_*` constants near the top of [geradesehmo.py](geradesehmo.py) drive `colorir_illustrious`. `main()` does not touch them — the batch and the 11 approved pages are still Z-Image-Turbo.

Three things differ from the Z-Image track, and the third is the one that bites: it is SDXL, so `CheckpointLoaderSimple` replaces the split loaders; `cfg=6` means **there is a negative prompt**, and constraints like "solid black fill" finally work stated negatively; and it is a **booru-tag model, not a prose model** — feeding it `STYLE_PREFIX` returns a 3×3 grid of stickers rather than a page. The tag rewrite of the same constraints lives in `ILL_POSITIVO` / `ILL_NEGATIVO`. Clip skip is 2, matching how the LoRA was trained.

**Ask the model for line art. Do not decolourise afterwards.** That sentence cost several rounds to arrive at, and the failed path is worth recording because it *looked* like it was working.

The failure came in two layers. First, the test harness ran `preprocess_bw()` over the download and overwrote it, so every Illustrious image was judged only after being flattened into black mush; on that evidence the model looked hopeless. Then, having discovered the raw output was a beautiful flat-colour illustration measuring `fora = 0.0%`, the obvious move was to vectorise it in colour and classify each region as ink or paintable by fill luminance. That produced **218 paintable regions with the largest at 10% of the page** — better numbers than anything else in this project, and a genuinely terrible drawing. Luminance does not distinguish a dark *stroke* from a dark *fill*: the blue water (luminance 69) and the rock (135) were classified as ink and rendered as solid black slabs. No threshold fixes it; the information needed to separate the two is not in the colour.

What works is the booru line-art tags, in `ILL_POSITIVO`: `lineart, monochrome, greyscale, white background, no shading` returns an ink drawing already in black and white — average saturation 1.6 out of 255 on the raw output. With no colour to strip, there is nothing to misclassify.

Two more tags carry the composition: `solo` and `centered composition`. Without them the character lands in a corner with half the page empty. And `very thick bold black outlines` must stay out — pushed hard, it stops the model drawing and returns blobs.

From `VAEDecode` onward this track is identical to the Z-Image one: `ColorirLimpar`, `ColorirDiagnostico`, `ColorirVetorizar`, then `conversor_linhas.py`. Measured across three seeds: 67, 82 and 83 areas, and the 83 passes every check with its largest region at 16%. That is more paintable areas than any Z-Image page (which tops out at 75).

The lesson generalises past this model: **a metric can only rank pages that are already the right kind of thing.** 218 regions was a real count of real regions on a page nobody would print.

### Not a converter

[app.py](app.py) at the repo root is a separate tkinter SVG colorizer (deps `svglib`/`reportlab`/`Pillow`).

## Adding a color

Textures are one flat PNG per color per brush: `assets/textures/{basic,pencil,giz}/<HEX>.png`. [assets/textures/basic/cores.py](assets/textures/basic/cores.py) generates the solid `basic/` squares from a hex list; the `pencil/` and `giz/` sets were produced elsewhere and are not identical to `basic/`.

The palettes shown in the UI are hardcoded asset-path lists in `_getTexturesForBrush` in [paleta.dart](lib/models/paleta.dart) — one list per `BrushType`, containing duplicates. Adding a color means adding the PNG *and* the path string to each brush's list.

## Premium gating (currently inconsistent)

Two competing sources of truth:

- [shape_grid.dart:42](lib/views/shape_grid.dart:42) sets `_isPremiumUser = true` for any logged-in user (marked TODO) and passes it down to the canvas, which controls whether pencil/chalk brushes unlock (`BrushType.isPremium`).
- [AuthService.isPremiumUser()](lib/services/auth_service.dart:19) always returns `false` (TODO: check Firestore) and is never called.

Guests additionally have `isPremium` drawings filtered out and lock-overlaid in the grid. Any real entitlement work should collapse these into `AuthService` + a backend check.

## Known rough edges

[PLANO.md](PLANO.md) tracks the agreed remediation for the three big ones (premium gating, Stripe on web, versioning the web platform) and lists the product decisions still open.

- [loginpage.dart](lib/views/loginpage.dart) reimplements email and Google sign-in against `FirebaseAuth`/`GoogleSignIn` directly instead of using `AuthService`, which is therefore mostly dead code. Roughly half the file is a commented-out older copy of the same page — the same pattern appears in `shape.dart` and `auth_service.dart`. Delete rather than duplicate when touching these.
- [stripe_service.dart](lib/services/stripe_service.dart:9) has `YOUR_BACKEND_URL` / `YOUR_STRIPE_PUBLISHABLE_KEY` placeholders; `initializeStripe()` runs at startup in `main()` and its failure is only logged. There is no backend in this repo — `/create-payment-intent` must be provided elsewhere, and premium status should be granted by a webhook, not by the client's `initiatePayment` return value.
- `package:http` is imported by `stripe_service.dart` but is only a transitive dependency; add it to `pubspec.yaml` if the analyzer flags it.
- `flutter_stripe` has no web implementation at this version: on web, `StripeService.initializeStripe()` throws `Unsupported operation: Platform._operatingSystem`. `main()` catches and logs it, so the app still runs, but on a web-only target the whole `flutter_stripe` payment sheet is dead code. A real checkout has to go through Stripe Checkout / Payment Links (redirect) or Stripe.js, not this package.
- `android/app/google-services.json` is committed despite being listed in `.gitignore` (it predates the rule).
- `lib.zip` is a committed snapshot of an older `lib/` (pre-`services/`, pre-`premium_page.dart`) that also contains `firebase_options.dart`. Don't edit against it.
