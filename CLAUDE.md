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
- B-roll lunghi: Manuel carica girati lunghi; prendi solo i momenti salienti (non per forza tutti) e nei reel
  successivi usa altri momenti degli stessi file, così non deve ricaricare tutto. Tieni traccia dei pezzi usati
  in `projects/broll_usati.md` (file, intervallo, reel).
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
   **Per i nuovi reel parlati usa `projects/reel_kit.py`** (motore comune: segmenti, B-roll, titoli in alto con
   barra/numero, evidenziatore arancio, sottotitoli, sfx, loudness esatta): esempi `infortunio_regole.py`,
   `panca_fermi.py`; serie con intro comune: `input_giusti.py`.
   Note pratiche: parakeet salta pezzi nelle clip lunghe con pause → trascrivi a blocchi di voce; i suoi tempi
   parola sono in anticipo ~0.3 s. Il loudnorm a passata singola su reel corti resta a -12.5: reel_kit corregge
   col guadagno misurato. I vecchi script usano `/home/user/Video-maker`: crea il symlink
   `ln -s /home/user/video-maker /home/user/Video-maker`. Clip HLG in luce calda (pelle rossa, bianchi slavati):
   tonemap `hable` npl=100 + `colorbalance` (vedi `COLORFIX` in `input_giusti.py`).
4. **Controlla sempre** i fotogrammi del risultato (contact sheet) e il loudness prima di consegnare. Manuel lo
   chiede esplicitamente: prima di ogni invio ricontrolla TUTTO, sia che si veda bene (testi leggibili e non tagliati,
   soggetto non coperto da dischi/oggetti, niente fotogrammi sfocati o vuoti, niente flash tra gli stacchi) sia che
   rispetti ogni sua indicazione data in chat. Correggi prima di mandare.
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
- **Metodo standard (Manuel: "voglio che fai più o meno sempre questa")**: `projects/cover_panca_v2.py`. Sfondo = Manuel
  che fa l'esercizio, ingrandito e spostato in modo che si veda bene in alto a destra; davanti Manuel scontornato a
  mezzo busto, grande, un po' a sinistra del centro, con un'espressione FORTE presa dal parlato (perplesso/deciso:
  scegli la più marcata, non la prima che va bene); titolo centrato sotto il mento. Sottotitolo bruciato sul petto
  tolto con inpaint, bordi dei ricci ricolorati (niente alone del muro), mano senza buchi, fondo sfumato al buio.
- Script modello: `projects/cover_panca_v2.py` (standard), `cover_piede.py`, `cover_respiro.py`, `cover_panni.py`.

## Storie (set da 4 + il reel come 4ª)

- Struttura tipica: 1-2 storie con box domanda (risposta multipla o aperta) o slider, 1 spiegazione minima +
  "IL REEL NELLA PROSSIMA STORIA", (reel), storia finale con domanda corta oppure link ("Vuoi farti correggere lo
  squat da me? CLICCA QUI" con zona per lo sticker link). Prima proponi le idee, Manuel dice sì/no.
- Stile: foto reale scurita in navy, etichette nei riquadri, arancio come accento, zona sticker libera,
  footer con puntini e @_manuelferrante. Helper in `projects/stories_set2.py`, esempio completo `stories_set3.py`.
- **Logo** piccolo in alto a sinistra (x 56, y 262, largo 170): `assets/brand/logo_mf_trasparente.png`
  (originale: `logo_mf_originale.png`). Titoli da y 400 in giù. Nei reel per ora niente logo.
- Brand: navy `#14304F`, arancio `#E8662C`, avorio `#F2EEE3`.

## Serie "Input giusti" (ottobre 2026, una puntata ogni mercoledì)

- 4 reel: muscle up -> trazioni -> dip -> squat (in quest'ordine). Intro uguale per tutti ("input giusti per far
  recepire le informazioni nel modo corretto"), poi subito la parte dell'esercizio.
- Storie per puntata (5): 1) richiamo alla serie, puzzle a 4 pezzi che si scopre un pezzo a puntata, titolo
  "Input giusti per trasformare informazioni in qualcosa di utile"; 2) "Quale input utilizzeresti?" con zona libera
  per lo sticker (le opzioni le mette Manuel); 3) soluzione argomentata, coerente con il reel; 4) il reel;
  5) "Vuoi farti analizzare <esercizio>? Compila il form qua sotto" con zona per lo sticker link.
- Editing richiesto: oltre ai sottotitoli (centrati, in basso), **titoli in alto** più grandi in riquadri curati
  (nero/arancio, Inter Black Italic, y ~280-500) sui concetti chiave; immagini/clip a tema Pixabay mentre parla per
  tenere alta l'attenzione; sfx leggeri sull'hook e all'entrata di ogni esercizio.
- Caption per ogni reel: apertura comune sul concetto di input giusti, poi la parte specifica dell'esercizio, e in
  chiusura l'invito ai commenti: non sono gli unici input, se te ne vengono in mente altri scrivili nei commenti.

- Stato: 4 reel + copertine + storie + caption consegnati e approvati (ottobre 2026), script `input_giusti.py`,
  `cover_input_giusti.py`, `stories_input_giusti.py`.

## Altri reel approvati (ottobre 2026)

- "3 regole d'oro dopo un infortunio" (`infortunio_regole.py`) e "fermi lunghi in panca" (`panca_fermi.py`), con
  copertine `cover_inf_panca.py` e storie `stories_inf_panca.py` (box domanda aperto, sondaggio, spiegazione,
  form). Nelle storie sui temi di salute: riga "sempre con il via libera del tuo medico o fisioterapista".

## Format "IG1" (riferimento in Drive, cartella parlati, novembre 2026)

Reel tecnico/storytelling di 20-25 s max sul modello del video di riferimento (registrazione schermo di un altro
creator: si prende lo STILE, mai le sue clip). Struttura: hook domanda + risposta secca, contesto, problema,
step 1-2, risultato, chiusura che riprende l'hook. Tagli stretti su silenzi ed "ehm".
Elementi da riprodurre: schede scure a tutto schermo tra un pezzo di parlato e l'altro con occhiello piccolo
spaziato ("— IL PROBLEMA", "— STEP 01") + titolo grande in serif (una parola in corsivo), animazioni a linee
sottili bianche con accenti arancio (schemi, archi/gauge che si riempiono, curve che salgono, numeri grandi
in riquadro arancio); B-roll in riquadro arrotondato al centro della scheda o picture-in-picture in alto a
sinistra sul parlato con didascalia in corsivo; transizioni morbide e più sfx (sempre leggeri).
I sottotitoli restano quelli approvati (bianchi, parola chiave arancio).

## Reel di novembre 2026 (consegnati) e feedback di Manuel da ricordare sempre

- "In che giorni allenarsi" (format IG1): `giorni_allenamento.py` (versioni A 18 s / B 23 s), schede animate
  `giorni_cards.py` su `ig1_cards.py` (fondo scuro, serif Instrument Serif in `assets/fonts/`, gauge, split, settimana,
  batteria), copertina `cover_giorni.py`, storie `stories_giorni.py` (sondaggio, slider, spiegazione 3 punti, form
  "programmazione su misura per te"). `reel_kit.py` ora ha `overlays` (B-roll in riquadro con didascalia) e la
  dissolvenza opzionale come 8° campo dei B-roll.
- "L'intenzione" (reel muto con musica): `intenzione.py` (V1 split screen, V2 bianco e nero -> colore sul drop),
  copertina split `cover_intenzione.py`, musica originale `sfx/make_music.py` (drop al secondo esatto).
- Pubblicati come reel di prova: Manuel li ha tagliati entrambi a ~18 s.

Feedback (valgono per tutti i prossimi video):
- **Versioni di prova = stessa durata (~18 s), cambia solo il formato/approccio**, non la lunghezza. Copertina e
  caption uguali tra le versioni, così il test misura solo il montaggio.
- Durata giusta per i reel: ~18 s. Meglio corto e denso che lungo.
- Copy/script: parla a un **atleta intermedio che vuole diventare avanzato e si allena da solo** (4 sedute intense);
  tono da coach di forza serio. Concetti con il perché (es. sistema nervoso, recupero), niente elenchi di giorni o
  numeri che non hanno senso (es. "72 ore"), niente frasi vaghe tipo "i giorni contano quanto la scheda" senza
  spiegare. Chiusure che chiede: "Ti è stato utile? Com'è la tua split settimanale? Fammelo sapere nei commenti".
- Manuel registra uno script unico: le versioni le ricavi tu con i tagli. Taglia TUTTE le pause (anche 0,2-0,5 s),
  1,1x, prendi la take migliore quando ripete ("ripeto").
- Format IG1: Manuel in camera solo a inizio e fine (e poco nel mezzo, sempre coperto da B-roll in riquadro, titoli
  o sottotitoli). Nel mezzo schede animate e B-roll; animazioni dove cala l'attenzione; sfx leggeri ma curati.
- Reel "a contrasto" (stile 2IG): **stesso video/esercizio** per bianco e nero (rallentato, momenti in cui perde
  tempo, è distratto, poca intenzione) e colore (le ripetizioni in cui dà tutto). Etichette solo se il girato le
  mostra davvero (niente "CELLULARE" senza un telefono in scena), centrate e sempre alla stessa altezza. Esercizi
  che vuole: muscle up, panca, curl bicipiti (+ squat). Ricontrolla il cambio di musica sul testo chiave.
- Bianco e nero: abbastanza luminoso da leggere bene il soggetto (gamma ~1.25), mai scuro.
- Copertine: gli piace il fondo con lui che fa l'esercizio (es. squat) e lui scontornato più piccolo e di lato,
  con un frame in cui sorride/è aperto (scelto il 152,6 del parlato); fai scegliere il frame se è incerto, mandando
  una striscia di candidati con i secondi.
- Storie: domande banali (quiz generici) bocciate; meglio slider o domande che fanno riflettere. Form finale:
  "Vuoi una programmazione su misura per te?".
- Prima di ogni invio: controllo completo (immagini, testi non tagliati, soggetto visibile, musica/drop, loudness,
  ogni indicazione della chat). Manuel scrive spesso "Fatto?": rispondi con lo stato preciso.
- Caption: Manuel le fa anche con un'altra AI; il prompt-modello è in `projects/caption_style.md`.
- Nota tecnica: non usare `pkill -f`/`pgrep -f` con stringhe che compaiono nel tuo stesso comando (uccide la shell);
  usa il PID o `pgrep -a python3 | grep`.

## Linee guida contenuti (da un reel di riferimento sull'algoritmo, mandato da Manuel a novembre 2026)

Valgono per ogni nuovo contenuto (idea, script, hook, caption):
- **Parti dall'esperienza.** Modalità 1: un episodio vero, un risultato o una situazione vissuta con un atleta (o da
  Manuel stesso); le call/analisi con i clienti sono la fonte principale. Modalità 2: se il tema è generico,
  chiediti quali elementi, dati e situazioni reali inserire per "portarlo a terra" e renderlo unico.
- **Specifica il tema.** Non "come migliorare lo squat" ma "come un mio atleta ha sbloccato lo squat a 180 kg
  cambiando un solo input" (tema generico -> contesto preciso + risultato concreto).
- **Stile e comunicazione = personal brand.** Non vince il contenuto "più giusto", vince chi arriva al potenziale
  cliente e trasmette un messaggio chiaro. Obiettivo: essere un riferimento per il pubblico prima di pensare alle
  vendite (niente toni da venditore).
- Quando proponi idee o script, chiedi a Manuel l'episodio/il dato reale se manca, invece di inventarlo.

## Caption

Vedi `projects/caption_style.md` (esempi approvati, l'ultimo scritto da Manuel). In breve:
apertura sulla domanda/confusione del lettore (mai la stessa frase del reel), risposta semplice col perché,
beneficio positivo (non l'errore), max 1-2 emoji, niente hashtag, niente em dash (—).
CTA: "Se ti interessano questi contenuti, seguimi." oppure "Se vuoi farti analizzare lo squat da me: LINK 🔗 in BIO".

## Reel "THIS IS STREETLIFTING" (novembre 2026, trial reel A/B)

- Edit hype muto con musica sui riferimenti in Drive (sottocartella "Riferimenti"): `this_is_streetlifting.py`, musica
  originale phonk 130 BPM `sfx/make_phonk.py`, copertina `cover_streetlifting.py`. Ordine fisso: muscle up -> trazioni
  (chin up) -> dip -> squat, ogni scritta solo sul suo esercizio; chiusura "THIS IS STREETLIFTING". A = con i nomi,
  B = solo la chiusura. Stile: intro B/N con flash negativi/arancio, drop a colori sul beat, punch-in, raffica, Anton.
  V2 (feedback): niente intro lenta (solo 2 beat), **niente ripetizioni** degli esercizi, tutto "tremato" a jump-cut
  come la raffica (gli e' piaciuta di piu'), alzate complete; V3: muscle up tagliato appena sopra la sbarra e
  subito le trazioni, 13.9 s, cosi' il finale (la parte piu' bella) si vede.
- **Clip iPhone HLG nei reel "cinematici"**: il tonemap zscale gonfia i colori (Manuel: "si vede che c'era HDR"). Base
  naturale = HLG letto come SDR (`scale=in_color_matrix=bt2020:out_color_matrix=bt709`) + `grade()` dello script.
- I file grandi su Drive non si caricano dal connettore: si mandano in chat, Manuel li sposta in "montati"
  (`1CQ_3Nnt_mpPjLTmcc--1Dagis5yhmkOC`).

## In sospeso

- Analisi Instagram via Graph API (solo lettura): partire SOLO quando Manuel dà il via. Servono account
  professionale, app Meta, token come secret d'ambiente (mai in chat), host graph.instagram.com/graph.facebook.com.

## Vecchia pipeline (legacy)

`make_reel.py` / `make_cover.py` con JSON (`projects/streetlifting_635.json`): stile vecchio (Anton, azzurro
`5CE1F6`, busto scontornato). Manuel ha chiesto di ripartire da zero con lo stile sopra: usarla solo se la chiede.

## Analisi performance reel (12 novembre 2026, insights mandati da Manuel)

Dati (views / salti / media / visite profilo / follow): Abbandonare un esercizio 3.540 / 31,9% / 8 s su 14 / 28 / 0;
Respiro panca 3.120 / 43,3% / 8 su 16 / 15 / 0; Non è forte 2.734 / 43,1% / 6 su 8 / 9 / 1; Attiva il dorsale
1.488 / 45,3% / 8 su 15 / 11 / 0; Giorni B 645 / 68,2% / 6 su 23 / 3 / 0. "Muscle up +60kg" (65,6K) e il lead
magnet "50/60/70 kg alle trazioni" (11,2K) erano SPONSORIZZATI: non usarli come riferimento organico. Riferimenti organici
(tutti pubblicati come trial e poi nel feed): massimo 3,5K (Abbandonare), buoni ~2K, andati male ~500. Quello che
decide la diffusione e' la percentuale di salti: 31,9% -> 3,5K; ~43% -> 2,7-3,1K; 45% -> 1,5K; 68% -> 645.
Lezioni: in 4 reel su 5 la prima frattura è a 1,5-3 s, quando si stacca dalla faccia a B-roll/scheda prima di aver
chiuso il gancio; le schede animate scure come prima immagine o entro 3 s fanno crollare (Giorni B); funziona il caso
reale con persona e prima/dopo (Abbandonare). Animazioni sì, ma sopra un caso concreto e dopo il gancio.
Visite al profilo alte ma follow quasi zero: manca una promessa chiara di cosa si ottiene seguendo.
DM: arrivano SOLO dalle sponsorizzate; nei reel organici nessuna chiusura da' un motivo per scrivere.
Regole di montaggio da qui in avanti (obiettivo salti < 35%): prima immagine = Manuel in camera che guarda
l'obiettivo o un movimento forte; nessuno stacco su B-roll o scheda prima che la frase del gancio sia finita; nessuna
scheda scura entro i primi 3 s; il gancio parte da un caso o un numero reale, mai da una domanda che seleziona.
Funnel (Manuel, 12/11/2026): obiettivo principale = coaching online. Scala: programma gratuito via DM -> programmi
sul sito (9 EUR singola alzata, 19 EUR completi) -> modulo coaching su manuelferrante.it. 6 clienti arrivati da
Instagram finora; programma gratis dato a ~4 persone. Ultimi 30 gg: 6.100 visite profilo, +44 follower, 9 tap sul link.
Reel sugli atleti funzionano anche organici (da 3 trazioni a 75 kg: ~3K senza ads): parlare dei suoi atleti e taggarli.
Sponsorizzate finite a inizio novembre (ultime: obiettivo "visite al profilo", 3 EUR/giorno, nessun DM): il calo
delle views di novembre e' la fine delle ads. Prossimo test: stesse ads DOPO aver cambiato bio e fissati, confrontando
follow e DM ogni 100 visite.
Posizionamento (Manuel): coach di FORZA, non solo streetlifting (allena anche powerlifting e palestra); target da
intermedio ad avanzato con un obiettivo in kg, "prima i kg, l'estetica viene di conseguenza". Niente nomi di atleti
in bio. Clienti coaching: arrivano dal MODULO sul sito (~1 al mese), non dai DM; i DM portavano acquisti dei programmi
(con le sponsorizzate). Link in bio: 1) sito (coaching e programmi), 2) WhatsApp precompilato per il programma gratis.

## Documento idee e strategia (Google Doc `1GdYfZRjIfezq_w6JzbGntxbta1NikE8CYbRuJm1LEk0`)
Idee da fare / fatte (barrate), analisi di uno stratega, protocolli. Da tenere sempre presenti:
- Struttura: PROBLEMA SPECIFICO -> conseguenza -> ragionamento/soluzione di Manuel; 1 reel = 1 concetto; reel a cerchio
  (il finale riprende l'hook); "questo reel potrebbe pubblicarlo identico un altro coach?" Se si', manca Manuel.
- Linguaggio da evitare: "ti svelo il segreto", "3 errori che stai facendo", "devi assolutamente", "se vuoi migliorare".
- CTA coerente con l'obiettivo (commento / salvataggio / discussione), non sempre "scrivimi".
- Case study: "era bloccato qui -> abbiamo cambiato X perche' -> dopo N settimane Y".
- Protocolli: trazioni (dato gratis a 3 persone -> 1 cliente, 4 mesi, 290 EUR); dip (Vincenzo, peso corporeo zavorrato a
  15 anni); squat (Jasmin 200 kg); muscle up (Nicolo' +30 kg, Lorenzo record italiano).
Test di novembre 2026: 3 trial, uno per formato (esercizio, programmazione, case study), stesse regole dei primi 3 s,
~18 s; confronto su salti, media visione, visite profilo ogni 1000 views, follow, fascia 13-17.
Sito manuelferrante.it (visto 12/11): hero "Iniziamo a lavorare insieme / Non solo allenarti, ma godendoti ogni passo",
form breve subito sotto (sport, obiettivi, nome, numero), poi risultati (Nicolo' trazioni 70 kg, Jasmin squat 200 kg,
Arianna squat 100 kg, muscle up 28,75 kg), metodo in 5 passi, programmi PDF 8 settimane (Single lift, Street 4 e
Street 3 a 19 EUR, Forza & Fisico in arrivo), video testimonianze, FAQ.
Identita': Manuel vuole restare ATLETA + coach (nome profilo approvato "Manuel Ferrante | Atleta Streetlifting & Strength
Coach"). I contenuti da atleta restano, ma come prova del metodo (decisioni sul proprio allenamento, gare), non come diario.
Script dei 3 reel di test (tacco nello squat completo; Vincenzo ganci + struttura; percentuali in attesa della tesi):
`projects/script_test_novembre.md`, MESSI DA PARTE da Manuel il 12/11, da riprendere piu' avanti. Domande aperte: tesi
sulle percentuali, dati di Vincenzo + ok genitori, se vuole guardare gratis gli squat di chi scrive, ok a "link nel
profilo" nelle chiusure, conferma che la prima cosa forte va nei primi 2-3 s. Lista operativa: `projects/todo_manuel.md`.
Script "a loop" (richiesta di Manuel, 12/11): il gancio iniziale e' forte e il finale si collega all'inizio, cosi' il
video ricomincia senza stacco (l'ultima frase resta aperta e la prima la completa). La CTA va prima della frase-ponte
o nella caption, mai dopo, altrimenti rompe il loop. Valido per i prossimi script, compresi quelli in
`projects/script_test_novembre.md`.
Trial "THIS IS STREETLIFTING" (13 s, muto con musica, 13/11): 170 views, salti 64,3%, media 3 s, 0 follow, 99,4% non
follower, ~40% fuori Italia (India 14,8%, Iran 11,8%, Turchia, Polonia). Meta' del pubblico perso entro ~2 s. Lezione:
l'edit hype senza parlato e con testo in inglese non ha una promessa nei primi secondi e attira pubblico estero che
non puo' diventare cliente. Non pubblicato nel feed.
Regola (approvata da Manuel 13/11): gli edit hype muti solo per i follower (storie o post occasionali), mai come trial
per crescere; per persone nuove che possono diventare clienti serve il parlato in italiano con il gancio sul problema.

## GoodLift (novembre 2026)
Web app gratuita di Manuel che giudica le alzate (GOOD LIFT / NO REP, replay con linee):
https://manuelferrante-rgb.github.io/Manuel-Ferrante-Coaching/goodlift/ (poi manuelferrante.it/goodlift).
Script di Manuel: `projects/goodlift_script_promozione.md`; versione adattata agli insight in
`projects/brief_editor_novembre.md` (sez. 4): Telegram e storie subito, trial reel ~18 s dopo il 19/11 con GoodLift
aggiunto ai link in bio. Telegram solo per il gruppo atleti. Mai "giudice ufficiale" o "precisione al 100%".
Ok dell'atleta per ogni video mostrato. Per i reel GoodLift la CTA "link in bio" e' approvata (scelta di Manuel).
Dentro GoodLift niente titoli o frasi di vendita (Manuel: "brutti, non e' questo lo scopo"): solo i bottoni
WhatsApp precompilato "vengo da GoodLift" e candidatura con utm_source=goodlift.
Brief generale per la chat editor: `projects/brief_editor_novembre.md` (aggiornalo quando cambiano le regole).
Prompt riutilizzabili per altre AI (16/11): `projects/prompt_ai_copy.md` (ganci, script a loop, caption, copertina) e
`projects/prompt_ai_montaggio.md` (montaggio e controlli dei primi 3 s). Aggiornali quando arrivano nuovi insight.

## Trial "Tacco si' o no" (16/11/2026, insight dopo ~15 ore)
3 versioni da 22-23 s, girate in camera a casa, titolo in alto + sottotitoli, copertina "TACCO SI' O NO? DIPENDE DA QUESTO".
- V1 gancio domanda "Il tacco ti aiuta?" (titoli IL TACCO AIUTA? / PUNTO DEBOLE): 199 views, salti 68,8%, media 5 s, 0 follow.
- V2 "Tacco si', tacco no" + "Jasmin squatta con il tacco... li alleno tutti e due io": 235 views, salti 55,1%, media 6 s, 0 follow.
- V3 "Jasmin: 200 kg di squat con il tacco, e Nicolo' non lo usa": 165 views, salti 51,4%, media 6 s, 0 follow.
Tutte: 97-100% non follower, Italia 92-96%, 25-34 la fascia piu' grande (13-17 dal 6% al 20%), 81-89% delle views dalla
tab Reels (la copertina li' non si vede: conta il primo fotogramma), 1 like/commento/salvataggio circa.
Lezioni: conferma che numero + caso reale batte la domanda (69% -> 51%), ma 51% e' ancora lontano dal 35%. Media 5-6 s:
la risposta va data entro 5 s, non alla fine. 22-23 s e' troppo. "Dipende" non e' una risposta: serve una presa di
posizione netta. Primo fotogramma = Manuel fermo in una stanza: il caso (200 kg) era detto, non mostrato -> si apre
sull'alzata vera. Due testi insieme nel primo secondo (titolo in alto + sottotitolo) = troppo da leggere.
Campione piccolo (~200 views per versione): differenze di pochi punti non sono affidabili, 69 vs 51 si'.
Rifacimento: `projects/brief_editor_novembre.md`, sezione 5.

## Rifacimento "Tacco o senza" (17/11/2026, insight dopo ~1 giorno) - PRIMO TRIAL SOTTO IL 35%
Stesso corpo, 14 s, split screen Jasmin col tacco | Nicolo' senza, musica GTA bassa. Cambia solo il gancio:
- A "Jasmin squatta 200 kg col tacco. Nicolo', senza." (etichette 200 KG | SENZA): 1.592 views, salti 30,1%, media 9 s
  su 14, 18 like, 7 commenti, 2 salvataggi, 0 follow; 90% dalla tab Reels; 13-17 18%, 18-24 31%, 25-34 36%; Italia 97%.
- B "Due miei atleti. Uno squatta col tacco..." (etichetta COL TACCO): 341 views, salti 38,0%, media 6 s, 0 follow.
Rispetto alle 3 versioni del 16/11 (51-69% di salti, 22-23 s): alzate vere nel primo fotogramma, 14 s, risposta entro
5 s ("decide la caviglia"), CTA binaria nei commenti (7 commenti).
A batte B solo per il gancio: numero + nome dell'atleta + contrasto in una frase, scritti con 1 parola per lato.
"Due miei atleti" senza numero = generico.
FORMULA VINCENTE (format "Due atleti, una scelta"): [Atleta 1] fa [kg] [scelta A]. [Atleta 2], [scelta B]. -> "Li
alleno tutti e due. Decide [fattore]." -> perche' per l'uno -> perche' per l'altro -> "Tu? Scrivimi A o B." -> ponte.
Problema rimasto: 0 follow anche a 1.600 views -> serve una promessa di serie (caption e copertina riconoscibile).
Nuovo contenuto con questa formula: `projects/brief_editor_novembre.md`, sezione 6.
Aggiornamento 18/11: A ~2.000 views, B ~580. Due persone che hanno commentato "tacco/senza" hanno poi scritto in DM,
una forse interessata al coaching: PRIMI DM DA UN REEL ORGANICO. La CTA binaria nei commenti apre la conversazione;
rispondere a ogni commento con una domanda personale che porta in DM (es. chiedere il loro video di squat).
Decisione: A condiviso nel feed ("Share to everyone"), B resta trial. Regola: un trial che scende sotto il 35% di salti
e porta commenti/DM va nel feed; gli altri restano trial.

## Puntata 2 "Giù o in alto" (dip, pubblicata 18/11 alle 21, insight il 19/11 pomeriggio)
14 s, split Lorenzo | Giacomo, "Decide il tuo punto debole", musica GTA bassa.
- A numero+nome "Lorenzo fa dip con 70 kg guardando giù. Giacomo, in alto.": 1.974 views, salti 27,3% (record), media
  10 s su 14, 10 like, 1 commento, 2 repost, 4 salvataggi, 5 visite profilo, 0 follow; 13-17 solo 1,2%, 18-24 39%,
  25-34 47%, 35-44 7,5%.
- B problema "Nel dip ti pianti in chiusura?": 1.920 views, salti 29,9%, media 9 s, 21 like, 1 commento, 2 salvataggi,
  4 visite profilo, 0 follow; 13-17 18,4%.
Lezioni: il format regge (2 puntate su 2 sotto il 30%). Numero + nome batte il problema sui salti e soprattutto sul
pubblico (adulti, quasi zero 13-17). Commenti calati (1 contro 7 del tacco): "giù o in alto" divide meno di "tacco o
senza". Visite profilo ~0,25% e follow 0: il format porta views, non ancora clienti -> prossimo reel con focus coaching.
A nel feed. Prossimo: `projects/brief_editor_novembre.md`, sezione 7.

## Idea in coda (19/11): trial "solo testo" sul tempo in palestra
Riferimento mandato da Manuel (reel inglese di un powerlifter, 12 s, solo testo sopra uno squat): "Il powerlifting non
ti ruba tempo, lo gestisci male" -> "30 minuti di riscaldamento, chiacchiere tra le serie, telefono: per questo ci metti
3 ore" -> "timer, riscaldamento mirato, recuperi solo quanto serve: 60-90 minuti". Manuel: farlo per gli atleti in
generale (non solo PL), come trial semplice. Testo in italiano, gancio provocatorio sul problema, 10-12 s, alzata vera
sotto. I numeri (60-90 minuti) vanno confermati da Manuel. Da fare dopo il reel "Ti fidi della tua scheda?".

## Puntata coaching "Ti fidi della tua scheda?" (Elisabetta, pubblicata 19/11 ~19:00, insight 20/11 9:30) - BOCCIATA
4 trial da 17 s:
- A "Ti fidi della tua scheda? Elisabetta all'inizio no." (sopra la sua trazione): 148 views, salti 72,1%, media 3 s.
- A + scheda animata ("la programmazione la decido io"): 150 views, salti 67,6%, media 3 s.
- B split PRIMA/OGGI "0 KG - Elisabetta non riusciva a fare una trazione...": 169 views, salti 54,2%, media 4 s, 2 visite.
- B + scheda animata: 163 views, salti 53,3%, media 4 s; pubblico 56% donne (gli altri ~70% uomini).
0 follow ovunque. Tacco e dip a pari ore avevano ~2.000 views.
Cause: gancio a domanda di nuovo pessimo (68-72%); il tema "fidarsi/metodo" è astratto, non c'è una scelta tecnica
con un numero forte; "da 0 a 10 kg" non colpisce un pubblico al 70% maschile intermedio; 17 s invece di 14; 4 versioni
quasi uguali lo stesso giorno (meglio massimo 2).
Lezione: il coaching NON va messo come tema del reel. Si mette DENTRO il format che funziona (atleta + numero forte +
scelta tecnica + "li alleno tutti e due"), nella caption e nelle risposte ai commenti (il tacco ha portato i DM cosi').
Rifacimento: `projects/brief_editor_novembre.md`, sezione 9.
Stato 20/11: le 4 versioni di Elisabetta sono ARCHIVIATE da Manuel (non cancellate). Nel pomeriggio: nuovo script per
Elisabetta (es. "Settimana 3: zero zavorra", brief 9b) + panca linea sul palmo (8a) + reel solo testo sul tempo (8b).
Rimontaggio Elisabetta (9 s, brief 9c, insight dopo ~5 ore, 20/11 15:50): A prima/dopo con contatore +10 KG: 143 views, salti 53% (dato da Manuel),
media 4 s su 9, 0 follow. B metodo prima ("Tu l'obiettivo, io il percorso"): 180 views, salti 63,4%, media 3 s,
3 commenti (uno di Elisabetta), 0 follow. Montaggio migliore non basta: il limite e' l'argomento (fiducia/metodo,
0->10 kg). Chiuso il tema: si passa a "Settimana 3: zero zavorra", panca linea sul palmo, reel solo testo sul tempo.

## Riferimento "in meno di 60 secondi" (mandato da Manuel 20/11, creator di marketing, 60 s)
Una sola ripresa in camera, sfondo neutro; in alto per 2 s il titolo-promessa ("COME ACQUISIRE CLIENTI SU INSTAGRAM IN
MENO DI 60 SECONDI"); in basso un grande cronometro rosso a cifre digitali che conta i secondi per tutto il video;
sottotitoli piccoli di 2-3 parole; nessun B-roll; finisce a 59 s. La tensione la crea il timer ("ce la fa?") e la
promessa precisa. Uso per Manuel: format "Il metodo in 30 secondi" (brief sez. 10): il coaching mostrato come
procedimento concreto, non come tema astratto. Da testare in trial contro il format "Due atleti, una scelta".
CONTENUTO del riferimento (quello che Manuel voleva far studiare, 20/11): non inseguire views e follower ma diventare
un riferimento per il potenziale cliente prima della vendita; i contenuti da soli non bastano: servono FLUSSI DI
ACQUISIZIONE che aprono chat ogni settimana con persone in target; farsi ricordare e riconoscere (dettagli); relazione
di fiducia, il motore e' l'allineamento sui valori; non fare il supereroe; cucire la comunicazione sul potenziale
cliente; ignorare i consigli decontestualizzati. Applicazione per Manuel: commenti a due risposte -> risposta con
domanda personale -> DM (gia' visto col tacco); parola chiave nei commenti per ricevere un protocollo (il protocollo
trazioni dato a 3 persone ha portato 1 cliente da 290 EUR); obiettivo di N conversazioni in target a settimana;
format, copertina, musica e frase ricorrenti ("Li alleno tutti e due") per essere riconoscibile.
Tre reel del 20/11 (metodo in 30 secondi con cronometro, panca linea sul palmo 150 kg, tempo in palestra):
`projects/brief_20nov_tre_reel.md`. Scarico = settimana di volume qualitativo a bassa intensità (Manuel).
CTA per reel (Manuel 20/11): ogni reel ha o la domanda a due risposte o la parola chiave nei commenti; Manuel risponde e
manda i protocolli a mano. Reel 1 = "Commenta TRAZIONI" (protocollo trazioni), reel 2 = dita/palmo, reel 3 = sopra/sotto 90 min.

## Insight 21/11/2026 (report completo: `projects/report_21nov.md`)
Panca A "Spingo 150 kg di panca" (alzata + 150 KG): 2.791 views, salti 31,3%, 8 s su 13, 33 like, 18 SALVATAGGI,
4 visite, 1 follow. Panca B (apre sulla mano): 137 views ma salti 26,3% (Instagram non l'ha distribuito: due video
quasi uguali pubblicati insieme, non e' un giudizio sul gancio). Tempo in palestra (solo testo "Allenarti non ti ruba
tempo. Lo perdi tu." sul suo squat): 1.676 views, 32,1%, 8 s su 13, 24 like, 3 commenti, 2 FOLLOW. Elisabetta
rimontata: 149-190 views, 53-65% (tema chiuso).
Lezioni: tre format che funzionano: tecnico con numero forte (views + salvataggi), scelta tra due atleti (commenti +
DM), testo che pizzica sul problema sopra un'alzata vera (follow). Media visione 8 s: risposta, consiglio e domanda
entro l'8° secondo; domanda anche come scritta a schermo, in caption e nel commento fissato. 13 s la durata buona.
Due versioni non insieme alla stessa ora. Messaggio di benvenuto personalizzato a ogni nuovo follower: ha portato una
candidatura (21/11). Pubblico 96-97% uomini, 25-34 al 40%.
