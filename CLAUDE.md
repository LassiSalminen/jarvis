# J.A.R.V.I.S. / U.L.T.R.O.N. — projektikonteksti

Puhu minulle suomeksi.

## Mikä tämä on
Henkilökohtainen tekoälyassistentti Lassille (v5.0). Yksi yhtenäinen
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
**Mallivalinta tehtävän mukaan**: mekaaniset JSON-kutsut (ruoan makroarvio,
ateriavaihtoehdot, tekniikkaohje) ajetaan `API_MODEL_FAST`illa
(Claude Haiku 4.5) — syy ei ole hinta vaan nopeus ja se että pienempi malli
lipsuu harvemmin selittämään JSONin ympärille. Persoona, luennot, ohjelman
generointi ja valmentajan kommentit pysyvät Sonnetilla, koska siellä laatu on
koko pointti. `askClaude(system,messages,max,model)` — neljäs parametri
valitsee mallin, ja varamalliketju toimii kummallakin polulla.
PIN kysytään laitteella ja elää vain localStoragessa — EI koskaan koodiin.
`WORKER_URL` on koodissa (ei salaisuus).

## Toiminnot (v5.0)
- **HUOM merkkijonot onclick-attribuutissa**: `ptAttr()` tuottaa JSON-lainaukset
  (`"arvo"`), joten se toimii VAIN yksinkertaisilla lainausmerkeillä rajatussa
  attribuutissa: `onclick='fn(${ptAttr(x)})'`. Kaksinkertaisissa lainausmerkeissä
  selain katkaisee attribuutin ensimmäiseen sisempään `"`-merkkiin ja onclickistä
  jää pelkkä `fn(` — nappi näyttää normaalilta mutta ei tee mitään. Näin oli
  rikki ravintohistorian päivän avaus ja treenin poisto (korjattu v5.0).
  Numeroargumentit (`fn(${i})`) eivät tarvitse ptAttria lainkaan.
- **Raaka-aineet grammoina** (`options[].items` = `[{n,m}]`): ateriavaihtoehto
  kertoo jokaisen raaka-aineen punnittavan määrän. `ptMealItems()` sietää myös
  merkkijonolistan ja vaihtoehtoiset kenttänimet, ja vanhat tallennukset (joissa
  aterian nimi oli itse ainesosaluettelo) renderöityvät ennallaan. Listat ovat
  kiinni oletuksena — 5 ateriaa × 3 vaihtoehtoa × 5 ainesosaa on 75 riviä —
  paitsi vuorossa olevalla aterialla. Määrät tallentuvat myös kirjaukseen,
  koska aterian nimi on nykyään lyhyt eikä kertoisi enää mitä söi.
- **Trendipaino** (`ptTrendWeight`, 7 pv liukuva keskiarvo): `ptCalcTargets`
  laskee kaiken trendistä, ei tämän aamun lukemasta. `profile.weight` pysyy
  viimeisimpänä punnituksena (se näkyy lomakkeessa), mutta yksi suolainen ilta
  ei enää siirrä kalorimäärää eikä merkitse ruokavaliota vanhentuneeksi.
  Saman päivän punnitus korvaa aiemman (`ptPushWeight`). Sama periaate kuin
  ravintohistorian 7 pv keskiarvossa: trendi kertoo suunnan, yksi aamu ei.
- **Usein syödyt** (`ptFavFoods`/`ptLogFav`): ravintohistoriasta kootaan
  vähintään kahdesti kirjatut ruoat nappilistaksi → kirjaus yhdellä
  napautuksella ilman tekoälykutsua, toimii offline. Makrot keskiarvoistetaan
  (sama ruoka on arvioitu eri kerroilla eri tavalla). Annoskerroin ½/1/1½/2
  koskee seuraavaa kirjausta ja palautuu ykköseen — pysyvä kerroin unohtuisi
  päälle. Kertoimella raaka-ainemäärät jätetään pois, koska ne pätevät vain
  täydelle annokselle.
- **Lepokello**: laskee päättymisaikaleimasta (`ptRestEnd`), ei tikeistä —
  taskussa näyttö sammuu ja selain hyllyttää ajastimet, jolloin vanha
  vähennyslaskuri jäi jälkeen. Värinä lopussa (`navigator.vibrate`), koska
  kelloa ei katsota vaan odotetaan. Lepoaika on liikekohtainen: ohjelman
  `rest`-kenttä voittaa, muuten `PT_COMPOUND`-nimitunnistus antaa
  perusliikkeille 150 s ja eristäville 90 s (vanhat ohjelmat saavat järkevän
  oletuksen ilman uudelleengenerointia).
- **Jumitus ja tauko painoehdotuksessa**: `ptStallCount` laskee montako treeniä
  sama paino on ollut jumissa; kolmen jälkeen ehdotus kevenee 10 % sen sijaan
  että toistaisi ikuisesti "pidä sama paino ja hae toistot loppuun". Yli 21 pv
  tauko keventää samoin. `ptDaysSinceWorkout` näkyy TÄNÄÄN-näkymässä ja yli
  5 päivän tauosta tulee huomautus — aloittelijalla käyntien loppuminen kaataa
  homman, ei ohjelmointi.
- **Uutiset**: tekoälysuodatus on parannus, ei ehto. Aiemmin sen kaatuminen
  tyhjensi näkymän tekstiin "Uutisten haku epäonnistui." vaikka otsikot olivat
  jo haettuna, eikä virhettä näkynyt missään. Nyt suodatus ajetaan
  `API_MODEL_FAST`illa kahdella yrityksellä, ja jos se ei vastaa, näytetään
  tuoreimmat otsikot sellaisenaan + kerrotaan miksi. Hakuvirhe kertoo syyn.
  **worker.js**: `YLE_TEKNOLOGIA` poistui käytöstä (feeds.yle.fi vastaa 400
  "Invalid publishers") → tilalle Tivi (tekniikka) ja ESS (Lahden seudun
  paikallisuutiset, joita suodatin pyysi mutta yksikään lähde ei tarjonnut).
  Per-lähde aikakatkaisu 8 s. **Vaatii workerin päivityksen Cloudflareen** —
  HTML toimii ilman sitä, vain tekniikkauutiset jäävät HN:n varaan.
- **Ruokamieltymykset** (`profile.diet/likes/dislikes/foodNotes/cooking`):
  erityisruokavalio, mitä syö mielellään, mitä ei syö, kokkausinto ja vapaat
  huomiot menevät ruokavalion promptiin. Ilman näitä ehdotukset ovat
  geneeristä broileria ja riisiä. Muokataan RUOKA → 🍽 MIELTYMYKSET.
- **Ruokavalion vanhentuminen**: `pt.meals` tallentaa mille tavoitteelle se
  koottiin (`forKcal`/`forProtein`). `ptMealsStale()` vertaa nykyiseen; yli
  100 kcal / 10 g heitto tai muuttuneet mieltymykset merkitsevät sen
  vanhentuneeksi. Tavoitteen vaihto (`ptSetGoalMode`, `ptSaveProfile`) kokoaa
  ruokavalion **automaattisesti uusiksi** — vanha ruokavalio vääriin
  kaloreihin on pahempi kuin ei ruokavaliota, koska se näyttää oikealta.
  Pieni heitto ei laukaise uudelleenkokoamista, jottei päivittäinen punnitus
  tee sitä turhaan.
- **HUOM tavoitteen ristiriita**: painotavoite (`goalWeight`) ja ruokavalion
  tavoite (`dietGoal`) ovat eri kenttiä ja voivat sotia keskenään — esim.
  tavoite pudottaa 12 kg mutta `dietGoal:'massa'` eli ylijäämä. Ennen v4.8
  TAVOITE-osio tulosti tästä nollia ("0 kg viikossa, 0 kuukautta") kertomatta
  mitään. `ptGoalHtml` käsittelee nyt neljä tapausta: normaali pudotus,
  **ristiriita** (punainen varoitus + korjausnapit `ptSetGoalMode`),
  lihominen (ylijäämä on tarkoitus) ja tavoitteessa. Älä palauta tilaa jossa
  nollat renderöityvät kuin ne olisivat oikea vastaus.
- **HUOM painotavoite ja vaje**: `ptCalcTargets` laskee kalorivajeen
  **viikkovauhtina kehonpainosta**, ei kiinteänä prosenttina: recomp 0,5 %/vko,
  rasvanpudotus 0,75 %/vko, rasvakilo = 7700 kcal. Turvaraja estää menemästä
  perusaineenvaihdunnan (tai 1500/1200 kcal) alle — liian jyrkkä vaje söisi
  lihasta, mikä on päinvastoin kuin tavoite. Vajeella proteiini nostetaan
  2,1 g/kg. Profiilissa on `goalWeight`; TAVOITE-osio näyttää laskennan auki
  (ylläpito → vaje → viikkovauhti → arvioitu kesto).
- **HUOM isot JSON-vastaukset**: älä pyydä yhtä jättimäistä JSONia. Ruokavalio
  (5 ateriaa × 3 vaihtoehtoa) katkesi token-kattoon ja katkennut JSON näytti
  samalta kuin täysi epäonnistuminen. Se pyydetään nyt **ateria kerrallaan**
  (5 pientä kutsua), jolloin yhden kaatuminen ei vie muita ja edistyminen
  näkyy. `ptParseJson` osaa myös korjata katkenneen vastauksen.
- **HUOM Claude-kutsut**: assistant-prefill EI toimi (Sonnet 5 palauttaa
  `invalid_request_error: This model does not support assistant...`).
  JSON-vastauksen tiukennus tehdään lisäohjeella käyttäjäviestissä.
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
  (`pt.meals`), mitoitettu osumaan päivän tavoitteeseen ja jokaisen
  raaka-aineen määrä grammoina; vaihtoehdon voi kirjata yhdellä
  napautuksella ilman uutta tekoälykutsua.
  **Ravintohistoria**: `pt.food` on aina sisältänyt päivämäärän, mutta
  kaikki lukupaikat suodattivat sen tähän päivään — historia oli tallessa
  mutta näkymätön (korjattu v4.7). `ptFoodByDay()` koostaa sen ja KEHITYS
  näyttää 14 päivän palkit, 7 pv liukuvan keskiarvon (se luku joka kertoo
  suunnan, ei yksittäinen päivä) ja päivän napautuksella sen ateriat.
  Historia menee myös buildContextiin, joten chat osaa vastata
  "paljonko söin eilen". Kehitys: liikekohtainen
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
