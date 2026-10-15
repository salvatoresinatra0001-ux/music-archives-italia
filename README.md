# Music Archives Italia — Archivio musicale indipendente

Portale editoriale in lingua italiana, a cura di Salvatore Sinatra, dedicato a sei progetti musicali:

1. Mylène Farmer
2. Assemblage 23
3. MESH
4. Sandra
5. The Birthday Massacre
6. Ville Valo / HIM / VV / Heartagram

## Stato

**Repository pubblico predisposto per GitHub Pages.** La pubblicazione dei siti è prevista a partire dai pacchetti locali `v13.1.0`. Il sito non deve essere considerato pubblicato fino al completamento del caricamento dell'archivio e di un deployment GitHub Pages riuscito.

## Modalità consigliata di distribuzione

Il repository utilizza un workflow GitHub Actions che estrae e verifica **un unico archivio ZIP di distribuzione** denominato:

`music-archives-italia-v13.1-GITHUB-PAGES-REPOSITORY-PRONTO.zip`

L'archivio deve contenere alla radice `index.html` e le cartelle:

- `mylene-farmer-italia/`
- `assemblage23-italia/`
- `mesh-italia/`
- `sandra-music-italia/`
- `thebirthdaymassacre-italia/`
- `ville-valo-him-heartagram-italia/`

Per pubblicare:

1. Caricare tramite **Add file → Upload files** il file ZIP indicato nella radice di `main`.
2. Aprire **Settings → Pages → Build and deployment** e selezionare **GitHub Actions** come origine di pubblicazione.
3. Aprire **Actions → Distribuisci Music Archives Italia** e avviare **Run workflow** se non è partito automaticamente.
4. Verificare che tutti i siti funzionino e che l'indirizzo Pages risponda con codice 200.

URL previsto dopo la pubblicazione: https://salvatoresinatra0001-ux.github.io/music-archives-italia/

## Note editoriali e legali

- Progetto indipendente e non affiliato agli artisti.
- Il materiale fotografico, musicale, i marchi e le copertine sono di proprietà dei rispettivi aventi diritto. Utilizzare solamente file con diritti e licenze adeguati.
- Le edizioni v13.1 includono indicazioni temporanee `noindex`, mantenute fino alla revisione finale.
- GitHub Pages pubblica il sito su Internet; il repository è pubblico.
- Gli archivi storici rimangono contenuti nel pacchetto sorgente. Il workflow esclude la directory `storico/` dall'artefatto web per non distribuire inutilmente archivi ZIP precedenti.

## Versionamento

`v13.1.0`: edizione prepubblicazione dei sei siti HTML, consultabile anche localmente.

## Gestione

Salvatore Sinatra — progetto indipendente, Italia.
