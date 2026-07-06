# J.A.R.V.I.S. / U.L.T.R.O.N. — projektikonteksti

Puhu minulle suomeksi.

## Mikä tämä on
Henkilökohtainen tekoälyassistentti Lassille (v3.2). Yksi yhtenäinen
käyttöliittymä: chat + HUD + henkilökohtainen tietopankki (PKB) + oppiminen.
Tabletille (vanha Honor Android) ja muille laitteille, asennetaan PWA:na.
Kaksi persoonaa: U.L.T.R.O.N. (oletus, synkkä sarkasmi) ja J.A.R.V.I.S.
(kohtelias hovimestari) — vaihdettavissa käyttöliittymästä.

## Tiedostot
- `jarvis.html` — koko käyttöliittymä (HTML/CSS/JS yhdessä tiedostossa).
  Julkaistaan GitHub Pagesiin: https://lassisalminen.github.io/jarvis/jarvis.html
- `worker.js` — Cloudflare Worker: (1) proxy Claude APIin (avain palvelimella),
  (2) wiki KV:hen → sama muisti kaikilla laitteilla, (3) uutisfeed,
  (4) ElevenLabs TTS + Scribe-transkriptio, (5) Garmin-synkkaus.
  EI koskaan GitHubiin (.gitignore hoitaa).
- `manifest.json`, `sw.js`, ikonit — PWA (network-first-cache).
- `MUISTI-ARKKITEHTUURI.md` — pitkän aikavälin muistijärjestelmän spesifikaatio.
- `ASENNUS.md` — pystytysopas.

## Arkkitehtuuri
UI (GitHub Pages) → Cloudflare Worker → Claude API + KV-muisti.
Malli: Claude Sonnet 5, automaattinen fallback Sonnet 4.6:een (`API_MODEL`).
PIN kysytään laitteella ja elää vain localStoragessa — EI koskaan koodiin.
`WORKER_URL` on koodissa (ei salaisuus).

## Toiminnot (v3.2)
- **Chat**: persoonamoodit, markdown-renderöinti (mdRender, XSS-suojattu),
  historia säilyy localStoragessa yli latausten, yritä uudelleen -nappi,
  pikatoiminto-chipit (tilanne/treeni/sää/sähkö/uutiset). 👍-nosto → rawLog.
- **Konteksti** (buildContext): NYT-tilannekuva (wiki-id `nyt-konteksti`),
  relevantit wiki-sivut avainsanahaulla, Garmin-data + historia, sää +
  3 pv ennuste, sähkön spot + halvin tunti, uutiset.
- **Knowledge**: kaatopaikka (raaka syöte → Claude jäsentää wiki-sivuiksi)
  + yhteenveto-välilehti. Tiedostot: txt/md/pdf/kuvat/audio.
  "Kokoa päivä" klo 21 + automaattisiivous (pruneWiki) — järjestelmäsivut
  `nyt-konteksti` ja `yleiskatsaus` on suojattu siivoukselta.
- **Oppi**: SM-2-kertausalgoritmi, päiväputki. **Luennot**: generointi +
  TTS-toisto (ElevenLabs/Web Speech), e-kirjalukutila, audio IndexedDB:ssä.
- **Uutiset**: worker hakee, Claude suodattaa kiinnostusten mukaan.
- **Sijoitus**: salkku + live-kurssit + AI-arviot (ei sijoitusneuvontaa).
- **HUD**: arc reactor, sää+ennuste, sähkö+halvin tunti, Garmin, mittarit.
- **Varmuuskopio**: vie/tuo JSON (mobiili-INFO-välilehti).

## Suunnitteluperiaatteet (tärkeää)
- Lassi EI halua olla "librarian" — tekoäly hoitaa organisoinnin automaattisesti.
- Yksi yhtenäinen käyttöliittymä on kova vaatimus.
- Mahdollisimman vähällä vaivalla mahdollisimman hyvä tulos.
- Tumma UI: leipäteksti neutraali + vaalea, väri vain aksenttina.

## Estetiikka
Arc reactor -animaatio, navy + moodiväri (ULTRON punainen / JARVIS cyan),
Orbitron + Share Tech Mono, HUD-tunnelma.

## Julkaisu (git)
Kun muokkaat julkaistavia tiedostoja (`jarvis.html`, `manifest.json`, `sw.js`,
ikonit), committaa ja pushaa muutokset GitHubiin automaattisesti muokkauksen
jälkeen — GitHub Pages päivittyy pushista. `worker.js` EI koskaan GitHubiin.
Muutosten jälkeen: aja `node --check` irrotetulle skriptilohkolle ennen pushia.
HUOM: worker.js-muutokset eivät tule voimaan ennen kuin Lassi päivittää
workerin Cloudflareen käsin — älä riko HTML:ää workerin uusilla endpointeilla
ilman fallbackia.

## Seuraavat askeleet
MUISTI-ARKKITEHTUURI.md:n siirtymäpolku: privaatti jarvis-knowledge-repo →
Python-työkalut (lint/rebuild/consolidate) → retrieve()-endpoint Workeriin →
automaattinen muistilouhinta keskusteluista (confidence/importance/source).
