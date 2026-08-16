# J.A.R.V.I.S. — Asennusopas

Tavoite: J.A.R.V.I.S. toimii millä tahansa laitteella, missä vain, ja muistaa
saman tietopankin kaikkialla. Tee tämä kerran tietokoneella.

Sinulla on kolme tiedostoa:
- `jarvis-deploy.html`  → käyttöliittymä (nimetään lopuksi jarvis.html)
- `worker.js`           → "aivot pilvessä" (Cloudflare)
- `manifest.json`       → tekee siitä sovelluksen tabletilla

Kokonaisaika: ~30–40 min. Kaikki ilmaista.

---

## VAIHE 1 — Hae Claude API -avain (5 min)

1. Mene osoitteeseen: https://console.anthropic.com
2. Kirjaudu / luo tili.
3. Lisää hieman saldoa (Billing) — pieni summa (esim. 5 $) riittää
   henkilökohtaiseen käyttöön pitkäksi aikaa.
4. Vasemmalta "API Keys" → "Create Key". Anna nimi esim. "jarvis".
5. KOPIOI avain heti talteen (alkaa `sk-ant-...`). Sitä ei näytetä uudelleen.

---

## VAIHE 2 — Luo Cloudflare-tili ja Worker (15 min)

1. Mene: https://dash.cloudflare.com/sign-up — luo ilmainen tili.
2. Vasemmasta valikosta: "Workers & Pages" → "Create" → "Create Worker".
3. Anna nimi, esim. `jarvis`. Klikkaa "Deploy" (oletuskoodi, ei väliä).
4. Klikkaa "Edit code". Poista kaikki valmis koodi ja liitä tilalle
   `worker.js`-tiedoston sisältö kokonaisuudessaan. Paina "Deploy".
5. Ota talteen Workerin osoite ylhäältä, muotoa:
   `https://jarvis.SINUN-NIMI.workers.dev`

### 2b — Kytke muisti (KV-tietokanta)
1. "Workers & Pages" → vasemmalla "KV" → "Create a namespace".
   Nimi esim. `jarvis-kv`. Luo.
2. Mene takaisin Workeriisi → "Settings" → "Bindings" → "Add" → "KV namespace".
   - Variable name: `JARVIS_KV`   (tasan tämä nimi!)
   - KV namespace: valitse `jarvis-kv`
   - Tallenna.

### 2c — Lisää API-avain salaisuutena
1. Saman Workerin "Settings" → "Variables and Secrets" → "Add".
2. Type: Secret.
   - Name: `ANTHROPIC_API_KEY`  (tasan tämä nimi!)
   - Value: liitä VAIHE 1:n avain (`sk-ant-...`)
   - Tallenna.
3. **TÄRKEÄ suoja — lisää toinen Secret:**
   - Name: `JARVIS_PIN`
   - Value: **pitkä, satunnainen koodi**, esim. `y075-bsbg-agy5-6r6q-r143`
   - Tallenna.

   Miksi tämä on tärkeä, ei vapaaehtoinen: Workerin osoite näkyy
   `jarvis.html`:ssä, joka on julkinen. PIN on AINOA portti joka estää muita
   käyttämästä Claude-saldoasi ja lukemasta/pyyhkimästä tietopankkiasi.
   Workerissa ei ole yrityskattoa, joten lyhyt PIN (esim. `1234` tai
   `nastola1234`) murtuu väsytyksellä sekunneissa — **käytä pitkää satunnaista
   jonoa.** Et joudu näppäilemään sitä usein (laite muistaa sen kirjautumisen
   jälkeen), joten pituus ei haittaa arjessa.

   **Tallenna PIN heti salasanojen hallintaan** (Google Password Manager,
   Samsung Pass tai Bitwarden). Cloudflare EI näytä secretin arvoa
   jälkikäteen — jos unohdat sen, joudut vaihtamaan sen kaikkialle uudelleen.

### 2d — (Suositeltu) Laadukas luentoääni: Google Cloud TTS

Ilman tätä luennot luetaan laitteen omalla puheäänellä (kelaus ei toimi).
Tällä saat luonnollisen neuroäänen + kelattavan soittimen + offline-MP3:t.

**Kustannuksista — lue tämä ennen kuin generoit kymmenen luentoa.**
Ilmaiskiintiö EI ole sama kaikille äänille: Standard- ja WaveNet-äänillä on
oma kuukausittainen ilmaiskiintiönsä, mutta laadukkaammat perheet (Chirp,
Studio, Neural2) laskutetaan eri taksalla ja voivat jäädä kokonaan
ilmaiskiintiön ulkopuolelle. Sovelluksen oletusääni on Chirp3-HD, eli se
ei välttämättä ole ilmainen. Tarkista voimassa olevat hinnat ja kiintiöt:
https://cloud.google.com/text-to-speech/pricing

Mittakaava: yksi normaalipituinen luento on noin 20 000 merkkiä, joten
maksullisillakin taksoilla puhutaan senteistä per luento — ei kympeistä.
Aseta silti **budjettihälytys** (Billing → Budgets & alerts, esim. 5 €/kk),
niin yllätyksiä ei tule. Jos haluat pysyä varmasti ilmaisessa, valitse
sovelluksessa ääneksi `fi-FI-Wavenet-A` tai `fi-FI-Standard-A`
(LUENNOT → SÄÄDÄ).

1. Mene: https://console.cloud.google.com — kirjaudu Google-tilillä ja luo
   projekti (esim. `jarvis-tts`). Google vaatii laskutustilin aktivoinnin
   myös ilmaiskiintiön käyttöön.
2. Ylähaku: "Cloud Text-to-Speech API" → **Enable**.
3. Vasen valikko: "APIs & Services" → "Credentials" → "Create Credentials"
   → **API key**. Kopioi avain talteen.
4. (Suositus) Klikkaa avainta → "API restrictions" → rajaa vain
   "Cloud Text-to-Speech API" → Save.
5. Cloudflare: Workerisi → Settings → Variables and Secrets → Add:
   - Type: **Secret**
   - Name: `GOOGLE_TTS_API_KEY` (tasan tämä nimi!)
   - Value: äsken kopioitu avain → **Deploy**.
6. Muista myös päivittää Workerin koodi ("Edit code" → liitä uusin
   `worker.js` → Deploy), jos siinä ei vielä ole `/api/gtts`-reittiä.
7. Testaa heti: sovellus → OPPI → **LUENNOT** → **SÄÄDÄ** →
   **▶ KUUNTELE NÄYTE**. Näyte kertoo myös mitä ääntä oikeasti käytettiin,
   joten näet suoraan jos valitsemasi ääni ei ollut saatavilla.
8. Sovelluksessa: uusille luennoille HQ-ääni ladataan automaattisesti heti
   generoinnin perään. Vanhoille luennoille: avaa luento → paina
   **⭳ LATAA HQ-ÄÄNI**. Ääni tallentuu laitteelle ja toimii sen jälkeen
   offline-tilassa kelattavana.

Jos näyte sanoo "GOOGLE_TTS_API_KEY puuttuu workerista", secret ei ole
perillä: tarkista nimen kirjoitusasu (tasan `GOOGLE_TTS_API_KEY`) ja se
että painoit Cloudflaressa **Deploy** tallennuksen jälkeen.

### 2e — (Vapaaehtoinen) Garmin-synkkaus käskystä: ⚡ SYNKKAA -nappi

Garmin-data haetaan automaattisesti kolmen tunnin välein. Tällä lisäyksellä
saat HUDiin napin, joka käynnistää haun heti — kätevä esimerkiksi juuri ennen
salia tai heti treenin jälkeen.

Ilman tätä kaikki muu toimii normaalisti: nappi kertoo silloin selkokielisesti
ettei toimintoa ole käytössä, ja synkkauksen voi ajaa käsin GitHubissa
(Actions → Garmin sync → Run workflow).

1. Mene: https://github.com/settings/personal-access-tokens → **Generate new
   token** (fine-grained).
2. Asetukset:
   - **Repository access**: Only select repositories → `LassiSalminen/jarvis`
   - **Permissions** → Repository permissions → **Actions: Read and write**
   - Expiration: valitse mieleisesi (muista uusia token sen umpeutuessa)
3. Kopioi token heti talteen — GitHub näyttää sen vain kerran.
4. Cloudflare: Workerisi → Settings → Variables and Secrets → Add:
   - Type: **Secret**
   - Name: `GITHUB_TOKEN` (tasan tämä nimi!)
   - Value: äsken kopioitu token → **Deploy**.
5. Päivitä Workerin koodi ("Edit code" → liitä uusin `worker.js` → Deploy),
   jotta `/api/garminsync`-reitti tulee käyttöön.
6. Sovelluksessa: HUD → Garmin-kortti → **⚡ SYNKKAA**. Nappi näyttää
   ajastimen ja hakee uuden datan itsestään heti kun ajo valmistuu
   (tavallisesti noin minuutti).

### 2f — (Vapaaehtoinen) Telegram-botti: ilmoitukset kelloon ja merkinnät puhelimesta

Telegram-botti on kaksisuuntainen: se lähettää sinulle ilmoituksia (jotka
Garmin Epix näyttää automaattisesti, koska kello peilaa puhelimen ilmoitukset)
ja ottaa vastaan merkintöjä samaan tietopankkiin kuin sovellus.

Tee vaiheet järjestyksessä — botti ei tee mitään ennen kuin kaikki kolme
salaisuutta ovat paikallaan.

**1. Luo botti (5 min)**
1. Avaa Telegram ja hae käyttäjä **@BotFather**.
2. Lähetä `/newbot`.
3. Anna botille nimi (esim. `Jarvis`) ja käyttäjätunnus joka päättyy
   `bot`-sanaan (esim. `lassi_jarvis_bot`). Tunnuksen pitää olla vapaa.
4. BotFather antaa **tokenin** muotoa `1234567890:AAE...`. Kopioi se heti.
   **Tämä on salasana bottiisi** — älä liitä sitä chattiin, sähköpostiin,
   GitHubiin tai selaimen osoiteriville.

**2. Vie token ja oma salasana Cloudflareen (3 min)**
1. Cloudflare → Workerisi → Settings → Variables and Secrets → Add:
   - Type: **Secret**, Name: `TELEGRAM_BOT_TOKEN`, Value: BotFatherin token.
2. Lisää **toinen** secret:
   - Name: `TELEGRAM_SECRET`
   - Value: **pitkä satunnainen jono**, jonka keksit itse
     (esim. `q8fj-2mzp-71xd-vk04-ba9r`). Tämä ei ole mistään saatu — se on
     sinun oma. Telegram lähettää sen jokaisessa viestissä, ja se on ainoa
     asia joka erottaa aidon Telegramin siitä että joku muu kutsuu workerisi
     osoitetta suoraan.
3. Paina **Deploy**.

**3. Päivitä workerin koodi**
Workerissa on nyt useampi päivittämätön muutos (uutislähteet + Telegram).
Cloudflare → Workerisi → **Edit code** → korvaa kaikki uusimmalla
`worker.js`-tiedostolla → **Deploy**.

**4. Kytke botti sovelluksesta (10 sekuntia)**
Avaa J.A.R.V.I.S. → mobiilinäkymässä **INFO**-välilehti → JÄRJESTELMÄ-kortti →
**✈ KYTKE TELEGRAM**.

Tämä kertoo Telegramille mihin osoitteeseen viestit lähetetään. Se tehdään
sovelluksesta eikä selaimen osoiteriviltä siksi, että Telegramin omissa
ohjeissa neuvottu tapa vaatisi tokenin liittämisen URLiin — sieltä se jäisi
selaushistoriaan ja voisi synkkautua muille laitteille.

**5. Lukitse botti itsellesi (2 min) — älä jätä tätä tekemättä**
1. Avaa Telegramissa oma bottisi ja lähetä sille mikä tahansa viesti.
2. Botti vastaa: `Chat-tunnisteesi on: 123456789`.
3. Cloudflare → Settings → Variables and Secrets → Add:
   - Type: **Secret**, Name: `TELEGRAM_CHAT_ID`, Value: tuo numero → **Deploy**.
4. Lähetä botille `/status`. Nyt sen pitäisi kertoa tietopankin tilanne.

Ennen kohtaa 3 botti kertoo vain chat-tunnisteen eikä tee mitään muuta —
se ei siis vuoda dataa. Mutta lukitus kannattaa tehdä heti: ilman sitä kuka
tahansa bottisi tunnuksen arvaava voisi myöhemmissä vaiheissa kirjoittaa
tietopankkiisi ja kuluttaa Claude-saldoasi.

**6. Kytke ajastukset päälle (aamubriiffi, muistutukset)**

Ilman tätä botti vastaa kysymyksiin mutta ei lähetä mitään itse.

1. Cloudflare → Workerisi **jarvis** → **Settings** → **Trigger Events**
   (tai vasemmalta "Triggers") → **Add** → **Cron Trigger**.
2. Kirjoita kentään tasan tämä:

       0 * * * *

   Se tarkoittaa "kerran tunnissa tasalta". **Älä kirjoita tähän kellonaikoja.**
   Cloudflaren ajastin käy UTC-ajassa, jolloin klo 7 Suomen aikaa olisi kesällä
   04 ja talvella 05 — kiinteä aika siirtyisi tunnin väärään paikkaan lokakuun
   lopussa eikä mikään kertoisi siitä. Worker herää joka tunti ja päättää itse
   Suomen paikallisajan perusteella mitä on aika tehdä.
3. **Deploy**.

Ajastukset ja niiden oletusajat:

| Klo | Mitä | Lähtee vain jos |
|---|---|---|
| 7 | Aamubriiffi: sää, sähkö, keho, treeni, 3 uutista | aina |
| 12 | Lounasmuistutus | ruokakirjauksia puuttuu |
| 18 | Illallismuistutus | ruokakirjauksia puuttuu |
| 20 | Proteiinimuistutus | alle 70 % tavoitteesta |
| 16 | Treenimuistutus | ei treeniä tänään ja 2+ pv edellisestä |
| 21 | Iltakysely: "mitä teit tänään?" | aina |

Muistutukset lähtevät **vain kun niillä on asiaa**. Muistutus joka tulee myös
silloin kun asia on hoidettu opitaan ohittamaan, ja lakkaa sen jälkeen
toimimasta silloinkin kun sillä olisi väliä.

Aikojen muuttaminen: `PUT /api/cron` (PIN:n takana). Lääkemuistutus on pois
päältä oletuksena — kytke `laakeKaytossa: true` ja aseta `laake`-tunti.

Testaus ilman odottelua: `POST /api/cron/run?tehtava=aamu` ajaa yhden
tehtävän heti ja ohittaa sekä kellonajan että päivälukon. Kelpaavat tunnisteet:
`aamu`, `lounas`, `illallinen`, `proteiini`, `treeni`, `laake`, `ilta`.

**7. Varmista että ilmoitukset näkyvät kellossa**
- Puhelin: Asetukset → Sovellukset → Telegram → Ilmoitukset päälle.
- Garmin Connect -sovellus: Asetukset → Älyilmoitukset → varmista että
  Telegram on sallittujen listalla.
- Testi: lähetä botille `/status` ja katso tuleeko ilmoitus kelloon.

**Vianetsintä — aloita aina tästä**

Botti hylkää kelpaamattomat viestit **hiljaa**. Se on turvallisuusominaisuus,
mutta se tarkoittaa ettei vikatilanteessa näy mitään. Siksi on oma nappi:

INFO → JÄRJESTELMÄ → **✈ TARKISTA TILA**

Se kysyy Telegramilta mitä se ajattelee webhookista ja kertoo suomeksi mitä
on korjattavana. Tyypilliset vastaukset:

| Mitä lukee | Mitä tehdä |
|---|---|
| "Workeria ei ole päivitetty" | Kohta 3 jäi tekemättä — liitä worker.js ja Deploy |
| "TELEGRAM_BOT_TOKEN puuttuu" | Secretin nimi väärin tai Deploy painamatta |
| "TELEGRAM_SECRET puuttuu" | Sama, toiselle secretille |
| "Telegramilla ei ole webhookia" | Paina ✈ KYTKE TELEGRAM |
| "Webhook osoittaa väärään paikkaan" | Paina ✈ KYTKE TELEGRAM |
| "TELEGRAM_CHAT_ID puuttuu" | Lähetä botille viesti, lisää saamasi numero |
| "Telegramin viimeisin virhe: …401…" | `TELEGRAM_SECRET` on eri kuin kytkentähetkellä — paina ✈ KYTKE TELEGRAM uudestaan |
| "N viestiä jonossa" | Telegram ei saa viestejä perille; katso yllä oleva virhe |

Jos kaikki on kunnossa mutta botti on silti hiljaa, tarkista että kirjoitat
**oikealle** botille — BotFatherilla voi olla useampi.

---

## VAIHE 3 — Liitä osoite käyttöliittymään (3 min)

Avaa `jarvis-deploy.html` tekstieditorissa (esim. VS Code).
Etsi aivan alusta skripti-osiosta tämä rivi ja muokkaa:

    const WORKER_URL = "https://OMA-WORKER.workers.dev";

- Laita WORKER_URL:ksi oma osoitteesi VAIHE 2:sta (ilman kauttaviivaa lopussa).

Tallenna tiedosto.

**PIN-koodia EI laiteta tähän tiedostoon.** Sovellus kysyy sen omalla
kirjautumisruudulla ensimmäisellä avauksella ja muistaa sen laitteessa.
Näin PIN ei koskaan päädy julkiseen GitHub-repoon. (WORKER_URL saa olla
koodissa — se ei ole salaisuus.)

---

## VAIHE 4 — Julkaise GitHub Pagesissa (10 min)

1. GitHubissa: luo uusi repositorio, esim. `jarvis`. (Public.)
2. Lataa siihen kolme tiedostoa:
   - nimeä `jarvis-deploy.html` uudelleen → `jarvis.html`
   - `manifest.json`
   (worker.js EI tule tänne — se on jo Cloudflaressa.)
3. Repositorion "Settings" → "Pages" → "Branch": valitse `main` ja `/root`,
   tallenna.
4. Hetken kuluttua saat osoitteen muotoa:
   `https://SINUN-NIMI.github.io/jarvis/jarvis.html`

Avaa se! J.A.R.V.I.S. toimii nyt verkossa.

---

## VAIHE 5 — Asenna sovelluksena tabletille / puhelimelle

Avaa yllä oleva osoite laitteen selaimessa:
- Android (Chrome): valikko ⋮ → "Lisää aloitusnäyttöön".
- iPhone/iPad (Safari): jakokuvake → "Lisää Koti-valikkoon".

Nyt sinulla on J.A.R.V.I.S.-kuvake. Avautuu kokoruututilassa kuin sovellus.
Sama tietopankki näkyy joka laitteella, koska se on Cloudflaressa.

Ensimmäisellä avauksella sovellus kysyy **PIN-koodin** (VAIHE 2c). Syötä se
kerran — laite muistaa sen jatkossa. Toista tämä jokaisella laitteella.

---

## Turvallisuus ja PIN:n vaihtaminen

**Onko Workeri suojattu? — 10 sekunnin testi.**
Avaa selaimessa: `https://OMA-WORKER.workers.dev/api/wiki`
- Näkyy `{"error":"unauthorized"}` → hyvä, PIN-portti on päällä.
- Näkyy `[]` tai listaa tekstiä → portti EI ole päällä, kuka tahansa näkee
  datasi. Lisää `JARVIS_PIN`-secret (VAIHE 2c) heti.

**PIN:n vaihtaminen myöhemmin** (esim. jos epäilet sen vuotaneen tai se on
liian lyhyt):
1. Cloudflare → Workeri `jarvis` → "Settings" → "Variables and Secrets" →
   `JARVIS_PIN` → "Edit" → kirjoita uusi pitkä satunnainen arvo → "Deploy".
   (Secretin vanhaa arvoa ei näytetä — se vain korvataan.)
2. Päivitä uusi `jarvis.html` GitHubiin ja avaa sovellus laitteella (sulje ja
   avaa, jotta uusi versio latautuu).
3. Laitteella: paina info-näkymän JÄRJESTELMÄ-kortista
   **"⟲ VAIHDA PIN / KIRJAUDU ULOS"** → syötä uusi PIN. Sama jokaisella
   laitteella. (Jos vanha PIN on yhä muistissa, sovellus kirjaa sinut ulos
   automaattisesti heti kun se huomaa ettei PIN enää kelpaa.)

**Tallenna PIN aina salasanojen hallintaan** (Google Password Manager,
Samsung Pass, Bitwarden). Älä koskaan käytä samaa PIN:iä joka on joskus ollut
kovakoodattuna koodissa — se voi olla GitHubin versiohistoriassa.

---

## Vianetsintä

- "Ei vastaa / virhe chatissa" → tarkista että WORKER_URL on oikein eikä
  perässä ole kauttaviivaa, ja että ANTHROPIC_API_KEY on tallennettu Workeriin.
- "401 unauthorized" / kirjautumisruutu palaa → syöttämäsi PIN ei täsmää
  Workerin `JARVIS_PIN`-arvoon. Syötä oikea PIN, tai vaihda Workerin arvo
  (ks. "PIN:n vaihtaminen" yllä).
- "Wiki ei tallennu" → tarkista KV-bindingin nimi: täytyy olla JARVIS_KV.
- Sää ei näy → Open-Meteo voi olla hetkellisesti alhaalla, ei vaadi avainta.

## Huomioita
- Raakaloki (👍-merkityt chatit) tallentuu laitekohtaisesti. Itse wiki ja
  päiväkoonnit synkkaavat kaikkialle. Tee "Kokoa päivä" sillä laitteella
  jolla päivän aikana merkitsit juttuja — koonti menee yhteiseen wikiin.
