# Runnable SQL notebooks

[**Your contact-center dashboard may be lying to you**](contact-center-metrics.ipynb)
demonstrates three measurement traps: missing handle times, averaging averages,
and immature first-contact-resolution cohorts. The notebook includes invented
data, all SQL, observed outputs, and executable assertions.

Open it in Jupyter or import the `.ipynb` into Kaggle. Use Python, CPU only,
and internet off. No external dataset or package installation is needed to run
the cells. Importing a notebook does not automatically publish it.

Suggested Kaggle description: Three SQL traps in AHT and first-contact resolution,
with synthetic data, explicit denominators, repeat-contact windows, and checks.
Suggested tags, subject to Kaggle's available tag names: SQL, business analytics,
data cleaning, education. The Kaggle account and a Kaggle publication URL have
not yet been verified.

## Maintain one source of truth

The notebook embeds the existing contact-center SQL rather than downloading
mutable files at runtime. Rebuild it when that SQL or its fixture changes:

```bash
python scripts/build_contact_center_notebook.py --execute
python scripts/build_contact_center_notebook.py --check
python -m unittest discover -s tests -v
```

The build uses only the standard library. `--execute` executes the generated
Python cells in order and saves actual stdout as notebook outputs. The existing test command executes
the notebook cells from an empty temporary directory and detects source drift.
An optional full Jupyter execution needs `nbformat`, `nbclient`, and `ipykernel`;
those packages are only for authoring and are not dependencies of the SQL demos.

All data is synthetic. The notebook credits AI assistance and makes no claims
about client outcomes, competition scores, medals, or account standing.
