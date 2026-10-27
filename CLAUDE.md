# Video-maker: reel e storie Instagram per Manuel Ferrante (@_manuelferrante)

Manuel è coach di streetlifting/calisthenics. Usa Claude come **editor autonomo**: manda parlati, B-roll e istruzioni,
Claude monta e consegna. Si risponde **sempre in italiano**, tono diretto. Non chiedergli di scegliere tra opzioni
tecniche: decidi tu, consegna, lui corregge sul risultato. Chiedi solo se manca qualcosa di essenziale.

Strumenti (ffmpeg, modelli ASR in `models/`, font Inter/Anton/Noto Emoji) li installa `.claude/hooks/session-start.sh`.
HuggingFace è bloccato: i modelli arrivano da GitHub (già fatto dall'hook).

## Da dove arrivano i file

- Caricati in chat: `/root/.claude/uploads/<id-sessione>/...` (copiali in `src_<nome>/`, gitignored).
- Google Drive (cartella condivisa "chiunque abbia il link"): cerca con il connettore Drive
  (`parentId = '<id cartella>'`) e scarica con
  `curl -sSL "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`.
  Cartelle usate: `1QHzJwYsUyXiTqqHcIZhj9Rsb44N-_rtc` (parlati), `1Ko5w_pQKPRjSpGm9DkB8uOMUMCLhHmxh` (nuova).
- Stock: Pixabay (`PIXABAY_API_KEY` in env, host pixabay.com / cdn.pixabay.com). Pexels non disponibile.
- Output sempre in `out/<nome>/` (gitignored). Si consegnano con SendUserFile; lo script va committato in `projects/`.

## Flusso di lavoro (reel)

1. **Trascrivi** il parlato: `python3 analyze_clips.py out/x.json <clip>` dà testo e tempi; per i tagli usa
   l'energia della voce (soglia ~ picco-30/32 dB a blocchi di 10 ms) e la trascrizione per segmenti (vedi
   `projects/piede_esterno.py`, lista `SEGS`). Il modello sbaglia termini tecnici: correggi a mano.
   Se ci sono doppie take o frasi che Manuel poi rinnega ("no, questa non mi piace"), tienine una / tagliale.
   **Il parlato NON va usato per forza tutto**: si tiene solo quello che serve.
2. **Guarda i B-roll** (fotogrammi con `tile` e timestamp) e abbina a ogni frase la clip IN TEMA con le parole.
3. **Scrivi uno script Python per reel** in `projects/<nome>.py` (modelli: `piede_esterno.py` = completo con hook
   animato, punti numerati, B-roll, sfx; `respiro_panca.py` = parlato + citazione + scheda barrata;
   `india_reel.py` = voiceover + cartina animata `map_italia_india.py`; `panni_giungla.py` = muto, solo scritta POV).
   Pipeline: un ffmpeg per segmento (`-ss/-t` PRIMA di `-i`), concat, overlay dei B-roll con `enable`,
   grafiche PIL in RGBA (qtrle) sovrapposte, sottotitoli ASS, mix audio numpy.
   Stacchi: renderizza ogni B-roll +0.1 s e anticipalo di 0.02 s (`setpts=...+{t0 - 0.02}`), altrimenti compaiono
   1-2 fotogrammi del parlato tra un B-roll e l'altro.
4. **Controlla sempre** i fotogrammi del risultato (contact sheet) e il loudness prima di consegnare.
5. Consegna: reel + copertina (+ caption in chat, + storie se richieste). Poi commit + push sul branch di lavoro.

## Regole del reel (approvate da Manuel)

- **Nessun punto morto.** Voce senza pause, **velocità 1,1x** (atempo), loudnorm -14 LUFS. B-roll muti.
- Durata: quella che serve senza buchi (reel parlati 15-19 s; reel virali/POV 7-9 s).
- **Hook forte** nei primi 1-2 s, Manuel grande o un'animazione (es. riquadro che parte dal dito e si apre a tutto
  schermo seguendo la mano, `card.mov` in `piede_esterno.py`).
- **B-roll su quasi ogni frase**, coerenti con le parole: suoi video, atleti, animazioni mie (PIL), stock Pixabay.
  Atleti: **non ripetere la stessa persona** (al massimo una); Manuel che si sistema / il suo squat si possono
  ripetere. Sui momenti "subito migliora": stacchi veloci tra atleti diversi (bam bam).
- Reel sempre "animato" ma **senza forzarlo**: niente animazioni a raffica, testi leggibili e fermi.
- **Effetti sonori LEGGERI** (`sfx/`, generati da `sfx/make_sfx*.py`, niente licenze): `comparsa`, `trascina`,
  `punto_1-3`, `disegno`, `whoosh`, `swoosh`, `pop`, `hit`, `aereo_decollo/atterraggio`. Fruscio sugli stacchi
  quasi impercettibile (vol ~0.06). Mai suoni forti. Musica: la mette Manuel su Instagram.
- **Colore naturale**: nessun grading sul parlato iPhone; i clip HLG (`arib-std-b67`) solo tonemap
  (`zscale ... tonemap=mobius`, vedi `TONEMAP` negli script). Gli effetti "opachi" sono stati bocciati.
- **Niente loghi/outro di altri** nelle clip (taglia prima dell'outro). Le citazioni di altri creator vanno tradotte
  nei sottotitoli; il nome si tagga, non si scrive.
- **CTA nel parlato**: per ora NIENTE "link in bio" (Manuel sta costruendo il funnel sul sito). Chiudere su un
  invito tipo "provaci e fammi sapere" / "e tu cosa ne pensi?".

## Sottotitoli standard

- Bianchi, **Inter ExtraBold ~78-84**, bordo nero 7 + leggera ombra, **nessun riquadro dietro**; pagine brevi per
  frase di senso (max 2 righe), piccolo "pop" d'ingresso. Una parola chiave può essere arancio `#E8662C`.
- Centrati, di default **y ~1450**, appena sotto il mento quando c'è la faccia (mai sopra bocca/faccia).
  Sempre nella safe zone (y 250-1580, x 60-1020).
- Etichette/grafiche: Inter Black Italic in riquadri neri o arancio, sempre nella safe zone, mai sulla testa.
- Reel POV/virali: una sola scritta per tutto il video, bianca con bordo nero, centrata un po' sopra il centro
  (y ~760); il video è abbastanza corto da ripartire mentre la leggi.

## Copertina

- Stile: fotogramma forte (Manuel con espressione decisa o la scena), titolo su 2 righe: riquadro nero +
  riquadro arancio (Inter Black Italic), nella fascia y ~1060-1250.
- Curiosità: si può sfocare la parte che "spoilera" (es. il piede disegnato) e rendere **illeggibile** il riquadro
  arancio (si vede che c'è scritto qualcosa ma non si legge). Faccia sempre nitida.
- Per i POV: stessa scritta del reel. **Sempre anteprima del ritaglio 3:4 della griglia** (y 240-1680).
- Script modello: `projects/cover_piede.py`, `cover_respiro.py`, `cover_panni.py`.

## Storie (set da 4 + il reel come 4ª)

- Struttura tipica: 1-2 storie con box domanda (risposta multipla o aperta) o slider, 1 spiegazione minima +
  "IL REEL NELLA PROSSIMA STORIA", (reel), storia finale con domanda corta oppure link ("Vuoi farti correggere lo
  squat da me? CLICCA QUI" con zona per lo sticker link). Prima proponi le idee, Manuel dice sì/no.
- Stile: foto reale scurita in navy, etichette nei riquadri, arancio come accento, zona sticker libera,
  footer con puntini e @_manuelferrante. Helper in `projects/stories_set2.py`, esempio completo `stories_set3.py`.
- **Logo** piccolo in alto a sinistra (x 56, y 262, largo 170): `assets/brand/logo_mf_trasparente.png`
  (originale: `logo_mf_originale.png`). Titoli da y 400 in giù. Nei reel per ora niente logo.
- Brand: navy `#14304F`, arancio `#E8662C`, avorio `#F2EEE3`.

## Caption

Vedi `projects/caption_style.md` (esempi approvati, l'ultimo scritto da Manuel). In breve:
apertura sulla domanda/confusione del lettore (mai la stessa frase del reel), risposta semplice col perché,
beneficio positivo (non l'errore), max 1-2 emoji, niente hashtag, niente em dash (—).
CTA: "Se ti interessano questi contenuti, seguimi." oppure "Se vuoi farti analizzare lo squat da me: LINK 🔗 in BIO".

## In sospeso

- Analisi Instagram via Graph API (solo lettura): partire SOLO quando Manuel dà il via. Servono account
  professionale, app Meta, token come secret d'ambiente (mai in chat), host graph.instagram.com/graph.facebook.com.

## Vecchia pipeline (legacy)

`make_reel.py` / `make_cover.py` con JSON (`projects/streetlifting_635.json`): stile vecchio (Anton, azzurro
`5CE1F6`, busto scontornato). Manuel ha chiesto di ripartire da zero con lo stile sopra: usarla solo se la chiede.
