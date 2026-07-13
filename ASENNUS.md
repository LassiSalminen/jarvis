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
Ilmaiskiintiö ~1 milj. merkkiä/kk ≈ kymmeniä luentoja ilmaiseksi.

1. Mene: https://console.cloud.google.com — kirjaudu Google-tilillä ja luo
   projekti (esim. `jarvis-tts`). Huom: Google vaatii laskutustilin
   aktivoinnin, mutta ilmaiskiintiön sisällä ei veloiteta mitään.
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
7. Sovelluksessa: uusille luennoille HQ-ääni ladataan automaattisesti heti
   generoinnin perään. Vanhoille luennoille: avaa luento → paina
   **⭳ LATAA HQ-ÄÄNI**. Ääni tallentuu laitteelle ja toimii sen jälkeen
   offline-tilassa kelattavana.

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
