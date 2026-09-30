# ⚡ NovaWatt Analytics — plateforme décisionnelle d'un fournisseur d'électricité

> **Projet en construction (étape 1/6).** Le README final « recruteur » arrive à l'étape 6.

**NovaWatt** est un fournisseur d'électricité verte **fictif**. Ce projet construit sa plateforme
analytique pour répondre à la question de sa direction :

> *« On gagne des clients, mais est-ce qu'on gagne de l'argent ? Quels clients acquérir,
> lesquels perd-on, et pourquoi ? »*

Indicateurs : **MRR**, **cohortes de rétention**, **CAC**, **churn**, **LTV/CAC** et **marge par client**
calculée à partir du coût et du contenu carbone **réels** de l'électricité, heure par heure.

## Données

| Source | Type | Contenu |
|---|---|---|
| [RTE éCO2mix](https://odre.opendatasoft.com/explore/dataset/eco2mix-national-cons-def/) | Réelle | Consommation France, production par filière, taux de CO₂ (pas de 30 min) |
| [Open-Meteo](https://open-meteo.com/) | Réelle | Température moyenne journalière de 8 grandes villes |
| Générateur Python (`generator/`) | Simulée | Clients, contrats, factures, dépenses marketing |

Les données clients sont **simulées** : aucune entreprise ne publie ses données clients (RGPD).
Le générateur est piloté par les données réelles (un hiver froid augmente les factures et les résiliations).

## Architecture

```
API RTE éCO2mix ─┐                                  ┌─ staging ─ intermediate ─ marts ─┐
                 ├─► extract ─► landing (JSON) ─► DuckDB (raw) ─► dbt ─────────────────────► Streamlit
API Open-Meteo ──┘                                  └──────── tests & documentation ───┘
Générateur ─────────────────────────────────────────┘
```

## Feuille de route

- [x] **1. Ingestion** RTE + météo → DuckDB, tests unitaires, CI
- [ ] **2. Générateur** de clients, contrats, factures, marketing
- [ ] **3. dbt staging** : sources, nettoyage, dictionnaire de données
- [ ] **4. dbt marts** : MRR, cohortes, CAC, churn, marge (SQL avancé)
- [ ] **5. Dashboard** Streamlit en ligne
- [ ] **6. Note de synthèse** managériale + README final

## Lancer l'étape 1

```bash
cp .env.example .env              # Windows : copy .env.example .env
python -m venv .venv
source .venv/bin/activate         # Windows : .venv\Scripts\activate
pip install -r requirements.txt

pytest -v                         # tests (API simulées)
python -m ingestion.extract       # API -> data/landing/*.json
python -m ingestion.load_raw      # JSON -> DuckDB (schéma raw) + contrôles qualité
```

Explorer la base :

```bash
python -c "import duckdb; print(duckdb.connect('data/novawatt.duckdb').sql('SELECT * FROM raw.eco2mix LIMIT 5'))"
```

## Structure

```
ingestion/      extraction API + chargement DuckDB (étape 1)
generator/      données clients simulées (étape 2)
dbt_novawatt/   modélisation dbt (étapes 3-4)
app/            dashboard Streamlit (étape 5)
docs/           règles de gestion, dictionnaire, note de synthèse
tests/          tests unitaires Python
```
