# devops-azure-governance

scripts to manage azure: subscription, policy, policy initiatives

## Project structure

* `src/.env/prod`
  * contiene variabili di ambiente
* `src/policty` contiene i file terraform per poter creare e gestire le policy

## Glossario

* Policy set = Policy initiatives

## Policy Logica e struttura

Le policy sono state cosi divise:

## Policy trasversali Root SL Pagamenti e servizi

Attualmente viene applicata la policy `Inherith tag from Subscription if not exist`,
per semplificare l'utilizzo della regola visto che doveva essere applicata più volta sia è scelto
di creare delle regole custom che avessero già dentro di se il tag da controllare.

Attulamente i tags scelti sono:

```js
tags_subscription_to_inherith = [
  "CreatedBy",
  "Environment",
  "Owner",
  "Source",
  "CostCenter",
  "BusinessUnit",
]
```

## Policy per ambiente

Visto l'utilizzo dei management groups con la logica di raggruppamento per ambiente, si è scelto la logica di creare due tipologie di policy set:

* **enforced**: raccoglitore di policy che avranno un effetto di tipo imperativo sulle risorse associate, vietando la creazione o l'aggiornamento di tutte quelle risorse che non rispettino le regole indicate
* **advice**: raccoglitore di policy che servono solo come consultazione, questo si è reso necessario nel caso in cui si voglia introdurre una nuova policy ma non si voglia forzare la mano per la sua attuazione

## Policy attivate di tipo Enforced

* `allowed locations`:`/providers/Microsoft.Authorization/policyDefinitions/e56962a6-4747-49cd-b67b-bf8b01975c4c`
  * Verifica se la risorsa viene creata nella region definita

## Policy attivate di tipo Advice

* `allowed sku vm`:`/providers/Microsoft.Authorization/policyDefinitions/cccc23c7-8427-4f53-ad12-b6a63eb452b3`
  * Verifica che le VM o scale set abbiano lo sku impostato

* `tag inherith form subscription`:`/providers/microsoft.authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c`
  * Tutte le risorse contenute all'interno della subscription ereditano un determinato tag.

## Terraform

### How to use it

```bash
sh terraform.sh apply prod
```

## Azure policy docs

[Policy structure definition](https://docs.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure?WT.mc_id=Portal-Microsoft_Azure_Policy)
