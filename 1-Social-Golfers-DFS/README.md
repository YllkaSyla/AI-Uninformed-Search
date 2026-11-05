# Social Golfers Problem – DFS me Backtracking

**Detyra e parë semestrale – Inteligjenca Artificiale (AI), 2026/2027**
**Tema:** Teknikat e painformuara të kërkimit (*Uninformed Search Techniques*)

---

## Përmbajtja

1. [Hyrje](#1-hyrje)
2. [Përshkrimi i problemit](#2-përshkrimi-i-problemit)
3. [Modelimi matematikor (Problem Modeling)](#3-modelimi-matematikor-problem-modeling)
4. [Paraqitja e problemit (Problem Representation)](#4-paraqitja-e-problemit-problem-representation)
5. [Funksioni objektiv (Objective Function)](#5-funksioni-objektiv-objective-function)
6. [Hapësira e kërkimit dhe peizazhi (Search Space & Landscape)](#6-hapësira-e-kërkimit-dhe-peizazhi-search-space--landscape)
7. [DFS me Backtracking](#7-dfs-me-backtracking)
8. [Implementimi në Python](#8-implementimi-në-python)
9. [Si ekzekutohet programi](#9-si-ekzekutohet-programi)
10. [Rezultatet, testimi dhe validimi](#10-rezultatet-testimi-dhe-validimi)
11. [Analiza e kompleksitetit](#11-analiza-e-kompleksitetit)
12. [Përfundimi](#12-përfundimi)
13. [Referencat](#13-referencat)

---

## 1. Hyrje

Ky projekt e zgjidh problemin e lojtarëve të golfit (*Social Golfer Problem*) me algoritmin e kërkimit në thellësi me kthim prapa (*Depth-First Search with Backtracking*). Projekti përmban:

- modelimin matematikor të problemit;
- variablat, domenet, kufizimet dhe paraqitjen e gjendjes;
- funksionin objektiv;
- llogaritjen e hapësirës së kërkimit dhe shpjegimin e peizazhit;
- implementimin në Python (`social_golfers.py`);
- testet automatike (`tests/test_social_golfers.py`).

Të gjitha rezultatet numerike në këtë dokument vijnë ose nga ekzekutimi real i programit, ose nga një llogaritje matematikore e shpjeguar.

---

## 2. Përshkrimi i problemit

32 lojtarë golfi luajnë një herë në javë, gjithmonë në 8 grupe me nga 4 lojtarë. Për sa javë mund të luajnë, në mënyrë që **asnjë çift lojtarësh të mos jetë në të njëjtin grup më shumë se një herë**?

Në formë të përgjithshme: a mund të planifikohen n = g × p lojtarë në g grupe me p lojtarë për w javë, pa u takuar asnjë çift më shumë se një herë?

Problemi shfaqet në dy forma:

| Forma | Pyetja |
|---|---|
| Problem vendimi (*decision problem*) SGP(g, p, w) | A ekziston orar i vlefshëm për w javë? |
| Problem optimizimi (*optimization problem*) | Cili është w maksimal për g dhe p të dhëna? |

Ky projekt trajton formën e optimizimit për g = 8 dhe p = 4. Algoritmi e zgjidh atë duke u përpjekur ta zgjerojë orarin javë pas jave.

---

## 3. Modelimi matematikor (Problem Modeling)

### 3.1 Parametrat

| Simboli | Kuptimi | Vlera |
|---|---|---|
| g | numri i grupeve në javë | 8 |
| p | numri i lojtarëve në grup | 4 |
| n = g · p | numri i lojtarëve | 32 |
| w | numri i javëve | i panjohur, maksimizohet |
| P = {0, …, n−1} | bashkësia e lojtarëve | {0, …, 31} |
| T = {1, …, w} | bashkësia e javëve | |

### 3.2 Formulimi

Orari i javës t është një ndarje (*partition*) e lojtarëve në g grupe:

```
Πₜ = { Bₜ,₁, Bₜ,₂, …, Bₜ,g }
```

ku për çdo grup vlen:

1. |Bₜ,ⱼ| = p (çdo grup ka p lojtarë)
2. Bₜ,ᵢ ∩ Bₜ,ⱼ = ∅ për i ≠ j (grupet nuk mbivendosen)
3. Bₜ,₁ ∪ … ∪ Bₜ,g = P (të gjithë lojtarët luajnë)

Orari i plotë është vargu i javëve:

```
S = (Π₁, Π₂, …, Π_w)
```

### 3.3 Kushti kryesor

Le të jetë m(a, b) numri i javëve në të cilat lojtarët a dhe b janë në të njëjtin grup:

```
m(a, b) = | { t ∈ T : ∃ j, {a, b} ⊆ Bₜ,ⱼ } |
```

Kushti i problemit është:

```
m(a, b) ≤ 1   për çdo çift a ≠ b
```

Kjo është ekuivalente me: dy grupe nga javë të ndryshme kanë më së shumti një lojtar të përbashkët, |Bₜ,ᵢ ∩ Bₜ',ⱼ| ≤ 1 për t ≠ t'.

Problemi i optimizimit është:

```
w* = max { w : ekziston orari S = (Π₁, …, Π_w) që plotëson të gjitha kushtet }
```

### 3.4 Interpretimi me graf

Çdo lojtar është nyje në grafin e plotë K₃₂, dhe çdo çift i mundshëm është brinjë (gjithsej C(32,2) = 496). Një grup me 4 lojtarë mbulon C(4,2) = 6 brinjë, kështu një javë mbulon 8 · 6 = 48 brinjë. Kushti kryesor do të thotë që asnjë brinjë nuk mbulohet nga dy javë të ndryshme.

### 3.5 Supozimet

1. Grupet janë të paemërtuara: renditja e grupeve brenda javës nuk ka rëndësi.
2. Renditja e lojtarëve brenda grupit nuk ka rëndësi.
3. Javët mund të ndërrohen mes vete pa e prishur vlefshmërinë.
4. Lojtarët janë simetrikë: riemërtimi i tyre jep përsëri orar të vlefshëm.
5. Të gjithë lojtarët luajnë çdo javë.
6. g dhe p janë fikse gjatë gjithë javëve.

Supozimet 1–4 janë simetri të problemit. Ato shfrytëzohen në algoritëm (seksioni 4.4).

### 3.6 Shembull i vogël: SGP(2, 2), n = 4

| Java | Grupi 1 | Grupi 2 |
|---|---|---|
| 1 | {0, 1} | {2, 3} |
| 2 | {0, 2} | {1, 3} |
| 3 | {0, 3} | {1, 2} |

Pas 3 javësh janë përdorur të 6 çiftet, prandaj java e 4-t është e pamundur dhe w* = 3. Programi e gjen këtë orar (seksioni 10).

---

## 4. Paraqitja e problemit (Problem Representation)

### 4.1 Variablat

| Opsioni | Variabla | Domeni |
|---|---|---|
| A | xₜ,ₐ = grupi i lojtarit a në javën t | {1, …, 8} |
| **B (i zgjedhur)** | **Bₜ,ⱼ = grupi j në javën t** | **bashkësitë me 4 lojtarë** |
| C | Πₜ = ndarja e plotë e javës t | ≈ 5.93 × 10¹⁹ vlera |

Përdoret **opsioni B**: variabla Bₜ,ⱼ paraqet grupin e j-të të javës t. Arsyet:

- Kushtet "grupi ka 4 lojtarë" dhe "lojtari nuk përsëritet në javë" plotësohen nga vetë mënyra e gjenerimit të kandidatëve.
- Çiftet e përsëritura zbulohen menjëherë kur propozohet grupi.
- Një nivel i pemës së kërkimit është një vendim për një grup, siç kërkohet nga DFS.

Opsioni A lejon gjendje me grupe të paplota, ndërsa opsioni C ka domen shumë të madh për t'u gjeneruar vlerë pas vlere.

Për w javë ka w · g variabla, p.sh. 80 për w = 10.

### 4.2 Domenet

**Domeni fillestar (statik):**

```
D(Bₜ,ⱼ) = { B ⊆ P : |B| = 4 },    |D| = C(32, 4) = 35 960
```

**Domeni aktual (dinamik):** gjatë kërkimit, një grup B është kandidat vetëm nëse:

1. asnjë lojtar i B nuk është vendosur më parë në javën aktuale;
2. asnjë çift brenda B nuk është takuar më parë;
3. B përmban lojtarin më të vogël të pavendosur në javën aktuale (rregulli SB2).

**Shembull:** me javën 1 të fiksuar, grupi i parë i javës 2 duhet të përmbajë lojtarin 0 dhe nga një lojtar prej 3 grupeve të ndryshme të javës 1 (jo nga grupi i lojtarit 0). Numri i kandidatëve është:

```
C(7, 3) · 4³ = 35 · 64 = 2 240
```

Kjo vlerë verifikohet me test (`test_number_of_candidates`).

### 4.3 Kufizimet (Hard Constraints)

| Nr. | Kufizimi | Formulimi | Si plotësohet në kod |
|---|---|---|---|
| C1 | Çdo lojtar në saktësisht një grup në javë | ∀t, ∀a: \|{ j : a ∈ Bₜ,ⱼ }\| = 1 | `generate_groups()` përdor vetëm lojtarë të pavendosur |
| C2 | Çdo grup ka 4 lojtarë | \|Bₜ,ⱼ\| = 4 | kandidatët gjenerohen me `combinations(…, p-1)` |
| C3 | Çdo javë ka 8 grupe | \|Πₜ\| = 8 | java mbyllet vetëm pas grupit të 8-të |
| C4 | Asnjë çift nuk takohet dy herë | m(a, b) ≤ 1 | `is_valid_group()` kontrollon 6 çiftet kundrejt `used_pairs` |
| C5 | Të gjithë lojtarët luajnë çdo javë | ∪ⱼ Bₜ,ⱼ = P | 8 · 4 = 32 lojtarë të ndryshëm pas 8 grupesh |

C1 dhe C5 shprehin të njëjtën gjë nga dy anë: me C2 dhe C3, 32 lojtarë të ndryshëm të vendosur do të thotë që secili luan saktësisht një herë.

C2, C3 dhe C1/C5 plotësohen nga struktura e kërkimit. **C4 është kufizimi që kontrollohet në mënyrë aktive** dhe që shkakton Backtracking. Funksioni `validate_schedule()` megjithatë i kontrollon të pesë kufizimet nga fillimi, pa u mbështetur në kërkimin.

### 4.4 Thyerja e simetrisë (Symmetry Breaking)

Këto rregulla nuk janë pjesë e problemit. Ato shtohen që DFS të mos kontrollojë disa herë orare që janë në thelb të njëjta.

| Nr. | Rregulli | Simetria që eliminohet |
|---|---|---|
| SB1 | Lojtarët brenda grupit në rend rritës: `(0, 4, 8, 12)` | renditja brenda grupit |
| SB2 | Grupi i ri përmban lojtarin më të vogël të pavendosur, kështu grupet renditen sipas lojtarit të parë | renditja e grupeve |
| SB3 | Java 1 fiksohet: (0,1,2,3), (4,5,6,7), …, (28,29,30,31) | riemërtimi i lojtarëve |

**Pse SB3 nuk e humb asnjë zgjidhje:** lojtarët e javës së parë të çdo orari të vlefshëm mund të riemërtohen në 0, 1, …, 31 sipas grupeve. Riemërtimi ndryshon vetëm emrat e çifteve, prandaj orari mbetet i vlefshëm.

Simetria e ndërrimit të javëve (supozimi 3) **nuk** eliminohet: e njëjta bashkësi javësh mund të arrihet në renditje të ndryshme.

### 4.5 Gjendja fillestare (Initial State)

- **Teorikisht:** orari i zbrazët S₀ = ( ), pa asnjë çift të përdorur.
- **Në implementim:** pas SB3, kërkimi fillon me javën 1 të fiksuar dhe 48 çifte të shënuara si të përdorura. DFS fillon nga grupi i parë i javës 2.

### 4.6 Gjendja përfundimtare dhe testi i qëllimit (Goal State, Goal Test)

**Testi i vlefshmërisë për w javë:**

```
Goal(S, w)  ⇔  |S| = w  dhe  S plotëson C1–C5
```

**Ndalimi i kërkimit të optimizimit.** Sa herë përfundon një javë e re, orari ruhet nëse ka më shumë javë se më i miri deri atëherë. Kërkimi ndalet kur:

| Rasti | Kuptimi i rezultatit |
|---|---|
| Arrihet kufiri teorik W_max | rezultati është optimal, sepse nuk mund të ketë më shumë javë |
| Pema kontrollohet e tëra (*exhausted*) | rezultati është **dëshmuar** optimal |
| Mbaron kufiri i kohës | rezultati është më i miri i gjetur, por **nuk është dëshmuar** optimal |

Gjetja e një orari me w javë dëshmon vetëm që w* ≥ w. Dëshmia që w është maksimumi kërkon arritjen e kufirit teorik ose kërkim shterues.

### 4.7 Paraqitja e gjendjes në Python (State Representation)

| Elementi | Në Python | Struktura dhe arsyeja |
|---|---|---|
| Grupi Bₜ,ⱼ | `(0, 4, 8, 12)` | **tuple**: i pandryshueshëm, i renditur (SB1), mund të futet në set |
| Java aktuale | `current_week = [(0,4,8,12), …]` | **listë**: grupet shtohen dhe hiqen nga fundi (`append` / `pop`) gjatë Backtracking |
| Javët e plota | `weeks = [java1, java2, …]` | **listë javësh**: ruan renditjen për shtypje |
| Çiftet e takuara | `used_pairs = {(0,1), (0,2), …}` | **set tuples (a, b), a < b**: kontrolli "a është takuar ky çift?" në O(1) |
| Lojtarët e vendosur këtë javë | `placed = {0, 4, 8, …}` | **set**: kontroll i shpejtë nëse lojtari është i lirë |
| Numri i takimeve m(a, b) | `{(0,1): 1, …}` | **dictionary**: përdoret në `calculate_objective()` dhe `validate_schedule()` |

Shembull i një orari të pjesshëm (java 1 e plotë, java 2 me 2 nga 8 grupe):

```python
weeks = [
    [(0,1,2,3), (4,5,6,7), (8,9,10,11), (12,13,14,15),
     (16,17,18,19), (20,21,22,23), (24,25,26,27), (28,29,30,31)]
]
current_week = [(0,4,8,12), (1,5,9,13)]
```

---

## 5. Funksioni objektiv (Objective Function)

### 5.1 Përkufizimi

Funksioni objektiv mat **numrin e javëve të plota dhe të vlefshme**:

```
f(S) = |S|        (maksimizohet)
```

me kusht që S të plotësojë C1–C5.

### 5.2 Masa e shkeljes së kufizimit C4

```
V(S) = Σ_{a<b} max(0, m(a, b) − 1)
```

V(S) është numri i takimeve të përsëritura. Orari është i vlefshëm vetëm nëse **V(S) = 0**. Në kod të dyja vlerat kthehen nga `calculate_objective(schedule)`, si `(f, V)`.

### 5.3 Lidhja me numrin maksimal të javëve

```
w* = max f(S),   me kusht V(S) = 0 dhe C1, C2, C3, C5
f(S) ≤ W_max = ⌊(n − 1)/(p − 1)⌋ = 10
```

**W_max = 10 është vetëm kufi i sipërm teorik** (seksioni 6.6). Ai tregon se 11 javë janë të pamundura, por vetë ky argument nuk dëshmon se ekziston orar me 10 javë.

### 5.4 Funksioni objektiv kundrejt kufizimeve të detyrueshme

| | Kufizimet e detyrueshme | Funksioni objektiv |
|---|---|---|
| Roli | përcaktojnë **cili orar lejohet** | përcakton **cili orar i lejuar është më i mirë** |
| Natyra | po / jo | vlerë numerike |
| Në DFS | çdo shkelje → refuzim i menjëhershëm, Backtracking | krahasohen vetëm oraret e vlefshme |
| Shembull | V(S) = 0 | f(S) = 5 javë |

DFS nuk krijon kurrë gjendje me V(S) > 0, sepse grupi që do ta shkaktonte refuzohet para se të shtohet. Prandaj V(S) përdoret kryesisht në validimin përfundimtar.

Algoritmet që lejojnë gjendje të pavlefshme (p.sh. Simulated Annealing) përdorin një funksion të penalizuar, si F(S) = f(S) − λ · V(S). **Ky projekt nuk e përdor**, sepse DFS punon vetëm me gjendje të vlefshme.

### 5.5 Shembull konkret

Java 1 është e fiksuar.

- Grupi i propozuar `(0, 1, 4, 5)` për javën 2: çiftet (0,1) dhe (4,5) janë takuar në javën 1, kështu V do të bëhej ≥ 2. Grupi **refuzohet**.
- Grupi i propozuar `(0, 4, 8, 12)`: asnjë nga 6 çiftet nuk është takuar, V mbetet 0. Grupi **pranohet**.

---

## 6. Hapësira e kërkimit dhe peizazhi (Search Space & Landscape)

### 6.1 Numri i grupeve të mundshme

```
C(32, 4) = 32! / (4! · 28!) = 35 960
```

Ky është domeni fillestar i çdo variable Bₜ,ⱼ.

### 6.2 Numri i ndarjeve të mundshme për një javë

Me grupe të emërtuara (grupi 1, grupi 2, …):

```
32! / (4!)⁸ = 2 390 461 829 733 887 910 000 000 ≈ 2.39 × 10²⁴
```

Meqë grupet janë të paemërtuara (supozimi 1), pjesëtohet edhe me 8! renditjet e grupeve:

```
32! / ((4!)⁸ · 8!) = 59 287 247 761 257 140 625 ≈ 5.93 × 10¹⁹
```

Shpjegimi: 32! janë të gjitha renditjet e lojtarëve. Pjesëtohet me (4!)⁸, sepse renditja brenda secilit nga 8 grupet nuk ka rëndësi, dhe me 8!, sepse renditja e grupeve nuk ka rëndësi.

Të dyja vlerat llogariten nga `search_space()` dhe verifikohen me teste.

### 6.3 Hapësira e kërkimit për disa javë

Shënojmë me 𝒫 = 5.93 × 10¹⁹ numrin e ndarjeve për një javë. Pa marrë parasysh kushtin C4, çdo javë zgjidhet në mënyrë të pavarur:

| Javë w | 𝒫^w (pa simetri) | 𝒫^(w−1) (java 1 e fiksuar) |
|---|---|---|
| 5 | ≈ 7.33 × 10⁹⁸ | ≈ 1.24 × 10⁷⁹ |
| 10 | ≈ 5.37 × 10¹⁹⁷ | ≈ 9.05 × 10¹⁷⁷ |

Hapësira rritet në mënyrë **eksponenciale** me numrin e javëve. Kushti C4 e zvogëlon shumë numrin e orareve të vlefshme, por kërkimi duhet ta zbulojë këtë duke provuar.

### 6.4 Hapësira e kërkimit, pema e kërkimit dhe peizazhi

| Koncepti | Çfarë është | Në këtë problem |
|---|---|---|
| **Hapësira e kërkimit (*Search Space*)** | bashkësia e të gjitha zgjidhjeve kandidate të plota | të gjitha oraret me w javë, ku çdo javë është ndarje e 32 lojtarëve |
| **Pema e kërkimit (*Search Tree*)** | struktura që ndërton algoritmi; çdo nyje është gjendje e pjesshme | rrënja = java 1; çdo nivel = një grup i vendosur; gjethet = orare të plota ose rrugë pa vazhdim |
| **Peizazhi (*Landscape*)** | hapësira e kërkimit + relacioni i fqinjësisë + funksioni që vlerëson cilësinë e çdo zgjidhjeje | oraret me w javë, fqinjësia "ndërro dy lojtarë", dhe vlerësimi V(S) |

**Peizazhi në detaj.** Peizazhi përkufizohet si treshja (X, N, V):

- **X**: oraret e plota me w javë që plotësojnë C1, C2, C3, C5 (por jo domosdoshmërisht C4).
- **N(S)**: fqinjët e një orari. Fqinj i S është çdo orar që merret duke ndërruar dy lojtarë nga grupe të ndryshme të së njëjtës javë. Ky ndërrim i ruan C1, C2, C3, C5. Për një javë ka C(32,2) − 8 · C(4,2) = 496 − 48 = **448** ndërrime të tilla, pra çdo orar ka 448 · (w − 1) fqinjë kur java 1 është e fiksuar.
- **V(S)**: "lartësia" e çdo pike në peizazh, pra numri i çifteve të përsëritura.

Zgjidhjet e vlefshme janë pikat me V(S) = 0, minimumet globale të peizazhit. Peizazhi ka edhe **minimume lokale**: orare me V(S) > 0 ku asnjë ndërrim i vetëm nuk e ul V. Kjo është arsyeja pse metodat e kërkimit lokal (*local search*) mund të ngecin.

**Rëndësi:** DFS **nuk lëviz nëpër peizazh** përmes fqinjëve. Ai ndërton zgjidhjen grup pas grupi në pemën e kërkimit dhe nuk krijon kurrë orare me V > 0. Peizazhi përshkruan strukturën e problemit, dhe dallimi tregon pse problemi është i vështirë për çdo metodë: hapësira është e madhe, dhe zgjidhjet e vlefshme janë shumë të rralla në të.

### 6.5 Faktori i degëzimit dhe thellësia e kërkimit

**Thellësia (*Search Depth*):** çdo nivel vendos një grup. Me javën 1 të fiksuar, një orar me w javë kërkon

```
d = (w − 1) · g   nivele;   për w = 10: d = 9 · 8 = 72
```

**Faktori i degëzimit (*Branching Factor*):** për grupin e j-të të një jave, lojtari i parë është i detyruar (SB2) dhe zgjidhen 3 lojtarë nga ata të mbetur. Pa kushtin C4, numri i kandidatëve është:

| Grupi j | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| C(31 − 4(j−1), 3) | 4 495 | 2 925 | 1 771 | 969 | 455 | 165 | 35 | 1 |

Prodhimi i këtyre numrave është saktësisht 59 287 247 761 257 140 625 = 𝒫. Kjo tregon që pema e kërkimit e një jave, pa kushtin C4, ka aq gjethe sa ndarje ka hapësira e kërkimit. Me kushtin C4, faktori i degëzimit bie shumë: p.sh. grupi i parë i javës 2 ka vetëm **2 240** kandidatë në vend të 4 495.

Faktori maksimal i degëzimit është b ≤ C(n − 1, p − 1) = C(31, 3) = 4 495.

### 6.6 Kufiri teorik i sipërm për numrin e javëve

**Argumenti sipas lojtarit:** Çdo lojtar ka 31 partnerë të mundshëm. Çdo javë luan me 3 partnerë, dhe sipas kushtit C4 ata duhet të jenë të rinj. Pra pas w javësh ka takuar 3w partnerë të ndryshëm:

```
3w ≤ 31   ⇒   w ≤ 31/3 ≈ 10.33   ⇒   w ≤ 10
```

**Argumenti sipas numrit total të çifteve:** Gjithsej ka C(32,2) = 496 çifte, dhe çdo javë përdor 8 · C(4,2) = 48 çifte të reja:

```
48w ≤ 496   ⇒   w ≤ 10.33   ⇒   w ≤ 10
```

**Në përgjithësi:**

```
w ≤ ⌊ (n − 1) / (p − 1) ⌋
```

Të dy argumentet japin të njëjtën formulë, sepse C(n,2) / (g · C(p,2)) = (n−1)/(p−1).

**Kujdes:** ky është **kufi i sipërm teorik**. Ai dëshmon që 11 javë janë të pamundura, por nuk dëshmon që ekzistojnë 10. Për shembull, për SGP(2, 3) kufiri është 2 javë, por programi dëshmon me kërkim shterues që maksimumi është vetëm **1** (seksioni 10). Për rastin 8-4, literatura raporton ekzistencën e një orari me 10 javë (shih [6]), por **programi ynë nuk e gjen atë** brenda kohës së testuar.

---

## 7. DFS me Backtracking

### 7.1 Nyja e kërkimit (Search Node)

Një nyje është një **orar i pjesshëm**: javët e plota (`weeks`), grupet e vendosura në javën aktuale (`current_week`), lojtarët e vendosur këtë javë (`placed`) dhe çiftet e takuara (`used_pairs`). Fëmijët e një nyjeje janë gjendjet që merren duke shtuar një grup të vlefshëm.

### 7.2 Si funksionon

1. Fillon me javën 1 të fiksuar.
2. Për grupin e ardhshëm gjeneron kandidatët: lojtari më i vogël i lirë dhe 3 lojtarë të tjerë të lirë.
3. Për çdo kandidat kontrollon nëse ndonjë nga 6 çiftet e tij është takuar më parë.
4. Kandidatët që shkelin kushtin refuzohen.
5. Kandidati i vlefshëm shtohet, dhe kërkimi vazhdon rekursivisht me grupin e ardhshëm. Pas grupit të 8-të fillon java e re.
6. Nëse për një gjendje nuk ka asnjë kandidat të vlefshëm, ndodh **Backtracking**: hiqet grupi i fundit dhe provohet kandidati i radhës.
7. Sa herë përfundon një javë, orari ruhet nëse është më i gjati deri atëherë.
8. Kërkimi ndalet kur arrihet kufiri teorik, kur kontrollohet e gjithë pema, ose kur mbaron koha.

DFS e eksploron pemën në thellësi: zbret gjithmonë te fëmija i parë i vlefshëm dhe kthehet prapa vetëm kur një degë nuk ka vazhdim.

### 7.3 Pseudokodi (pjesë ndihmëse)

```text
funksioni SOLVE(g, p, kufiri_kohës):
    fikso javën 1: (0..p-1), (p..2p-1), ...
    shëno çiftet e javës 1 në used_pairs
    best ← [java 1]
    nëse DFS() == false:
        arsyeja ← "exhausted"           // e gjithë pema u kontrollua
    kthe best

funksioni DFS():
    nodes ← nodes + 1
    nëse koha > kufiri_kohës:
        arsyeja ← "time_limit";  kthe true

    nëse current_week ka g grupe:                       // java u plotësua
        shto current_week në weeks
        nëse |weeks| > |best|:  best ← kopje e weeks
        nëse |weeks| == W_max:
            arsyeja ← "upper_bound";  kthe true
        fillo javë të re (current_week ← [], placed ← ∅)
        nëse DFS() == true:  kthe true
        rikthe javën e mëparshme
        kthe false

    available ← lojtarët që nuk janë në placed (të renditur)
    për çdo grup në GENERATE_GROUPS(available, used_pairs, p):
        ADD_GROUP(grup)                                 // zgjerimi i gjendjes
        nëse DFS() == true:  kthe true
        BACKTRACK()                                     // hiq grupin, liro çiftet
    kthe false                                          // asnjë kandidat nuk funksionoi

funksioni GENERATE_GROUPS(available, used_pairs, p):
    first ← available[0]                                // SB2
    për çdo kombinim rest me p-1 lojtarë nga available[1:]:
        grup ← (first) + rest                           // SB1: i renditur
        nëse asnjë çift i grupit nuk është në used_pairs:   // C4
            jep grup
```

---

## 8. Implementimi në Python

I gjithë kodi është në `social_golfers.py`. Përdoren vetëm biblioteka standarde të Python-it (`itertools`, `math`, `time`, `sys`).

| Funksioni / Metoda | Roli | Lidhja me modelin |
|---|---|---|
| `pair_key(a, b)` | kthen çiftin si `(min, max)` | çifti {a, b} |
| `group_pairs(group)` | 6 çiftet e një grupi | çiftet e Bₜ,ⱼ |
| `is_valid_group(group, used_pairs)` | kontrollon kufizimin C4 | m(a, b) ≤ 1 |
| `generate_groups(available, used_pairs, p)` | gjeneron domenin aktual | C1, C2, C4, SB1, SB2 |
| `upper_bound(n, p)` | kufiri teorik i sipërm | ⌊(n−1)/(p−1)⌋ |
| `count_meetings(schedule)` | numëron m(a, b) me dictionary | m(a, b) |
| `calculate_objective(schedule)` | kthen (f, V) | f(S), V(S) |
| `validate_schedule(schedule, g, p)` | validim i pavarur i C1–C5 | të gjitha kufizimet |
| `SocialGolfersDFS.add_group()` | zgjerimi i gjendjes | vendosja e Bₜ,ⱼ |
| `SocialGolfersDFS.backtrack()` | heq grupin e fundit | Backtracking |
| `SocialGolfersDFS.dfs()` | kërkimi rekursiv | DFS |
| `SocialGolfersDFS.solve()` | fikson javën 1 dhe nis DFS | SB3, gjendja fillestare |
| `search_space(g, p)` | C(n,p), 𝒫, numri i çifteve | seksioni 6 |
| `print_schedule()`, `main()` | shfaqja e rezultateve | |

Kandidatët gjenerohen me një **generator** (`yield`). Kështu në çdo nivel të rekursionit nuk ruhet lista e të gjithë kandidatëve, por vetëm pozita aktuale në `combinations`.

---

## 9. Si ekzekutohet programi

Kërkohet Python 3.8 ose më i ri. Nuk ka nevojë për instalim paketash.

Kjo detyrë është pjesë e repository-t `AI-Uninformed-Search`, ku secila detyrë ka folderin e vet me kodin, testet dhe README-në:

```text
AI-Uninformed-Search/
├── 1-Social-Golfers-DFS/
│   ├── README.md
│   ├── social_golfers.py
│   └── tests/
│       └── test_social_golfers.py
├── 2-Sudoku-BFS/
├── 3-Latin-Square-IDDFS/
└── 4-Search-Trees/
```

Hapni folderin `AI-Uninformed-Search` në VS Code, hapni terminalin (**Terminal → New Terminal**) dhe hyni në folderin e kësaj detyre:

```bash
cd 1-Social-Golfers-DFS
```

Pastaj ekzekutoni:

```bash
# Konfigurimi kryesor: g = 8, p = 4, kufiri i kohës 60 sekonda
python social_golfers.py

# Parametra të tjerë: g, p, kufiri i kohës në sekonda
python social_golfers.py 8 4 300
python social_golfers.py 3 3 10

# Testet
python -m unittest discover tests -v
```

Në disa sisteme komanda është `python3` në vend të `python`.

---

## 10. Rezultatet, testimi dhe validimi

### 10.1 Konfigurimi kryesor: n = 32, g = 8, p = 4

Ekzekutimi `python social_golfers.py 8 4 60`:

```text
Numri i lojtarëve (n):           32
Numri i grupeve (g):             8
Madhësia e grupit (p):           4
Kufiri teorik i sipërm:          10 javë (nuk garantohet)
Grupe të mundshme C(32,4):      35,960
Ndarje të mundshme për javë:     59,287,247,761,257,140,625
Kufiri i kohës:                  60 s
----------------------------------------------------------------------
Numri i javëve të gjetura:       5
Java  1: (0,1,2,3)  (4,5,6,7)  (8,9,10,11)  (12,13,14,15)  (16,17,18,19)  (20,21,22,23)  (24,25,26,27)  (28,29,30,31)
Java  2: (0,4,8,12)  (1,5,9,13)  (2,6,10,14)  (3,7,11,15)  (16,20,24,28)  (17,21,25,29)  (18,22,26,30)  (19,23,27,31)
Java  3: (0,5,10,15)  (1,4,11,14)  (2,7,8,13)  (3,6,9,12)  (16,21,26,31)  (17,20,27,30)  (18,23,24,29)  (19,22,25,28)
Java  4: (0,6,11,13)  (1,7,10,12)  (2,4,9,15)  (3,5,8,14)  (16,22,27,29)  (17,23,26,28)  (18,20,25,31)  (19,21,24,30)
Java  5: (0,7,9,14)  (1,6,8,15)  (2,5,11,12)  (3,4,10,13)  (16,23,25,30)  (17,22,24,31)  (18,21,27,28)  (19,20,26,29)
----------------------------------------------------------------------
Çifte të përsëritura V(S):       0
Nyje të vizituara:               896,503
Operacione Backtracking:         893,354
Koha e ekzekutimit:              60.00 s
Orari është i vlefshëm:          PO
Arsyeja e ndalimit:              Mbaroi koha -> rezultati është më i miri i gjetur, por NUK është dëshmuar optimal.
```

Me kufi kohe 5 minuta (`python social_golfers.py 8 4 300`), rezultati mbetet i njëjtë:

| Kufiri i kohës | Javë të gjetura | Nyje të vizituara | Backtracking | V(S) | I vlefshëm |
|---|---|---|---|---|---|
| 60 s | 5 | 896 503 | 893 354 | 0 | PO |
| 300 s | 5 | 4 587 519 | 4 571 928 | 0 | PO |

Numri i nyjeve dhe i operacioneve Backtracking varet nga shpejtësia e kompjuterit, sepse kërkimi ndalet pas një kohe të caktuar, jo pas një numri të caktuar nyjesh. Në një kompjuter më të shpejtë vizitohen më shumë nyje brenda së njëjtës kohë. Numri i javëve dhe orari janë të njëjtë në çdo ekzekutim, sepse kandidatët provohen gjithmonë në të njëjtën renditje.

**Interpretimi:**

- DFS gjen një orar të vlefshëm me **5 javë**, me V(S) = 0, dhe validimi i pavarur e konfirmon.
- Pesë javët gjenden shumë shpejt, pothuajse pa Backtracking. Më pas kërkimi kalon të gjithë kohën duke u kthyer prapa: degët e para që zgjodhi për javët 2–5 nuk lejojnë javën e 6-të, dhe pema nën to është shumë e madhe për t'u kontrolluar e tëra.
- Rezultati tregon që **w* ≥ 5**. Nuk dëshmon që 5 është maksimumi: kufiri teorik është 10, dhe literatura raporton orar me 10 javë [6]. Ky dallim është kufizim i pritur i kërkimit të painformuar në një hapësirë kaq të madhe.

### 10.2 Instanca të vogla (verifikimi i saktësisë)

Rezultatet nga ekzekutimi i programit:

| Instanca | n | Kufiri teorik | Javë të gjetura | Nyje | Backtracking | Arsyeja e ndalimit |
|---|---|---|---|---|---|---|
| SGP(2, 2) | 4 | 3 | 3 | 7 | 0 | arrihet kufiri → optimal |
| SGP(2, 3) | 6 | 2 | 1 | 2 | 0 | pema e plotë → **dëshmuar** optimal |
| SGP(3, 2) | 6 | 5 | 5 | 20 | 3 | arrihet kufiri → optimal |
| SGP(3, 3) | 9 | 4 | 4 | 13 | 0 | arrihet kufiri → optimal |
| SGP(4, 4) | 16 | 5 | 5 | 21 | 0 | arrihet kufiri → optimal |
| SGP(4, 3) | 12 | 5 | 4 | 1 439 948 | 1 355 976 | koha (20 s) → jo i dëshmuar |
| SGP(5, 3) | 15 | 7 | 6 | 1 575 452 | 1 527 859 | koha (30 s) → jo i dëshmuar |

SGP(2, 3) është shembull i rëndësishëm: kufiri teorik është 2 javë, por me javën 1 = {0,1,2}, {3,4,5}, grupi i lojtarit 0 në javën 2 duhet të përmbajë dy lojtarë nga {3,4,5}. Atëherë lojtarët 1 dhe 2 mbeten bashkë me lojtarin e tretë, dhe çifti (1,2) përsëritet. Programi e dëshmon këtë me kërkim shterues. Pra **kufiri teorik nuk arrihet gjithmonë**.

### 10.3 Testet automatike

Skedari `tests/test_social_golfers.py` përmban 24 teste (`unittest`, pa paketa shtesë):

| Grupi i testeve | Çka verifikon |
|---|---|
| `TestHelpers` | çiftet (6 për grup, 48 për javë), refuzimi i `(0,1,4,5)` dhe pranimi i `(0,4,8,12)` |
| `TestGenerateGroups` | kandidatët përmbajnë lojtarin më të vogël, kanë 4 lojtarë të renditur, nuk përsërisin çifte; numri i tyre është 2 240 |
| `TestSearchSpaceAndBound` | C(32,4) = 35 960, 𝒫 = 59 287 247 761 257 140 625, kufiri i sipërm |
| `TestObjectiveAndValidation` | f dhe V; validimi zbulon numër të gabuar grupesh, madhësi të gabuar, lojtar dy herë në javë, çift të përsëritur |
| `TestDFS` | rezultatet e njohura për SGP(2,2), SGP(2,3), SGP(3,3); orar i vlefshëm për 8-4; Backtracking e rikthen gjendjen saktë |

Rezultati i ekzekutimit `python -m unittest discover tests -v`:

```text
Ran 24 tests in 3.042s

OK
```

---

## 11. Analiza e kompleksitetit

### 11.1 Parametrat

- **b (faktori i degëzimit):** b ≤ C(n − 1, p − 1) = 4 495. Faktori real është shumë më i vogël për shkak të C4, dhe zvogëlohet me çdo grup të vendosur (seksioni 6.5).
- **d (thellësia):** d = (w − 1) · g. Për w = 10, d = 72.

### 11.2 Kompleksiteti kohor (Time Complexity)

Në rastin më të keq, DFS viziton të gjitha nyjet e pemës. Kufiri i përgjithshëm është **O(b^d)**. Për këtë problem mund të jepet kufi më i saktë: pa kushtin C4, pema e çdo jave ka saktësisht 𝒫 gjethe, kështu numri i gjetheve për w javë është më së shumti

```
𝒫^(w−1) ≈ 9.05 × 10¹⁷⁷   për w = 10
```

Çdo nyje kërkon gjenerimin e kandidatëve: provohen më së shumti C(31, 3) = 4 495 kombinime, secila me 6 kontrolle në set në O(1). Pra puna për nyje është O(C(n−1, p−1) · p²).

**Supozimet:** këto janë kufij të sipërm. Ata supozojnë që C4 nuk pret asnjë degë, gjë që në praktikë nuk ndodh.

### 11.3 Kompleksiteti hapësinor (Space Complexity)

- Thellësia e rekursionit: d = 72 thirrje.
- Në çdo nivel ruhet vetëm generator-i i kandidatëve, jo lista e tyre: O(p) për nivel.
- `used_pairs`: më së shumti C(n, 2) = 496 çifte, pra O(n²).
- `best_schedule`: O(w · n).

Gjithsej: **O(d · p + n² + w · n)**, pra hapësira rritet linearisht me thellësinë. Kjo është përparësia kryesore e DFS ndaj BFS, i cili do të duhej të ruante një nivel të tërë të pemës.

### 11.4 Ndikimi i kontrollit të kufizimeve dhe i Backtracking

- **Kontrolli i C4** ndodh menjëherë kur propozohet grupi, jo pasi të plotësohet orari. Kështu një degë e pavlefshme pritet sapo shfaqet, dhe e gjithë nënpema e saj nuk vizitohet kurrë. Shembull: për grupin e parë të javës 2 mbeten 2 240 nga 4 495 kandidatë.
- **Backtracking** e bën kërkimin të plotë (*complete*): nëse ekziston zgjidhje, ajo gjendet herët a vonë, sepse çdo alternativë provohet. Por kur zgjedhjet e hershme janë të gabuara, algoritmi duhet të kontrollojë të gjithë nënpemën nën to para se t'i ndryshojë. Kjo është arsyeja e numrit të madh të operacioneve Backtracking në rastin 8-4.
- **Thyerja e simetrisë** (SB1–SB3) e zvogëlon pemën: SB1 dhe SB2 me faktorët (4!)⁸ · 8! për javë, SB3 me një javë të tërë.

### 11.5 Kompleksiteti teorik kundrejt statistikave reale

Formulat teorike japin rastin më të keq (≈ 10¹⁷⁷ gjethe), ndërsa programi viziton rreth 9 × 10⁵ nyje në 60 sekonda. Dallimi vjen nga dy arsye:

1. Kushti C4 dhe thyerja e simetrisë presin pjesën më të madhe të pemës.
2. Kërkimi ndalet nga kufiri i kohës, kështu viziton vetëm një pjesë të vogël të pemës së mbetur.

Statistikat reale (nyjet, Backtracking, koha) varen nga instanca, renditja e kandidatëve dhe shpejtësia e kompjuterit. Kompleksiteti teorik varet vetëm nga madhësia e problemit.

---

## 12. Përfundimi

- Problemi u modelua matematikisht si varg ndarjesh javore me kushtin m(a, b) ≤ 1.
- U zgjodhën variablat Bₜ,ⱼ (grupi si variabël), me domen fillestar C(32,4) = 35 960 dhe domen dinamik që e ngushton kërkimi.
- Funksioni objektiv f(S) = numri i javëve u maksimizua me kushtin V(S) = 0.
- Hapësira e kërkimit është ≈ 5.93 × 10¹⁹ ndarje për javë, dhe rritet eksponencialisht me numrin e javëve.
- Kufiri teorik i sipërm është **10 javë**. Ai është kufi, jo zgjidhje e garantuar.
- DFS me Backtracking gjeti një orar të vlefshëm me **5 javë** për 32 lojtarë, të verifikuar me validim të pavarur. Ky rezultat nuk është dëshmuar optimal.
- Në instancat e vogla, programi arrin kufirin teorik ose e dëshmon optimumin me kërkim shterues.

Kërkimi i painformuar është i plotë dhe ka nevojë për pak memorie, por në një hapësirë kaq të madhe nuk mjafton për të gjetur orarin me 10 javë. Për këtë nevojiten teknika të tjera të kursit, si *forward checking*, heuristikat e renditjes ose kërkimi lokal.

---

## 13. Referencat

1. S. Russell, P. Norvig, *Artificial Intelligence: A Modern Approach*, 3rd ed., Kapitulli 3 (Solving Problems by Searching).
2. Z. Michalewicz, D. B. Fogel, *How to Solve It: Modern Heuristics*, 2nd ed., Springer, 2004, Kapitujt 1–3.
3. N. Musliu, *Uninformed Search*, TU Wien: http://www.dbai.tuwien.ac.at/staff/musliu/ProblemSolvingAI/Class2UninformedSearch.pdf
4. N. Musliu, *Basic Concepts of Problem Solving*, TU Wien: http://www.dbai.tuwien.ac.at/staff/musliu/ProblemSolvingAI/class1BasicConcepts.pdf
5. W. Harvey, *CSPLib Problem 010: Social Golfers Problem*, https://www.csplib.org
6. *Social golfer problem*, Wikipedia: https://en.wikipedia.org/wiki/Social_golfer_problem (ekzistenca e orarit 8-4-10, i ndërtuar në mënyrë eksplicite nga A. Aguado në vitin 2004).# Social Golfers Problem – DFS me Backtracking

**Detyra e parë semestrale – Inteligjenca Artificiale (AI), 2026/2027**
**Tema:** Teknikat e painformuara të kërkimit (*Uninformed Search Techniques*)

---

## Përmbajtja

1. [Hyrje](#1-hyrje)
2. [Përshkrimi i problemit](#2-përshkrimi-i-problemit)
3. [Modelimi matematikor (Problem Modeling)](#3-modelimi-matematikor-problem-modeling)
4. [Paraqitja e problemit (Problem Representation)](#4-paraqitja-e-problemit-problem-representation)
5. [Funksioni objektiv (Objective Function)](#5-funksioni-objektiv-objective-function)
6. [Hapësira e kërkimit dhe peizazhi (Search Space & Landscape)](#6-hapësira-e-kërkimit-dhe-peizazhi-search-space--landscape)
7. [DFS me Backtracking](#7-dfs-me-backtracking)
8. [Implementimi në Python](#8-implementimi-në-python)
9. [Si ekzekutohet programi](#9-si-ekzekutohet-programi)
10. [Rezultatet, testimi dhe validimi](#10-rezultatet-testimi-dhe-validimi)
11. [Analiza e kompleksitetit](#11-analiza-e-kompleksitetit)
12. [Përfundimi](#12-përfundimi)
13. [Referencat](#13-referencat)

---

## 1. Hyrje

Ky projekt e zgjidh problemin e lojtarëve të golfit (*Social Golfer Problem*) me algoritmin e kërkimit në thellësi me kthim prapa (*Depth-First Search with Backtracking*). Projekti përmban:

- modelimin matematikor të problemit;
- variablat, domenet, kufizimet dhe paraqitjen e gjendjes;
- funksionin objektiv;
- llogaritjen e hapësirës së kërkimit dhe shpjegimin e peizazhit;
- implementimin në Python (`social_golfers.py`);
- testet automatike (`tests/test_social_golfers.py`).

Të gjitha rezultatet numerike në këtë dokument vijnë ose nga ekzekutimi real i programit, ose nga një llogaritje matematikore e shpjeguar.

---

## 2. Përshkrimi i problemit

32 lojtarë golfi luajnë një herë në javë, gjithmonë në 8 grupe me nga 4 lojtarë. Për sa javë mund të luajnë, në mënyrë që **asnjë çift lojtarësh të mos jetë në të njëjtin grup më shumë se një herë**?

Në formë të përgjithshme: a mund të planifikohen n = g × p lojtarë në g grupe me p lojtarë për w javë, pa u takuar asnjë çift më shumë se një herë?

Problemi shfaqet në dy forma:

| Forma | Pyetja |
|---|---|
| Problem vendimi (*decision problem*) SGP(g, p, w) | A ekziston orar i vlefshëm për w javë? |
| Problem optimizimi (*optimization problem*) | Cili është w maksimal për g dhe p të dhëna? |

Ky projekt trajton formën e optimizimit për g = 8 dhe p = 4. Algoritmi e zgjidh atë duke u përpjekur ta zgjerojë orarin javë pas jave.

---

## 3. Modelimi matematikor (Problem Modeling)

### 3.1 Parametrat

| Simboli | Kuptimi | Vlera |
|---|---|---|
| g | numri i grupeve në javë | 8 |
| p | numri i lojtarëve në grup | 4 |
| n = g · p | numri i lojtarëve | 32 |
| w | numri i javëve | i panjohur, maksimizohet |
| P = {0, …, n−1} | bashkësia e lojtarëve | {0, …, 31} |
| T = {1, …, w} | bashkësia e javëve | |

### 3.2 Formulimi

Orari i javës t është një ndarje (*partition*) e lojtarëve në g grupe:

```
Πₜ = { Bₜ,₁, Bₜ,₂, …, Bₜ,g }
```

ku për çdo grup vlen:

1. |Bₜ,ⱼ| = p (çdo grup ka p lojtarë)
2. Bₜ,ᵢ ∩ Bₜ,ⱼ = ∅ për i ≠ j (grupet nuk mbivendosen)
3. Bₜ,₁ ∪ … ∪ Bₜ,g = P (të gjithë lojtarët luajnë)

Orari i plotë është vargu i javëve:

```
S = (Π₁, Π₂, …, Π_w)
```

### 3.3 Kushti kryesor

Le të jetë m(a, b) numri i javëve në të cilat lojtarët a dhe b janë në të njëjtin grup:

```
m(a, b) = | { t ∈ T : ∃ j, {a, b} ⊆ Bₜ,ⱼ } |
```

Kushti i problemit është:

```
m(a, b) ≤ 1   për çdo çift a ≠ b
```

Kjo është ekuivalente me: dy grupe nga javë të ndryshme kanë më së shumti një lojtar të përbashkët, |Bₜ,ᵢ ∩ Bₜ',ⱼ| ≤ 1 për t ≠ t'.

Problemi i optimizimit është:

```
w* = max { w : ekziston orari S = (Π₁, …, Π_w) që plotëson të gjitha kushtet }
```

### 3.4 Interpretimi me graf

Çdo lojtar është nyje në grafin e plotë K₃₂, dhe çdo çift i mundshëm është brinjë (gjithsej C(32,2) = 496). Një grup me 4 lojtarë mbulon C(4,2) = 6 brinjë, kështu një javë mbulon 8 · 6 = 48 brinjë. Kushti kryesor do të thotë që asnjë brinjë nuk mbulohet nga dy javë të ndryshme.

### 3.5 Supozimet

1. Grupet janë të paemërtuara: renditja e grupeve brenda javës nuk ka rëndësi.
2. Renditja e lojtarëve brenda grupit nuk ka rëndësi.
3. Javët mund të ndërrohen mes vete pa e prishur vlefshmërinë.
4. Lojtarët janë simetrikë: riemërtimi i tyre jep përsëri orar të vlefshëm.
5. Të gjithë lojtarët luajnë çdo javë.
6. g dhe p janë fikse gjatë gjithë javëve.

Supozimet 1–4 janë simetri të problemit. Ato shfrytëzohen në algoritëm (seksioni 4.4).

### 3.6 Shembull i vogël: SGP(2, 2), n = 4

| Java | Grupi 1 | Grupi 2 |
|---|---|---|
| 1 | {0, 1} | {2, 3} |
| 2 | {0, 2} | {1, 3} |
| 3 | {0, 3} | {1, 2} |

Pas 3 javësh janë përdorur të 6 çiftet, prandaj java e 4-t është e pamundur dhe w* = 3. Programi e gjen këtë orar (seksioni 10).

---

## 4. Paraqitja e problemit (Problem Representation)

### 4.1 Variablat

| Opsioni | Variabla | Domeni |
|---|---|---|
| A | xₜ,ₐ = grupi i lojtarit a në javën t | {1, …, 8} |
| **B (i zgjedhur)** | **Bₜ,ⱼ = grupi j në javën t** | **bashkësitë me 4 lojtarë** |
| C | Πₜ = ndarja e plotë e javës t | ≈ 5.93 × 10¹⁹ vlera |

Përdoret **opsioni B**: variabla Bₜ,ⱼ paraqet grupin e j-të të javës t. Arsyet:

- Kushtet "grupi ka 4 lojtarë" dhe "lojtari nuk përsëritet në javë" plotësohen nga vetë mënyra e gjenerimit të kandidatëve.
- Çiftet e përsëritura zbulohen menjëherë kur propozohet grupi.
- Një nivel i pemës së kërkimit është një vendim për një grup, siç kërkohet nga DFS.

Opsioni A lejon gjendje me grupe të paplota, ndërsa opsioni C ka domen shumë të madh për t'u gjeneruar vlerë pas vlere.

Për w javë ka w · g variabla, p.sh. 80 për w = 10.

### 4.2 Domenet

**Domeni fillestar (statik):**

```
D(Bₜ,ⱼ) = { B ⊆ P : |B| = 4 },    |D| = C(32, 4) = 35 960
```

**Domeni aktual (dinamik):** gjatë kërkimit, një grup B është kandidat vetëm nëse:

1. asnjë lojtar i B nuk është vendosur më parë në javën aktuale;
2. asnjë çift brenda B nuk është takuar më parë;
3. B përmban lojtarin më të vogël të pavendosur në javën aktuale (rregulli SB2).

**Shembull:** me javën 1 të fiksuar, grupi i parë i javës 2 duhet të përmbajë lojtarin 0 dhe nga një lojtar prej 3 grupeve të ndryshme të javës 1 (jo nga grupi i lojtarit 0). Numri i kandidatëve është:

```
C(7, 3) · 4³ = 35 · 64 = 2 240
```

Kjo vlerë verifikohet me test (`test_number_of_candidates`).

### 4.3 Kufizimet (Hard Constraints)

| Nr. | Kufizimi | Formulimi | Si plotësohet në kod |
|---|---|---|---|
| C1 | Çdo lojtar në saktësisht një grup në javë | ∀t, ∀a: \|{ j : a ∈ Bₜ,ⱼ }\| = 1 | `generate_groups()` përdor vetëm lojtarë të pavendosur |
| C2 | Çdo grup ka 4 lojtarë | \|Bₜ,ⱼ\| = 4 | kandidatët gjenerohen me `combinations(…, p-1)` |
| C3 | Çdo javë ka 8 grupe | \|Πₜ\| = 8 | java mbyllet vetëm pas grupit të 8-të |
| C4 | Asnjë çift nuk takohet dy herë | m(a, b) ≤ 1 | `is_valid_group()` kontrollon 6 çiftet kundrejt `used_pairs` |
| C5 | Të gjithë lojtarët luajnë çdo javë | ∪ⱼ Bₜ,ⱼ = P | 8 · 4 = 32 lojtarë të ndryshëm pas 8 grupesh |

C1 dhe C5 shprehin të njëjtën gjë nga dy anë: me C2 dhe C3, 32 lojtarë të ndryshëm të vendosur do të thotë që secili luan saktësisht një herë.

C2, C3 dhe C1/C5 plotësohen nga struktura e kërkimit. **C4 është kufizimi që kontrollohet në mënyrë aktive** dhe që shkakton Backtracking. Funksioni `validate_schedule()` megjithatë i kontrollon të pesë kufizimet nga fillimi, pa u mbështetur në kërkimin.

### 4.4 Thyerja e simetrisë (Symmetry Breaking)

Këto rregulla nuk janë pjesë e problemit. Ato shtohen që DFS të mos kontrollojë disa herë orare që janë në thelb të njëjta.

| Nr. | Rregulli | Simetria që eliminohet |
|---|---|---|
| SB1 | Lojtarët brenda grupit në rend rritës: `(0, 4, 8, 12)` | renditja brenda grupit |
| SB2 | Grupi i ri përmban lojtarin më të vogël të pavendosur, kështu grupet renditen sipas lojtarit të parë | renditja e grupeve |
| SB3 | Java 1 fiksohet: (0,1,2,3), (4,5,6,7), …, (28,29,30,31) | riemërtimi i lojtarëve |

**Pse SB3 nuk e humb asnjë zgjidhje:** lojtarët e javës së parë të çdo orari të vlefshëm mund të riemërtohen në 0, 1, …, 31 sipas grupeve. Riemërtimi ndryshon vetëm emrat e çifteve, prandaj orari mbetet i vlefshëm.

Simetria e ndërrimit të javëve (supozimi 3) **nuk** eliminohet: e njëjta bashkësi javësh mund të arrihet në renditje të ndryshme.

### 4.5 Gjendja fillestare (Initial State)

- **Teorikisht:** orari i zbrazët S₀ = ( ), pa asnjë çift të përdorur.
- **Në implementim:** pas SB3, kërkimi fillon me javën 1 të fiksuar dhe 48 çifte të shënuara si të përdorura. DFS fillon nga grupi i parë i javës 2.

### 4.6 Gjendja përfundimtare dhe testi i qëllimit (Goal State, Goal Test)

**Testi i vlefshmërisë për w javë:**

```
Goal(S, w)  ⇔  |S| = w  dhe  S plotëson C1–C5
```

**Ndalimi i kërkimit të optimizimit.** Sa herë përfundon një javë e re, orari ruhet nëse ka më shumë javë se më i miri deri atëherë. Kërkimi ndalet kur:

| Rasti | Kuptimi i rezultatit |
|---|---|
| Arrihet kufiri teorik W_max | rezultati është optimal, sepse nuk mund të ketë më shumë javë |
| Pema kontrollohet e tëra (*exhausted*) | rezultati është **dëshmuar** optimal |
| Mbaron kufiri i kohës | rezultati është më i miri i gjetur, por **nuk është dëshmuar** optimal |

Gjetja e një orari me w javë dëshmon vetëm që w* ≥ w. Dëshmia që w është maksimumi kërkon arritjen e kufirit teorik ose kërkim shterues.

### 4.7 Paraqitja e gjendjes në Python (State Representation)

| Elementi | Në Python | Struktura dhe arsyeja |
|---|---|---|
| Grupi Bₜ,ⱼ | `(0, 4, 8, 12)` | **tuple**: i pandryshueshëm, i renditur (SB1), mund të futet në set |
| Java aktuale | `current_week = [(0,4,8,12), …]` | **listë**: grupet shtohen dhe hiqen nga fundi (`append` / `pop`) gjatë Backtracking |
| Javët e plota | `weeks = [java1, java2, …]` | **listë javësh**: ruan renditjen për shtypje |
| Çiftet e takuara | `used_pairs = {(0,1), (0,2), …}` | **set tuples (a, b), a < b**: kontrolli "a është takuar ky çift?" në O(1) |
| Lojtarët e vendosur këtë javë | `placed = {0, 4, 8, …}` | **set**: kontroll i shpejtë nëse lojtari është i lirë |
| Numri i takimeve m(a, b) | `{(0,1): 1, …}` | **dictionary**: përdoret në `calculate_objective()` dhe `validate_schedule()` |

Shembull i një orari të pjesshëm (java 1 e plotë, java 2 me 2 nga 8 grupe):

```python
weeks = [
    [(0,1,2,3), (4,5,6,7), (8,9,10,11), (12,13,14,15),
     (16,17,18,19), (20,21,22,23), (24,25,26,27), (28,29,30,31)]
]
current_week = [(0,4,8,12), (1,5,9,13)]
```

---

## 5. Funksioni objektiv (Objective Function)

### 5.1 Përkufizimi

Funksioni objektiv mat **numrin e javëve të plota dhe të vlefshme**:

```
f(S) = |S|        (maksimizohet)
```

me kusht që S të plotësojë C1–C5.

### 5.2 Masa e shkeljes së kufizimit C4

```
V(S) = Σ_{a<b} max(0, m(a, b) − 1)
```

V(S) është numri i takimeve të përsëritura. Orari është i vlefshëm vetëm nëse **V(S) = 0**. Në kod të dyja vlerat kthehen nga `calculate_objective(schedule)`, si `(f, V)`.

### 5.3 Lidhja me numrin maksimal të javëve

```
w* = max f(S),   me kusht V(S) = 0 dhe C1, C2, C3, C5
f(S) ≤ W_max = ⌊(n − 1)/(p − 1)⌋ = 10
```

**W_max = 10 është vetëm kufi i sipërm teorik** (seksioni 6.6). Ai tregon se 11 javë janë të pamundura, por vetë ky argument nuk dëshmon se ekziston orar me 10 javë.

### 5.4 Funksioni objektiv kundrejt kufizimeve të detyrueshme

| | Kufizimet e detyrueshme | Funksioni objektiv |
|---|---|---|
| Roli | përcaktojnë **cili orar lejohet** | përcakton **cili orar i lejuar është më i mirë** |
| Natyra | po / jo | vlerë numerike |
| Në DFS | çdo shkelje → refuzim i menjëhershëm, Backtracking | krahasohen vetëm oraret e vlefshme |
| Shembull | V(S) = 0 | f(S) = 5 javë |

DFS nuk krijon kurrë gjendje me V(S) > 0, sepse grupi që do ta shkaktonte refuzohet para se të shtohet. Prandaj V(S) përdoret kryesisht në validimin përfundimtar.

Algoritmet që lejojnë gjendje të pavlefshme (p.sh. Simulated Annealing) përdorin një funksion të penalizuar, si F(S) = f(S) − λ · V(S). **Ky projekt nuk e përdor**, sepse DFS punon vetëm me gjendje të vlefshme.

### 5.5 Shembull konkret

Java 1 është e fiksuar.

- Grupi i propozuar `(0, 1, 4, 5)` për javën 2: çiftet (0,1) dhe (4,5) janë takuar në javën 1, kështu V do të bëhej ≥ 2. Grupi **refuzohet**.
- Grupi i propozuar `(0, 4, 8, 12)`: asnjë nga 6 çiftet nuk është takuar, V mbetet 0. Grupi **pranohet**.

---

## 6. Hapësira e kërkimit dhe peizazhi (Search Space & Landscape)

### 6.1 Numri i grupeve të mundshme

```
C(32, 4) = 32! / (4! · 28!) = 35 960
```

Ky është domeni fillestar i çdo variable Bₜ,ⱼ.

### 6.2 Numri i ndarjeve të mundshme për një javë

Me grupe të emërtuara (grupi 1, grupi 2, …):

```
32! / (4!)⁸ = 2 390 461 829 733 887 910 000 000 ≈ 2.39 × 10²⁴
```

Meqë grupet janë të paemërtuara (supozimi 1), pjesëtohet edhe me 8! renditjet e grupeve:

```
32! / ((4!)⁸ · 8!) = 59 287 247 761 257 140 625 ≈ 5.93 × 10¹⁹
```

Shpjegimi: 32! janë të gjitha renditjet e lojtarëve. Pjesëtohet me (4!)⁸, sepse renditja brenda secilit nga 8 grupet nuk ka rëndësi, dhe me 8!, sepse renditja e grupeve nuk ka rëndësi.

Të dyja vlerat llogariten nga `search_space()` dhe verifikohen me teste.

### 6.3 Hapësira e kërkimit për disa javë

Shënojmë me 𝒫 = 5.93 × 10¹⁹ numrin e ndarjeve për një javë. Pa marrë parasysh kushtin C4, çdo javë zgjidhet në mënyrë të pavarur:

| Javë w | 𝒫^w (pa simetri) | 𝒫^(w−1) (java 1 e fiksuar) |
|---|---|---|
| 5 | ≈ 7.33 × 10⁹⁸ | ≈ 1.24 × 10⁷⁹ |
| 10 | ≈ 5.37 × 10¹⁹⁷ | ≈ 9.05 × 10¹⁷⁷ |

Hapësira rritet në mënyrë **eksponenciale** me numrin e javëve. Kushti C4 e zvogëlon shumë numrin e orareve të vlefshme, por kërkimi duhet ta zbulojë këtë duke provuar.

### 6.4 Hapësira e kërkimit, pema e kërkimit dhe peizazhi

| Koncepti | Çfarë është | Në këtë problem |
|---|---|---|
| **Hapësira e kërkimit (*Search Space*)** | bashkësia e të gjitha zgjidhjeve kandidate të plota | të gjitha oraret me w javë, ku çdo javë është ndarje e 32 lojtarëve |
| **Pema e kërkimit (*Search Tree*)** | struktura që ndërton algoritmi; çdo nyje është gjendje e pjesshme | rrënja = java 1; çdo nivel = një grup i vendosur; gjethet = orare të plota ose rrugë pa vazhdim |
| **Peizazhi (*Landscape*)** | hapësira e kërkimit + relacioni i fqinjësisë + funksioni që vlerëson cilësinë e çdo zgjidhjeje | oraret me w javë, fqinjësia "ndërro dy lojtarë", dhe vlerësimi V(S) |

**Peizazhi në detaj.** Peizazhi përkufizohet si treshja (X, N, V):

- **X**: oraret e plota me w javë që plotësojnë C1, C2, C3, C5 (por jo domosdoshmërisht C4).
- **N(S)**: fqinjët e një orari. Fqinj i S është çdo orar që merret duke ndërruar dy lojtarë nga grupe të ndryshme të së njëjtës javë. Ky ndërrim i ruan C1, C2, C3, C5. Për një javë ka C(32,2) − 8 · C(4,2) = 496 − 48 = **448** ndërrime të tilla, pra çdo orar ka 448 · (w − 1) fqinjë kur java 1 është e fiksuar.
- **V(S)**: "lartësia" e çdo pike në peizazh, pra numri i çifteve të përsëritura.

Zgjidhjet e vlefshme janë pikat me V(S) = 0, minimumet globale të peizazhit. Peizazhi ka edhe **minimume lokale**: orare me V(S) > 0 ku asnjë ndërrim i vetëm nuk e ul V. Kjo është arsyeja pse metodat e kërkimit lokal (*local search*) mund të ngecin.

**Rëndësi:** DFS **nuk lëviz nëpër peizazh** përmes fqinjëve. Ai ndërton zgjidhjen grup pas grupi në pemën e kërkimit dhe nuk krijon kurrë orare me V > 0. Peizazhi përshkruan strukturën e problemit, dhe dallimi tregon pse problemi është i vështirë për çdo metodë: hapësira është e madhe, dhe zgjidhjet e vlefshme janë shumë të rralla në të.

### 6.5 Faktori i degëzimit dhe thellësia e kërkimit

**Thellësia (*Search Depth*):** çdo nivel vendos një grup. Me javën 1 të fiksuar, një orar me w javë kërkon

```
d = (w − 1) · g   nivele;   për w = 10: d = 9 · 8 = 72
```

**Faktori i degëzimit (*Branching Factor*):** për grupin e j-të të një jave, lojtari i parë është i detyruar (SB2) dhe zgjidhen 3 lojtarë nga ata të mbetur. Pa kushtin C4, numri i kandidatëve është:

| Grupi j | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| C(31 − 4(j−1), 3) | 4 495 | 2 925 | 1 771 | 969 | 455 | 165 | 35 | 1 |

Prodhimi i këtyre numrave është saktësisht 59 287 247 761 257 140 625 = 𝒫. Kjo tregon që pema e kërkimit e një jave, pa kushtin C4, ka aq gjethe sa ndarje ka hapësira e kërkimit. Me kushtin C4, faktori i degëzimit bie shumë: p.sh. grupi i parë i javës 2 ka vetëm **2 240** kandidatë në vend të 4 495.

Faktori maksimal i degëzimit është b ≤ C(n − 1, p − 1) = C(31, 3) = 4 495.

### 6.6 Kufiri teorik i sipërm për numrin e javëve

**Argumenti sipas lojtarit:** Çdo lojtar ka 31 partnerë të mundshëm. Çdo javë luan me 3 partnerë, dhe sipas kushtit C4 ata duhet të jenë të rinj. Pra pas w javësh ka takuar 3w partnerë të ndryshëm:

```
3w ≤ 31   ⇒   w ≤ 31/3 ≈ 10.33   ⇒   w ≤ 10
```

**Argumenti sipas numrit total të çifteve:** Gjithsej ka C(32,2) = 496 çifte, dhe çdo javë përdor 8 · C(4,2) = 48 çifte të reja:

```
48w ≤ 496   ⇒   w ≤ 10.33   ⇒   w ≤ 10
```

**Në përgjithësi:**

```
w ≤ ⌊ (n − 1) / (p − 1) ⌋
```

Të dy argumentet japin të njëjtën formulë, sepse C(n,2) / (g · C(p,2)) = (n−1)/(p−1).

**Kujdes:** ky është **kufi i sipërm teorik**. Ai dëshmon që 11 javë janë të pamundura, por nuk dëshmon që ekzistojnë 10. Për shembull, për SGP(2, 3) kufiri është 2 javë, por programi dëshmon me kërkim shterues që maksimumi është vetëm **1** (seksioni 10). Për rastin 8-4, literatura raporton ekzistencën e një orari me 10 javë (shih [6]), por **programi ynë nuk e gjen atë** brenda kohës së testuar.

---

## 7. DFS me Backtracking

### 7.1 Nyja e kërkimit (Search Node)

Një nyje është një **orar i pjesshëm**: javët e plota (`weeks`), grupet e vendosura në javën aktuale (`current_week`), lojtarët e vendosur këtë javë (`placed`) dhe çiftet e takuara (`used_pairs`). Fëmijët e një nyjeje janë gjendjet që merren duke shtuar një grup të vlefshëm.

### 7.2 Si funksionon

1. Fillon me javën 1 të fiksuar.
2. Për grupin e ardhshëm gjeneron kandidatët: lojtari më i vogël i lirë dhe 3 lojtarë të tjerë të lirë.
3. Për çdo kandidat kontrollon nëse ndonjë nga 6 çiftet e tij është takuar më parë.
4. Kandidatët që shkelin kushtin refuzohen.
5. Kandidati i vlefshëm shtohet, dhe kërkimi vazhdon rekursivisht me grupin e ardhshëm. Pas grupit të 8-të fillon java e re.
6. Nëse për një gjendje nuk ka asnjë kandidat të vlefshëm, ndodh **Backtracking**: hiqet grupi i fundit dhe provohet kandidati i radhës.
7. Sa herë përfundon një javë, orari ruhet nëse është më i gjati deri atëherë.
8. Kërkimi ndalet kur arrihet kufiri teorik, kur kontrollohet e gjithë pema, ose kur mbaron koha.

DFS e eksploron pemën në thellësi: zbret gjithmonë te fëmija i parë i vlefshëm dhe kthehet prapa vetëm kur një degë nuk ka vazhdim.

### 7.3 Pseudokodi (pjesë ndihmëse)

```text
funksioni SOLVE(g, p, kufiri_kohës):
    fikso javën 1: (0..p-1), (p..2p-1), ...
    shëno çiftet e javës 1 në used_pairs
    best ← [java 1]
    nëse DFS() == false:
        arsyeja ← "exhausted"           // e gjithë pema u kontrollua
    kthe best

funksioni DFS():
    nodes ← nodes + 1
    nëse koha > kufiri_kohës:
        arsyeja ← "time_limit";  kthe true

    nëse current_week ka g grupe:                       // java u plotësua
        shto current_week në weeks
        nëse |weeks| > |best|:  best ← kopje e weeks
        nëse |weeks| == W_max:
            arsyeja ← "upper_bound";  kthe true
        fillo javë të re (current_week ← [], placed ← ∅)
        nëse DFS() == true:  kthe true
        rikthe javën e mëparshme
        kthe false

    available ← lojtarët që nuk janë në placed (të renditur)
    për çdo grup në GENERATE_GROUPS(available, used_pairs, p):
        ADD_GROUP(grup)                                 // zgjerimi i gjendjes
        nëse DFS() == true:  kthe true
        BACKTRACK()                                     // hiq grupin, liro çiftet
    kthe false                                          // asnjë kandidat nuk funksionoi

funksioni GENERATE_GROUPS(available, used_pairs, p):
    first ← available[0]                                // SB2
    për çdo kombinim rest me p-1 lojtarë nga available[1:]:
        grup ← (first) + rest                           // SB1: i renditur
        nëse asnjë çift i grupit nuk është në used_pairs:   // C4
            jep grup
```

---

## 8. Implementimi në Python

I gjithë kodi është në `social_golfers.py`. Përdoren vetëm biblioteka standarde të Python-it (`itertools`, `math`, `time`, `sys`).

| Funksioni / Metoda | Roli | Lidhja me modelin |
|---|---|---|
| `pair_key(a, b)` | kthen çiftin si `(min, max)` | çifti {a, b} |
| `group_pairs(group)` | 6 çiftet e një grupi | çiftet e Bₜ,ⱼ |
| `is_valid_group(group, used_pairs)` | kontrollon kufizimin C4 | m(a, b) ≤ 1 |
| `generate_groups(available, used_pairs, p)` | gjeneron domenin aktual | C1, C2, C4, SB1, SB2 |
| `upper_bound(n, p)` | kufiri teorik i sipërm | ⌊(n−1)/(p−1)⌋ |
| `count_meetings(schedule)` | numëron m(a, b) me dictionary | m(a, b) |
| `calculate_objective(schedule)` | kthen (f, V) | f(S), V(S) |
| `validate_schedule(schedule, g, p)` | validim i pavarur i C1–C5 | të gjitha kufizimet |
| `SocialGolfersDFS.add_group()` | zgjerimi i gjendjes | vendosja e Bₜ,ⱼ |
| `SocialGolfersDFS.backtrack()` | heq grupin e fundit | Backtracking |
| `SocialGolfersDFS.dfs()` | kërkimi rekursiv | DFS |
| `SocialGolfersDFS.solve()` | fikson javën 1 dhe nis DFS | SB3, gjendja fillestare |
| `search_space(g, p)` | C(n,p), 𝒫, numri i çifteve | seksioni 6 |
| `print_schedule()`, `main()` | shfaqja e rezultateve | |

Kandidatët gjenerohen me një **generator** (`yield`). Kështu në çdo nivel të rekursionit nuk ruhet lista e të gjithë kandidatëve, por vetëm pozita aktuale në `combinations`.

---

## 9. Si ekzekutohet programi

Kërkohet Python 3.8 ose më i ri. Nuk ka nevojë për instalim paketash.


```text
AI-Uninformed-Search/
├── 1-Social-Golfers-DFS/
│   ├── README.md
│   ├── social_golfers.py
│   └── tests/
│       └── test_social_golfers.py
├── 2-Sudoku-BFS/
├── 3-Latin-Square-IDDFS/
└── 4-Search-Trees/
```

Hapni terminalin (**Terminal → New Terminal**) dhe hyni në folderin e kësaj detyre:

```bash
cd 1-Social-Golfers-DFS
```

Pastaj ekzekutoni:

```bash
# Konfigurimi kryesor: g = 8, p = 4, kufiri i kohës 60 sekonda
python social_golfers.py

# Parametra të tjerë: g, p, kufiri i kohës në sekonda
python social_golfers.py 8 4 300
python social_golfers.py 3 3 10

# Testet
python -m unittest discover tests -v
```

Në disa sisteme komanda është `python3` në vend të `python`.

---

## 10. Rezultatet, testimi dhe validimi

### 10.1 Konfigurimi kryesor: n = 32, g = 8, p = 4

Ekzekutimi `python social_golfers.py 8 4 60`:

```text
Numri i lojtarëve (n):           32
Numri i grupeve (g):             8
Madhësia e grupit (p):           4
Kufiri teorik i sipërm:          10 javë (nuk garantohet)
Grupe të mundshme C(32,4):      35,960
Ndarje të mundshme për javë:     59,287,247,761,257,140,625
Kufiri i kohës:                  60 s
----------------------------------------------------------------------
Numri i javëve të gjetura:       5
Java  1: (0,1,2,3)  (4,5,6,7)  (8,9,10,11)  (12,13,14,15)  (16,17,18,19)  (20,21,22,23)  (24,25,26,27)  (28,29,30,31)
Java  2: (0,4,8,12)  (1,5,9,13)  (2,6,10,14)  (3,7,11,15)  (16,20,24,28)  (17,21,25,29)  (18,22,26,30)  (19,23,27,31)
Java  3: (0,5,10,15)  (1,4,11,14)  (2,7,8,13)  (3,6,9,12)  (16,21,26,31)  (17,20,27,30)  (18,23,24,29)  (19,22,25,28)
Java  4: (0,6,11,13)  (1,7,10,12)  (2,4,9,15)  (3,5,8,14)  (16,22,27,29)  (17,23,26,28)  (18,20,25,31)  (19,21,24,30)
Java  5: (0,7,9,14)  (1,6,8,15)  (2,5,11,12)  (3,4,10,13)  (16,23,25,30)  (17,22,24,31)  (18,21,27,28)  (19,20,26,29)
----------------------------------------------------------------------
Çifte të përsëritura V(S):       0
Nyje të vizituara:               896,503
Operacione Backtracking:         893,354
Koha e ekzekutimit:              60.00 s
Orari është i vlefshëm:          PO
Arsyeja e ndalimit:              Mbaroi koha -> rezultati është më i miri i gjetur, por NUK është dëshmuar optimal.
```

Me kufi kohe 5 minuta (`python social_golfers.py 8 4 300`), rezultati mbetet i njëjtë:

| Kufiri i kohës | Javë të gjetura | Nyje të vizituara | Backtracking | V(S) | I vlefshëm |
|---|---|---|---|---|---|
| 60 s | 5 | 896 503 | 893 354 | 0 | PO |
| 300 s | 5 | 4 587 519 | 4 571 928 | 0 | PO |

Numri i nyjeve dhe i operacioneve Backtracking varet nga shpejtësia e kompjuterit, sepse kërkimi ndalet pas një kohe të caktuar, jo pas një numri të caktuar nyjesh. Në një kompjuter më të shpejtë vizitohen më shumë nyje brenda së njëjtës kohë. Numri i javëve dhe orari janë të njëjtë në çdo ekzekutim, sepse kandidatët provohen gjithmonë në të njëjtën renditje.

**Interpretimi:**

- DFS gjen një orar të vlefshëm me **5 javë**, me V(S) = 0, dhe validimi i pavarur e konfirmon.
- Pesë javët gjenden shumë shpejt, pothuajse pa Backtracking. Më pas kërkimi kalon të gjithë kohën duke u kthyer prapa: degët e para që zgjodhi për javët 2–5 nuk lejojnë javën e 6-të, dhe pema nën to është shumë e madhe për t'u kontrolluar e tëra.
- Rezultati tregon që **w* ≥ 5**. Nuk dëshmon që 5 është maksimumi: kufiri teorik është 10, dhe literatura raporton orar me 10 javë [6]. Ky dallim është kufizim i pritur i kërkimit të painformuar në një hapësirë kaq të madhe.

### 10.2 Instanca të vogla (verifikimi i saktësisë)

Rezultatet nga ekzekutimi i programit:

| Instanca | n | Kufiri teorik | Javë të gjetura | Nyje | Backtracking | Arsyeja e ndalimit |
|---|---|---|---|---|---|---|
| SGP(2, 2) | 4 | 3 | 3 | 7 | 0 | arrihet kufiri → optimal |
| SGP(2, 3) | 6 | 2 | 1 | 2 | 0 | pema e plotë → **dëshmuar** optimal |
| SGP(3, 2) | 6 | 5 | 5 | 20 | 3 | arrihet kufiri → optimal |
| SGP(3, 3) | 9 | 4 | 4 | 13 | 0 | arrihet kufiri → optimal |
| SGP(4, 4) | 16 | 5 | 5 | 21 | 0 | arrihet kufiri → optimal |
| SGP(4, 3) | 12 | 5 | 4 | 1 439 948 | 1 355 976 | koha (20 s) → jo i dëshmuar |
| SGP(5, 3) | 15 | 7 | 6 | 1 575 452 | 1 527 859 | koha (30 s) → jo i dëshmuar |

SGP(2, 3) është shembull i rëndësishëm: kufiri teorik është 2 javë, por me javën 1 = {0,1,2}, {3,4,5}, grupi i lojtarit 0 në javën 2 duhet të përmbajë dy lojtarë nga {3,4,5}. Atëherë lojtarët 1 dhe 2 mbeten bashkë me lojtarin e tretë, dhe çifti (1,2) përsëritet. Programi e dëshmon këtë me kërkim shterues. Pra **kufiri teorik nuk arrihet gjithmonë**.

### 10.3 Testet automatike

Skedari `tests/test_social_golfers.py` përmban 24 teste (`unittest`, pa paketa shtesë):

| Grupi i testeve | Çka verifikon |
|---|---|
| `TestHelpers` | çiftet (6 për grup, 48 për javë), refuzimi i `(0,1,4,5)` dhe pranimi i `(0,4,8,12)` |
| `TestGenerateGroups` | kandidatët përmbajnë lojtarin më të vogël, kanë 4 lojtarë të renditur, nuk përsërisin çifte; numri i tyre është 2 240 |
| `TestSearchSpaceAndBound` | C(32,4) = 35 960, 𝒫 = 59 287 247 761 257 140 625, kufiri i sipërm |
| `TestObjectiveAndValidation` | f dhe V; validimi zbulon numër të gabuar grupesh, madhësi të gabuar, lojtar dy herë në javë, çift të përsëritur |
| `TestDFS` | rezultatet e njohura për SGP(2,2), SGP(2,3), SGP(3,3); orar i vlefshëm për 8-4; Backtracking e rikthen gjendjen saktë |

Rezultati i ekzekutimit `python -m unittest discover tests -v`:

```text
Ran 24 tests in 3.042s

OK
```

---

## 11. Analiza e kompleksitetit

### 11.1 Parametrat

- **b (faktori i degëzimit):** b ≤ C(n − 1, p − 1) = 4 495. Faktori real është shumë më i vogël për shkak të C4, dhe zvogëlohet me çdo grup të vendosur (seksioni 6.5).
- **d (thellësia):** d = (w − 1) · g. Për w = 10, d = 72.

### 11.2 Kompleksiteti kohor (Time Complexity)

Në rastin më të keq, DFS viziton të gjitha nyjet e pemës. Kufiri i përgjithshëm është **O(b^d)**. Për këtë problem mund të jepet kufi më i saktë: pa kushtin C4, pema e çdo jave ka saktësisht 𝒫 gjethe, kështu numri i gjetheve për w javë është më së shumti

```
𝒫^(w−1) ≈ 9.05 × 10¹⁷⁷   për w = 10
```

Çdo nyje kërkon gjenerimin e kandidatëve: provohen më së shumti C(31, 3) = 4 495 kombinime, secila me 6 kontrolle në set në O(1). Pra puna për nyje është O(C(n−1, p−1) · p²).

**Supozimet:** këto janë kufij të sipërm. Ata supozojnë që C4 nuk pret asnjë degë, gjë që në praktikë nuk ndodh.

### 11.3 Kompleksiteti hapësinor (Space Complexity)

- Thellësia e rekursionit: d = 72 thirrje.
- Në çdo nivel ruhet vetëm generator-i i kandidatëve, jo lista e tyre: O(p) për nivel.
- `used_pairs`: më së shumti C(n, 2) = 496 çifte, pra O(n²).
- `best_schedule`: O(w · n).

Gjithsej: **O(d · p + n² + w · n)**, pra hapësira rritet linearisht me thellësinë. Kjo është përparësia kryesore e DFS ndaj BFS, i cili do të duhej të ruante një nivel të tërë të pemës.

### 11.4 Ndikimi i kontrollit të kufizimeve dhe i Backtracking

- **Kontrolli i C4** ndodh menjëherë kur propozohet grupi, jo pasi të plotësohet orari. Kështu një degë e pavlefshme pritet sapo shfaqet, dhe e gjithë nënpema e saj nuk vizitohet kurrë. Shembull: për grupin e parë të javës 2 mbeten 2 240 nga 4 495 kandidatë.
- **Backtracking** e bën kërkimin të plotë (*complete*): nëse ekziston zgjidhje, ajo gjendet herët a vonë, sepse çdo alternativë provohet. Por kur zgjedhjet e hershme janë të gabuara, algoritmi duhet të kontrollojë të gjithë nënpemën nën to para se t'i ndryshojë. Kjo është arsyeja e numrit të madh të operacioneve Backtracking në rastin 8-4.
- **Thyerja e simetrisë** (SB1–SB3) e zvogëlon pemën: SB1 dhe SB2 me faktorët (4!)⁸ · 8! për javë, SB3 me një javë të tërë.

### 11.5 Kompleksiteti teorik kundrejt statistikave reale

Formulat teorike japin rastin më të keq (≈ 10¹⁷⁷ gjethe), ndërsa programi viziton rreth 9 × 10⁵ nyje në 60 sekonda. Dallimi vjen nga dy arsye:

1. Kushti C4 dhe thyerja e simetrisë presin pjesën më të madhe të pemës.
2. Kërkimi ndalet nga kufiri i kohës, kështu viziton vetëm një pjesë të vogël të pemës së mbetur.

Statistikat reale (nyjet, Backtracking, koha) varen nga instanca, renditja e kandidatëve dhe shpejtësia e kompjuterit. Kompleksiteti teorik varet vetëm nga madhësia e problemit.

---

## 12. Përfundimi

- Problemi u modelua matematikisht si varg ndarjesh javore me kushtin m(a, b) ≤ 1.
- U zgjodhën variablat Bₜ,ⱼ (grupi si variabël), me domen fillestar C(32,4) = 35 960 dhe domen dinamik që e ngushton kërkimi.
- Funksioni objektiv f(S) = numri i javëve u maksimizua me kushtin V(S) = 0.
- Hapësira e kërkimit është ≈ 5.93 × 10¹⁹ ndarje për javë, dhe rritet eksponencialisht me numrin e javëve.
- Kufiri teorik i sipërm është **10 javë**. Ai është kufi, jo zgjidhje e garantuar.
- DFS me Backtracking gjeti një orar të vlefshëm me **5 javë** për 32 lojtarë, të verifikuar me validim të pavarur. Ky rezultat nuk është dëshmuar optimal.
- Në instancat e vogla, programi arrin kufirin teorik ose e dëshmon optimumin me kërkim shterues.

Kërkimi i painformuar është i plotë dhe ka nevojë për pak memorie, por në një hapësirë kaq të madhe nuk mjafton për të gjetur orarin me 10 javë. Për këtë nevojiten teknika të tjera të kursit, si *forward checking*, heuristikat e renditjes ose kërkimi lokal.

---

## 13. Referencat

1. S. Russell, P. Norvig, *Artificial Intelligence: A Modern Approach*, 3rd ed., Kapitulli 3 (Solving Problems by Searching).
2. Z. Michalewicz, D. B. Fogel, *How to Solve It: Modern Heuristics*, 2nd ed., Springer, 2004, Kapitujt 1–3.
3. N. Musliu, *Uninformed Search*, TU Wien: http://www.dbai.tuwien.ac.at/staff/musliu/ProblemSolvingAI/Class2UninformedSearch.pdf
4. N. Musliu, *Basic Concepts of Problem Solving*, TU Wien: http://www.dbai.tuwien.ac.at/staff/musliu/ProblemSolvingAI/class1BasicConcepts.pdf
5. W. Harvey, *CSPLib Problem 010: Social Golfers Problem*, https://www.csplib.org
6. *Social golfer problem*, Wikipedia: https://en.wikipedia.org/wiki/Social_golfer_problem (ekzistenca e orarit 8-4-10, i ndërtuar në mënyrë eksplicite nga A. Aguado në vitin 2004).