# Sudoku Solver – BFS me Backtracking

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
7. [BFS me Backtracking](#7-bfs-me-backtracking)
8. [Implementimi në Python](#8-implementimi-në-python)
9. [Si ekzekutohet programi](#9-si-ekzekutohet-programi)
10. [Rezultatet, testimi dhe validimi](#10-rezultatet-testimi-dhe-validimi)
11. [Analiza e kompleksitetit](#11-analiza-e-kompleksitetit)
12. [Përfundimi](#12-përfundimi)
13. [Referencat](#13-referencat)

---

## 1. Hyrje

Ky projekt e zgjidh lojën Sudoku me algoritmin e kërkimit në gjerësi me kthim prapa (*Breadth-First Search with Backtracking*). Programi i zgjidh tri nivele: **Easy**, **Medium** dhe **Hard**. Projekti përmban:

- modelimin matematikor të problemit;
- variablat, domenet, kufizimet dhe paraqitjen e gjendjes;
- funksionin objektiv;
- llogaritjen e hapësirës së kërkimit dhe shpjegimin e peizazhit;
- implementimin në Python (`sudoku_bfs.py`);
- testet automatike (`tests/test_sudoku_bfs.py`).

Të gjitha rezultatet numerike në këtë dokument vijnë ose nga ekzekutimi real i programit, ose nga një llogaritje matematikore e shpjeguar.

---

## 2. Përshkrimi i problemit

Sudoku luhet në një grid 9 × 9, i ndarë në 9 kuti 3 × 3. Disa qeliza janë të plotësuara që në fillim (numrat e dhënë, *givens*). Detyra është të plotësohen qelizat e zbrazëta me numrat 1–9 në mënyrë që:

- çdo **rresht** të përmbajë numrat 1–9 saktësisht një herë;
- çdo **kolonë** të përmbajë numrat 1–9 saktësisht një herë;
- çdo **kuti 3 × 3** të përmbajë numrat 1–9 saktësisht një herë.

Një Sudoku i mirëformuar ka **saktësisht një zgjidhje**. Ndryshe nga problemi i golfistëve, këtu nuk kërkohet optimizim: kërkohet gjetja e një plotësimi që i plotëson të gjitha kushtet. Pra Sudoku është **problem i plotësimit të kufizimeve** (*Constraint Satisfaction Problem*, CSP).

### 2.1 Tri nivelet

Niveli përcaktohet nga numri i numrave të dhënë: sa më pak numra, aq më shumë variabla dhe aq më e madhe pema e kërkimit.

| Niveli | Numra të dhënë | Qeliza të zbrazëta | Burimi |
|---|---|---|---|
| Easy | 36 | 45 | shembull i zakonshëm niveli të lehtë |
| Medium | 30 | 51 | shembulli i njohur nga artikulli "Sudoku" në Wikipedia [5] |
| Hard | 21 | 60 | puzzle i publikuar nga Arto Inkala (2012) si "Sudoku më i vështirë" [6] |

```text
EASY                       MEDIUM                     HARD
. . . | 2 6 . | 7 . 1      5 3 . | . 7 . | . . .      8 . . | . . . | . . .
6 8 . | . 7 . | . 9 .      6 . . | 1 9 5 | . . .      . . 3 | 6 . . | . . .
1 9 . | . . 4 | 5 . .      . 9 8 | . . . | . 6 .      . 7 . | . 9 . | 2 . .
------+-------+------      ------+-------+------      ------+-------+------
8 2 . | 1 . . | . 4 .      8 . . | . 6 . | . . 3      . 5 . | . . 7 | . . .
. . 4 | 6 . 2 | 9 . .      4 . . | 8 . 3 | . . 1      . . . | . 4 5 | 7 . .
. 5 . | . . 3 | . 2 8      7 . . | . 2 . | . . 6      . . . | 1 . . | . 3 .
------+-------+------      ------+-------+------      ------+-------+------
. . 9 | 3 . . | . 7 4      . 6 . | . . . | 2 8 .      . . 1 | . . . | . 6 8
. 4 . | . 5 . | . 3 6      . . . | 4 1 9 | . . 5      . . 8 | 5 . . | . 1 .
7 . 3 | . 1 8 | . . .      . . . | . 8 . | . 7 9      . 9 . | . . . | 4 . .
```

Programi e verifikon (seksioni 10) që secili prej tyre ka **saktësisht një zgjidhje**.

---

## 3. Modelimi matematikor (Problem Modeling)

### 3.1 Parametrat dhe bashkësitë

| Simboli | Kuptimi |
|---|---|
| R = C = {0, …, 8} | rreshtat dhe kolonat |
| (r, c) | qeliza në rreshtin r dhe kolonën c |
| D = {1, …, 9} | vlerat e mundshme |
| G ⊆ R × C | qelizat me numra të dhënë (*givens*), me vlerë g(r, c) |
| E = (R × C) \ G | qelizat e zbrazëta, \|E\| = k |
| b(r, c) = 3·⌊r/3⌋ + ⌊c/3⌋ | numri i kutisë 3 × 3 ku ndodhet qeliza |

### 3.2 Njësitë dhe fqinjët

Një **njësi** (*unit*) është një rresht, një kolonë ose një kuti. Ka 27 njësi: 9 rreshta, 9 kolona, 9 kuti.

Dy qeliza janë **fqinje** (*peers*) nëse ndodhen në të njëjtën njësi. Çdo qelizë ka saktësisht **20 fqinjë**: 8 në rresht, 8 në kolonë dhe 4 të tjerë në kuti.

### 3.3 Formulimi

Kërkohet një funksion x : R × C → D (vlera e çdo qelize) që plotëson:

```
x(r, c) ≠ x(r, c')     për c ≠ c'                          (rreshti)
x(r, c) ≠ x(r', c)     për r ≠ r'                          (kolona)
x(r, c) ≠ x(r', c')    për (r,c) ≠ (r',c') me b(r,c) = b(r',c')   (kutia)
x(r, c) = g(r, c)      për (r, c) ∈ G                       (numrat e dhënë)
```

Meqë çdo njësi ka 9 qeliza dhe 9 vlera, kushti "vlera të ndryshme" është ekuivalent me "çdo vlerë 1–9 shfaqet saktësisht një herë".

### 3.4 Supozimet

1. Grid-i është 9 × 9 me kuti 3 × 3.
2. Numrat e dhënë janë të saktë dhe nuk ndryshohen.
3. Puzzle-i fillestar nuk përmban konflikte (programi e kontrollon këtë).
4. Kërkohet një zgjidhje. Programi mund ta vazhdojë kërkimin edhe për t'i numëruar të gjitha (opsioni `--all`).

---

## 4. Paraqitja e problemit (Problem Representation)

### 4.1 Variablat

```
X(r,c)   për çdo qelizë të zbrazët (r, c) ∈ E
```

Numri i variablave është k = 45 (Easy), 51 (Medium), 60 (Hard). Qelizat e dhëna nuk janë variabla, sepse vlera e tyre është fikse.

### 4.2 Domenet

**Domeni fillestar (statik):** D(X(r,c)) = {1, 2, …, 9}.

**Domeni aktual (dinamik):** vlerat që nuk shfaqen tashmë te 20 fqinjët e qelizës:

```
D_aktual(X(r,c)) = {1..9} \ { x(r',c') : (r',c') fqinj i (r,c) dhe i plotësuar }
```

**Shembull (Medium, qeliza (0, 2)):** rreshti përmban 5, 3, 7; kolona përmban 8; kutia përmban 5, 3, 6, 9, 8. Vlerat e përdorura janë {3, 5, 6, 7, 8, 9}, kështu domeni aktual është **{1, 2, 4}**. Kjo vlerë verifikohet me test (`test_candidates_of_first_empty_cell`).

### 4.3 Kufizimet (Hard Constraints)

| Nr. | Kufizimi | Si plotësohet në kod |
|---|---|---|
| C1 | çdo rresht ka vlera të ndryshme | `candidates()` përjashton vlerat e rreshtit |
| C2 | çdo kolonë ka vlera të ndryshme | `candidates()` përjashton vlerat e kolonës |
| C3 | çdo kuti 3 × 3 ka vlera të ndryshme | `candidates()` përjashton vlerat e kutisë |
| C4 | numrat e dhënë nuk ndryshohen | BFS plotëson vetëm qelizat `'0'` |

C1–C3 kontrollohen **sapo vendoset një vlerë**: një fëmijë krijohet vetëm për vlerat e domenit aktual. Pra në pemën e kërkimit nuk krijohet asnjë gjendje me konflikt. Funksioni `validate_solution()` megjithatë i kontrollon të katër kufizimet nga fillimi, pa u mbështetur në kërkimin.

Në Sudoku nuk ka **soft constraints**: të gjitha kushtet janë të detyrueshme.

### 4.4 Gjendja fillestare (Initial State)

Grid-i i puzzle-it, me qelizat e dhëna të plotësuara dhe qelizat e tjera `'0'`. Ky është rrënja e pemës së kërkimit.

### 4.5 Gjendja përfundimtare dhe testi i qëllimit (Goal State, Goal Test)

```
Goal(S)  ⇔  asnjë qelizë nuk është e zbrazët  dhe  S plotëson C1–C4
```

Meqë BFS nuk krijon kurrë gjendje me konflikt, në kod testi i qëllimit është vetëm "grid-i nuk ka më `'0'`" (`next_empty_cell(grid) == -1`). Vlefshmëria e plotë verifikohet më pas në mënyrë të pavarur.

### 4.6 Paraqitja e gjendjes në Python (State Representation)

| Elementi | Në Python | Arsyeja |
|---|---|---|
| Grid-i (nyja) | string me 81 karaktere, p.sh. `"530070000600195000…"` | i pandryshueshëm, kompakt në memorie (rreth 130 bytes); BFS ruan shumë gjendje njëkohësisht |
| Qeliza (r, c) | indeksi `i = 9·r + c` | një numër i vetëm në vend të dy koordinatave |
| Qelizë e zbrazët | karakteri `'0'` | |
| Fqinjët | `PEERS[i]`, tuple me 20 indekse | llogariten një herë në fillim |
| Rradha e BFS | `collections.deque` | `append` dhe `popleft` në O(1) |
| Vlerat e përdorura | `set` brenda `candidates()` | kontroll i shpejtë "a është përdorur kjo vlerë?" |

Fëmija i një gjendjeje krijohet si string i ri: `grid[:cell] + value + grid[cell+1:]`. Prindi mbetet i pandryshuar, gjë që është e nevojshme në BFS, sepse prindi dhe vëllezërit e fëmijës presin ende në rradhë.

---

## 5. Funksioni objektiv (Objective Function)

### 5.1 Përkufizimi

Sudoku nuk ka "zgjidhje më të mirë" dhe "më të keqe": një grid ose është zgjidhje, ose nuk është. Prandaj funksioni objektiv mat **sa larg është një grid nga zgjidhja**, përmes numrit të konflikteve:

```
f(S) = | { (i, j) : i < j,  i dhe j fqinje,  x(i) = x(j) ≠ 0 } |        (minimizohet)
```

Pra f(S) numëron çiftet e qelizave fqinje që kanë të njëjtën vlerë. Bashkë me të, programi raporton edhe numrin e qelizave të zbrazëta:

```
e(S) = numri i qelizave me vlerë 0
```

**Zgjidhje** është çdo grid me **f(S) = 0 dhe e(S) = 0**. Minimumi i f është 0, dhe arrihet saktësisht te zgjidhjet. Në kod të dyja vlerat kthehen nga `calculate_objective(grid)`, si `(f, e)`.

### 5.2 Funksioni objektiv kundrejt kufizimeve

| | Kufizimet C1–C4 | Funksioni objektiv f(S) |
|---|---|---|
| Roli | përcaktojnë **cili grid është zgjidhje** | mat **sa kufizime shkelen** |
| Natyra | po / jo | vlerë numerike ≥ 0 |
| Në BFS | çdo vlerë që do të shkaktonte konflikt nuk krijohet fare | mbetet gjithmonë 0 gjatë kërkimit |
| Përdorimi kryesor | gjenerimi i fëmijëve | validimi dhe përshkrimi i peizazhit (seksioni 6.4) |

### 5.3 Shembull konkret

Zgjidhja e nivelit Medium ka rreshtin e parë `5 3 4 6 7 8 9 1 2` dhe f = 0. Nëse ndërrohen dy vlerat e para, rreshti bëhet `3 5 4 6 7 8 9 1 2`. Rreshti mbetet në rregull, por 3-shi dhe 5-shi tani përsëriten në kolonat e tyre, kështu f(S) > 0 dhe grid-i nuk është më zgjidhje. Ky rast verifikohet me test (`test_conflicts_are_counted`).

---

## 6. Hapësira e kërkimit dhe peizazhi (Search Space & Landscape)

### 6.1 Hapësira naive

Çdo qelizë e zbrazët merr një nga 9 vlera, pa kontrolluar asnjë kufizim:

```
|S_naive| = 9^k
```

### 6.2 Paraqitje më e mirë: permutacione për rresht

Nëse çdo rresht plotësohet si permutacion i vlerave që i mungojnë, kushti C1 plotësohet automatikisht. Nëse rreshti r ka kᵣ qeliza të zbrazëta, ka kᵣ! mënyra për t'i plotësuar:

```
|S_rresht| = k₀! · k₁! · … · k₈!
```

### 6.3 Pas domenit fillestar

Nëse çdo qelizë merr vetëm vlerat e domenit të saj aktual në gjendjen fillestare:

```
|S_domen| = Π |D_aktual(X(r,c))|
```

### 6.4 Vlerat për tri nivelet (nga `search_space()`)

| Niveli | k | 9^k | Permutacione për rresht | Pas domenit fillestar |
|---|---|---|---|---|
| Easy | 45 | 8.72 × 10⁴² | 5.15 × 10¹⁸ | 1.39 × 10¹¹ |
| Medium | 51 | 4.63 × 10⁴⁸ | 2.40 × 10²³ | 4.25 × 10²² |
| Hard | 60 | 1.79 × 10⁵⁷ | 6.99 × 10³⁰ | 9.58 × 10³⁶ |

Për krahasim, numri i të gjitha grid-ave të plota dhe të vlefshme të Sudoku-së është rreth 6.67 × 10²¹ [7]. Nga gjithë këto, një puzzle i mirëformuar lejon vetëm **një**.

Dy paraqitjet e fundit ngushtojnë hapësirën në mënyra të ndryshme, prandaj nuk janë domosdoshmërisht të renditura njësoj për çdo nivel. Te Hard, për shembull, paraqitja me permutacione është më e vogël, sepse rreshtat kanë shumë qeliza të zbrazëta dhe secila ka domen të madh.

### 6.5 Hapësira e kërkimit, pema e kërkimit dhe peizazhi

| Koncepti | Çfarë është | Në këtë problem |
|---|---|---|
| **Hapësira e kërkimit (*Search Space*)** | bashkësia e zgjidhjeve kandidate të plota | të gjitha mënyrat e plotësimit të k qelizave (seksionet 6.1–6.3) |
| **Pema e kërkimit (*Search Tree*)** | struktura që ndërton algoritmi; çdo nyje është gjendje e pjesshme | rrënja = puzzle-i; niveli i = i qeliza të plotësuara; gjethet = zgjidhje ose degë pa vazhdim |
| **Peizazhi (*Landscape*)** | hapësira + fqinjësia + funksioni që vlerëson cilësinë e çdo gjendjeje | grid-at e plotë, fqinjësia "ndërro dy qeliza në rresht", vlerësimi f(S) |

**Peizazhi në detaj**, treshja (X, N, f):

- **X**: grid-at e plotë ku çdo rresht është permutacion i 1–9 dhe numrat e dhënë janë në vend. Kështu C1 dhe C4 plotësohen gjithmonë, ndërsa C2 dhe C3 mund të shkelen.
- **N(S)**: fqinj i S është çdo grid që merret duke ndërruar dy qeliza **jo të dhëna** në të njëjtin rresht. Numri i fqinjëve është Σᵣ C(kᵣ, 2): **90** për Easy, **120** për Medium, **172** për Hard.
- **f(S)**: lartësia e çdo pike në peizazh, pra numri i konflikteve në kolona dhe kuti.

Zgjidhja është **minimumi global**, me f = 0. Peizazhi ka edhe **minimume lokale**: grid-a me f > 0 ku asnjë ndërrim i vetëm nuk e ul f. Kjo është arsyeja pse metodat e kërkimit lokal mund të ngecin në Sudoku.

**Rëndësi:** BFS **nuk lëviz nëpër peizazh**. Ai ndërton zgjidhjen qelizë pas qelize në pemën e kërkimit dhe nuk krijon kurrë grid me konflikt. Peizazhi përshkruan strukturën e problemit, jo mënyrën si punon BFS.

### 6.6 Faktori i degëzimit dhe thellësia

- **Thellësia (d):** çdo nivel plotëson një qelizë, prandaj zgjidhja është gjithmonë në thellësinë **d = k** (45, 51, 60). Të gjitha zgjidhjet janë në të njëjtin nivel, në fund të pemës.
- **Faktori i degëzimit (b):** b ≤ 9. Faktori real është |D_aktual| e qelizës që plotësohet, zakonisht shumë më pak se 9 për shkak të kufizimeve.

---

## 7. BFS me Backtracking

### 7.1 Nyja e kërkimit (Search Node)

Një nyje është një **grid i pjesshëm**: puzzle-i me disa nga qelizat e zbrazëta të plotësuara, pa asnjë konflikt. Fëmijët e saj janë grid-at që merren duke plotësuar qelizën e ardhshme të zbrazët me secilën vlerë të domenit të saj aktual.

### 7.2 Si funksionon BFS

1. Rrënja (puzzle-i) futet në rradhë (*queue*).
2. Merret nyja **e para** nga rradha (FIFO).
3. Nëse grid-i nuk ka qeliza të zbrazëta, kjo është zgjidhja.
4. Përndryshe, zgjidhet qeliza e ardhshme e zbrazët, me radhë rresht pas rreshti.
5. Llogaritet domeni aktual i saj (vlerat që nuk shkelin C1–C3).
6. Për çdo vlerë të lejuar krijohet një fëmijë dhe futet **në fund** të rradhës.
7. Nëse domeni është bosh, nyja braktiset (**backtracking**).
8. Përsëritet nga hapi 2.

Për shkak të rradhës FIFO, BFS i viziton të gjitha nyjet e nivelit i para se të kalojë te niveli i + 1. Pra pema eksplorohet **nivel pas niveli**.

### 7.3 Ku është "Backtracking" në BFS

Te DFS, backtracking do të thotë: hiq vlerën e fundit dhe provo tjetrën. Te BFS nuk ka një rrugë të vetme për t'u kthyer prapa, sepse shumë degë eksplorohen paralelisht. Këtu backtracking zbatohet si parimi i **kërkimit me kthim prapa** (*backtracking search*):

- variablat caktohen **një nga një**;
- kufizimet kontrollohen **menjëherë** te zgjidhja e pjesshme, jo pasi të plotësohet grid-i;
- një vlerë që shkel kufizimet **nuk krijohet fare**;
- një nyje ku qeliza e ardhshme nuk ka asnjë vlerë të lejuar **braktiset** (*dead end*), dhe kërkimi vazhdon me alternativat e tjera që presin në rradhë.

Dallimi praktik: pa këtë kontroll, BFS do të gjeneronte deri në 9^k nyje dhe do t'i kontrollonte vetëm në fund. Me të, degët e pavlefshme priten sapo shfaqen.

### 7.4 Pseudokodi (pjesë ndihmëse)

```text
funksioni BFS_SOLVE(puzzle, find_all):
    nëse puzzle ka konflikte:  kthe "invalid_puzzle"
    queue ← [puzzle]                                    // gjendja fillestare
    solutions ← []
    sa kohë queue nuk është bosh:
        grid ← queue.popleft()                          // FIFO
        cell ← qeliza e parë e zbrazët në grid
        nëse cell nuk ekziston:                         // testi i qëllimit
            shto grid në solutions
            nëse jo find_all:  kthe solutions
            vazhdo
        values ← CANDIDATES(grid, cell)                 // domeni aktual
        nëse values është bosh:
            dead_ends ← dead_ends + 1                   // BACKTRACKING
            vazhdo
        për çdo v në values:                            // zgjerimi
            queue.append(grid me cell = v)
    kthe solutions                                      // "exhausted"

funksioni CANDIDATES(grid, cell):
    used ← vlerat e 20 fqinjëve të cell
    kthe {1..9} \ used
```

---

## 8. Implementimi në Python

I gjithë kodi është në `sudoku_bfs.py`. Përdoren vetëm biblioteka standarde (`collections`, `math`, `time`, `sys`).

| Funksioni | Roli | Lidhja me modelin |
|---|---|---|
| `build_peers()` / `PEERS` | 20 fqinjët e çdo qelize | njësitë dhe fqinjët (3.2) |
| `candidates(grid, cell)` | domeni aktual i qelizës | C1, C2, C3 |
| `is_valid_puzzle(grid)` | kontrollon puzzle-in fillestar | supozimi 3 |
| `next_empty_cell(grid)` | qeliza e ardhshme për t'u plotësuar | renditja e variablave |
| `count_conflicts(grid)` | numëron konfliktet | f(S) |
| `calculate_objective(grid)` | kthen (f, e) | f(S), e(S) |
| `validate_solution(solution, puzzle)` | validim i pavarur i C1–C4 | të gjitha kufizimet |
| `bfs_solve(puzzle, find_all)` | BFS me backtracking | seksioni 7 |
| `search_space(puzzle)` | 9^k, permutacionet, domeni, fqinjët | seksioni 6 |
| `print_grid()`, `solve_level()`, `main()` | shfaqja e rezultateve | |

`bfs_solve()` ka edhe një kufi sigurie prej 5 000 000 nyjesh të gjeneruara (`MAX_GENERATED`). BFS i ruan të gjitha nyjet e nivelit aktual në memorie, dhe ky kufi e pengon programin të harxhojë gjithë memorien e kompjuterit në një puzzle shumë të vështirë. Për tri nivelet e këtij projekti, kufiri nuk arrihet.

---

## 9. Si ekzekutohet programi

Kërkohet Python 3.8 ose më i ri. Nuk ka nevojë për instalim paketash.

```text
AI-Uninformed-Search/
├── 1-Social-Golfers-DFS/
├── 2-Sudoku-BFS/
│   ├── README.md
│   ├── sudoku_bfs.py
│   └── tests/
│       └── test_sudoku_bfs.py
├── 3-Latin-Square-IDDFS/
└── 4-Search-Trees/
```

Hapni terminalin (**Terminal → New Terminal**) dhe hyni në folderin e kësaj detyre:

```bash
cd 2-Sudoku-BFS
```

Nëse terminali është në folderin e një detyre tjetër, p.sh. `1-Social-Golfers-DFS`, përdorni `cd ..\2-Sudoku-BFS`.

Pastaj ekzekutoni:

```bash
# Të tri nivelet
python sudoku_bfs.py

# Vetëm një nivel
python sudoku_bfs.py easy
python sudoku_bfs.py medium
python sudoku_bfs.py hard

# Numërimi i të gjitha zgjidhjeve (BFS vazhdon deri në fund të pemës)
python sudoku_bfs.py --all

# Testet
python -m unittest discover tests -v
```

---

## 10. Rezultatet, testimi dhe validimi

### 10.1 Rezultatet për tri nivelet

Ekzekutimi `python sudoku_bfs.py`:

| Niveli | d (thellësia) | Nyje të gjeneruara | Degë të braktisura | Rradha max | Koha | f(S) | E vlefshme |
|---|---|---|---|---|---|---|---|
| Easy | 45 | 69 | 11 | 5 | 0.00 s | 0 | PO |
| Medium | 51 | 4 632 | 1 371 | 738 | 0.02 s | 0 | PO |
| Hard | 60 | 2 068 781 | 705 261 | 356 812 | 8.11 s | 0 | PO |

Ndryshe nga detyra me golfistët, këtu kërkimi **nuk ndalet nga koha**, por kur gjen zgjidhjen. Prandaj numri i nyjeve, i degëve të braktisura dhe madhësia e rradhës janë **të njëjta në çdo kompjuter**. Vetëm koha e ekzekutimit varet nga shpejtësia e kompjuterit.

**Zgjidhja e nivelit Hard:**

```text
8 1 2 | 7 5 3 | 6 4 9
9 4 3 | 6 8 2 | 1 7 5
6 7 5 | 4 9 1 | 2 8 3
------+-------+------
1 5 4 | 2 3 7 | 8 9 6
3 6 9 | 8 4 5 | 7 2 1
2 8 7 | 1 6 9 | 5 3 4
------+-------+------
5 2 1 | 9 7 4 | 3 6 8
4 3 8 | 5 2 6 | 9 1 7
7 9 6 | 3 1 8 | 4 5 2
```

### 10.2 Numërimi i zgjidhjeve (`--all`)

Me opsionin `--all`, BFS nuk ndalet te zgjidhja e parë, por vazhdon deri sa rradha të zbrazet:

| Niveli | Numri i zgjidhjeve | Nyje të gjeneruara | Arsyeja e ndalimit |
|---|---|---|---|
| Easy | 1 | 69 | e gjithë pema u kontrollua |
| Medium | 1 | 4 632 | e gjithë pema u kontrollua |
| Hard | 1 | 2 068 781 | e gjithë pema u kontrollua |

Secili puzzle ka **saktësisht një zgjidhje**. Numri i nyjeve është **i njëjtë** si kur kërkimi ndalet te zgjidhja e parë. Arsyeja: të gjitha zgjidhjet janë në thellësinë d = k, në nivelin e fundit. BFS e arrin këtë nivel vetëm pasi t'i ketë zgjeruar të gjitha nivelet më lart. Meqë zgjidhja është unike, ajo është e vetmja nyje e nivelit të fundit. Pra te Sudoku-ja BFS **e gjen zgjidhjen vetëm pasi ta ketë kontrolluar gjithë pemën**.

### 10.3 Si rritet rradha e BFS (niveli Hard)

Numri i nyjeve në disa nga 61 nivelet e pemës (nga 0 deri në 60):

| Niveli (qeliza të plotësuara) | 0 | 5 | 10 | 20 | 25 | 30 | 35 | 45 | 52 | 53–60 |
|---|---|---|---|---|---|---|---|---|---|---|
| Nyje | 1 | 306 | 3 828 | 4 782 | 189 960 | **356 783** | 9 508 | 16 590 | 4 | 1 |

Niveli më i gjerë është niveli 30, me 356 783 nyje. Pas tij, kufizimet presin pothuajse të gjitha degët, dhe nga niveli 53 deri në fund mbetet vetëm një nyje, rruga drejt zgjidhjes. Shuma e nyjeve në të gjitha nivelet është 2 068 781, sa numri i nyjeve të gjeneruara.

### 10.4 Testet automatike

Skedari `tests/test_sudoku_bfs.py` përmban 21 teste (`unittest`, pa paketa shtesë):

| Grupi i testeve | Çka verifikon |
|---|---|
| `TestModel` | çdo qelizë ka 20 fqinjë; domeni i qelizës (0, 2) te Medium është {1, 2, 4}; renditja e qelizave; puzzle-t janë të vlefshëm; numri i numrave të dhënë |
| `TestObjectiveAndValidation` | f = 0 për zgjidhjen; konfliktet numërohen; validimi refuzon grid të paplotë, zgjidhje të gabuar dhe numra të dhënë të ndryshuar |
| `TestSearchSpace` | 9^k; hapësira pas domenit është më e vogël se ajo naive |
| `TestBFS` | të tri nivelet zgjidhen dhe zgjidhjet janë të vlefshme; Easy dhe Medium kanë zgjidhje unike; puzzle pa zgjidhje dhe puzzle i pavlefshëm trajtohen saktë |

Rezultati i ekzekutimit `python -m unittest discover tests -v`:

```text
Ran 21 tests in 8.249s

OK
```

---

## 11. Analiza e kompleksitetit

### 11.1 Parametrat

- **b (faktori i degëzimit):** b ≤ 9.
- **d (thellësia):** d = k, numri i qelizave të zbrazëta. Zgjidhja është gjithmonë në thellësinë d.

### 11.2 Kompleksiteti kohor (Time Complexity)

Në rastin më të keq, BFS viziton të gjitha nyjet e pemës deri në thellësinë d:

```
1 + b + b² + … + b^d = (b^(d+1) − 1)/(b − 1)  =  O(b^d)
```

Për Hard, me b = 9 dhe d = 60, kjo do të ishte rreth 2 × 10⁵⁷ nyje. Puna për nyje është konstante: kontrollohen 20 fqinjë dhe krijohen më së shumti 9 fëmijë.

### 11.3 Kompleksiteti hapësinor (Space Complexity)

BFS i ruan në rradhë të gjitha nyjet e nivelit që po eksplorohet. Në rastin më të keq kjo është **O(b^d)**, njësoj si koha. Kjo është dobësia kryesore e BFS:

| | BFS (kjo detyrë) | DFS (detyra 1) |
|---|---|---|
| Memoria | O(b^d): një nivel i tërë i pemës | O(d): vetëm rruga aktuale |
| Hard, në praktikë | rradha arrin **356 812** grid-a | do të ruante vetëm 60 nivele |

Me rreth 130 bytes për grid, 356 812 grid-a zënë afërsisht 46 MB. Kjo është ende e pranueshme, por rritet shpejt me vështirësinë e puzzle-it. Pikërisht për këtë arsye ekziston kufiri `MAX_GENERATED`.

### 11.4 Ndikimi i kontrollit të kufizimeve

Pa kontrollin e kufizimeve, BFS do të duhej të gjeneronte 9^60 ≈ 1.79 × 10⁵⁷ gjethe për Hard. Me kontrollin, gjeneron vetëm **2 068 781 nyje**. Çdo vlerë që shkel C1–C3 nuk krijohet fare, kështu e gjithë nënpema e saj nuk ekziston.

### 11.5 Kompleksiteti teorik kundrejt statistikave reale

| Niveli | Kufiri teorik 9^k | Nyje reale |
|---|---|---|
| Easy | 8.72 × 10⁴² | 69 |
| Medium | 4.63 × 10⁴⁸ | 4 632 |
| Hard | 1.79 × 10⁵⁷ | 2 068 781 |

Formulat teorike supozojnë që çdo qelizë ka 9 vlera të mundshme dhe që asnjë degë nuk pritet. Në praktikë, numrat e dhënë dhe kontrolli i kufizimeve e ngushtojnë domenin shumë. Te Easy, shumica e qelizave kanë vetëm një vlerë të lejuar kur u vjen radha, prandaj pema është pothuajse një rrugë e vetme.

---

## 12. Përfundimi

- Sudoku u modelua si CSP me variablat X(r,c) për qelizat e zbrazëta, domenin {1, …, 9} dhe kufizimet e rreshtit, kolonës, kutisë dhe numrave të dhënë.
- Funksioni objektiv f(S) numëron konfliktet. Zgjidhje është grid-i i plotë me f(S) = 0.
- Hapësira naive është 9^k: nga 8.72 × 10⁴² (Easy) deri në 1.79 × 10⁵⁷ (Hard).
- BFS me backtracking i zgjidhi të tri nivelet. Të tri zgjidhjet u verifikuan me validim të pavarur, dhe u dëshmua që secili puzzle ka saktësisht një zgjidhje.
- Meqë zgjidhja është gjithmonë në nivelin e fundit të pemës, BFS e gjen atë vetëm pasi t'i ketë eksploruar të gjitha nivelet. Kostoja kryesore është memoria: te Hard, rradha arrin 356 812 grid-a.

BFS është i plotë dhe gjen gjithmonë zgjidhjen nëse ajo ekziston, por përparësia e tij kryesore, gjetja e zgjidhjes më të cekët, nuk ka vlerë te Sudoku-ja, sepse të gjitha zgjidhjet janë në të njëjtën thellësi. Për këtë lloj problemi, DFS do të përdorte shumë më pak memorie, dhe teknikat CSP si *forward checking* ose *minimum remaining values* do ta zvogëlonin pemën edhe më shumë.

---

## 13. Referencat

1. S. Russell, P. Norvig, *Artificial Intelligence: A Modern Approach*, 3rd ed., Kapitulli 3 (Solving Problems by Searching) dhe Kapitulli 6 (Constraint Satisfaction Problems).
2. Z. Michalewicz, D. B. Fogel, *How to Solve It: Modern Heuristics*, 2nd ed., Springer, 2004, Kapitujt 1–3.
3. N. Musliu, *Uninformed Search*, TU Wien: http://www.dbai.tuwien.ac.at/staff/musliu/ProblemSolvingAI/Class2UninformedSearch.pdf
4. N. Musliu, *Basic Concepts of Problem Solving*, TU Wien: http://www.dbai.tuwien.ac.at/staff/musliu/ProblemSolvingAI/class1BasicConcepts.pdf
5. *Sudoku*, Wikipedia: https://en.wikipedia.org/wiki/Sudoku
6. "Can You Solve the Hardest-Ever Sudoku?", ABC News, qershor 2012: https://abcnews.go.com/blogs/headlines/2012/06/can-you-solve-the-hardest-ever-sudoku
7. *Mathematics of Sudoku*, Wikipedia: https://en.wikipedia.org/wiki/Mathematics_of_Sudoku
8. Sudoku Space: http://www.sudoku-space.com/sudoku.php