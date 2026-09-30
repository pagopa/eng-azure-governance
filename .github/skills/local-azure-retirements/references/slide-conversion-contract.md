# Slide Conversion Contract

This reference defines deterministic grouping and conversion from aggregate
02 to slide TSV 03 for `comitato_azure_retirements_v2`.

## Input and output

- Input: `src/comitato/comitato_azure_retirements_v2/exports/YYYY/MM/02_azure_retirements_aggregate.tsv`
- Output: `src/comitato/comitato_azure_retirements_v2/exports/YYYY/MM/03_azure_retirements_slide.tsv`

## Ordered output schema

The header must contain these 19 columns in this exact order:

1. `id_elemento`
2. `titolo_breve`
3. `descrizione_breve`
4. `comitato_priorità`
5. `impatto_microsoft`
6. `comitato_descrizione`
7. `comitato_retirement_date`
8. `comitato_piattaforme`
9. `retirement_date`
10. `stato_data`
11. `giorni_ritardo`
12. `descrizione_originale_completa`
13. `azione_originale`
14. `fonti`
15. `link_fonti`
16. `ambito_impatto`
17. `id_advisor`
18. `id_service_health`
19. `risorse_json`

## Grouping and identity

- Group by `advisor-type:<recommendation_type_id>` when an Advisor type id exists.
- Otherwise group by `service-health:<tracking_id>` when a Service Health tracking id exists.
- Otherwise group by `aggregate:<aggregate_id>`.
- `id_elemento` is `azure-retirement:v2:` followed by the SHA-256 hex digest of the UTF-8 group key.
- The primary date is the earliest exact retirement date in the group, from recommendation or metadata retirement dates. When none exists, use the earliest image removal date. Exclude the group only when that date is beyond the committee window.
- Sort by primary date ascending, using `9999-99-99` when missing, then `id_elemento`.

## Projection rules

| Field | Rule |
| --- | --- |
| `titolo_breve` | First available technology or service, retiring feature, then problem title. |
| `descrizione_breve` | First problem title, then retiring feature, then technology or service. Do not add a draft prefix. |
| `comitato_priorità` | Empty. |
| `impatto_microsoft` | Highest Advisor impact: `High` → `Alto`, `Medium` → `Medio`, `Low` → `Basso`; empty for Service Health-only groups. |
| `retirement_date` | One line per date as `YYYY-MM-DD — <meaning>`, ordered by date. Updates keep only the oldest and latest date per source. |
| `stato_data` | Exactly one of `Data non disponibile`, `Date discordanti`, `Scaduta`, or `In scadenza`. More than one distinct retirement date yields `Date discordanti`; multiple image removal dates do not. |
| `giorni_ritardo` | Days between the primary date and `as_of_date` for `Scaduta` rows; empty otherwise. |
| `link_fonti` | Sorted union of the group `source_links_json` values. |
| `id_advisor` | `https://portal.azure.com/#view/Microsoft_Azure_Expert/RecommendationListBlade/recommendationTypeId/<id>` per Advisor recommendation type id. |
| `id_service_health` | `https://app.azure.com/h/<tracking_id>` per Service Health tracking id. |
| `ambito_impatto` | JSON with platform, subscription, resource, environment, service, and region counts. Environments are `PROD`, `UAT`, `DEV`, and `ALTRO`; names begin with `PROD-`, `PROD_`, `UAT-`, `UAT_`, `DEV-`, or `DEV_`, case-insensitively. Global rows use `{"globale": true}`. |
| `risorse_json` | Compact JSON grouped as platform → subscription name → resource group → resource names. Global rows use `{"ALL":"global"}`. |

Date meanings are `Data di ritiro (Azure Advisor)`,
`Data di ritiro (metadati Azure Advisor)`, `Rimozione immagine (Azure Advisor)`,
`Data di ritiro (Azure Service Health)`,
`Aggiornamento meno recente osservato (Azure Advisor)`,
`Aggiornamento meno recente osservato (Azure Service Health)`,
`Ultimo aggiornamento (Azure Advisor)`,
`Ultimo aggiornamento (Azure Service Health)`, `Avviso pubblicato il`, and
`Avviso attivo fino al`.

## Committee YAML

Live execution reads the YAML mapping by `id_elemento` before slide encoding.
It keeps `comitato_descrizione` when `descrizione_originale_completa` is
unchanged, and clears only that description when the source description changes.
It always keeps `comitato_retirement_date`, refreshes the original description,
links, and retirement date list, and drops ids absent from the run. The date
list keeps every slide date as `{data, tipo, fonte}`; `tipo` is one of
`ritiro`, `rimozione_immagine`, `avviso_inizio`, `avviso_fine`,
`aggiornamento_meno_recente`, or `ultimo_aggiornamento`. YAML `link_fonti`
omits Azure portal links, and descriptions longer than 100 characters use
folded style. Non-empty committee values fill the
slide cells. Write the YAML only after publication succeeds. Replay does not
read or write the YAML; replayed committee cells stay empty.
