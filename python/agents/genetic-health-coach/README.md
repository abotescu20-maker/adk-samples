# Genetic Health Coach Agent

Agent demonstrativ construit cu [Python Agent Development Kit](https://github.com/google/adk-python)
care analizează fișiere VCF adnotate și generează rapoarte personalizate pentru sport,
nutriție și terapii pe baza mutațiilor identificate.

## Funcționalități

* Citește un fișier VCF adnotat și extrage genele împreună cu mutațiile și metadatele
  principale (impact, efecte, genotip, HGVS).
* Construiește rapoarte tematice (sport, nutriție, terapii) ce includ argumentație și
  recomandări adaptate pentru genele identificate.
* Poate salva rapoartele rezultate local sau pe un server FTP prin intermediul
  instrumentului `persist_report`.
* Oferă un format de răspuns standardizat în limba română, cu raționament înaintea
  recomandărilor, conform cerințelor din enunț.

## Structură

```
python/agents/genetic-health-coach/
├── README.md
├── genetic_health_coach/
│   ├── __init__.py
│   ├── agent.py
│   ├── prompt.py
│   └── tools/
│       ├── __init__.py
│       ├── subject_analysis.py
│       └── vcf_parser.py
├── pyproject.toml
├── sample_data/
│   └── example_annotated.vcf
└── tests/
    └── test_tools.py
```

## Configurare

1. Instalați dependențele folosind Poetry:

   ```bash
   cd python/agents/genetic-health-coach
   poetry install
   ```

2. Copiați fișierul `.env.example` (dacă există) și setați cheia API pentru Gemini sau
   configurați autentificarea Vertex AI conform documentației ADK.

3. Rulați agentul în directorul `genetic_health_coach/` cu:

   ```bash
   adk run .
   ```

   O conversație tipică poate începe cu un prompt de genul:

   > Analizează fișierul `sample_data/example_annotated.vcf` și generează un raport pentru
   > sport, nutriție și terapii. Salvează rezultatul în `rapoarte/analiza.txt`.

4. Pentru o rulare completă direct din terminal (fără interfață web sau dialog cu agentul),
   folosiți scriptul CLI inclus în pachet:

   ```bash
   cd python/agents/genetic-health-coach
   poetry run genetic-health-coach-report sample_data/example_annotated.vcf
   ```

   Veți obține în consolă rapoartele pentru sport, nutriție și terapii în formatul cerut
   (raționament urmat de recomandări). Puteți filtra subiectele cu `-s/--subject` (de ex.
   `--subject sport --subject nutritie`), comuta ieșirea în JSON cu `--json` sau salva
   rezultatul într-un fișier folosind `--output cale/raport.txt` (directoarele se creează
   automat). Comanda `poetry run genetic-health-coach-report --list-subjects` afișează
   lista completă de subiecte acceptate.

5. Pentru a persista ieșirea, indicați în conversație calea locală sau URL-ul FTP
   dorit, de exemplu:

   ```text
   Te rog salvează raportul în `~/rapoarte/genetic_health.txt`.
   ```

   Pentru FTP, specificați un URL de forma `ftp://exemplu.ro/rapoarte/raport.txt` și,
   dacă este necesar, furnizați și credențiale ori un director în care să fie plasat
   fișierul.

## Demonstrație web locală

Pentru a testa rapid agentul într-o interfață web accesibilă prin link local,
porniți serverul HTTP inclus în proiect (nu sunt necesare dependențe externe):

```bash
cd python/agents/genetic-health-coach
poetry install
poetry run genetic-health-coach-demo
```

Apoi deschideți în browser adresa [http://localhost:8000](http://localhost:8000).
Pagina vă permite să încărcați un fișier VCF (puteți folosi exemplul din
`sample_data/example_annotated.vcf`), să bifați temele dorite și să generați
raportul direct din navigator. Rezultatul include acum un rezumat general al
genelor detectate, astfel încât să puteți vedea imediat ce mutații au fost
parcurse chiar dacă pentru unele gene nu există încă recomandări dedicate.
Pentru integrare automată, endpoint-ul `POST /api/analyze` întoarce același
rezultat în format JSON.

> Sfaturi:
> * Pentru a oferi acces altor dispozitive din aceeași rețea, porniți serverul cu `poetry run genetic-health-coach-demo --host 0.0.0.0 --port 8000` și accesați apoi linkul afișat în terminal.
> * Variabilele de mediu `GENETIC_HEALTH_COACH_HOST` și `GENETIC_HEALTH_COACH_PORT` pot fi folosite pentru a seta implicit hostul și portul atunci când porniți serverul.

### Sandbox rapid cu Docker

Dacă nu doriți să instalați dependențele local, în directorul proiectului este
disponibil un fișier `Dockerfile` împreună cu `docker-compose.yml` care
pregătesc un mediu de testare complet funcțional. Pașii sunt:

```bash
cd python/agents/genetic-health-coach
docker compose up --build
```

Comanda va construi imaginea, va instala automat dependențele și va porni
serverul demo pe portul 8000. Accesați apoi
[http://localhost:8000](http://localhost:8000) pentru a încărca propriile fișiere
VCF sau pentru a folosi exemplul inclus (`sample_data/example_annotated.vcf`).
Containerul montează directorul `sample_data/` în modul read-only, astfel încât
datele de test să fie la îndemână fără configurări suplimentare. Pentru a opri
mediul de testare, folosiți `Ctrl+C` sau rulați `docker compose down` într-un
terminal separat.

## Testare

Pachetul include teste unitare pentru instrumentele de parsare și pentru generarea
rapoartelor tematice. Rulați testele cu:

```bash
pytest
```

## Date de exemplu

Directorul `sample_data/` conține un fișier VCF adnotat sintetic care acoperă câteva gene
uzuale (MTHFR, FTO, ACTN3, COMT, VDR, IL6, SOD2) pentru a demonstra comportamentul agentului.
