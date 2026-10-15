# Music Archives Italia — Archivio musicale indipendente

Portale editoriale in lingua italiana, a cura di Salvatore Sinatra, dedicato a sei progetti musicali:

1. Mylène Farmer
2. Assemblage 23
3. MESH
4. Sandra
5. The Birthday Massacre
6. Ville Valo / HIM / VV / Heartagram

## Heartagram Italia v1.1 — edizione aggiuntiva (15 ottobre 2026)

La sezione **Ville Valo / HIM / Heartagram** dell'archivio v13.1 rimane intatta.

In aggiunta, il workflow GitHub Pages integra un adattamento statico della homepage **Heartagram Italia v1.1**, sulla base dei contenuti recuperati dal progetto Sites:

- Pagina nuova GitHub Pages: https://salvatoresinatra0001-ux.github.io/music-archives-italia/heartagram-italia/
- Sezione preesistente preservata: https://salvatoresinatra0001-ux.github.io/music-archives-italia/ville-valo-him-heartagram-italia/
- Sito Sites integrale di riferimento: https://heartagram-italia-v11.free-trail-0346.chatgpt.site/
- Sorgenti adattamento/istruzioni per futura repository autonoma: [heartagram-italia/](heartagram-italia/)

Il workflow aggiunge anche un collegamento alla nuova edizione dentro la pagina storica. La nuova pagina non è un'esportazione esatta e completa del progetto Sites: immagini, sottopagine e funzioni non disponibili come codice sorgente **non sono state replicate**.

**Repository autonoma prevista:** "salvatoresinatra0001-ux/heartagram-italia". I file necessari sono già predisposti nella sottocartella sopra; la nuova repository deve ancora essere creata e configurata manualmente.

## Stato

**GitHub Pages attivo.** Il deployment del pacchetto v13.1.0 è risultato riuscito il 15 ottobre 2026. La nuova edizione Heartagram v1.1 viene pubblicata dal workflow aggiornato; verificare la relativa esecuzione dopo le modifiche.

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
