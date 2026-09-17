# ALBERT Sentiment Classification

A compact transformer experiment in sentiment classification, responsible evaluation, and the difference between predictive performance and genuine generalization.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Model: ALBERT](https://img.shields.io/badge/Model-ALBERT-6B5B95)](https://arxiv.org/abs/1909.11942)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

## At a glance

| Dimension | Detail |
|---|---|
| Task | Binary sentiment classification |
| Backbone | `albert-base-v2` |
| Source data | Phrase-level movie-review sentiment from the Stanford Sentiment Treebank, distributed through Kaggle's *Sentiment Analysis on Movie Reviews* competition |
| Label design | Ratings 0-1 become negative, 3-4 become positive, and neutral rating 2 is excluded |
| Historical split | 80/20 random phrase split with `random_state=42` |
| Historical held-out result | 93.79% accuracy and 94.30% F1 |
| Status | Portfolio and research artifact, not a production model |

## Why this project matters

Text classification looks deceptively simple: map language to a label and optimize a loss function. The harder problem is deciding what the label means, what evidence the model is allowed to learn from, and whether the evaluation actually measures generalization.

This project fine-tunes ALBERT, a parameter-efficient transformer encoder, on phrase-level sentiment. It demonstrates the full modeling path from label construction and token-length analysis through tokenization, fine-tuning, metric computation, and confusion-matrix analysis. It also preserves the most important lesson from the experiment: a strong score is only as credible as the split, baseline, and assumptions behind it.

## Results

The recorded notebook run reports the following metrics on its held-out phrase split:

| Metric | Score |
|---|---:|
| Accuracy | 93.79% |
| Precision | 94.91% |
| Recall | 93.69% |
| F1 | 94.30% |
| Cross-entropy loss | 0.275 |

These numbers describe one historical run. They are useful evidence that the pipeline learned the task, but they are not a production claim and should not be read as an estimate of performance on independent reviews.

## Method

1. Load Kaggle's `train.tsv` phrase-level sentiment data.
2. Convert five sentiment classes into a binary target.
3. Remove neutral phrases.
4. Inspect token-length distribution and set a maximum sequence length of 65.
5. Encode phrases with the `albert-base-v2` tokenizer.
6. Fine-tune `AlbertForSequenceClassification` for two epochs.
7. Evaluate accuracy, precision, recall, F1, loss, and the confusion matrix.

### Historical training configuration

| Parameter | Value |
|---|---:|
| Epochs | 2 |
| Batch size | 12 |
| Learning rate | 2e-5 |
| Maximum sequence length | 65 tokens |
| Optimizer | AdamW |
| Scheduler | Linear decay, no warmup |
| Gradient clipping | 1.0 |

## Evaluation integrity

The source data contains multiple phrases derived from the same full sentence. The historical notebook splits rows at the phrase level, so related fragments can appear on both sides of the split. That overlap may inflate the reported score by rewarding recognition of closely related language rather than generalization to unseen reviews.

A stronger follow-up evaluation should:

- split by `SentenceId`, not `PhraseId`;
- create distinct training, validation, and test partitions;
- seed Python, NumPy, PyTorch, and sampler behavior;
- compare ALBERT with a TF-IDF plus logistic-regression baseline;
- report class balance, class-specific metrics, confidence intervals, and calibration;
- analyze performance by phrase length, negation, ambiguity, and intensity; and
- test on an external review corpus before making deployment claims.

This limitation is documented deliberately. Technical credibility comes from making the boundary of the evidence visible.

## Reproduce the notebook

The dataset is not redistributed in this repository.

1. Use Python 3.10 or 3.11.
2. Download `train.tsv` from the [Kaggle competition data page](https://www.kaggle.com/competitions/sentiment-analysis-on-movie-reviews/data).
3. Place `train.tsv` in the repository root.
4. Create an isolated environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter lab
```

5. Open `albert-binary-text-classification-movie-reviews.ipynb` and run the cells in order.

A CUDA-capable GPU is strongly recommended. The notebook includes outputs from a completed historical run, but exact results can vary because the original experiment did not seed every stochastic component.

## Repository structure

```text
.
├── albert-binary-text-classification-movie-reviews.ipynb
├── DATA_CARD.md
├── MODEL_CARD.md
├── requirements.txt
├── LICENSE
└── README.md
```

- **Notebook:** executable analysis, training loop, evaluation, and visualizations.
- **Data card:** dataset lineage, transformation, and split limitations.
- **Model card:** intended use, metrics, limitations, and responsible-use boundaries.
- **Requirements:** compatibility set for reproducing the historical notebook.

## What I would build next

The next iteration would separate the historical artifact from a rigorously reproducible experiment. It would add a group-aware split, deterministic configuration, a classical baseline, modular training code, lightweight tests, saved evaluation artifacts, and automated checks. The goal would not be a larger headline metric. It would be a result that survives closer questioning.

## Responsible use

Movie-review polarity is a low-stakes benchmark. The same pipeline should not be transferred directly to employment, healthcare, education, credit, moderation, or other consequential settings. Sentiment labels compress context, culture, sarcasm, disagreement, and emotional ambiguity into a narrow target. In higher-stakes use, those simplifications must be treated as model risk rather than ground truth.

## Author

**Neal Vazquez**  
Data scientist working across AI, analytics, digital experience, and decision-making.  
[Portfolio](https://neal-vazquez.com) · [GitHub](https://github.com/neal-vazquez)

## License

Licensed under the [GNU General Public License v3.0](LICENSE).
