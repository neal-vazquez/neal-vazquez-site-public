"""Build a self-contained teaching notebook from the tested SQL source files.

The generated notebook uses Python's standard library. Kaggle/Jupyter provide
the notebook interface; no data download, account secret, or GPU is required.
"""
import argparse
import contextlib
import io
import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'notebooks' / 'contact-center-metrics.ipynb'
EXAMPLE = ROOT / 'examples' / 'contact-center'


def build():
    cells = []

    def add(kind, text):
        cell = {'cell_type': kind, 'id': f'cell-{len(cells):02d}',
                'metadata': {}, 'source': textwrap.dedent(text).strip() + '\n'}
        if kind == 'code':
            cell.update(execution_count=None, outputs=[])
        cells.append(cell)

    add('markdown', '''
        # Your contact-center dashboard may be lying to you
        ## Three SQL traps in average handle time and first-contact resolution

        A dashboard can contain perfectly valid SQL and still answer the wrong
        question. This notebook uses **11 invented contacts** to show how an
        innocent-looking denominator, an average of averages, or an incomplete
        follow-up window changes the story.

        **You will build:** a queue-level report with defensible AHT and FCR
        definitions, then deliberately break the assumptions and inspect the result.

        **Run all cells in order.** Python 3.10+ and SQLite 3.25+ are sufficient.
        No downloads, package installation, GPU, network access, or private data.
        All results describe this tiny synthetic fixture, not a client or employer.

        Project direction: Neal Vazquez. Notebook, SQL and checks developed with
        ChatGPT assistance. This notebook extends the
        [public SQL case study](https://github.com/neal-vazquez/neal-vazquez-site-public/tree/main/examples/contact-center).
    ''')
    add('markdown', '''
        ### 1. Define the question before the query

        Which queue warrants investigation, and do we have enough evidence to
        compare performance? AHT means average handle time. FCR means first-contact
        resolution; here it is a **seven-day operational proxy**, not a survey measure.

        | Quantity | Definition in this exercise |
        | --- | --- |
        | Contact | One logical contact after upstream deduplication and transfer consolidation |
        | AHT | Known handle seconds / handled contacts with known duration |
        | First contact | Earliest handled contact for a case across all observed history |
        | Eligible FCR case | First contact in the reporting period, with a complete seven-day observation window |
        | FCR numerator | Eligible cases marked resolved at first contact, with no handled repeat within seven days |
        | Pending | Seven-day follow-up not complete; not a resolved or failed case yet |

        Reporting: **September 1 through September 9, 2026, UTC**. Observations
        stop strictly before September 16 at 00:00 UTC. Repeats after the reporting
        period can still change the outcome of cases that started during it.
    ''')
    add('code', '''
        import json
        import sqlite3
        from statistics import mean

        assert sqlite3.sqlite_version_info >= (3, 25, 0), 'SQLite window functions required'
        PARAMS = {
            'start_at': '2026-09-01 00:00:00',
            'end_at': '2026-09-10 00:00:00',
            'as_of': '2026-09-16 00:00:00',
        }

        def show_table(rows, columns=None):
            if not rows:
                print('(no rows)')
                return
            columns = columns or list(rows[0])
            print(' | '.join(columns))
            print(' | '.join('---' for _ in columns))
            for row in rows:
                print(' | '.join('NULL' if row.get(c) is None else str(row[c]) for c in columns))
    ''')
    for name, filename in [('SCHEMA_SQL', 'schema.sql'), ('FIXTURE_SQL', 'fixture.sql')]:
        add('code', name + ' = ' + repr((EXAMPLE / filename).read_text(encoding='utf-8')))
    add('code', '''
        def connect():
            db = sqlite3.connect(':memory:')
            db.row_factory = sqlite3.Row
            db.executescript(SCHEMA_SQL)
            db.executescript(FIXTURE_SQL)
            return db

        db = connect()
        show_table([dict(r) for r in db.execute('SELECT * FROM contacts ORDER BY started_at, contact_id')])
    ''')
    add('markdown', '''
        ### 2. Keep contact counts and case outcomes at their own grains

        The query below ranks the complete observed case history **before**
        selecting the reporting cohort. It aggregates contact metrics and case
        outcomes separately, then joins the two summaries at queue grain.
        `NOT EXISTS` detects repeats without multiplying rows and inflating totals.

        A repeat exactly seven days later counts. A first contact whose seven-day
        boundary equals the exclusive observation cutoff remains pending. Tied
        contact timestamps use ID order for deterministic selection; the data
        cannot establish an actual within-timestamp order.
    ''')
    add('code', 'METRICS_SQL = ' + repr((EXAMPLE / 'queue_metrics.sql').read_text(encoding='utf-8')) + '\nprint(METRICS_SQL)')
    add('code', '''
        def report(connection, params=None):
            params = PARAMS if params is None else params
            if not params['start_at'] < params['end_at'] <= params['as_of']:
                raise ValueError('Require start_at < end_at <= as_of in canonical UTC format')
            return [dict(row) for row in connection.execute(METRICS_SQL, params)]

        rows = report(db)
        show_table(rows, ['queue', 'handled_contacts', 'timed_contacts',
                          'aht_seconds', 'eligible_cases', 'fcr_cases', 'fcr_pct', 'pending_cases'])
        assert rows[0]['aht_seconds'] == 324
        assert rows[1]['aht_seconds'] == 660
        assert sum(r['offered_contacts'] for r in rows) == 10
    ''')
    add('markdown', '''
        ### Trap 1: Missing duration is not zero duration

        Technical handled four contacts, but one duration is unknown. Dividing
        known seconds by all four contacts silently treats the missing value as
        zero. The observed-duration AHT uses three contacts and reports coverage.

        Excluding the missing duration does **not** prove that 660 seconds is an
        unbiased estimate of all technical contacts. The sensitivity calculation
        below makes the missing-value assumption explicit.
    ''')
    add('code', '''
        technical = next(r for r in rows if r['queue'] == 'technical')
        observed_aht = technical['total_handle_seconds'] / technical['timed_contacts']
        zero_imputed_aht = technical['total_handle_seconds'] / technical['handled_contacts']
        print(f'Observed-duration AHT: {observed_aht:.0f}s (3 of 4 contacts)')
        print(f'Silent zero-imputation: {zero_imputed_aht:.0f}s')
        print(f'Difference relative to observed-duration AHT: {100 * (zero_imputed_aht / observed_aht - 1):.1f}%')
        sensitivity = [{'assumed_missing_seconds': missing,
                        'all_four_contact_aht': (technical['total_handle_seconds'] + missing) / 4}
                       for missing in [0, 300, 660, 1200]]
        show_table(sensitivity)
        assert (observed_aht, zero_imputed_aht) == (660, 495)
    ''')
    add('markdown', '''
        ### Trap 2: Averaging queue averages changes the unit of analysis

        Each queue does not contain the same number of timed contacts. If the
        target is the average **contact**, reconstruct it from total seconds and
        total timed contacts. An equal-weight queue mean answers a different question.
    ''')
    add('code', '''
        weighted_aht = sum(r['total_handle_seconds'] for r in rows) / sum(r['timed_contacts'] for r in rows)
        unweighted_aht = mean(r['aht_seconds'] for r in rows)
        print(f'Contact-weighted AHT: {weighted_aht:.0f}s')
        print(f'Equal-weight queue mean: {unweighted_aht:.0f}s')
        print(f'Overstatement for the contact-level question: {100 * (unweighted_aht / weighted_aht - 1):.2f}%')
        assert (weighted_aht, unweighted_aht) == (450, 492)
    ''')
    add('markdown', '''
        ### Trap 3: An incomplete observation window is not a success

        Billing has one recent first contact that is still pending. Calling it
        resolved too early changes the denominator and numerator. Technical has
        a repeat contact after the reporting period that must still affect FCR.

        These are counterfactual edits to an in-memory copy of invented data.
        They demonstrate measurement failure, not a causal business intervention.
    ''')
    add('code', '''
        billing = next(r for r in rows if r['queue'] == 'billing')
        print(f"Billing mature-case FCR: {billing['fcr_cases']}/{billing['eligible_cases']} = {billing['fcr_pct']}%; pending: {billing['pending_cases']}")
        print('Prematurely counting the pending case as resolved: 3/4 = 75%')

        altered = connect()
        altered.execute("DELETE FROM contacts WHERE contact_id = 'c10'")
        incomplete = next(r for r in report(altered) if r['queue'] == 'technical')
        altered.close()
        print(f"Technical with complete follow-up: {technical['fcr_pct']}%")
        print(f"Technical with the later repeat omitted: {incomplete['fcr_pct']}%")
        assert incomplete['offered_contacts'] == technical['offered_contacts']
        assert incomplete['fcr_cases'] == technical['fcr_cases'] + 1

        boundary_rows = report(db, {**PARAMS, 'as_of': '2026-09-16 11:00:00'})
        later_rows = report(db, {**PARAMS, 'as_of': '2026-09-16 11:00:01'})
        assert boundary_rows[0]['pending_cases'] == 1
        assert later_rows[0]['pending_cases'] == 0
        print('Maturity boundary verified: equality remains pending; one second later it is eligible.')
    ''')
    add('markdown', '''
        ### 3. Make the business conclusion as careful as the SQL

        Technical has higher observed AHT and lower FCR in this fixture. That
        warrants investigation, not a ranking of agent quality. There are only
        three mature cases per queue, one missing duration, and no adjustment
        for case complexity, routing, or channel mix.

        | Tempting claim | What the evidence actually supports |
        | --- | --- |
        | Technical agents are slower | Observed timed contacts in Technical take longer in this invented sample |
        | Cutting AHT improves service | No intervention or customer-experience outcome was measured |
        | No repeat means resolved | Only within this observation window, linkage system, and explicit resolution proxy |
        | A zero rate and missing rate are equivalent | An empty denominator yields NULL, which preserves uncertainty |

        In a real analysis, investigate same-issue repeats and missing durations,
        compare like cases, and evaluate resolution and customer experience
        alongside handle time. Late ingestion needs a completeness watermark
        and cohort restatement. This exercise does not model detailed transfer
        legs, source revisions, business-hour calendars, or causal effects.
    ''')
    add('code', '''
        unknown_durations = connect()
        unknown_durations.execute('UPDATE contacts SET handle_seconds = NULL WHERE handled = 1')
        assert all(r['aht_seconds'] is None for r in report(unknown_durations))
        unknown_durations.close()
        empty = connect()
        empty.execute('DELETE FROM contacts')
        assert report(empty) == []
        empty.close()
        db.close()
        print('All notebook assertions passed. Unknown is preserved as unknown.')
    ''')
    add('markdown', '''
        ### Try a meaningful variation

        Change one assumption at a time: move a repeat to exactly seven days,
        place a first contact before the reporting window, or send a repeat to
        another queue. Predict the effect before running it. Case outcomes belong
        to the first handled contact's queue; contact volume belongs to the queue
        that handled each contact.

        Source, boundary tests, and reproducible build:
        [neal-vazquez-site-public](https://github.com/neal-vazquez/neal-vazquez-site-public).
        The notebook embeds the repository's synthetic fixture and SQL so it
        works offline. Its source-sync test prevents the two versions drifting.
    ''')
    return {'cells': cells, 'metadata': {
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python', 'version': '3.12'},
    }, 'nbformat': 4, 'nbformat_minor': 5}


def source_only(notebook):
    """Ignore runtime outputs while checking generated sources for drift."""
    return [(c['cell_type'], ''.join(c['source'])) for c in notebook['cells']]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--execute', action='store_true', help='Execute the trusted generated Python cells and save actual stdout')
    args = parser.parse_args()
    expected = build()
    if args.check:
        actual = json.loads(TARGET.read_text(encoding='utf-8'))
        if source_only(actual) != source_only(expected):
            raise SystemExit('Notebook source drift: run python scripts/build_contact_center_notebook.py')
        print('Notebook sources match the current SQL and fixture.')
    else:
        if args.execute:
            scope = {'__name__': '__main__'}
            execution_count = 0
            for cell in expected['cells']:
                if cell['cell_type'] != 'code':
                    continue
                execution_count += 1
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exec(compile(cell['source'], '<generated-notebook>', 'exec'), scope)
                cell['execution_count'] = execution_count
                if output.getvalue():
                    cell['outputs'] = [{'output_type': 'stream', 'name': 'stdout', 'text': output.getvalue()}]
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(json.dumps(expected, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        print(TARGET.relative_to(ROOT))


if __name__ == '__main__':
    main()
