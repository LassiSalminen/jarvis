# J.A.R.V.I.S. — Muistiarkkitehtuuri (spesifikaatio)

Henkilökohtaisen tietopankin ja tekoälymuistin arkkitehtuuri. Suunniteltu
kestämään 10+ vuotta, kymmeniä tuhansia dokumentteja ja miljoonia muisti-
merkintöjä, mallista riippumatta (OpenAI, Claude, Gemini, paikalliset mallit).

**Perusperiaate: tiedostot ovat totuus.** Kaikki pysyvä tieto on Markdown-
tiedostoja YAML-metadatalla Git-repossa. Kaikki muu — indeksit, embeddings-
vektorit, graafit, tietokannat — on *johdettua dataa*, joka voidaan aina
rakentaa uudelleen tiedostoista. Tämä on ainoa formaatti, joka varmasti
aukeaa vielä 2036: pelkkää tekstiä.

---

## 1. Kansiorakenne

```
knowledge/
├── profile/                  # Kuka Lassi on (pysyvin kerros)
│   ├── core.md               # Ydinidentiteetti — EI koskaan unohdeta
│   ├── preferences.md        # Mieltymykset (ruoka, tyyli, työtavat...)
│   ├── health.md             # Terveys (yksityisyystaso: secret)
│   ├── career.md             # Urahistoria
│   └── education.md          # Koulutus
│
├── entities/                 # Asiat joilla on identiteetti ja historia
│   ├── people/               # person-*.md
│   ├── organizations/        # org-*.md
│   ├── projects/             # project-*.md
│   ├── skills/               # skill-*.md
│   └── things/               # laitteet, omaisuus (thing-*.md)
│
├── memory/                   # Ajassa syntyvä muisti
│   ├── episodic/             # Päiväkirja + keskustelutiivistelmät
│   │   └── 2026/07/2026-07-06.md
│   ├── semantic/             # Tislatut faktat ja opit (wiki-sivut)
│   ├── decisions/            # Päätökset perusteluineen (ADR-tyyli)
│   ├── timeline/             # Elämän merkkipaalut, vuosi per tiedosto
│   │   └── 2026.md
│   └── stream/               # Raaka muistivirta (JSONL, koneskaalainen)
│       └── 2026/07.jsonl
│
├── work/                     # Aktiivinen tekeminen
│   ├── now.md                # NYKYINEN KONTEKSTI (aina promptiin)
│   ├── goals.md              # Tavoitteet aikajänteittäin
│   └── tasks/                # task-*.md (avoimet) + done/ (valmiit)
│
├── library/                  # Ulkoinen tieto
│   ├── references/           # ref-*.md — linkit, kirjat, artikkelit
│   ├── procedures/           # proc-*.md — ohjeet, reseptit, prosessit
│   └── documents/            # Alkuperäiset tiedostot + rinnakkainen
│       ├── src/              #   pdf/kuva/docx sellaisenaan
│       └── extracted/        #   sama sisältö tekstinä (OCR/parsittu)
│
├── inbox/                    # Käsittelemätön syöte — AI tyhjentää
│
├── archive/                  # Sama rakenne kuin yllä; ei-aktiivinen tieto
│
└── system/                   # Koneisto (johdettu data — rakennettavissa)
    ├── schemas/              # Tietotyyppien määritykset (YAML)
    ├── index/                # Generoidut hakemistot (haku, linkit)
    │   ├── catalog.md        # 1 rivi / tiedosto: id + kuvaus (LLM-haku)
    │   ├── links.json        # Käänteislinkit (backlinks)
    │   └── search.db         # SQLite FTS5 -tekstihaku
    └── embeddings/           # Vektorit (gitignore; uudelleenlaskettavissa)
        └── chunks.db
```

Suunnitteluperusteet:

- **`profile/` erillään `memory/`stä**: identiteetti muuttuu hitaasti,
  muisti kasvaa joka päivä. Eri elinkaaret → eri kansiot.
- **`stream/` (JSONL) erillään Markdownista**: miljoonat muistimerkinnät
  eivät voi olla miljoona tiedostoa. Raaka virta on append-only JSONL;
  vain *tislattu* tieto ylenee Markdown-sivuiksi (tuhansia, ei miljoonia).
- **`system/` on kokonaan uudelleenrakennettavissa** komennolla
  `python tools/rebuild.py`. Jos indeksi korruptoituu tai vaihdat
  vektorikantaa, mitään ei menetetä.
- **`archive/` peilaa päärakennetta**, jolloin arkistointi on pelkkä
  tiedoston siirto ja polku kertoo aina tyypin.

## 2. Nimeämiskäytännöt

| Sääntö | Esimerkki |
|---|---|
| kebab-case, ei ääkkösiä, ei välilyöntejä | `project-jarvis.md` |
| Tyyppiprefiksi entiteeteille | `person-`, `org-`, `project-`, `skill-`, `task-`, `ref-`, `proc-`, `thing-` |
| ISO 8601 -päiväprefiksi ajallisille | `2026-07-06-paatos-cloudflare.md` |
| ID = tyyppi + kaksoispiste + slug | `person:antti-makinen`, `decision:2026-07-06-cloudflare` |
| ID ei koskaan muutu, vaikka tiedosto siirtyy | linkit osoittavat ID:hen, ei polkuun |

ID polun sijaan on kriittinen valinta: arkistointi, uudelleenorganisointi
ja kansiorakenteen muutokset eivät riko yhtään linkkiä, koska
`system/index/` ratkaisee ID → polku.

## 3. Metadataformaatti (YAML-frontmatter)

Jokainen Markdown-tiedosto alkaa frontmatterilla. Pakolliset kentät:

```yaml
---
id: project:jarvis              # pysyvä tunniste
type: project                   # tietotyyppi (ks. §5)
title: "J.A.R.V.I.S."
created: 2026-06-28
updated: 2026-07-06
tags: [ai, pkb, pwa]
summary: >                      # 1–3 lausetta — embeddingin ja
  Henkilökohtainen tekoälyassistentti; PWA + Cloudflare Worker +
  Claude API. Toimii tabletilla ja puhelimella.
status: active                  # active | paused | done | superseded | archived
privacy: private                # public | private | secret
schema_version: 1
links:
  - rel: owned-by
    to: person:lassi
  - rel: uses-skill
    to: skill:javascript
  - rel: decided-by
    to: decision:2026-07-06-cloudflare
source:                         # mistä tieto on peräisin
  kind: conversation            # conversation | document | manual | import
  ref: memory/episodic/2026/06/2026-06-28.md
---
```

Lisäkentät tyypin mukaan (esim. muistimerkinnöillä `confidence`,
`importance`, `expires`). `summary` on pakollinen kaikille: se on
(1) LLM-haun ensimmäinen taso, (2) embeddingin ensisijainen sirpale,
(3) ihmisen silmäiltävä yhden rivin totuus.

**Kaksi linkkitasoa:** frontmatterin `links` on koneluettava ja tyypitetty;
leipätekstin `[[wiki-linkit]]` ovat kevyitä ihmislinkkejä. Indeksointi lukee
molemmat ja generoi käänteislinkit — käsin ei ylläpidetä koskaan
kaksisuuntaisuutta.

## 4. Tiedostomallit (templatet)

Mallit ovat `system/schemas/`-kansiossa. Kolme esimerkkiä:

**Henkilö** (`entities/people/person-antti-makinen.md`)

```markdown
---
id: person:antti-makinen
type: person
title: "Antti Mäkinen"
summary: "Työkaveri Yritys Oy:ssä, backend-osaaja, tavattu 2024."
tags: [tyokaveri]
privacy: private
links:
  - rel: works-at
    to: org:yritys-oy
  - rel: collaborates-on
    to: project:jarvis
---

## Perustiedot
Rooli, miten tunnetaan, yhteystiedot.

## Historia
- 2026-07-01 — Auttoi Cloudflare-ongelmassa. [[2026-07-01]]

## Huomioita
Preferenssit, keskustelunaiheet, mitä kannattaa muistaa.
```

**Päätös** (`memory/decisions/2026-07-06-github-julkaisuautomaatio.md`) —
ADR-malli (Architecture Decision Record) sovellettuna elämään:

```markdown
---
id: decision:2026-07-06-github-julkaisuautomaatio
type: decision
title: "Julkaisu automatisoidaan git push -pohjaisesti"
summary: "JARVIS julkaistaan GitHub Pagesiin automaattipushilla; worker.js ei koskaan repoon."
status: active
links:
  - rel: concerns
    to: project:jarvis
  - rel: evidence
    to: ref:asennus-md
---

## Konteksti
Miksi päätös piti tehdä.

## Vaihtoehdot
Mitä harkittiin ja miksi hylättiin.

## Päätös
Mitä päätettiin.

## Seuraukset
Mitä tästä seuraa. Milloin kannattaa arvioida uudelleen.
```

**Muistimerkintä** (rivi `memory/stream/2026/07.jsonl`-tiedostossa):

```json
{"id":"mem:01J9ZK3W","ts":"2026-07-06T14:32:00+03:00","kind":"preference",
 "statement":"Lassi haluaa tummissa käyttöliittymissä leipätekstin neutraalina ja vaaleana; väri vain aksenttina.",
 "confidence":0.95,"importance":4,
 "source":{"kind":"conversation","ref":"conv:2026-07-02-ui-palaute","quote":"toi cyan-teksti on rasittavaa lukea"},
 "entities":["project:jarvis","person:lassi"],
 "status":"active","extracted_by":"claude-fable-5"}
```

Muut tyypit noudattavat samaa kaavaa: frontmatter + `## Tiivistelmä`-henkinen
alku + vapaamuotoiset osiot. Skeema määrää pakolliset kentät, ei osioita —
sisältö saa elää.

## 5. Tietotyypit

| Tyyppi | Kansio | Ydinkysymys |
|---|---|---|
| `person` | entities/people | Kuka? Miten liittyy elämääni? |
| `organization` | entities/organizations | Mikä taho? |
| `project` | entities/projects | Mitä rakennetaan, missä tilassa? |
| `skill` | entities/skills | Mitä osaan, millä tasolla, mistä näyttö? |
| `thing` | entities/things | Laite/omaisuus: hankinta, huolto, ohjeet |
| `decision` | memory/decisions | Mitä päätettiin ja miksi? |
| `event` | memory/timeline | Mitä tapahtui, milloin? |
| `note` (semantic) | memory/semantic | Tislattu fakta/oppi aiheesta |
| `journal` | memory/episodic | Mitä päivänä X tapahtui ja puhuttiin? |
| `memory` | memory/stream | Atominen muistimerkintä (JSONL) |
| `task` | work/tasks | Mitä pitää tehdä, mihin mennessä? |
| `goal` | work/goals.md | Mihin pyritään? |
| `preference` | profile/preferences.md + stream | Mistä pidän / en pidä? |
| `procedure` | library/procedures | Miten X tehdään? |
| `reference` | library/references | Ulkoinen lähde + oma arvio |
| `document` | library/documents | Alkuperäinen tiedosto + teksti |
| `conversation` | memory/episodic (tiivistelmä) | Mitä keskusteltiin? |

Uusi tyyppi lisätään kirjoittamalla skeema `system/schemas/`-kansioon —
arkkitehtuuri ei muutu.

## 6. Suhteet tietojen välillä

Tyypitetyt relaatiot frontmatterin `links`-listassa. Perussanasto:

```
owned-by, works-at, member-of          # kuuluminen
collaborates-on, involves              # osallistuminen
uses-skill, demonstrates, learned-from # osaaminen
concerns, decided-by, evidence         # päätöksenteko
part-of, depends-on, related           # rakenne
supersedes, superseded-by              # elinkaari
derived-from, source                   # alkuperä
```

Vastaukset kysyttyihin tapauksiin:

- **Projekti → ihmiset:** projekti listaa `involves: person:x` (rooli
  vapaaehtoisena lisäkenttänä). Henkilösivulle EI kirjoiteta mitään käsin —
  käänteislinkki syntyy indeksissä. Yksi suunta on totuus, toinen johdettu.
- **Taito → projektit:** relaatio elää *projektissa* (`uses-skill`), koska
  projekti on tapahtumapaikka. Taitosivun "näyttö"-osio generoidaan
  käänteislinkeistä: "JavaScript — näyttöä: [[project:jarvis]], ...".
- **Päätös → dokumentit:** `evidence: ref:x` tai `evidence: doc:x`.
  Päätös linkittää aina lähteisiinsä, jotta 5 vuoden päästä voi tarkistaa
  *mihin tietoon* päätös perustui.
- **Keskustelu → muistit:** keskustelutiivistelmä (episodic) saa ID:n
  `conv:2026-07-06-aihe`. Jokainen siitä louhittu muistimerkintä kantaa
  `source.ref: conv:...` + sitaatin. Suunta on muisti → keskustelu;
  "mitä tästä keskustelusta opittiin" on indeksikysely.

Sääntö: **relaatio kirjoitetaan sinne, missä se syntyy, tasan kerran.**
Kaksisuuntaisuus on aina koneen työtä.

## 7. Muistin elinkaari

```
INBOX      kaikki syöte tänne: chat-nostot, dokumentit, sähköpostit,
  │        äänimuistiot. Ei mitään vaatimuksia formaatille.
  ▼
EXTRACT    AI lukee syötteen ja louhii atomiset merkinnät (§8) +
  │        päättää: uusi tiedosto / olemassa olevan päivitys / vain stream.
  ▼
CATEGORIZE AI valitsee tyypin ja sijainnin skeemojen perusteella.
  │        Epävarmat → inbox/review/ ihmiselle (harvinaista).
  ▼
LINK       AI etsii katalogista liittyvät entiteetit ja lisää relaatiot.
  │        Tässä syntyy verkosto — tärkein automaation arvo.
  ▼
EMBED      Uudet/muuttuneet sirpaleet vektoroidaan, indeksit päivittyvät.
  │        (system/ päivittyy — git-diffi näyttää vain lähdemuutokset.)
  ▼
CONSOLIDATE viikoittain: duplikaatit yhdistetään, ristiriidat ratkaistaan
  │        (uudempi + varmempi voittaa, häviäjä → superseded), streamin
  │        toistuvat havainnot tislataan semantic-sivuiksi. "Unen" vastine.
  ▼
ARCHIVE    status: done/superseded + 12 kk ilman viittauksia → archive/.
           Mitään ei poisteta — arkisto on haettavissa mutta pois
           aktiivihaun oletuspainotuksesta.
```

Lassi koskee tähän putkeen vain halutessaan. Librarian on kone.

## 8. AI-muisti (automaattinen louhinta)

Jokaisesta keskustelusta louhitaan nollasta N kappaletta merkintöjä:

| Laji | Esimerkki |
|---|---|
| `fact` | "Lassin Garmin on Epix-malli" |
| `preference` | "Ei halua värillistä leipätekstiä tummassa UI:ssa" |
| `goal` | "Haluaa JARVISista toisen aivon 10 v aikajänteellä" |
| `task` | "Testaa remote control puhelimella" |
| `decision` | "Julkaisu automatisoitiin git pushilla" |
| `idea` | "Luento-ominaisuus tablettiin" |
| `relationship` | "Antti auttoi Cloudflare-ongelmassa → skill:cloudflare" |

Jokaisella merkinnällä (ks. JSONL-malli §4):

- **confidence** 0–1: kuinka varmasti tämä on totta. Suora lainaus ≈ 0.95,
  päättely ≈ 0.6. Alle 0.5 ei nouse koskaan promptiin ilman merkintää
  "epävarma".
- **importance** 1–5: vaikuttaako tämä tuleviin vastauksiin. 5 = identiteetti-
  tason asia (ylenee heti `profile/`-tiedostoon), 1 = kohina (vanhenee).
- **source**: keskustelu-ID + sitaatti. Jokainen muisti on jäljitettävissä
  hetkeen, jona se syntyi — tämä ratkaisee ristiriidat ja hallusinaatiot.
- **status**: `active | superseded | expired`. Muisti ei koskaan muutu
  jälkikäteen (append-only); korjaus on uusi merkintä + vanhan supersede.

Ylenemissääntö: kun sama asia havaitaan ≥2 kertaa tai importance ≥4,
konsolidointi kirjoittaa/päivittää Markdown-sivun (preferences.md,
semantic-sivu, tms.) ja stream-merkinnät jäävät todistusaineistoksi.

## 9. Nykyinen konteksti (`work/now.md`)

Kevyt, aina ajantasainen, **max ~1500 tokenia**. Liitetään jokaiseen
prompt-kutsuun sellaisenaan — tämä on JARVISin "työmuisti".

```markdown
---
id: context:now
updated: 2026-07-06T15:20:00+03:00
---
## Aktiivista nyt
- [[project:jarvis]]: remote control + GitHub-julkaisu saatu toimimaan;
  seuraavaksi muistiarkkitehtuurin toteutus.

## Avoimet tehtävät (top 5)
- Testaa remote control puhelimella
- ...

## Odottaa / seurannassa
- GitHub Pages -deploy toimii; Cloudflare KV wikin takana.

## Tällä viikolla opittua
- Desktop-appi ei tue remote controlia; CLI tarvitaan.
```

Päivitys automaattinen: jokaisen merkittävän keskustelun/session päätteeksi
AI kirjoittaa tiedoston uusiksi (vanha versio jää Git-historiaan — ilmainen
"kontekstin aikakone"). Kokoraja pakottaa priorisoimaan: now.md ei ole
loki vaan tilannekuva.

## 10. Pitkäkestoinen muisti — mitä ei koskaan unohdeta

`profile/core.md` + kaikki tiedostot joilla `permanence: core`:

- Identiteetti: nimi, syntymäaika, perhe, asuinhistoria
- Terveys: allergiat, lääkitykset, diagnoosit (privacy: secret)
- Arvot ja periaatteet, isot elämänpäätökset perusteluineen
- Avainihmiset ja suhteiden luonne
- Timeline-merkkipaalut (memory/timeline/)
- Kaikki `decision`-tyyppiset — päätöshistoria on toistuvien virheiden rokote

Säännöt: core-tietoa ei arkistoida eikä vanhenneta koskaan; se voi vain
täydentyä tai saada korjausmerkinnän. Konsolidointi ei saa tiivistää
core-tiedostoja häviöllisesti. Git + etävarmuuskopio (privaatti repo tai
salattu varmuuskopio secreteille — ks. §13 yksityisyystasot).

## 11. Haku (retrieval) — vain olennainen kontekstiin

Neljä kerrosta, halvimmasta kalleimpaan; useimmat kyselyt pysähtyvät tasolle 2:

1. **Aina mukana** (0 hakua): `work/now.md` + `profile/core.md`-tiivistelmä
   + preferences-tiivistelmä. Yhteensä < 3k tokenia.
2. **Katalogihaku**: `system/index/catalog.md` — yksi rivi per tiedosto
   (id + summary). LLM lukee katalogin (tai sen FTS-suodatetun osan) ja
   *pyytää* tarvitsemansa tiedostot ID:llä. Sama malli kuin ihmisen
   hakemisto: ensin sisällysluettelo, sitten sivu.
3. **Hybridihaku**: BM25 (SQLite FTS5) + vektorihaku rinnakkain,
   reciprocal rank fusion. Sirpale = frontmatterin summary tai H2-osio,
   metadata mukana (tyyppi, tuoreus, importance painottavat).
4. **Graafilaajennus**: osumien `links`-relaatiot 1 hyppy ulospäin —
   "kysyit projektista, tässä myös sen päätökset ja ihmiset".

Palautusmuoto on aina *sitaatti + ID + polku*, ei anonyymi tekstimössö —
malli voi viitata lähteeseen ja käyttäjä porautua siihen.

Malliriippumattomuus: hakukerros on oma Python-palvelunsa (tai Worker),
joka palauttaa pelkkää tekstiä. LLM vaihtuu; rajapinta
`retrieve(query, k, filters) -> [chunks]` ei.

## 12. Tuleva laajentuminen

Kaikki integraatiot noudattavat samaa kuviota: **konnektori → inbox →
sama putki** (§7). Uusi lähde ei koskaan vaadi arkkitehtuurimuutosta.

| Lähde | Konnektorin tuotos inboxiin |
|---|---|
| Puheassistentti / realtime | keskustelutranskripti → conv-tiivistelmä + stream |
| Kalenteri | tapahtumat → timeline + task-synkka |
| Sähköposti | valikoidut viestit → document + louhinta |
| GitHub | commitit/issuet → projektien Historia-osiot |
| PDF/kuvat/OCR | src/ + extracted/ tekstipari (§1 library) |
| Kotiautomaatio | tila-snapshotit → stream (kind: observation) |
| Paikalliset mallit | sama retrieve()-rajapinta; embeddings vaihdettavissa |

Vektorikannan vaihto (SQLite → Chroma → Qdrant → mikä-2031-onkaan) on
turvallinen, koska embeddings on johdettua dataa: `rebuild.py` ajaa
tiedostot uuteen kantaan tunnissa.

## 13. Parhaat käytännöt (vaatimusten yli)

1. **Append-only-historia**: totuus ei koskaan katoa, se korvautuu
   (`superseded-by`). Git tekee tästä ilmaista.
2. **Skeemaversiointi**: `schema_version` jokaisessa tiedostossa +
   migraatioskriptit. 10 vuodessa skeema muuttuu varmasti.
3. **Yksityisyystasot**: `public | private | secret`. Secret-tiedostot
   eivät mene pilvi-LLM:lle ilman erillistä lupaa eivätkä ikinä julkiseen
   repoon; niille salattu varmuuskopio. Tämä repo on julkinen → varsinainen
   knowledge/-repo on OMA, PRIVAATTI repo.
4. **Lint CI:nä**: `python tools/lint.py` validoi frontmatterin skeemaa
   vasten, tarkistaa rikkinäiset ID-viittaukset ja duplikaatti-ID:t.
   Ajetaan pre-commit-hookissa — korruptio pysähtyy oveen.
5. **Konsolidointi on tärkein prosessi**: ilman "unta" muisti on
   kaatopaikka. Viikkoajo: dedup, ristiriidat, tislaus, now.md-siivous,
   arkistointi. Tämä on se, mikä erottaa toisen aivon lokitiedostosta.
6. **Luottamuksen rappeuma**: aikasidonnaiset faktat (työpaikka, osoite,
   laitteet) saavat `expires`- tai `review-after`-kentän; vanhentunut
   fakta putoaa hakupainotuksessa kunnes vahvistetaan.
7. **Mittarit**: konsolidointi raportoi kuukausittain: merkintöjä,
   ylennyksiä, ristiriitoja, orpolinkkejä. Muistin terveys näkyväksi.
8. **Evaluointisetti hauille**: ~30 kysymys–odotettu-lähde-paria.
   Kun embeddings-malli tai hakulogiikka vaihtuu, ajetaan setti ja
   verrataan — muistin regressiotestit.
9. **Poistumistie aina auki**: koko järjestelmän on auettava pelkällä
   tekstieditorilla ja grepillä. Jos jokin työkalu kuolee, tieto ei kuole.

---

## Suhde nykyiseen JARVIS-toteutukseen

Nykyinen: PWA (jarvis.html) → Cloudflare Worker → Claude API + KV-wiki.
Siirtymäpolku ilman että mikään hajoaa:

1. **Vaihe 1**: luodaan privaatti `jarvis-knowledge`-repo tällä rakenteella.
   Worker alkaa kirjoittaa wiki-tallennukset myös GitHubiin (GitHub API,
   contents-endpoint) → KV jää nopeaksi välimuistiksi, repo on totuus.
2. **Vaihe 2**: `tools/`-Python-skriptit (lint, rebuild, consolidate)
   ajetaan aluksi käsin/ajastettuna omalla koneella tai GitHub Actionsissa.
3. **Vaihe 3**: Worker saa `retrieve()`-endpointin (aluksi katalogi + FTS,
   vektorit myöhemmin) — chat alkaa hakea kontekstia sen kautta.
4. **Vaihe 4**: automaattinen louhinta jokaisen keskustelun päätteeksi
   (sama mekanismi kuin nykyinen "Kokoa päivä", mutta §8:n muotoon).
