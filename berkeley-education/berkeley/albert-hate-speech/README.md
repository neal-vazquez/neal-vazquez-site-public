# Hate Speech Classification with ALBERT

A Fall 2023 UC Berkeley DATASCI 266 team project comparing text-classification approaches on a labeled comment dataset.

**Team:** Cynthia Rosales and Neal Vazquez. This is collaborative coursework, not a deployed moderation system.

[Project report](Hate_Speech_Classification_Albert.pdf) · [Recorded notebook](Hate_Speech_Classification_Albert.ipynb) · [Neal's professional background](https://neal-vazquez.com/consulting/resume)

## Reviewer guide

The notebook includes random forest, logistic regression, CNN-LSTM, and ALBERT experiments. The section labeled “Linear Regression” actually uses scikit-learn's `LogisticRegression`.

| Component | What the notebook contains |
| --- | --- |
| Source data | A reference to Kaggle's `subhajeetdas/hate-comment` dataset; local input named `hate.csv` |
| Binary labels | Dataset labels `N` and `P` mapped to 0 and 1; invalid labels excluded |
| ALBERT | `albert-base-v2`, two epochs, maximum sequence length 512, batch size 6, four-step gradient accumulation |
| ALBERT split | An 80% row sample with `random_state=42`; remaining rows used for validation and final evaluation |
| Artifacts | Original PDF report and notebook with recorded outputs |

The full raw dataset is not included as a separate file. Notebook outputs contain sample comments from the research dataset, including offensive language. Those examples are study material, not statements by the project authors.

## Recorded ALBERT result

The notebook's saved Testing Summary reports:

| Metric | Recorded value |
| --- | ---: |
| Accuracy | 0.787956 |
| Precision | 0.726719 |
| Recall | 0.872746 |
| F1 | 0.793067 |

These are outputs of the historical notebook, not a new run or independently reproduced result. Precision, recall, and F1 in the final summary are recalculated from all collected predictions and labels. They are not the earlier per-batch averages.

## Evaluation limits

- **Validation and testing reuse the same partition.** The ALBERT loop evaluates `test_dataloader` after each epoch and again at the end. This is not a separate untouched test set.
- **Preprocessing differs across experiments.** In the earlier model path, word-frequency selection and tokenizer fitting occur before the split. That exposes vocabulary information from held-out rows. The ALBERT path splits before its separate cleaning and tokenization.
- **Baseline inputs need care.** The random forest and logistic regression receive padded token-index sequences, not TF-IDF features. Their scores are not a comparison against a tuned TF-IDF baseline.
- **The ALBERT ROC plot uses hard predictions.** Its curve does not characterize score-based ranking across thresholds.
- **Generalization remains unestablished.** This notebook does not establish performance on independent platforms, languages, dialects, or populations. Dataset labels are an operational research target, not a complete account of context or intent.

A stronger evaluation would fit learned preprocessing only on training data, use distinct train/validation/test partitions, check duplicates and label provenance, compare a tuned text baseline, and report errors and uncertainty across relevant groups. These are proposed improvements, not completed experiments.

## Reproduction status

The original notebook targets Google Colab, mounts Google Drive, uses local dataset and FastText-vector paths, and includes unpinned installation cells. Exact historical package versions are not recorded in this repository. It should therefore be treated as a recorded research artifact, not a verified one-command installation.

To inspect the work, open the PDF and notebook. Rerunning requires obtaining the source data and vectors, reviewing their terms, adjusting paths, and resolving a compatible environment. No retraining was performed for this documentation update.

## Scope and authorship

The model is for coursework and research review. The artifacts do not establish suitability for automated enforcement or decisions about people. Preserve team credit when describing the work. This September 2026 documentation review was prepared with ChatGPT assistance; the original report and notebook remain unchanged.

## Contact

For questions about Neal's contribution, use [his website](https://neal-vazquez.com/consulting#contact-form). Team authorship is credited above.
