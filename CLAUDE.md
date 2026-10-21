# Video-maker: reel Instagram per Manuel Ferrante (@_manuelferrante)

Manuel manda: i suoi clip parlati (selfie iPhone, spesso HDR/HLG, muro bianco dietro) + uno o più video di sfondo.
Si consegna SEMPRE il pacchetto completo: **reel + copertina + caption**. Si risponde in italiano.

Gli strumenti (dipendenze, modelli in `models/`, font) li installa `.claude/hooks/session-start.sh` all'avvio.
HuggingFace è bloccato dalla rete: i modelli si scaricano da GitHub (già fatto dall'hook).

## Flusso di lavoro

1. **Analizza i clip parlati**: `python3 analyze_clips.py out/draft.json <clip...>` (ordine = nome file, salvo
   indicazioni). Dà testo, taglio sulla voce reale e tempi parola. Rileggi e correggi a mano: il modello sbaglia
   termini tecnici e numeri (es. "masso l'app" = MUSCLE UP, "squadra" = SQUAT, "deep" = DIP). Se ci sono due take
   della stessa frase, tienine una sola (di solito la più recente) e dillo a Manuel.
2. **Guarda lo sfondo** (frame a 1-2 fps con `tile`, e scene cut con `select='gt(scene,0.25)'`) e capisci cosa
   succede e quando.
3. **Abbina lo sfondo alle parole**: sotto ogni frase va la parte di sfondo IN TEMA con quello che Manuel dice
   (dice "muscle up" → si vede il muscle up; dice un carico → si vede quell'alzata/quella scritta). Si possono
   spezzare più parti di sfondo dentro una stessa frase (`background` con `dur`). Evita outro/loghi di altri.
4. Scrivi `projects/<nome>.json` (modello: `projects/streetlifting_635.json`) e lancia
   `python3 make_reel.py projects/<nome>.json`. Controlla i frame del risultato prima di consegnare.
5. Copertina: sezione `cover` nello stesso JSON, `python3 make_cover.py projects/<nome>.json`.
6. Caption: vedi sotto. Consegna reel e copertina con SendUserFile, la caption in chat.
7. Commit + push sul branch di lavoro (non i video sorgente; gli output vanno in `out/`, ignorato da git:
   copia nella root del repo solo i file finali da consegnare se serve).

## Regole del reel (approvate da Manuel)

- **Durata massima ~10 s.** Tagliare tutte le pause: i tagli seguono l'energia della voce (analyze_clips), non i
  timestamp grezzi del modello (sono in anticipo di 0.3-0.5 s e lasciano vuoti tra le frasi).
- **Velocità ~1.1-1.15x** (`speed`, audio con atempo). Ultimo reel: 1.15.
- **Hook forte all'inizio**: la frase più eclatante (un numero, un record) apre il video, con Manuel grande.
- **Audio**: solo la voce di Manuel, sfondo muto, loudnorm -14 LUFS.
- **Colore pelle**: i clip iPhone HLG vanno convertiti con `HDR_TO_SDR` in make_reel.py (mobius npl=400 + sat 1.4
  + leggero warm). Non toccarlo: le versioni più chiare sono state bocciate come "cadaveriche".
  `probe_hdr` deve riconoscere HLG (attenzione all'output di ffprobe con la virgola finale).
- **Scontorno**: `Matter.run` toglie anche il muro bianco tra i ricci (colore muro campionato, `wall_thr` 44) e
  decontamina i bordi (`matter.clean`). Non abbassarlo: con la versione vecchia restava bianco tra i capelli.
- **Faccia (busto scontornato)**, layout a keyframe in `layouts`:
  - `big` (grande al centro, con punch) sulle cose eclatanti/hook;
  - `mid_l` / `mid_r` / `mid_c` per il parlato normale, faccia ALTA nella safe zone (occhi ~y 1440 su 1920);
  - `hidden` per sparire e lasciare vedere solo lo sfondo (es. mentre si vede un'alzata con la sua scritta).
  - Non esagerare con i movimenti: `still_until` tiene il busto fermo (niente dondolio) in un tratto.
    Nel reel approvato: grande sull'hook → scivola via → sparisce → rientra e resta fermo → zoom grande sul
    numero forte → normale fino alla fine.
- **Sottotitoli**: pagine per frase di senso ("|PAROLA" nel JSON forza una nuova pagina); font Anton, MAIUSCOLO, bianco con bordo nero + ombra, parola pronunciata in azzurro `5CE1F6`.
  Dimensione 74, max 3 parole per volta, centrati orizzontalmente, a ~72% dell'altezza (margin_v 520).
  Scrivere le parole come dette ("37 KG E MEZZO DI MUSCLE UP"), numeri in cifre.

## Copertina (stile dei riferimenti di Manuel)

- Frame dello sfondo più forte (atleta ben visibile, ritaglia via le scritte in sovrimpressione dello sfondo).
- Manuel scontornato in basso a sinistra con un'espressione forte (stupito, mano in faccia...).
- Titolo clickbait su 2-3 righe centrato, Anton ~125-150, bianco + parole chiave azzurre (`*parola` nel JSON),
  bordo e ombra neri, che passa sopra i capelli.
- **Deve funzionare nel ritaglio 3:4 della griglia profilo** (1080x1440 centrale: y 240-1680): faccia intera
  (dai capelli alla barba) e titolo dentro quella fascia. Fai sempre l'anteprima del ritaglio.

## Caption (stile approvato, vedi `projects/caption_style.md`)

- Apertura: il fatto/numero secco o direttamente il ragionamento, MAI la stessa frase del reel/copertina; max 1 emoji
  (anche a fine frase), da variare in base al tema (non sempre 👀).
- 3 paragrafi brevi e discorsivi sul significato per lo streetlifting, niente elenchi di numeri.
- **Nessun hashtag.** Niente em dash (—). Tono diretto, niente frasi da guru.
- Una sola CTA finale: "Se ti interessano questi contenuti, seguimi."
- Atleta e organizzatori: solo taggati da Manuel, non nominati nel testo.

## Cosa chiedere a Manuel solo se manca

Ordine dei clip se ambiguo, quale take tenere se ci sono doppioni, nome atleta/tag. Per il resto decidi tu e
proponi; Manuel corregge sul risultato.

## Brand (aggiornato)

- Logo: `assets/brand/logo_mf_originale.png` (originale su nero) e `assets/brand/logo_mf_trasparente.png` (scontornato).
- **Storie**: logo piccolo in alto a sinistra dentro la safe zone (x 56, y 262, largo 170 px), titoli da y 400 in giù
  (vedi `logo()` in `projects/stories_set2.py`). Nei reel per ora niente logo.

## Sottotitoli standard (aggiornato, reel India)

- Bianchi, Inter ExtraBold ~84, bordo nero 7 + leggera ombra, **nessun riquadro dietro**; pagine brevi per frase di senso
  (max 2 righe), piccolo "pop" d'ingresso.
- Centrati orizzontalmente, poco sotto la metà: di default y ~1450, appena sotto il mento quando c'è la faccia
  (mai sopra bocca/faccia). Sempre nella safe zone (y 250-1580, x 60-1020).
- Voce sempre senza pause e a 1,1x; B-roll (anche animazioni mie/stock Pixabay) su quasi ogni frase.
- Effetti sonori LEGGERI quando compaiono B-roll e grafiche (es. `sfx/comparsa.wav`, `trascina.wav`, `punto_1-3.wav`);
  il fruscio sugli stacchi dei B-roll quasi impercettibile (vol ~0.06). Mai suoni forti.
- Niente punti morti, reel sempre "animato" ma senza forzarlo. Il parlato che manda Manuel NON va usato per forza
  tutto: si taglia quello che non serve.
- B-roll atleti: non ripetere la stessa persona (al massimo una volta); Manuel che si sistema/il suo squat si possono
  usare più volte. Sui momenti "subito migliora" stacchi veloci tra atleti diversi (bam bam).
- CTA: per ora NIENTE "link in bio" (Manuel sta costruendo il funnel sul sito); chiudere su un invito tipo
  "provalo e fammi sapere".
