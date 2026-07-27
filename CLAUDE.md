# J.A.R.V.I.S. / U.L.T.R.O.N. — projektikonteksti

Puhu minulle suomeksi.

## Mikä tämä on
Henkilökohtainen tekoälyassistentti Lassille (v4.2). Yksi yhtenäinen
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

## Toiminnot (v4.2)
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
  **Luentoäänen luonnollisuus (v4.0)**: teksti valmistellaan puheeksi ennen
  lähetystä. `speechify()` poistaa markdownin (muuten ääni lukee tähdet ja
  otsikkoristit), avaa lyhenteet (esim.→esimerkiksi, n.→noin, %→prosenttia)
  ja nostaa luetelmakohdat omiksi kappaleikseen — pelkkä viivan poisto
  sulautti ne edelliseen virkkeeseen yhdeksi puuroksi. `ttsSsml()` merkitsee
  kappale- ja lauserajat `<break>`-tauoiksi. `splitSpeechText()` pilkkoo
  kappaleista (vanha `splitTextForTTS` liitti palat välilyönnillä ja hävitti
  kappalerajat); pala 2600 tavua, koska SSML kasvattaa kokoa ja Googen raja
  on 5000. Ääniasetukset LUENNOT-välilehdellä: ääni, puhenopeus (oletus
  0.92), taukojen pituus + näytteen kuuntelu; tallentuu `jarvis:tts`.
  **Fallback**: payloadissa lähetetään AINA sekä `text` että `ssml` — vanha
  worker käyttää `text`iä ja jättää `ssml`:n huomiotta, joten mikään ei
  rikkoudu ennen workerin päivitystä. Uusi worker kokeilee portaittain
  halutun äänen SSML:llä → sama ääni tekstinä → Wavenet SSML:llä, ja
  kertoo `X-TTS-Voice`-otsakkeessa mitä oikeasti käytettiin (kaikki äänet
  eivät tue SSML:ää, mm. Chirp-HD ottaa vain tekstiä).
- **Offline (reissutila)**: wiki + luennot peilataan localStorageen →
  listat toimivat ilman verkkoa; "Lataa kaikki HQ-äänet" -massalataus +
  tallennustilan näyttö luentolistassa; Oppi-kertaukset toimivat offline
  vaikka uuden oppitunnin haku epäonnistuu; sw.js cachettaa myös ikonit
  ja CDN-resurssit (fontit, pdf.js).
- **PT (Treeni)**: oma välilehti, alavälilehdet TÄNÄÄN / OHJELMA / RUOKA /
  KEHITYS. Claude generoi kuntosaliohjelman (aloittelija, 3× vk, perusliikkeet);
  **HUOM lukusyötteet**: painot ja toistot ovat `type="text"` +
  `inputmode="decimal"`, EIVÄT `type="number"`. Numerokenttä hylkää
  desimaalipilkun, joten suomalaisella näppäimistöllä kirjoitettu "42,5"
  muuttui tyhjäksi ja paino katosi hiljaa (korjattu v4.1). `ptNum()` hoitaa
  pilkun. Älä palauta `type="number"`ia.
  Mallin palauttama ohjelma normalisoidaan `ptNormalizeProgram()`illa
  (sets merkkijonona, reps numerona, nimetön päivä, tyhjä liikelista) —
  yksi outo kenttä rikkoisi muuten koko treeninäkymän.
  Väärin kirjatun treenin voi poistaa KEHITYS-välilehden historiasta;
  ilman sitä lipsahdus jäisi vääristämään painoehdotuksia pysyvästi.
  Treenin kesto tallentuu (`dur`) ja näkyy historiassa.
  treenin kirjaus prefiltteröi painot edellisestä kerrasta ja ehdottaa
  +1,25/2,5 kg kun kaikki toistot menivät ylärajaan; lepokello sarjan
  kuittauksesta; kesken oleva treeni säilyy localStoragessa (`jarvis:ptSession`)
  → salin kellarissa verkon katkeaminen ei hukkaa sarjoja. Garminin
  treenivalmius säätää päivän suositusta. Treeninäkymässä kiinteä
  edistymispalkki (x/y sarjaa), liikkeet numeroituna, nykyinen liike
  korostettuna ja valmiit himmennettynä; edistyminen päivittyy ilman
  uudelleenpiirtoa, joten syötekentän kohdistus ja vieritys eivät hyppää.
  Alavälilehdet toimivat myös kesken treenin (paluupalkki + PALAA-nappi) —
  ohjelmaa ja ravintoa voi vilkaista sarjojen välissä hylkäämättä treeniä.
  Liikkeissä ▶ VIDEO (YouTube-haku, ei yksittäinen video → ei rikkoudu) ja
  ⓘ TEKNIIKKA (Claude-ohje, tallentuu `pt.tech` → toimii sen jälkeen offline).
  Ravinto: Mifflin–St Jeor laskee kcal/proteiini/hiilari/rasva paikallisesti
  (toimii offline), ruoan kirjaus arkikielellä → Claude arvioi makrot.
  Ruokavalio vaihtoehtoineen: 5 ateriaa × 3 vaihtoehtoa makroineen
  (`pt.meals`), mitoitettu osumaan päivän tavoitteeseen; vaihtoehdon voi
  kirjata yhdellä napautuksella ilman uutta tekoälykutsua. Kehitys: liikekohtainen
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
- **Garmin-synkkaus**: worker EI hae Garminista mitään — se lukee vain KV:n
  arvon, jonka GitHub Actions (`.github/workflows/garmin-sync.yml` +
  `scripts/garmin_sync.py`) sinne työntää. Ajo **3 h välein** (cron
  `7 */3 * * *`). Ei yritetä osua kellonaikoihin: GitHubin ajastusjono
  viivästyttää ajoja tässä repossa johdonmukaisesti 2,5–3 h (mitattu:
  cron 03:00 UTC → ajot 05:35–06:06 UTC seitsemän päivän ajan), joten
  tarkat kellonajat ovat saavuttamattomissa — tiheys ratkaisee oikean
  ongelman. Skripti kierrättää Garmin-istuntotokenin KV:n kautta
  (`/api/garmintoken`), joten tiheämpi ajo ei tarkoita kahdeksaa
  kirjautumista; yksi ajo kestää ~30 s. Sovelluksen ⟳ PÄIVITÄ lukee vain KV:n uudestaan — se
  EI voi tehdä datasta tuoreempaa; tuoreus näkyy `updated`-leimasta
  ("35 min sitten"). Haku uusitaan myös kun sovellus palaa etualalle
  (>10 min) ja 30 min välein. Käsiajo: Actions → Garmin sync → Run workflow.
  **⚡ SYNKKAA** laukaisee oikean haun: sovellus → workerin
  `POST /api/garminsync` → GitHub `workflow_dispatch` → sama workflow kuin
  ajastuksella (logiikka pysyy yhdessä paikassa). Worker tarvitsee
  `GITHUB_TOKEN`-secretin (fine-grained PAT, Actions: Read and write).
  Sovellus pollaa `updated`-leimaa 10 s välein max 5 min ja poimii uuden
  datan itsestään. Fallback on kunnossa: 404 → "workeria ei ole päivitetty",
  501 → "GITHUB_TOKEN puuttuu", 502 → GitHubin virhe + ohje käsiajoon.
  Asennusohje: ASENNUS.md kohta 2e.
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
