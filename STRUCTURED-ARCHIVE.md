# Music Archives Italia — Structured Editorial Archive v3.0

Archivio musicale italiano indipendente a cura di Salvatore Sinatra.

## Modello dati
Il file `data/catalog.json` definisce sei artisti, pubblicazioni e fonti. Le pubblicazioni possono essere `pending` oppure `verified`; quelle verificate richiedono almeno un riferimento a una fonte presente nell'archivio. Nessun record discografico è stato inventato o marcato come verificato senza fonti.

## Generazione e controlli
`python3 scripts/build_archive.py --output _site` valida i dati, genera `catalogo.html` per ciascun artista e crea `sitemap.xml` e `robots.txt`. Il workflow GitHub Pages esegue il generatore prima del deployment: dati invalidi bloccano la pubblicazione.

## Prossimo popolamento
Per ciascuna edizione aggiungere identificativo univoco, titolo, anno, tipologia, stato di verifica e riferimenti a fonti HTTPS. Consultare `EDITORIAL-STANDARD.md` per criteri di attribuzione e diritti.
