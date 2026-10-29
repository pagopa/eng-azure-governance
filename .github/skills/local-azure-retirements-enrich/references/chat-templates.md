# Chat Presentation Templates

Render the following templates in Italian. Replace placeholders with observed
facts and absolute Markdown file links. Keep service names first, omit empty
sections, and never turn an unknown result into a green status.

## Editorial Review

Use this presentation after saving and validating the YAML, before requesting
publication approval. Counts refer to distinct entry IDs; field counts may
overlap. Include one compact row per changed entry, labeling changes outside
the selected month. Summarize wording in the table rather than pasting long
descriptions. Show an actual before/after excerpt for material wording changes;
use `vuoto` for a previously empty field. Keep all date conflicts and
unverified deadlines visible.
Count changes to `comitato_fonti` separately and summarize the reference titles
and URLs retained there. Do not append them to `comitato_descrizione`; Markdown
in this chat presentation does not authorize Markdown in editorial YAML text.

```markdown
## Comitato Azure · <YYYY/MM>

**✅ YAML salvato · ⏸ Slide non aggiornate**

**<N> voci modificate** · <D> descrizioni · <S> scadenze · <F> fonti editoriali · <I> nuove voci

### Cosa è cambiato

| Servizio / tecnologia | Modifica | Prima → Dopo | Scadenza / fonte |
|---|---|---|---|
| <servizio e versione> | <descrizione, data, fonti editoriali o nuova voce> | <sintesi del cambiamento reale> | <data, fonte e stato di verifica> |

### Da tenere presente

- <eventuale data discordante, fonte non verificata o limite residuo>

### Controlli

- <esito effettivo della validazione YAML e della completezza>
- <esito del confronto: dati originali e testi già approvati preservati>
- <esito del controllo: descrizioni senza Markdown e riferimenti in comitato_fonti>
- TSV e manifest mensile non modificati.

**File:** [YAML editoriale](<absolute-yaml-path>) · [Slide da aggiornare](<absolute-tsv-path>)

**Passo successivo:** serve la tua conferma nel modulo per applicare questi
contenuti alle slide di <YYYY/MM>.
```

For a no-op, replace the change count/table with "Nessuna modifica necessaria
al YAML" and show its checked state. For a declined review, report "YAML
salvato; aggiornamento slide non eseguito". For a missing response, report
"YAML salvato; approvazione in attesa". These are editorial outcomes, not
successful slide publications.

## Approval Form

Use `ask_user` after the rendered review. The form must have no preselected
answer. This is the presentation shape, not an instruction to call the tool
while authoring or reviewing this skill.

```json
{
  "message": "Il YAML è stato salvato. Autorizzi l'aggiornamento delle slide di <YYYY/MM> con le modifiche appena riepilogate?",
  "requestedSchema": {
    "properties": {
      "decision": {
        "type": "string",
        "title": "Come vuoi procedere?",
        "oneOf": [
          {"const": "publish", "title": "Approvo: aggiorna le slide"},
          {"const": "revise", "title": "Voglio modificare i contenuti"},
          {"const": "stop", "title": "Non aggiornare le slide"}
        ]
      }
    }
  }
}
```

## Publication Result

Use this template only for verified publication. Keep the distinction between
changed YAML entries and total slide rows explicit.

```markdown
## Comitato Azure · <YYYY/MM>

**✅ Slide aggiornate**

<N> voci editoriali modificate · <R> righe slide verificate

| Controllo | Esito |
|---|---|
| Launcher locale | <exit status e risultato JSON osservati> |
| Testi e scadenze nel TSV | <esito del confronto con il YAML> |
| Altri report e dati originali | <esito effettivo del confronto> |

**Da tenere presente:** <eventuali incertezze residue sulle fonti/date>

**File:** [YAML editoriale](<absolute-yaml-path>) · [Slide aggiornate](<absolute-tsv-path>)
```
