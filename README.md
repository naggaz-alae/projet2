# NovaWatt Analytics

Projet perso pour mon portfolio data. NovaWatt est un fournisseur d'électricité verte inventé, et
l'idée est de lui construire un petit outil d'analyse pour répondre à une question simple :
on gagne des clients, mais est-ce qu'on gagne vraiment de l'argent avec ?

Au final je veux pouvoir suivre le chiffre d'affaires mensuel (MRR), la rétention par cohorte,
le coût d'acquisition (CAC), le churn et la marge par client. La marge sera calculée avec le vrai
prix et le vrai taux de CO₂ de l'électricité en France, heure par heure.

Le projet est en cours : pour l'instant seule la première étape (l'ingestion des données) est faite.

## Les données

- **RTE éCO2mix** (données réelles) : consommation en France, production par filière et taux de CO₂, toutes les 30 minutes.
  [Lien vers le jeu de données](https://odre.opendatasoft.com/explore/dataset/eco2mix-national-cons-def/)
- **Open-Meteo** (données réelles) : température moyenne par jour dans 8 grandes villes françaises.
- **Données clients** (simulées) : clients, contrats, factures et dépenses marketing. Aucune
  entreprise ne publie ce genre de données, donc je les génère moi-même. Elles dépendent quand même
  des données réelles : par exemple un hiver froid fait monter les factures et les résiliations.

## Comment ça marche

```
API RTE + API Open-Meteo  ->  fichiers JSON  ->  DuckDB  ->  dbt  ->  dashboard Streamlit
Générateur de clients     ------------------->  DuckDB
```

Les réponses des API sont d'abord enregistrées telles quelles en JSON, ce qui permet de recharger
la base sans tout retélécharger. Elles sont ensuite chargées dans DuckDB, puis transformées avec dbt.

## Avancement

1. Ingestion des données RTE et météo dans DuckDB, avec tests et CI : **fait**
2. Générateur de données clients : à faire
3. Nettoyage des données avec dbt : à faire
4. Calcul des indicateurs (MRR, cohortes, CAC, churn, marge) : à faire
5. Dashboard Streamlit : à faire
6. Note de synthèse : à faire

## Lancer le projet

```bash
cp .env.example .env          # sous Windows : copy .env.example .env
python -m venv .venv
source .venv/bin/activate     # sous Windows : .venv\Scripts\activate
pip install -r requirements.txt

pytest -v                     # lance les tests
python -m ingestion.extract   # télécharge les données des API
python -m ingestion.load_raw  # charge les données dans DuckDB
```

Pour jeter un œil aux données chargées :

```bash
python -c "import duckdb; print(duckdb.connect('data/novawatt.duckdb').sql('SELECT * FROM raw.eco2mix LIMIT 5'))"
```

## Organisation du code

```
ingestion/      récupération des données et chargement dans DuckDB
generator/      génération des données clients (étape 2)
dbt_novawatt/   modèles dbt (étapes 3 et 4)
app/            dashboard (étape 5)
docs/           règles de calcul des indicateurs
tests/          tests unitaires
```

Les définitions des indicateurs (ce qu'on appelle un client actif, comment on compte le churn, etc.)
sont dans [docs/regles_de_gestion.md](docs/regles_de_gestion.md).
