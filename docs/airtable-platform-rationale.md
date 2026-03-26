# Airtable Platform Rationale

The original decision to use Airtable was reasonable.

If the priorities were:

- low-code support
- non-engineer maintainability
- built-in Interface pages
- built-in Automations
- web-based editing
- easy CRUD from scripts

then Airtable is much better aligned than Streamlit.

## Assessment

For `workflow + stewardship + review + lightweight app UI`, Airtable was the right instinct.

For `versioned canonical metadata model + safe schema evolution + repeatable rebuilds`, code/parquet/git are stronger.

The best fit for this project is the hybrid model the project moved toward:

- Airtable as the steward workspace and operational UI
- repo/parquet as the governed backbone

So the original instinct was not wrong. The main risk comes when Airtable is asked to be all of these at once:

- the UI
- the workflow engine
- the system of record
- the schema registry
- the migration layer
- the analytics layer

That is where Airtable starts to get brittle.

## CRUD And Stewardship

Airtable does support the desired operating model:

- maintain records manually in the web UI
- expose focused Interfaces to stewards
- run scripted creates/updates/deletes through the API
- use Automations for notifications, assignments, status changes, and queue movement

That part is viable.

## Design Decision

The key design decision is:

- Should Airtable be the primary authoring system?
- Or should Airtable be the steward-facing operational layer over a more controlled canonical model?

For this project, the second answer is better. It preserves the benefits of Airtable while reducing the risk of drift, accidental schema changes, and hard-to-reverse cleanup problems.

## Conclusion

The Airtable choice was strategically sound.

The improvement was not "don't use Airtable." It was:

- use Airtable for the parts it is best at
- keep the governed canonical model in repo/parquet where schema and rebuild behavior are easier to control
