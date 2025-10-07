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

4. Pentru a persista ieșirea, indicați în conversație calea locală sau URL-ul FTP
   dorit, de exemplu:

   ```text
   Te rog salvează raportul în `~/rapoarte/genetic_health.txt`.
   ```

   Pentru FTP, specificați un URL de forma `ftp://exemplu.ro/rapoarte/raport.txt` și,
   dacă este necesar, furnizați și credențiale ori un director în care să fie plasat
   fișierul.

## Testare

Pachetul include teste unitare pentru instrumentele de parsare și pentru generarea
rapoartelor tematice. Rulați testele cu:

```bash
pytest
```

## Date de exemplu

Directorul `sample_data/` conține un fișier VCF adnotat sintetic care acoperă câteva gene
uzuale (MTHFR, FTO, ACTN3, COMT, VDR, IL6, SOD2) pentru a demonstra comportamentul agentului.
