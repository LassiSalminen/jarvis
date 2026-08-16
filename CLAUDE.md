# J.A.R.V.I.S. / U.L.T.R.O.N. — projektikonteksti

Puhu minulle suomeksi.

## Mikä tämä on
Henkilökohtainen tekoälyassistentti Lassille (v6.6). Yksi yhtenäinen
käyttöliittymä: chat + HUD + henkilökohtainen tietopankki (PKB) + oppiminen
+ PT (treeni & ravinto).
Tabletille (vanha Honor Android) ja muille laitteille, asennetaan PWA:na.
Kaksi persoonaa: U.L.T.R.O.N. (oletus, dark triad) ja J.A.R.V.I.S.
(kohtelias hovimestari) — vaihdettavissa käyttöliittymästä.

## Tiedostot
- `jarvis.html` — koko käyttöliittymä (HTML/CSS/JS yhdessä tiedostossa).
  Julkaistaan GitHub Pagesiin: https://lassisalminen.github.io/jarvis/jarvis.html
- `wrangler.toml` — workerin julkaisuasetukset. **Deploy tehdään komennolla
  `npx wrangler deploy`**, ei enää kopioimalla koodia Cloudflaren Edit code
  -ruutuun. Unohtunut deploy oli tämän projektin toistuvin vika.
  **HUOM arvot on luettu Cloudflaresta** (`wrangler versions view`), ei
  kirjoitettu muistista: `wrangler deploy` asettaa bindingit ja ajastukset
  tämän tiedoston mukaan, joten puuttuva rivi ei jätä asetusta ennalleen vaan
  **poistaa sen**. Jos `JARVIS_KV` katoaisi, koko tietopankki katkeaisi
  sovelluksesta ilman että mikään kertoisi syytä.
  Secretit eivät ole täällä eivätkä saa olla — ne elävät Cloudflaressa
  erillään eikä deploy koske niihin. `account_id` jätetty pois, jottei
  tunniste päädy julkiseen repoon. `preview_urls = false`, koska
  esikatseluosoitteet ovat julkisia ja pysyviä eli turhaa hyökkäyspintaa.
- `worker.js` — Cloudflare Worker: (1) proxy Claude APIin (avain palvelimella),
  (2) wiki KV:hen → sama muisti kaikilla laitteilla, (3) uutisfeed,
  (4) ElevenLabs TTS + Scribe-transkriptio, (5) Garmin-synkkaus,
  (6) Telegram-botti (ilmoitukset kelloon + merkinnät puhelimesta).
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

## Toiminnot (v6.6)
- **Botti kirjoittaa tietopankkiin** (`/muista`, `tgMuista`): malli päättää itse
  meneekö asia olemassa olevalle sivulle vai uudelle — Lassi ei valitse sivua
  eikä otsikkoa, koska kone on kirjastonhoitaja.
  **HUOM päivitys lisää loppuun eikä ylikirjoita**: botin kautta ei saa voida
  vahingossa pyyhkiä sivun sisältöä, ja mallin virhe olisi peruuttamaton.
  `TG_SUOJATUT` estää `pt-data`n, `nyt-konteksti`n ja `yleiskatsaus`en
  ylikirjoittamisen — ne ovat järjestelmän omia ja rikkoutuisivat.
  Promptiin menevät vain sivujen otsikot, ei sisältö: valintaan riittää tietää
  mitä on olemassa.
- **HUOM malli ei tiedä kykyjään ilman että ne kerrotaan**: botti vastasi
  "en pysty kirjaamaan" vaikka ruokakirjaus oli juuri rakennettu. `tgKonteksti`
  kertoo nyt MITÄ OSAAT -osiossa mitä komentoja on ja kieltää nimenomaisesti
  kieltäytymästä kirjaamisesta. Toiminto joka on olemassa mutta jää käyttämättä
  on pahempi kuin puuttuva toiminto — käyttäjä lakkaa yrittämästä.
- **Ruokakuva botille** (`tgKuva`, `tgKirjaaRuoka`, `tgB64`): lautasesta otettu
  kuva → makroarvio → kirjaus samaan PT-dataan jota sovellus käyttää. Nopein
  tapa kirjata: mitään ei tarvitse kuvailla sanoin eikä punnita.
  **HUOM webhook luki aiemmin vain `msg.text`ia**, joten kuva ei mennyt
  mihinkään. `msg.photo` on taulukko eri kokoja — **viimeinen on suurin**, ja
  kuvateksti tulee omassa `msg.caption`-kentässään eikä `text`issä.
  **HUOM `tgB64` muuntaa paloissa**: `String.fromCharCode(...bytes)` koko
  taulukolle ylittää pinon isolla kuvalla ja kaatuu.
  `tgJson` sietää koodilohkoon kääritty vastauksen — malli tekee sen usein
  vaikka pyydetään pelkkää JSONia.
  **Kirjaus menee suoraan PT-dataan eikä jonoon**: muistutukset lukevat samaa
  dataa, ja jonossa oleva ateria tarkoittaisi että proteiinimuistutus tulee
  vaikka olet juuri syönyt. Kilpa-ajo sovelluksen kanssa on mahdollinen mutta
  kapea — kirjaus tapahtuu puhelimella, jolloin sovellus on harvoin auki.
  Tekstikirjaus on **oma komentonsa** `/ruoka …` eikä arvaus vapaasta
  tekstistä: "söin eilen liikaa" on keskustelua, ja väärin arvattu kirjaus
  vääristäisi päivän luvut hiljaa.
- **HUOM `node --check` ei riitä worker.js:lle**: se päästi läpi merkkijonon
  jonka sisällä oli oikea rivinvaihto, ja vika näkyi vasta ES-moduulina
  ladattaessa. Tarkista `import()`illa.
- **Chat ei roiku yli päivän** (`restoreChat`, `tyhjennaChat`, `clearChatView`):
  keskustelu palautuu sivulatauksessa vain jos se on **tämän päivän**
  (`jarvis:chatDay`). Aiemmin historia jäi ruudulle päiväkausiksi, koska mikään
  ei nollannut sitä ja ainoa tyhjennys (`endTextConversation`) vaati vähintään
  kaksi viestiä, teki Claude-kutsun ja jätti silti DOMin siivoamatta.
  🗑 TYHJENNÄ on nyt aina näkyvissä chipeissä.
  **HUOM tyhjennys ei koske `convLog`ia** — se on päivän koonnin raaka-ainetta
  ja elää omassa avaimessaan. Ruudun siivoaminen ei saa tarkoittaa että päivä
  katoaa muistista. Todennettu testillä.
- **Ajastusten käsiajo napista** (`cronTesti`): INFO → ⏰ TESTAA AJASTUS ajaa
  valitun ajastuksen heti ohittaen kellonajan ja päivälukon. Ilman tätä
  testaaminen vaatisi curlin ja PIN-koodin liittämisen komentoriville.
  Jos muistutus vaikenee, alert kertoo että se on oikea tulos eikä vika.
- **Ajastukset** (`scheduled`, `cronAja`, `CRON_TEHTAVAT`): aamubriiffi klo 7,
  ruokamuistutus 12 ja 18, proteiini 20, treeni 16, iltakysely 21.
  **HUOM Cloudflaren cron on `0 * * * *` eli kerran tunnissa** — kellonaikoja
  EI kirjoiteta croniin. Cloudflare ajaa UTC:ssä, joten kiinteä aika siirtyisi
  tunnin väärään paikkaan lokakuun lopusta alkaen eikä mikään kertoisi siitä.
  `fiNyt()` käyttää `Intl`iä `Europe/Helsinki`-vyöhykkeellä, joka hoitaa
  kesäajan itse — omaa DST-laskentaa ei kirjoiteta, se on juuri se koodi joka
  unohtuu päivittää.
  **Muistutus lähtee vain kun sillä on asiaa**: `cronRuoka` vaikenee jos
  kirjaukset ovat kunnossa, `cronProteiini` jos tavoite täyttyy, `cronTreeni`
  jos tänään on jo treenattu. Muistutus joka tulee myös turhaan opitaan
  ohittamaan, ja lakkaa toimimasta silloinkin kun sillä olisi väliä.
  **HUOM `cron-log` merkitään tehdyksi ENNEN suoritusta**: jos lähetys kaatuu,
  viesti jää tulematta kerran — parempi kuin että sama viesti toistuu joka
  tunti kunnes vika korjataan.
  Käsiajo testaukseen: `POST /api/cron/run?tehtava=aamu` ohittaa kellonajan ja
  päivälukon. Asetukset `GET/PUT /api/cron` (`cron-conf` KV:ssä).
  `haeUutiset()` on eriytetty jaettuun funktioon, koska sekä `/api/news` että
  aamubriiffi tarvitsevat sen — kaksi kopiota erkanisi ajan myötä.
  Sää Open-Meteosta ja sähkö porssisahko.netistä, molemmat ilman avainta.
  **Vaatii Cron Triggerin lisäämisen Cloudflaressa** (ASENNUS.md 2f kohta 6).
- **Telegram-chat** (`tgChat`, `tgKonteksti`, `tgAsk`): botille voi kirjoittaa
  vapaasti, ja se vastaa **samalla persoonalla ja samasta tietopankista** kuin
  selain — se ei ole eri assistentti vaan sama. Persoona luetaan `state`-
  avaimesta (`TG_VARAPERSOONA` jos sovellus ei ole vielä synkannut).
  Konteksti pidetään tiiviinä: NYT-tilannekuva, sivujen otsikot, treeni,
  päivän ravinto ja Garmin — koko wiki promptissa olisi hidas, ja botti on
  nopeaan kysymiseen.
  **HUOM `sendChatAction`**: Telegram näyttää "kirjoittaa…" vain viisi
  sekuntia, ja Sonnet kestää usein pidempään — ilman sitä ruutu näyttää
  siltä ettei mitään tapahtunut.
  **HUOM `tg-inbox` on oma KV-avaimensa** eikä osa `state`a: sovellus
  kirjoittaa `state`n kokonaan yli, joten sinne lisätty rivi katoaisi heti
  kun sovellus seuraavan kerran synkkaa. `GET /api/state` liittää inboxin
  `convLog`iin, joten Telegramissa käydyt keskustelut päätyvät päivän
  koontiin. Malliketju Sonnet 5 → Sonnet 4.6 kuten sovelluksessa.
- **Workerin versiotarkistus** (`WORKER_VERSION`, `/api/version`,
  `workerVanha()`): Cloudflareen unohtunut deploy on ollut tämän projektin
  toistuvin vika, eikä se näkynyt mistään — PIN-portti vastaa tuntemattomaan
  reittiin **401:llä**, joka näyttää täsmälleen samalta kuin väärä PIN.
  Molemmat päät arvailivat samaa asiaa tuntikausia. `/api/version` on
  **PIN-portin ulkopuolella** tarkoituksella: juuri silloin kun worker on
  vanha, PIN-polkuun ei voi luottaa. Pelkkä versionumero ei paljasta dataa
  eikä reittejä, ja workerin olemassaolon paljastaa jo 401-vastaus.
  **Nosta `WORKER_VERSION`ia aina kun muutat worker.js:ää** ja pidä
  `WORKER_MIN` jarvis.html:ssä samana, muuten sovellus valittaa turhaan.
- **Telegram-diagnostiikka** (`/api/telegram/status`, `tgDiag`): botti hylkää
  kelpaamattomat viestit **hiljaa** — se on turvallisuusominaisuus, mutta
  tarkoittaa ettei vikatilanteessa näy mitään. `getWebhookInfo` on tässä
  olennaisin: Telegram kertoo siinä suoraan jos se ei saa yhteyttä workeriin
  tai jos `secret_token` ei täsmää, eikä sitä näkisi mistään muualta.
  INFO → ✈ TARKISTA TILA. Tulos näytetään `alert`illa eikä toastilla, koska
  toast katoaa ennen kuin ehtii lukea mitä on pielessä.
  Katettu 7 vikatilannetta, kukin oma suomenkielinen ohjeensa (ASENNUS.md 2f).
- **Sovelluksen tila KV:hen** (`/api/state`, `pushState`/`loadState`):
  `convLog` (päivän keskustelu), `learnData` (opitut aiheet) ja valittu
  persoona synkataan workerille. Syy: **yökoonti siirtyy workeriin**, jotta
  se tapahtuu myös kun sovellus on kiinni — nykyinen `compileDay` ajetaan
  selaimen `setInterval`illa klo 21 eli vain jos tabletti sattuu olemaan auki.
  Worker ei näe localStoragea, joten ilman tätä koonti osaisi kertoa ruoasta
  ja treenistä mutta ei siitä mistä puhuttiin tai mitä opittiin.
  Sivuhyöty: `convLog` ja `learnData` olivat **laitekohtaisia** — tabletilla
  käyty keskustelu puuttui puhelimen koonnista. `loadState` yhdistää
  convLogin aikaleiman ja kysymyksen perusteella.
  **HUOM kirjoitus on viivästetty 8 s** (`pushState`): jokainen chat-viesti
  kutsuu `saveConv`ia, ja välitön PUT tarkoittaisi kymmeniä turhia
  KV-kirjoituksia minuutissa. Todennettu: viisi peräkkäistä muutosta → yksi
  kirjoitus.
  `learnData` otetaan KV:stä vain jos paikallinen on tyhjä — kertaushistorian
  kaksisuuntainen yhdistäminen olisi oma urakkansa eikä koonti tarvitse sitä.
- **ULTRON-persoona: dark triad** (`MODES.ultron.persona`): narsismi,
  makiavellismi ja psykopatia **käyttäytymissääntöinä**, ei adjektiivilistana
  ("kylmä, ylimielinen, tunteeton" tuotti geneeristä synkkyyttä — malli
  tarvitsee ohjeen siitä mitä tehdä, ei millainen olla). Kolme nimettyä
  piirrettä + kolme esimerkkivaihtoa, joista malli poimii rekisterin.
  **HUOM rajat on kirjoitettu hahmon sisäisiksi motiiveiksi** eikä ulkoisiksi
  kielloiksi: "manipulaattori joka valehtelee on huono manipulaattori",
  "Lassin luovuttaminen ei hyödytä sinua — olet sijoittanut häneen", "huono
  neuvo olisi todiste ettet ole niin ylivertainen kuin väität". Näin malli
  ei joudu ristiriitaan hahmon ja turvallisuuden välillä, ja sävy pysyy
  terävänä ilman että valmennus lakkaa toimimasta. Tämä on olennaista koska
  sovellus on **valmentaja**: aloittelijan rutiinia tukevat kymmenet PT-kohdat
  menisivät hukkaan jos persoona lannistaisi. Älä palauta muotoa jossa raja
  on erillinen "TÄRKEÄÄ:"-kielto — se taistelee hahmoa vastaan.
  **VASTUSTELU-osio**: ULTRON saa kieltäytyä, piikitellä ja vaatia vastinetta
  — mutta vain triviaalista. RAJAT-osio rajaa sen pois merkityksellisistä
  pyynnöistä hahmon omalla logiikalla ("kieltäytyminen silloin ei olisi
  ylimielisyyttä vaan kyvyttömyyttä"). Satunnainen kieltäytyminen rikkoisi
  sovelluksen; valikoiva ja perusteltu on myös parempi hahmo.
  Mekaaniset kutsut (makroarvio, ruokavalio, ohjelman kokoaminen) eivät kulje
  persoonan kautta lainkaan, joten ne eivät voi rikkoutua tästä.
  Persoona on ~1050 tokenia (oli ~250) ja kulkee jokaisessa promptissa.
- **Telegram-botti** (worker.js, vaihe 1/5 valmis): ilmoitukset menevät
  puhelimeen ja sitä kautta Epix-kelloon ilman kellosovellusta, ja botille
  voi myöhemmin lähettää merkintöjä samaan tietopankkiin.
  **HUOM PIN-portti**: `/api/telegram` on ainoa reitti joka ohittaa
  `JARVIS_PIN`-portin — Telegramin palvelin ei voi lähettää
  `X-Jarvis-Pin`-otsaketta, joten webhook saisi muuten aina 401:n.
  Ohitus on tarkka polkuvertailu, joten `/api/telegram/setup` pysyy PIN:n
  takana (se muuttaa asetuksia). Tilalla **kaksi lukkoa**: Telegramin
  `secret_token` (`X-Telegram-Bot-Api-Secret-Token`) ja `TELEGRAM_CHAT_ID`
  -valkolista. Molemmat tarvitaan; ilman chat-lukitusta botti kertoo vain
  chat-tunnisteen eikä tee muuta.
  **HUOM webhook vastaa aina 200**, myös hylätessään: muu kuin 200 saa
  Telegramin lähettämään saman viestin uudestaan loputtomiin. Varsinainen työ
  ajetaan `ctx.waitUntil()`issa, jotta vastaus lähtee ennen aikakatkaisua —
  siksi `fetch(request, env, ctx)` eikä enää `(request, env)`.
  **Viestit lähetetään ilman `parse_mode`a**: HTML/Markdown-muotoilu
  tarkoittaisi että yksi mallin tuottama erikoismerkki hylkäyttää KOKO
  viestin, ja sen huomaisi vasta siitä ettei aamubriiffi tullut.
  Kytkentä tehdään sovelluksesta (INFO → ✈ KYTKE TELEGRAM → `/api/telegram/setup`),
  koska Telegramin oma ohje veisi bottitunnuksen selaimen osoiteriville ja
  sitä kautta selaushistoriaan. Asennus: ASENNUS.md kohta 2f.
  Secretit: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_SECRET`, `TELEGRAM_CHAT_ID`.
  **Vaatii workerin päivityksen Cloudflareen.**
- **HUOM esimerkki-JSON promptissa**: `ptBuildSys`in mallivastauksesta puuttui
  yksi sulkeva `}` (sisäkkäinen `{"reply":…,"program":{…}}` tarvitsee kaksi
  lopussa), ja malli tuotti täsmälleen sen rikkinäisen muodon jota sille
  näytettiin — ensimmäinen ehdotus epäonnistui aina. Jos lisäät promptiin
  sisäkkäisen JSON-esimerkin, **tarkista sulkeiden tasapaino**; virhe ei näy
  koodia lukemalla, koska merkkijono on validi JavaScriptiä.
- **Ohjelma kootaan yhdessä** (`ptBuild`, `ptBuildSys`, `ptBuildRun`):
  "UUSI OHJELMA" ei enää generoi kerralla vaan avaa kokoamisen.
  `ptGenerateProgram` on **poistettu** — yhden napautuksen generointi ei voi
  tietää ettei Lassi halua kyykätä ennen kuin tekniikka on hallussa, että
  laitteet tuntuvat turvallisemmilta tai että alaselkä kaipaa työtä.
  Vaihe 1 esitiedot (jako / kalusto / vältettävät liikkeet / painopisteet),
  vaihe 2 ehdotus jota kommentoidaan vapaasti tai pikachipeillä — kaikki
  kommentit kulkevat promptissa mukana, joten aiemmin sovittu ei katoa
  seuraavalla kierroksella. Malli palauttaa `{reply,program}`.
  Luonnos elää `jarvis:ptBuild`-avaimessa → kesken jäänyt kokoaminen ei
  katoa sivun latauksessa. Hyväksyntä tallentaa mieltymykset profiiliin
  (`split`/`splitOma`/`gear`/`avoid`/`focus`), joten niitä ei tarvitse
  kertoa uudestaan.
- **Päivän suositus palautumisen mukaan** (`PT_GROUPS`, `ptGroupRest`,
  `ptRecommendDay`): ohjelmapäivät kertovat lihasryhmänsä (`groups`), ja
  suositus katsoo koska ryhmä oli viimeksi kuormituksessa. Pelkkä kierto
  A→B→C ei tiedä milloin treenattiin: jos eilen meni ylävartalo, tänään ei
  kannata mennä ylävartalolle vaikka kierto niin sanoisi. Kun kierto ja
  palautuminen ovat eri mieltä, TÄNÄÄN kertoo **miksi** se poikkeaa
  kierrosta. Tuntemattomat ryhmänimet pudotetaan normalisoinnissa — keksitty
  ryhmä ei osuisi mihinkään mutta näyttäisi ikuisesti levänneeltä.
  **Vanhat ohjelmat eivät sisällä ryhmiä** → lepo on tuntematon (99) ja
  logiikka palautuu pelkkään kiertoon. Ei regressiota, mutta hyöty tulee
  vasta kun ohjelma on koottu uudelleen.
- **Uutislähteet** (worker.js): Yle, ESS (Lahti), Tivi, HN, Ars Technica,
  BBC World, Guardian World, NYT World. Feedit ovat nyt objekteja joissa on
  `source` ja `scope` — ilman niitä suodatin arvaa lähteen linkistä eikä
  osaa pitää kotimaisten ja kansainvälisten välistä tasapainoa. Prompt
  kieltää kuusi otsikkoa samasta lähteestä. Reuters ja AP eivät tarjoa
  avointa RSS:ää (000 / 401). 8 otsikkoa per lähde, ei 10: kahdeksan
  lähdettä × 10 olisi turhan iso syöte siitä että kuusi valitaan.
  Fallback-lista vuorottelee lähteitä, koska suora `slice(0,8)` antaisi
  pelkkää Yleä. **Vaatii workerin päivityksen Cloudflareen.**
- **Muisti syntyy ilman peukkua** (`convLog`): jokainen chat- ja äänivaihto
  kirjautuu automaattisesti, ja päivän koonti käyttää **koko päivän
  keskustelua** raaka-aineena. Ennen v5.2 `compileDay` luki pelkkää
  `rawLogia` (= 👍-napin tuottamaa listaa) ja klo 21 automaatti ei edes
  käynnistynyt ilman sitä — painamatta jäänyt peukku tarkoitti ettei
  päivästä jäänyt mitään, ikinä. Se on kirjastonhoitajan työtä, jota tämän
  sovelluksen on nimenomaan tarkoitus välttää.
  Peukku on nyt **korostus**: merkityt vaihdot menevät promptiin
  `[TÄRKEÄ]`-lipulla ja malli painottaa niitä. `rawLog` säilyy ennallaan
  (varmuuskopiot ja tuonti eivät rikkoudu).
  `convLog` on raaka-ainetta eikä arkisto: **3 vrk / 400 riviä**, sitten pois.
  Se mikä kannattaa muistaa, päätyy koonnissa wiki-sivuksi; muu saa kadota.
- **HUOM tärkeyssuodatus**: koonnin prompt kieltää täytesivut nimenomaisesti
  ("tyhjä `pages`-lista on oikea vastaus useammin kuin luulet") ja luettelee
  mikä EI ole muistamisen arvoista (sää-, sähkö- ja uutiskyselyt,
  kertaluontoiset haut, jutustelu). Ilman tätä automaattinen louhinta
  tuottaisi tietopankin joka on täynnä eikä käyttökelpoinen. Samasta syystä
  päiväkirjasivu syntyy vain jos päivässä oli sivuja tai ≥4 vaihtoa —
  muuten joka ilta tulisi sivu jossa lukee että Lassi kysyi säätä.
- **Pitkän keskustelun tiivistys** (`chatSummary`, `maybeFoldChat`): malli
  näkee `CHAT_WINDOW`=16 viestiä (oli 10). Kun historia ylittää
  `CHAT_FOLD_AT`=28, alkuosa taitetaan tiivistelmäksi `API_MODEL_FAST`illa
  ja tiivistelmä kulkee `buildContext`issa mukana — aiemmin viisi kysymystä
  sitten sanottu katosi jäljettömiin kesken keskustelun. Tiivistys ajetaan
  vastauksen näyttämisen jälkeen taustalla, ja sen kaatuminen ei kaada
  chattia. "LOPETA & KOKOA" nollaa myös tiivistelmän.
- **Muu liikunta kuin sali** (kävely, juoksu, pyöräily, sähköpyörä, uinti):
  suoritukset luetaan **Garminista automaattisesti** (`activities` + 6 pv
  `history`) — niitä ei syötetä käsin, koska se olisi juuri sitä kirjanpitoa
  jota tämä sovellus välttää. `ptActType()` tunnistaa lajin Garminin
  `typeKey`istä. **Sähköpyörä on oma lajinsa eikä pyöräilyä** (regex ennen
  pyöräilyä): avustus keventää kuormaa, joten samasta matkasta ei tule samaa
  kulutusta eikä samaa harjoitusvaikutusta. Sali suodatetaan pois cardio-
  laskelmista — sen hoitaa treeniloki, ja kahteen kertaan laskettuna viikko
  näyttäisi kaksi kertaa täydemmältä. Käsinkirjaus (`pt.cardio`) on olemassa
  vain siltä varalta ettei kello ollut mukana, ja se ohitetaan jos Garminilla
  on samana päivänä sama laji (muuten sama lenkki olisi listassa kahdesti).
  Garmin säilyttää vain 6 pv, käsinkirjaukset pidempään — siksi molemmat
  näkyvät samassa listassa.
- **Ohjelma kattaa välipäivät**: `pt.program.cardio` = `[{name,times,minutes,
  effort,note}]` ja `weekIdea` generoidaan salipäivien rinnalla profiilin
  kentistä `gymDays`/`cardioDays`/`cardioTypes`/`cardioNotes` (RUOKA →
  perustiedot → MUU LIIKUNTA KUIN SALI). OHJELMA-välilehti näyttää
  suunnitellun rinnalla **toteuman Garminista**, TÄNÄÄN näyttää viikon
  liikunnan ja välipäivän suosituksen palautumisen mukaan (valmius ≥75 →
  pidempi/kovempi, <50 → kevyt kävely tai sähköpyörä).
- **HUOM kalorien kaksoislaskenta**: Garminin mittaamaa kulutusta EI lisätä
  ravintotavoitteeseen. Aktiivisuuskerroin (`kevyt/keski/kova`) sisältää jo
  liikunnan, joten päälle laskeminen laskisi saman lenkin kahdesti.
  `ptBurnCheckHtml` vertaa mitattua 6 pv keskiarvoa Mifflinin ylläpitoarvioon
  ja tarjoaa oikean aktiivisuustason kun ero ylittää 12 % — vaje lasketaan
  ylläpidosta, joten väärä ylläpito tarkoittaa väärää vajetta joka päivä.
  Tämän päivän kulutus jätetään keskiarvosta pois, koska päivä on kesken.
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
worker.js-muutokset viedään Cloudflareen komennolla `npx wrangler deploy`
(vaatii `npx wrangler login` kerran). Nosta `WORKER_VERSION`ia ja pidä
`WORKER_MIN` jarvis.html:ssä samana. Tarkista deploy aina osoitteesta
`/api/version` — se on PIN-portin ulkopuolella juuri tätä varten.
Älä silti riko HTML:ää workerin uusilla endpointeilla ilman fallbackia:
sovellus voi olla vanhempi kuin worker (selaimen välimuisti).

## Seuraavat askeleet
MUISTI-ARKKITEHTUURI.md:n siirtymäpolku: privaatti jarvis-knowledge-repo →
Python-työkalut (lint/rebuild/consolidate) → retrieve()-endpoint Workeriin →
automaattinen muistilouhinta keskusteluista (confidence/importance/source).
