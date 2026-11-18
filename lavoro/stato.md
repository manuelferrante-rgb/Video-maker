# Stato del lavoro (montaggio con il prompt "montatore di reel" di Manuel, dal 16/11/2026)

Ambiente: sessione cloud (non il computer di Manuel). Il materiale arriva in chat o da Drive; gli originali
restano in `src_*/` (sola lettura), lavoro su copie; consegne in `out/<nome>/consegna/`.
Controlli iniziali (16/11): Playwright + Chromium OK; FFmpeg ha vidstabdetect/vidstabtransform e deshake. Niente da installare.

## Reel in corso: 3 trial di test
Copy: `projects/copy_trial_novembre.md`.
- Trial 1 tacco: copy pronto, in attesa del girato (squat con/senza tacco) + parlato (3 take del gancio).
- Trial 2 percentuali: in attesa della tesi + caso reale.
- Trial 3 Vincenzo: in attesa di dati (partenza, blocco, cambio, tempo) + ok genitori + video 160 kg. Solo stacco, niente dip (monotematico).

## Risposte di Manuel alle domande iniziali
- 16/11: Manuel ha mandato `projects/prompt_ai_copy.md` e `projects/prompt_ai_montaggio.md`: il copy si fa col primo,
  il montaggio col secondo. Quindi: B-roll si', titoli in alto + grafiche (dopo il gancio), sfx leggeri generati,
  sottotitoli standard, NIENTE musica (la mette Manuel su Instagram), copertina standard, controllo in 8 punti.
- Tipo di video: parlato in camera + B-roll suoi + grafiche a meta' (scelta mia secondo prompt_ai_montaggio).

## Font e colori
Sottotitoli Inter ExtraBold bianchi, accento arancio #E8662C; titoli Inter Black Italic; navy #14304F, avorio #F2EEE3.

## Decisione 16/11 (trial tacco)
Copy definitivo: v5 in `projects/copy_trial_novembre.md`. Consegnare 3 VIDEO, uno per gancio (1, 2, 3), stesso montaggio
dopo il gancio, stessa durata il piu' possibile, stessa copertina e caption: Manuel li pubblica tutti e 3 come trial.
In attesa: parlato (3 ganci + corpo) e B-roll Jasmin con/senza tacco, Nicolo' gara, da dietro, box squat westside.

## 16/11 consegnato: trial tacco, 3 versioni (out/tacco/tacco_gancio1-3.mp4), copertina, caption (projects/caption_tacco.txt)
Durate 23,6 / 23,9 / 22,7 s, -14,2 LUFS, picco -1,2 dB. Script `projects/tacco.py`, copertina `projects/cover_tacco.py`.
Da confermare: @ di Jasmin e Nicolo', ok scritto; b4 e' a bassa risoluzione (256x480), usato solo in riquadro.

## 17/11 rifacimento "Tacco o senza" (brief sez. 5, branch festive-darwin mergiato)
Pronti: copertina `projects/cover_tacco_v2.py` (bozza col fotogramma del vecchio parlato), caption `projects/caption_tacco_v2.txt`.
In attesa: nuovo parlato (gancio A e B + corpo), video Jasmin 200 kg (nel repo del sito, non accessibile da qui:
chiesto a Manuel), conferma delle frasi su Jasmin "busto dritto" e Nicolo' "col tacco si sbilancia" (non dette da lui).
Nicolo' senza tacco: c'e' gia' b2 (gara). Montaggio max 18 s, primo fotogramma split screen con la voce sopra.
17/11 consegnato rifacimento: out/tacco_v2/tacco_v2_A.mp4 e _B.mp4 (14,3 s, -14,4 LUFS, picco -1,4), copertina
out/tacco/copertina_tacco_v2.jpg (fotogramma 34,9), caption projects/caption_tacco_v2.txt.

## 18/11 passaggio a una nuova chat: istruzioni in projects/handoff_18nov.md
