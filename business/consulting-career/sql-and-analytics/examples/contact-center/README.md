# Contact-center operations: useful metrics need defensible denominators

**Question:** Which queue warrants investigation, and can we trust the apparent difference in performance?

This standalone SQL exercise uses 11 invented contacts across two queues. It contains no employer or customer data and makes no claim about an actual organization's performance. Run from the repository root:

```bash
python scripts/contact_center.py
python -m unittest discover -s tests -v
```

Read the [query](queue_metrics.sql), [schema](schema.sql), [fixture](fixture.sql), and [tests](../../tests/test_contact_center.py). The website's historical SQL and schema are separate.

## Reproduced result

Reporting period: September 1 through September 9, 2026, UTC. Follow-up is observed strictly before September 16 at 00:00 UTC. Ten contacts fall in the reporting period; one later contact contributes follow-up evidence only.

| Queue | Offered | Handled | Timed | AHT, seconds | Eligible first-contact cases | FCR cases | FCR proxy | Pending cases |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Billing | 6 | 5 | 5 | 324 | 3 | 2 | 66.67% | 1 |
| Technical | 4 | 4 | 3 | 660 | 3 | 1 | 33.33% | 0 |

Technical has the larger observed AHT and lower FCR proxy. That is a diagnostic signal in this fixture, not evidence that its agents are less effective. Issue complexity, routing, channel mix, and missing duration data could explain the difference. Three eligible cases per queue cannot support a reliable performance ranking.

**Business interpretation:** investigate repeat-contact reasons and routing within comparable issue categories before setting an AHT reduction target. Validate the missing technical handle time first. Assess whether a proposed change improves resolution and customer experience alongside handle time; use a controlled comparison before claiming an effect. These are proposed investigative steps, not measured improvements.

## Metric contract

| Metric or grain | Definition |
| --- | --- |
| Contact | One logical contact, after upstream deduplication and transfer-leg consolidation; primary key rejects duplicate IDs. |
| Offered contacts | Contacts starting in the half-open reporting window `[start_at, end_at)`. This simplified exercise has only handled and abandoned outcomes. |
| AHT | Sum of known handle seconds divided by the number of handled contacts with known duration. Handle time represents talk + hold + after-contact work. Unknown durations remain missing, with their count reported. |
| Case | One issue, identified by a synthetic `case_id`. Correct same-issue linkage and complete earlier contact history are upstream requirements. |
| First contact | Earliest handled contact per case across all observed history, using `ROW_NUMBER`. Cohort membership is then restricted to the reporting window. |
| Eligible case | First contact occurred in the reporting period, and its entire seven-day follow-up interval is before the exclusive observation cutoff. |
| FCR proxy | Eligible cases whose first contact is marked resolved and has no further handled contact for the same issue within seven days, divided by all eligible cases. This operational proxy is not survey-confirmed resolution or a universal FCR definition. |
| Queue attribution | Contact metrics use each contact's queue. Case outcomes use the first handled contact's queue, including repeats in other queues. |

An abandoned attempt is reported in volume but does not establish a first handled contact or disqualify this handled-contact FCR proxy. Distinct contacts at the same timestamp are treated as repeats; ID order makes selection deterministic but cannot reconstruct actual order within a tied timestamp. A follow-up exactly seven days later counts as a repeat. A follow-up after the reporting period still affects FCR when it is within that interval. Records at or after the observation cutoff are excluded.

No complete follow-up means **pending**, not resolved. No eligible cases or no known handle times yields `NULL`, not a fabricated zero rate. Missing queue rows mean no offered contacts in this fixture; an operational dashboard would need a queue dimension and collection-health evidence to distinguish inactivity from missing ingestion.

## SQL design and common traps

1. Filter by the observation cutoff, then rank full case history. Filtering to the reporting period before ranking would turn old cases into false first contacts.
2. Aggregate contacts and case outcomes separately before joining at queue grain. Joining raw contacts to multiple follow-ups would multiply handle time and volume.
3. Use `NOT EXISTS` to test repeat contact without creating that join fan-out. The `(case_id, started_at, contact_id)` index supports case/time lookup; a small fixture establishes correctness, not production-scale performance.
4. Carry numerators and denominators through the report. Overall AHT is `3600 / 8 = 450` seconds, not the unweighted average of queue averages, `492`. Overall FCR is `3 / 6 = 50%`; recompute it from counts even when averaging percentages happens to match.
5. Expose missingness and maturity alongside the headline rates. A single missing technical duration means its AHT covers three of four handled contacts.

Parameters must be canonical UTC `YYYY-MM-DD HH:MM:SS` values with `start_at < end_at <= as_of`. This example assumes complete observations and stable case linkage through that cutoff. Late ingestion requires a data-completeness watermark and restated cohorts. It does not model source revisions, detailed transfer legs, business-hour calendars, CSAT, or causal effects.
