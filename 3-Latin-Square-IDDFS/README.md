# Latin Square – IDDFS me Backtracking

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
7. [IDDFS me Backtracking](#7-iddfs-me-backtracking)
8. [Implementimi në Python](#8-implementimi-në-python)
9. [Si ekzekutohet programi](#9-si-ekzekutohet-programi)
10. [Rezultatet, testimi dhe validimi](#10-rezultatet-testimi-dhe-validimi)
11. [Analiza e kompleksitetit](#11-analiza-e-kompleksitetit)
12. [Përfundimi](#12-përfundimi)
13. [Referencat](#13-referencat)

---

## 1. Hyrje

Ky projekt ndërton një katror latin n × n me algoritmin e kërkimit me thellim iterativ (*Iterative Deepening Depth-First Search*, IDDFS) dhe kthim prapa (*Backtracking*). Projekti përmban:

- modelimin matematikor të problemit;
- variablat, domenet, kufizimet dhe paraqitjen e gjendjes;
- funksionin objektiv;
- llogaritjen e hapësirës së kërkimit dhe shpjegimin e peizazhit;
- implementimin në Python (`latin_square_iddfs.py`);
- testet automatike (`tests/test_latin_square_iddfs.py`).

Të gjitha rezultatet numerike në këtë dokument vijnë ose nga ekzekutimi real i programit, ose nga një llogaritje matematikore e shpjeguar.

---

## 2. Përshkrimi i problemit

Një **katror latin** i rendit n është një grid n × n, i mbushur me numrat 1, …, n, ku secili numër shfaqet **saktësisht një herë në çdo rresht** dhe **saktësisht një herë në çdo kolonë**.

Për një hyrje n, programi duhet të printojë një matricë të tillë.

**Shembulli nga detyra (n = 5):**

```text
1 2 3 4 5
5 1 2 3 4
4 5 1 2 3
3 4 5 1 2
2 3 4 5 1
```

Për çdo n ≥ 1 ka shumë katrorë latinë, p.sh. 161 280 për n = 5. Detyra kërkon një prej tyre, jo një të caktuar. Prandaj çdo katror latin i vlefshëm është përgjigje e saktë. Programi e verifikon edhe shembullin e detyrës si të vlefshëm (test `test_example_from_task_is_valid`).

Ashtu si Sudoku, ky është **problem i plotësimit të kufizimeve** (CSP), por pa numra të dhënë: grid-i fillon bosh.

---

## 3. Modelimi matematikor (Problem Modeling)

### 3.1 Parametrat

| Simboli | Kuptimi |
|---|---|
| n | rendi i katrorit (hyrja) |
| R = C = {0, …, n−1} | rreshtat dhe kolonat |
| D = {1, …, n} | vlerat e mundshme |
| x(r, c) ∈ D | vlera në qelizën (r, c) |

### 3.2 Formulimi

Kërkohet një funksion x : R × C → D që plotëson:

```
x(r, c) ≠ x(r, c')    për çdo r dhe çdo c ≠ c'     (rreshti)
x(r, c) ≠ x(r', c)    për çdo c dhe çdo r ≠ r'     (kolona)
```

Meqë çdo rresht dhe çdo kolonë ka n qeliza dhe ka n vlera, kushti "vlera të ndryshme" është ekuivalent me "çdo vlerë 1..n shfaqet saktësisht një herë".

### 3.3 Ekzistenca e zgjidhjes

Për çdo n ≥ 1 ekziston të paktën një katror latin. Një ndërtim i drejtpërdrejtë është katrori ciklik x(r, c) = ((c − r) mod n) + 1, i cili jep pikërisht shembullin e detyrës. Pra këtu pyetja nuk është **nëse** ekziston zgjidhje, por si e gjen kërkimi i painformuar një të tillë.

### 3.4 Supozimet

1. n ≥ 1 është numër i plotë.
2. Grid-i fillon bosh: nuk ka numra të dhënë.
3. Kërkohet një katror latin, jo të gjithë.

---

## 4. Paraqitja e problemit (Problem Representation)

### 4.1 Variablat

```
X(r,c)   për r, c = 0, …, n−1
```

Ka **n²** variabla, p.sh. 25 për n = 5.

### 4.2 Domenet

**Domeni fillestar:** D(X(r,c)) = {1, …, n}.

**Domeni aktual:** vlerat që nuk janë përdorur ende në rreshtin r dhe në kolonën c:

```
D_aktual(X(r,c)) = {1..n} \ ( vlerat në rreshtin r  ∪  vlerat në kolonën c )
```

### 4.3 Kufizimet (Hard Constraints)

| Nr. | Kufizimi | Si plotësohet në kod |
|---|---|---|
| C1 | çdo rresht ka vlera të ndryshme | `is_consistent()` kontrollon `row_used[r][v]` |
| C2 | çdo kolonë ka vlera të ndryshme | `is_consistent()` kontrollon `col_used[c][v]` |

Kufizimet kontrollohen **sapo vendoset një vlerë**: një vlerë që shkel C1 ose C2 nuk provohet fare. Funksioni `validate_latin_square()` megjithatë i kontrollon të dy kufizimet nga fillimi, pa u mbështetur në kërkimin.

### 4.4 Renditja e variablave

Qelizat plotësohen **rresht pas rreshti**: (0,0), (0,1), …, (0,n−1), (1,0), … Qeliza në thellësinë `depth` është:

```
r, c = divmod(depth, n)
```

Kjo është renditje fikse, pa heuristikë, siç i përshtatet kërkimit të painformuar.

### 4.5 Gjendja fillestare, gjendja përfundimtare dhe testi i qëllimit

- **Gjendja fillestare:** grid-i bosh, në thellësinë 0.
- **Testi i qëllimit:**
  ```
  Goal(S)  ⇔  depth = n²  (të gjitha qelizat plot)
  ```
  Meqë asnjë vlerë që shkel kufizimet nuk vendoset, çdo grid i plotë i arritur është katror latin. Vlefshmëria verifikohet më pas në mënyrë të pavarur.

### 4.6 Paraqitja e gjendjes në Python (State Representation)

| Elementi | Në Python | Arsyeja |
|---|---|---|
| Grid-i | `grid`, listë listash n × n, 0 = bosh | vlerat ndryshohen dhe rikthehen gjatë backtracking |
| Vlerat e përdorura në rresht | `row_used[r][v]`, listë boolean | kontroll i C1 në O(1) |
| Vlerat e përdorura në kolonë | `col_used[c][v]`, listë boolean | kontroll i C2 në O(1) |
| Thellësia e nyjes | `depth`, numër i plotë 0..n² | përcakton qelizën dhe krahasohet me limitin |
| Iteracionet | `iterations`, listë tuples `(limiti, nyjet, rezultati)` | shfaqja dhe analiza e çdo iteracioni |

IDDFS, ashtu si DFS, mban vetëm **një grid** në memorie dhe e ndryshon atë në vend. Ky është dallimi kryesor nga BFS te Sudoku-ja, ku çdo nyje ishte kopje e veçantë.

---

## 5. Funksioni objektiv (Objective Function)

### 5.1 Përkufizimi

Për një grid të plotë S, funksioni objektiv numëron përsëritjet:

```
f(S) = Σ_r ( n − |vlera të ndryshme në rreshtin r| )
     + Σ_c ( n − |vlera të ndryshme në kolonën c| )        (minimizohet)
```

Nëse një rresht ka të gjitha vlerat të ndryshme, kontributi i tij është 0. Çdo vlerë që mungon, sepse në vend të saj është një përsëritje, shton 1.

**Zgjidhje** është çdo grid i plotë me **f(S) = 0**. Minimumi i f është 0, dhe arrihet saktësisht te katrorët latinë. Në kod: `calculate_objective(grid)`.

### 5.2 Funksioni objektiv kundrejt kufizimeve

| | Kufizimet C1, C2 | Funksioni objektiv f(S) |
|---|---|---|
| Roli | përcaktojnë **cili grid është katror latin** | mat **sa larg** është grid-i nga katrori latin |
| Natyra | po / jo | vlerë numerike ≥ 0 |
| Në IDDFS | vlerat që i shkelin nuk provohen | mbetet 0 gjatë kërkimit |
| Përdorimi kryesor | gjenerimi i fëmijëve | validimi dhe peizazhi (seksioni 6.4) |

### 5.3 Shembull konkret

```text
1 2        rreshtat: 0 + 0          1 2        rreshtat: 0 + 0
2 1        kolonat:  0 + 0          1 2        kolonat:  1 + 1
           f = 0 → katror latin                f = 2 → jo katror latin
```

Grid-i i djathtë ka rreshta në rregull, por në secilën kolonë një vlerë përsëritet. Ky rast verifikohet me test (`test_repeated_value_in_column`).

---

## 6. Hapësira e kërkimit dhe peizazhi (Search Space & Landscape)

### 6.1 Hapësira naive

Çdo qelizë merr një nga n vlera:

```
|S_naive| = n^(n²)
```

### 6.2 Paraqitje me permutacione për rresht

Nëse çdo rresht është permutacion i 1..n, kushti C1 plotësohet automatikisht:

```
|S_rresht| = (n!)^n
```

### 6.3 Numri i zgjidhjeve

Numri i katrorëve latinë L(n) është i njohur për n të vogla [5]:

| n | n^(n²) | (n!)^n | L(n) (zgjidhje) |
|---|---|---|---|
| 3 | 19 683 | 216 | 12 |
| 4 | 4.29 × 10⁹ | 331 776 | 576 |
| 5 | 2.98 × 10¹⁷ | 2.48 × 10¹⁰ | 161 280 |
| 6 | 1.03 × 10²⁸ | 1.39 × 10¹⁷ | 812 851 200 |

Zgjidhjet janë shumë më të rralla se kandidatët, por nuk mungojnë: për n = 5, rreth një nga 154 000 grid-a me rreshta permutacionesh është katror latin.

### 6.4 Hapësira e kërkimit, pema e kërkimit dhe peizazhi

| Koncepti | Çfarë është | Në këtë problem |
|---|---|---|
| **Hapësira e kërkimit (*Search Space*)** | bashkësia e zgjidhjeve kandidate të plota | n^(n²) grid-a, ose (n!)^n me rreshta permutacionesh |
| **Pema e kërkimit (*Search Tree*)** | struktura që ndërton algoritmi; çdo nyje është gjendje e pjesshme | rrënja = grid bosh; niveli i = i qeliza të plotësuara; thellësia n² |
| **Peizazhi (*Landscape*)** | hapësira + fqinjësia + funksioni që vlerëson cilësinë | grid-at me rreshta permutacionesh, "ndërro dy qeliza në rresht", f(S) |

**Peizazhi në detaj**, treshja (X, N, f):

- **X**: grid-at e plotë ku çdo rresht është permutacion i 1..n. Kështu C1 plotësohet gjithmonë, dhe f mat vetëm përsëritjet në kolona.
- **N(S)**: fqinj i S është çdo grid që merret duke ndërruar dy qeliza në të njëjtin rresht. Çdo grid ka n · C(n, 2) fqinjë, p.sh. **50** për n = 5.
- **f(S)**: lartësia e çdo pike në peizazh.

Katrorët latinë janë **minimumet globale**, me f = 0. Për n = 5 ka 161 280 të tillë, kështu peizazhi ka shumë "lugina" me f = 0, ndryshe nga Sudoku-ja, ku ishte vetëm një.

**Rëndësi:** IDDFS **nuk lëviz nëpër peizazh**. Ai ndërton zgjidhjen qelizë pas qelize në pemën e kërkimit dhe nuk krijon kurrë grid me konflikt.

### 6.5 Faktori i degëzimit dhe thellësia

- **Thellësia (d):** d = n². Çdo zgjidhje është në nivelin e fundit të pemës.
- **Faktori i degëzimit (b):** b ≤ n. Faktori real është |D_aktual| e qelizës, që zvogëlohet përgjatë rreshtit: qeliza e fundit e çdo rreshti ka më së shumti një vlerë të lejuar.

---

## 7. IDDFS me Backtracking

### 7.1 Ideja e IDDFS

IDDFS bashkon dy algoritme:

- nga **DFS** merr memorien e vogël: ruan vetëm rrugën aktuale;
- nga **BFS** merr vetinë që gjen zgjidhjen më të cekët, sepse e rrit thellësinë gradualisht.

Algoritmi ekzekuton **Depth-Limited Search (DLS)**, pra DFS që nuk zbret më thellë se një limit, me limit = 0, 1, 2, … Çdo iteracion e fillon kërkimin nga rrënja.

### 7.2 Rezultati i DLS

| Rezultati | Kuptimi |
|---|---|
| `True` | u gjet zgjidhje |
| `cutoff` | të paktën një degë arriti limitin pa zgjidhje; me limit më të madh mund të ketë zgjidhje |
| `failure` | e gjithë pema deri në limit u kontrollua dhe asnjë degë nuk arriti limitin: nuk ka zgjidhje |

IDDFS vazhdon me limitin e ardhshëm vetëm pas një `cutoff`.

### 7.3 Ku ndodh Backtracking

Brenda DLS, për qelizën (r, c):

1. provohen vlerat 1..n me radhë;
2. vlerat që shkelin C1 ose C2 anashkalohen, pa krijuar nyje;
3. vlera e lejuar vendoset, dhe DLS vazhdon rekursivisht me qelizën e ardhshme;
4. kur rekursioni kthehet pa zgjidhje, vlera **hiqet** (`backtrack()`) dhe provohet vlera e ardhshme.

### 7.4 Nyja e kërkimit (Search Node)

Një nyje është grid-i i pjesshëm në thellësinë `depth`: qelizat 0..depth−1 të plotësuara pa konflikt. Fëmijët e saj janë grid-at me qelizën `depth` të plotësuar me secilën vlerë të lejuar.

### 7.5 Pseudokodi (pjesë ndihmëse)

```text
funksioni IDDFS(n, step):
    limit ← 0
    përsërit:
        limit ← min(limit, n²)
        result ← DLS(0, limit)
        nëse result == true:     kthe zgjidhjen
        nëse result == failure:  kthe "nuk ka zgjidhje"
        limit ← limit + step                        // result == cutoff

funksioni DLS(depth, limit):
    nodes ← nodes + 1
    nëse depth == n²:     kthe true                 // testi i qëllimit
    nëse depth == limit:  kthe cutoff
    (r, c) ← divmod(depth, n)
    cutoff_occurred ← false
    për v = 1 deri n:
        nëse v është në rreshtin r ose në kolonën c:  vazhdo     // C1, C2
        ASSIGN(r, c, v)
        result ← DLS(depth + 1, limit)
        nëse result == true:    kthe true
        nëse result == cutoff:  cutoff_occurred ← true
        BACKTRACK(r, c, v)
    kthe cutoff nëse cutoff_occurred, përndryshe failure
```

### 7.6 Hapi i limitit (`--step`)

Në IDDFS klasik limiti rritet me 1. Programi lejon edhe një hap më të madh, p.sh. `--step=5` për n = 5, ku limiti rritet me një rresht të tërë: 0, 5, 10, 15, 20, 25. Kjo nuk e ndryshon algoritmin, vetëm ul numrin e iteracioneve. Zgjidhja që gjendet është e njëjta, sepse iteracioni i fundit është gjithmonë limiti n². Seksioni 10 i krahason të dy variantet.

---

## 8. Implementimi në Python

I gjithë kodi është në `latin_square_iddfs.py`. Përdoren vetëm biblioteka standarde (`math`, `time`, `sys`).

| Funksioni / Metoda | Roli | Lidhja me modelin |
|---|---|---|
| `LatinSquareIDDFS.is_consistent(r, c, v)` | kontrollon C1 dhe C2 | domeni aktual |
| `LatinSquareIDDFS.assign(r, c, v)` | vendos vlerën | zgjerimi i gjendjes |
| `LatinSquareIDDFS.backtrack(r, c, v)` | heq vlerën | backtracking |
| `LatinSquareIDDFS.dls(depth, limit)` | Depth-Limited Search | seksioni 7.2 |
| `LatinSquareIDDFS.iddfs()` | përsërit DLS me limit në rritje | seksioni 7.1 |
| `calculate_objective(grid)` | numëron përsëritjet | f(S) |
| `validate_latin_square(grid)` | validim i pavarur | C1, C2 |
| `search_space(n)` | n^(n²), (n!)^n, L(n), fqinjët | seksioni 6 |
| `worst_case_nodes(n)` | nyjet e IDDFS në pemën pa kufizime | seksioni 11.2 |
| `print_grid()`, `main()` | shfaqja e rezultateve | |

Programi ka edhe një kufi kohe, 120 sekonda si parazgjedhje (`--time=`). Kur kufiri mbaron, kërkimi ndalet dhe programi e raporton këtë si arsye ndalimi.

---

## 9. Si ekzekutohet programi

Kërkohet Python 3.8 ose më i ri. Nuk ka nevojë për instalim paketash.

```text
AI-Uninformed-Search/
├── 1-Social-Golfers-DFS/
├── 2-Sudoku-BFS/
├── 3-Latin-Square-IDDFS/
│   ├── README.md
│   ├── latin_square_iddfs.py
│   └── tests/
│       └── test_latin_square_iddfs.py
└── 4-Search-Trees/
```

Hapni terminalin (**Terminal → New Terminal**) dhe hyni në folderin e kësaj detyre:

```bash
cd 3-Latin-Square-IDDFS
```

Nëse terminali është në folderin e një detyre tjetër, p.sh. `2-Sudoku-BFS`, përdorni `cd ..\3-Latin-Square-IDDFS`.

Pastaj ekzekutoni:

```bash
# n = 5 (si në shembullin e detyrës), IDDFS klasik
python latin_square_iddfs.py

# n tjetër
python latin_square_iddfs.py 4

# Limiti rritet me një rresht të tërë
python latin_square_iddfs.py 5 --step=5

# Kufi kohe tjetër (në sekonda)
python latin_square_iddfs.py 6 --step=6 --time=60

# Testet
python -m unittest discover tests -v
```

Për n = 5, IDDFS klasik zgjat disa sekonda. Prisni deri në fund.

---

## 10. Rezultatet, testimi dhe validimi

### 10.1 Rezultati për n = 5

Ekzekutimi `python latin_square_iddfs.py`:

```text
Dalja:
  1 2 3 4 5
  2 1 4 5 3
  3 4 5 1 2
  4 5 2 3 1
  5 3 1 2 4
------------------------------------------------------------------
Objective function f(S):          0
Katrori latin është i vlefshëm:   PO
Nyje gjithsej (të gjitha iter.):  13,505,923
Operacione Backtracking:          13,505,872
Koha e ekzekutimit:               16.52 s
Arsyeja e ndalimit:               U gjet zgjidhja.
```

Katrori i gjetur ndryshon nga shembulli i detyrës, por është po aq i vlefshëm: çdo rresht dhe çdo kolonë përmban 1–5 saktësisht një herë. DFS provon vlerat 1..n me radhë, prandaj gjen katrorin latin të parë sipas renditjes leksikografike.

Numri i nyjeve dhe i operacioneve Backtracking është **i njëjtë në çdo kompjuter**, sepse kërkimi ndalet kur gjen zgjidhjen. Vetëm koha varet nga shpejtësia e kompjuterit.

### 10.2 Iteracionet e IDDFS për n = 5

| Limiti | Nyje në iteracion | Rezultati |
|---|---|---|
| 0 | 1 | cutoff |
| 5 | 326 | cutoff |
| 10 | 17 846 | cutoff |
| 15 | 316 886 | cutoff |
| 20 | 1 507 766 | cutoff |
| 21 | 1 669 046 | cutoff |
| 22 | 1 830 326 | cutoff |
| 23 | 1 991 606 | cutoff |
| 24 | 2 152 886 | cutoff |
| **25** | **38** | **zgjidhje** |

Programi i shfaq të 26 iteracionet. Tabela tregon një pjesë të tyre.

**Vërejtja kryesore:** iteracioni i fundit, me limit 25 = n², e gjen zgjidhjen pas vetëm **38 nyjeve**. Kjo është sa do të vizitonte një DFS i thjeshtë. Të gjitha nyjet e tjera, mbi 13.5 milionë, shpenzohen në iteracionet 0–24, të cilat nuk mund të gjejnë zgjidhje, sepse çdo zgjidhje është në thellësinë 25.

### 10.3 Numri i nyjeve në çdo nivel të pemës (n = 5)

Nga diferencat ndërmjet iteracioneve fitohet numri i nyjeve në çdo nivel, pra numri i grid-ave të pjesshëm pa konflikt:

| Niveli (qeliza të plotësuara) | 0 | 5 | 10 | 15 | 19 | 20 | 21–24 |
|---|---|---|---|---|---|---|---|
| Nyje | 1 | 120 | 5 280 | 66 240 | 334 080 | 161 280 | 161 280 |

Këta numra kanë kuptim të qartë kombinatorik:

- **Niveli 5 = 120 = 5!**: rreshti i parë mund të jetë çdo permutacion i 1..5.
- **Niveli 10 = 5 280 = 120 · 44**: rreshti i dytë duhet të ndryshojë nga i pari në çdo kolonë; ka 44 permutacione të tilla (çrregullime, *derangements*).
- **Niveli 20 = 161 280 = L(5)**: pasi plotësohen 4 rreshta, rreshti i 5-të është i përcaktuar plotësisht, sepse çdo kolonë ka vetëm një vlerë që i mungon. Prandaj numri i nyjeve mbetet 161 280 deri në fund, dhe është sa numri i të gjithë katrorëve latinë të rendit 5.

### 10.4 IDDFS klasik kundrejt hapit me rresht (n = 5)

| Varianti | Iteracione | Nyje gjithsej | Koha |
|---|---|---|---|
| `step = 1` (klasik) | 26 | 13 505 923 | 16.52 s |
| `step = 5` (një rresht) | 6 | 1 842 863 | 2.01 s |

Të dy variantet japin **të njëjtin katror latin**. Hapi më i madh e ul numrin e iteracioneve dhe, me to, numrin e nyjeve që vizitohen disa herë.

### 10.5 Vlera të tjera të n

| n | Nyje gjithsej | Iteracione | Rezultati |
|---|---|---|---|
| 1 | 3 | 2 | zgjidhje |
| 2 | 21 | 5 | zgjidhje |
| 3 | 326 | 10 | zgjidhje |
| 4 | 24 861 | 17 | zgjidhje |
| 5 | 13 505 923 | 26 | zgjidhje |
| 6 (`--step=6`, 60 s) | 71 812 367 | 5 | **koha mbaroi** gjatë iteracionit me limit 24 |

Për n = 6, edhe me hap prej një rreshti, iteracioni me limit 18 viziton 62.9 milionë nyje, dhe programi nuk e arrin limitin 36 brenda 60 sekondave. Kjo nuk do të thotë që nuk ka zgjidhje (ka 812 851 200), por që kostoja e iteracioneve të cekëta rritet shumë shpejt me n.

### 10.6 Testet automatike

Skedari `tests/test_latin_square_iddfs.py` përmban 16 teste (`unittest`, pa paketa shtesë):

| Grupi i testeve | Çka verifikon |
|---|---|
| `TestObjectiveAndValidation` | shembulli i detyrës është i vlefshëm me f = 0; përsëritjet në rreshta dhe kolona zbulohen dhe numërohen; rreshti i shkurtër dhe vlera jashtë domenit refuzohen |
| `TestSearchSpace` | n^(n²), (n!)^n, numri i fqinjëve, formula e rastit më të keq për n = 2 (57 nyje) |
| `TestIDDFS` | n = 1..4 zgjidhen saktë; zgjidhja del në limitin n²; numri i saktë i nyjeve për n = 2; n = 5; hapi më i madh jep të njëjtën zgjidhje me më pak nyje; backtracking e rikthen gjendjen; kufiri i kohës |

Rezultati i ekzekutimit `python -m unittest discover tests -v`:

```text
Ran 16 tests in 2.842s

OK
```

---

## 11. Analiza e kompleksitetit

### 11.1 Parametrat

- **b (faktori i degëzimit):** b ≤ n.
- **d (thellësia e zgjidhjes):** d = n².

### 11.2 Kompleksiteti kohor dhe numri i saktë i nyjeve në rastin më të keq

Në iteracionin me limit L, DLS viziton të gjitha nyjet e niveleve 0..L. Kështu nyjet e nivelit i vizitohen në iteracionet L = i, i+1, …, d, pra **(d + 1 − i) herë**. Në një pemë uniforme me faktor degëzimi b, ku zgjidhja është në nivelin e fundit:

```
N_IDDFS = (d+1)·1 + d·b + (d−1)·b² + … + 2·b^(d−1) + 1·b^d  =  Σ_{i=0}^{d} (d + 1 − i) · b^i   =   O(b^d)
```

**Shembull, n = 2** (b = 2, d = 4):

```
N = 5·1 + 4·2 + 3·4 + 2·8 + 1·16 = 5 + 8 + 12 + 16 + 16 = 57
```

Për krahasim, BFS ose DLS me një iteracion të vetëm do të vizitonin Σ bⁱ = 31 nyje. Për b të madh, përsëritja kushton pak, sepse shumica e nyjeve janë në nivelin e fundit, që vizitohet vetëm një herë. Për b = 2, IDDFS viziton afërsisht dyfishin.

| n | b = n, d = n² | N_IDDFS në pemën pa kufizime (`worst_case_nodes`) | Nyje reale (me kufizime) |
|---|---|---|---|
| 2 | 2, 4 | 57 | 21 |
| 3 | 3, 9 | 44 281 | 326 |
| 4 | 4, 16 | 7.64 × 10⁹ | 24 861 |
| 5 | 5, 25 | 4.66 × 10¹⁷ | 13 505 923 |

### 11.3 Kompleksiteti hapësinor (Space Complexity)

- Thellësia e rekursionit: më së shumti d = n² thirrje.
- Grid-i, `row_used` dhe `col_used`: O(n²).

Gjithsej: **O(n²) = O(d)**, njësoj si DFS. Kjo është përparësia kryesore ndaj BFS, i cili në rastin më të keq ruan O(b^d) nyje (te Sudoku-ja, rradha arriti 356 812 grid-a).

### 11.4 Ndikimi i kontrollit të kufizimeve dhe i backtracking

- Pa kufizime, pema e n = 5 do të kishte 5²⁵ ≈ 2.98 × 10¹⁷ gjethe. Me kontrollin e C1 dhe C2, çdo nivel ka më së shumti 334 080 nyje.
- Backtracking e rikthen grid-in në gjendjen e mëparshme pa e kopjuar, kështu memoria mbetet O(n²).

### 11.5 Pse IDDFS është i shtrenjtë për këtë problem

Përparësia e IDDFS, gjetja e zgjidhjes **më të cekët**, nuk ka vlerë këtu, sepse **të gjitha zgjidhjet janë në të njëjtën thellësi d = n²**. Çdo iteracion me limit më të vogël se n² është punë që nuk mund të japë zgjidhje. Për n = 5, një DFS i vetëm me limit 25 gjen zgjidhjen pas 38 nyjeve, ndërsa IDDFS viziton 13 505 923.

IDDFS është i dobishëm kur thellësia e zgjidhjes **nuk dihet** paraprakisht dhe mund të jetë e vogël, si te 8-Puzzle (detyra 4), ku zgjidhja më e shkurtër është ajo që kërkohet.

### 11.6 Kompleksiteti teorik kundrejt statistikave reale

Formula e seksionit 11.2 supozon pemë uniforme me b = n në çdo nivel. Në praktikë, kufizimet e ulin faktorin e degëzimit shumë: qeliza e fundit e çdo rreshti ka më së shumti një vlerë, dhe rreshti i fundit është plotësisht i përcaktuar. Prandaj numri real i nyjeve është me shumë rende madhësie më i vogël se kufiri teorik.

---

## 12. Përfundimi

- Katrori latin u modelua si CSP me n² variabla X(r,c), domen {1, …, n} dhe kufizimet e rreshtit dhe kolonës.
- Funksioni objektiv f(S) numëron përsëritjet. Zgjidhje është grid-i i plotë me f(S) = 0.
- Hapësira naive është n^(n²), p.sh. 2.98 × 10¹⁷ për n = 5, ndërsa ka 161 280 zgjidhje.
- IDDFS me backtracking gjeti një katror latin të vlefshëm për n = 1..5, të verifikuar me validim të pavarur.
- Për n = 5, iteracioni i fundit e gjeti zgjidhjen pas 38 nyjeve, por iteracionet e mëparshme vizituan mbi 13.5 milionë. Arsyeja është që të gjitha zgjidhjet janë në thellësinë n², kështu iteracionet e cekëta nuk mund të gjejnë zgjidhje.
- Për n = 6, IDDFS nuk e gjeti zgjidhjen brenda 60 sekondave.

IDDFS ka memorien e vogël të DFS dhe plotësinë e BFS, por për probleme ku thellësia e zgjidhjes dihet dhe është gjithmonë maksimale, një DFS i thjeshtë me backtracking është shumë më efikas.

---

## 13. Referencat

1. S. Russell, P. Norvig, *Artificial Intelligence: A Modern Approach*, 3rd ed., Kapitulli 3 (Solving Problems by Searching, seksioni për Iterative Deepening Search) dhe Kapitulli 6 (Constraint Satisfaction Problems).
2. Z. Michalewicz, D. B. Fogel, *How to Solve It: Modern Heuristics*, 2nd ed., Springer, 2004, Kapitujt 1–3.
3. N. Musliu, *Uninformed Search*, TU Wien: http://www.dbai.tuwien.ac.at/staff/musliu/ProblemSolvingAI/Class2UninformedSearch.pdf
4. N. Musliu, *Basic Concepts of Problem Solving*, TU Wien: http://www.dbai.tuwien.ac.at/staff/musliu/ProblemSolvingAI/class1BasicConcepts.pdf
5. OEIS A002860, *Number of Latin squares of order n*: https://oeis.org/A002860
6. *Latin square*, Wikipedia: https://en.wikipedia.org/wiki/Latin_square