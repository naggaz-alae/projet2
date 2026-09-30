# Projet dbt (étapes 3-4)

Modélisation en couches sur DuckDB :

- `models/staging/` : une vue nettoyée par source (`stg_rte__eco2mix`, `stg_app__clients`…)
- `models/intermediate/` : calculs réutilisables (`int_clients_mois`, `int_cout_horaire_profil`…)
- `models/marts/core/` : modèle en étoile (`fct_factures_mensuelles`, `dim_clients`…)
- `models/marts/business/` : indicateurs (`mrr_mensuel`, `retention_cohortes`, `cac_par_canal`, `marge_client`…)
- `seeds/` : offres, canaux, hausses de prix
- `tests/` : tests métier (ex. bouclage du MRR, règle RG-05)
