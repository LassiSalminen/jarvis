# J.A.R.V.I.S. — projektikonteksti

Puhu minulle suomeksi.

## Mikä tämä on
Henkilökohtainen tekoälyassistentti Iron Man -hengessä, Lassille.
Yksi yhtenäinen käyttöliittymä: chat + HUD + henkilökohtainen tietopankki (PKB).
Tabletille (vanha Honor Android) ja muille laitteille, asennetaan PWA-sovelluksena.

## Tiedostot
- `jarvis-deploy.html` — koko käyttöliittymä (HTML/CSS/JS yhdessä tiedostossa).
  Julkaistaan GitHub Pagesiin, nimetään julkaistaessa `jarvis.html`.
- `worker.js` — Cloudflare Worker. Hoitaa: (1) proxy Claude APIin niin että
  API-avain pysyy palvelimella, (2) wikin tallennus KV:hen → sama muisti kaikilla
  laitteilla. EI tule GitHubiin, vaan Cloudflareen.
- `manifest.json` — PWA-manifesti (kokoruututila tabletilla).
- `ASENNUS.md` — täydellinen pystytysopas. Seuraa tätä.

## Arkkitehtuuri
Käyttöliittymä (GitHub Pages) → Cloudflare Worker → Claude API + KV-muisti.
`jarvis-deploy.html`:n alussa on `WORKER_URL` ja `JARVIS_PIN` jotka pitää täyttää.

## Toiminnot
- Chat: J.A.R.V.I.S.-persoona, suomeksi, puhuttelee "Lassi"/"sir". Web Speech API (fi-FI).
- Knowledge: Karpathy-tyylinen PKB. Raaka syöte → Claude organisoi wiki-sivuiksi
  (otsikko, tiivistelmä, body, tagit). Reititys: kysymys vs. uusi tieto.
- Chat-viesteistä voi nostaa 👍 → tallentuu raakalokiin.
- "Kokoa päivä" (+ automaattinen klo 21): tekee päiväkirjamerkinnän ja poimii
  opit pysyviksi wiki-sivuiksi.
- Sää: Open-Meteo (Nastola, ei API-avainta).

## Suunnitteluperiaatteet (tärkeää)
- Lassi EI halua olla "librarian" — tekoäly hoitaa kaiken organisoinnin automaattisesti.
- Yksi yhtenäinen käyttöliittymä on kova vaatimus.
- Mahdollisimman vähällä vaivalla mahdollisimman hyvä tulos.

## Estetiikka
Arc reactor -animaatio, navy + cyan, Orbitron + Share Tech Mono -fontit, HUD-tunnelma.

## Julkaisu (git)
Kun muokkaat julkaistavia tiedostoja (`jarvis.html`, `manifest.json`, `sw.js`,
ikonit), committaa ja pushaa muutokset GitHubiin automaattisesti muokkauksen
jälkeen — GitHub Pages päivittyy pushista. `worker.js` EI koskaan GitHubiin
(.gitignore hoitaa tämän).

## Seuraavat askeleet
Pystytys ASENNUS.md:n mukaan: API-avain → Cloudflare Worker + KV → WORKER_URL
HTML:ään → GitHub Pages → asennus sovelluksena laitteille.
