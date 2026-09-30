# Règles de gestion — NovaWatt

Chaque indicateur est défini **une seule fois**, ici, avant d'être codé.
Chaque règle sera vérifiée par un test dbt (colonne « Test »), ajouté aux étapes 3-4.

| Réf. | Règle | Test dbt |
|---|---|---|
| RG-01 | Un client est **actif** un mois donné s'il a un contrat en cours au moins un jour de ce mois. | à venir |
| RG-02 | Le **churn** est daté au jour d'**effet** de la résiliation, pas au jour de la demande. | à venir |
| RG-03 | Le **MRR** = abonnement mensuel HT + consommation facturée HT du mois. Il **exclut** les frais de mise en service et les régularisations ponctuelles. | à venir |
| RG-04 | Le **CAC** du mois M = dépenses d'**acquisition** de M ÷ nouveaux clients de M. Les dépenses de fidélisation sont exclues. | à venir |
| RG-05 | **Bouclage du MRR** : MRR(M-1) + nouveaux + expansion − contraction − churn = MRR(M). | à venir |
| RG-06 | Un client qui revient après une résiliation est compté comme **réactivation**, pas comme nouveau client ; il reste dans sa cohorte d'origine. | à venir |
| RG-07 | Pour chaque créneau de 30 min, la donnée **définitive** RTE est prioritaire sur la donnée temps réel. | à venir |
| RG-08 | Les dates RTE sont stockées en **UTC** puis converties en heure de Paris dans dbt (gestion des changements d'heure). | à venir |
