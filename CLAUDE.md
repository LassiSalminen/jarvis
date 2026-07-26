# J.A.R.V.I.S. / U.L.T.R.O.N. — projektikonteksti

Puhu minulle suomeksi.

## Mikä tämä on
Henkilökohtainen tekoälyassistentti Lassille (v3.5). Yksi yhtenäinen
käyttöliittymä: chat + HUD + henkilökohtainen tietopankki (PKB) + oppiminen
+ PT (treeni & ravinto).
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

## Toiminnot (v3.5)
- **Chat**: persoonamoodit, markdown-renderöinti (mdRender, XSS-suojattu),
  historia säilyy localStoragessa yli latausten, yritä uudelleen -nappi,
  pikatoiminto-chipit (tilanne/treeni/sää/sähkö/uutiset). 👍-nosto → rawLog.
- **Konteksti** (buildContext): NYT-tilannekuva (wiki-id `nyt-konteksti`),
  relevantit wiki-sivut avainsanahaulla, Garmin-data + historia, sää +
  3 pv ennuste, sähkön spot + halvin tunti, uutiset.
- **Knowledge**: kaatopaikka (raaka syöte → Claude jäsentää wiki-sivuiksi;
  iso syöte pilkotaan otsikko-/kappalerajoista osiin ja käsitellään peräkkäin)
  + yhteenveto-välilehti. Tiedostot: txt/md/pdf/kuvat/audio.
  "Kokoa päivä" klo 21 + automaattisiivous (pruneWiki) — järjestelmäsivut
  `nyt-konteksti` ja `yleiskatsaus` on suojattu siivoukselta.
- **Oppi**: SM-2-kertausalgoritmi, päiväputki. **Luennot**: generointi
  pituusvalinnalla (tiivis/normaali/syvä) ja lukujen jatkuvuudella
  (punainen lanka + edellisen luvun loppu promptissa); HQ-ääni (Google TTS
  `/api/gtts`) ladataan automaattisesti generoinnin perään IndexedDB:hen →
  offline-kuuntelu; soittimessa ±15 s kelaus ja lukuvalikko;
  Media Session → lukitusnäytön/kuulokkeiden ohjaimet; keskeytynyt
  generointi jatkuu luonnoksesta (jarvis:lectureDraft) ja äänilataus
  ohittaa jo ladatut luvut; ❓-nappi luo luennosta kertauskortit Oppi-
  putkeen (SM-2); e-kirjalukutila; navigator.storage.persist() suojaa
  äänet tyhjennykseltä; fallback Web Speech.
- **Offline (reissutila)**: wiki + luennot peilataan localStorageen →
  listat toimivat ilman verkkoa; "Lataa kaikki HQ-äänet" -massalataus +
  tallennustilan näyttö luentolistassa; Oppi-kertaukset toimivat offline
  vaikka uuden oppitunnin haku epäonnistuu; sw.js cachettaa myös ikonit
  ja CDN-resurssit (fontit, pdf.js).
- **PT (Treeni)**: oma välilehti, alavälilehdet TÄNÄÄN / OHJELMA / RUOKA /
  KEHITYS. Claude generoi kuntosaliohjelman (aloittelija, 3× vk, perusliikkeet);
  treenin kirjaus prefiltteröi painot edellisestä kerrasta ja ehdottaa
  +1,25/2,5 kg kun kaikki toistot menivät ylärajaan; lepokello sarjan
  kuittauksesta; kesken oleva treeni säilyy localStoragessa (`jarvis:ptSession`)
  → salin kellarissa verkon katkeaminen ei hukkaa sarjoja. Garminin
  treenivalmius säätää päivän suositusta. Ravinto: Mifflin–St Jeor laskee
  kcal/proteiini/hiilari/rasva paikallisesti (toimii offline), ruoan kirjaus
  arkikielellä → Claude arvioi makrot, ateriaehdotukset. Kehitys: liikekohtainen
  painonnousu, kokonaiskuorma, paino, historia. Valmentajan kommentti
  tallennuksen jälkeen (ei estä tallennusta jos verkko pätkii).
  **Tallennus**: koko PT-tila on yhdessä wiki-sivussa (`pt-data`, body = JSON)
  → synkkaa laitteiden välillä olemassa olevalla `/api/wiki`-endpointilla,
  workeriin EI tarvittu mitään uutta. Sivu on piilotettu tietopankin listalta,
  siivoukselta, yleiskatsaukselta ja chatin wiki-haulta (`userWiki()`);
  chattiin menee sen sijaan luettava tiivistelmä buildContextissa.
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
Kun toiminnallisuus muuttuu, nosta `jarvis.html`:n `VERSION`-vakiota ja pidä
CLAUDE.md:n versionumero samana (BUILD päivittyy itsestään).
HUOM: worker.js-muutokset eivät tule voimaan ennen kuin Lassi päivittää
workerin Cloudflareen käsin — älä riko HTML:ää workerin uusilla endpointeilla
ilman fallbackia.

## Seuraavat askeleet
MUISTI-ARKKITEHTUURI.md:n siirtymäpolku: privaatti jarvis-knowledge-repo →
Python-työkalut (lint/rebuild/consolidate) → retrieve()-endpoint Workeriin →
automaattinen muistilouhinta keskusteluista (confidence/importance/source).
