# Image Converter GUI

Applicazione desktop per la conversione di immagini nei formati WebP e AVIF con generazione di multiple risoluzioni.

## Tech Stack

- **Python 3.12+**
- **Tkinter** (GUI builtin)
- **tkinterdnd2** - Drag & drop support
- **Pillow** - Elaborazione immagini
- **pillow-avif-plugin** - Supporto formato AVIF

## Struttura del Progetto

```
imgconverter/
├── main.py         # Entry point
├── converter.py   # Logica conversione immagini
├── gui.py         # Interfaccia GUI (Tkinter)
├── config.py     # Configurazione e gestione impostazioni
├── version.py    # Versione applicazione
├── build.sh      # Script per compilare eseguibile
└── requirements.txt
```

## Funzionamento

### Input
- Drag & drop: cartella o singolo file
- Dialog: selezione cartella o file
- Formati supportati: PNG, JPG, JPEG, BMP, TIFF, TIF, WEBP, AVIF, GIF, HEIC, HEIF

### Elaborazione
1. Rileva file immagine nella cartella sorgente
2. Per ogni file genera **5 versioni**:
   - `{nome}.webp` - originale convertito
   - `{nome}_large.webp`
   - `{nome}_medium.webp`
   - `{nome}_small.webp`
   - `{nome}_x-small.webp`
3. Threading parallelo per conversione veloce

### Opzioni Output
- **Cartella output**: personalizzabile o stessa del sorgente
- **Prefisso filename**: aggiungi prefisso ai file convertiti
- **Sovrascrivi**: sovrascrivi file esistenti
- **Skip esistenti**: salta file già convertiti
- **Prefisso**: aggiungi prefisso al nome file

### Formati Output
- WebP (nativo Pillow)
- AVIF (via pillow-avif-plugin)
- Entrambi

### Compressione
- Qualità configurabile: slider 0-100%
- Default: 90%

### Ridimensionamento
- Scala per larghezza (aspect ratio preservato)
- Metodo: LANCZOS, BICUBIC, BILINEAR, NEAREST
- Dimensioni configurabili:
  - Large: 1200px
  - Medium: 800px
  - Small: 400px
  - X-Small: 200px

### Extra
- **Export/Import config**: salva e carica configurazioni
- **Lista file**: visualizza file selezionati con stato
- **Log**: dettagli conversione con errori
- **Cancel**: annulla conversione in corso

## Interfaccia GUI

```
+------------------------------------------+
|  Image Converter v1.0.0                  |
+------------------------------------------+
|  [Cartella] [File] [Export] [Import]      |
|  +------------------------------------+  |
|  |   DROP FOLDER OR FILE HERE         |  |
|  +------------------------------------+  |
|  Formato: ( ) WebP ( ) AVIF ( ) Entrambi |
|  Qualità: [-----●-----] 90%            |
|  Cartella: [..........] [...]           |
|  Prefisso: [......] [✓Sovrascrivi][✓Skip] |
|  Dimensioni: [Large:1200] [Medium:800]  |
|  [Small:400] [X-Small:200] [Metodo:▼]   |
|  File: [img1.png] [img2.jpg] ...       |
|  [CONVERTI] [ANNULLA]                  |
|  [========--------] 66%               |
|  Log: ✓ img1.png: Convertiti 5 file   |
|  ✗ img2.jpg: Errore...               |
+------------------------------------------+
```

## Dipendenze

```
Pillow>=10.0.0
pillow-avif-plugin>=1.0.0
tkinterdnd2>=0.4.0
```

## Build Eseguibile

Per compilare l'eseguibile:

```bash
./build.sh
```

L'eseguibile viene generato in: `dist/ImageConverter`

## Versione

La versione è definita in `version.py`. Modificare il file e ricompilare per aggiornare.

## Configurazione

Le impostazioni utente vengono salvate in: `~/.imgconverter/config.json`

Per esportare/importare configurazioni:
- Usa i pulsanti "📤 Esporta Config" e "📥 Importa Config"