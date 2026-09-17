# Model Card

## Model summary

This repository fine-tunes `albert-base-v2` with a two-class sequence-classification head for positive versus negative movie-review phrase classification.

| Attribute | Value |
|---|---|
| Architecture | ALBERT transformer encoder |
| Base checkpoint | `albert-base-v2` |
| Framework | PyTorch and Hugging Face Transformers |
| Output | Negative or positive |
| Sequence limit | 65 tokens |
| Weights distributed | No |
| Status | Historical portfolio experiment |

## Intended use

The project is intended for:

- learning and demonstrating transformer fine-tuning;
- examining binary sentiment classification;
- comparing evaluation choices and their consequences; and
- serving as a transparent portfolio artifact.

It is not intended to support consequential decisions about people or to serve as a deployable moderation, employment, healthcare, education, credit, or safety system.

## Training data

The historical notebook uses phrase-level movie-review sentiment from Kaggle's *Sentiment Analysis on Movie Reviews* competition. Original labels 0 and 1 are mapped to negative, labels 3 and 4 are mapped to positive, and neutral label 2 is removed.

See [DATA_CARD.md](DATA_CARD.md) for lineage and limitations.

## Historical training configuration

- Optimizer: AdamW
- Learning rate: 2e-5
- Epochs: 2
- Batch size: 12
- Maximum sequence length: 65
- Scheduler: linear decay with no warmup
- Gradient clipping: 1.0

## Recorded evaluation

| Metric | Held-out phrase split |
|---|---:|
| Accuracy | 93.79% |
| Precision | 94.91% |
| Recall | 93.69% |
| F1 | 94.30% |
| Loss | 0.275 |

These are recorded outputs from one notebook run. No trained checkpoint is published, and the repository does not claim an independently reproduced benchmark.

## Limitations

### Split leakage risk

The historical split is random at the phrase level. Phrases derived from the same `SentenceId` can therefore appear in both training and held-out data. This may overstate generalization.

### Reproducibility

The dataframe split is fixed, but the historical notebook does not seed every stochastic component. Model initialization, sampling, and hardware behavior can produce different results.

### Benchmark scope

The input domain is movie-review language. Performance does not establish robustness for social media, customer feedback, workplace communication, clinical text, or other domains.

### Label compression

Binary polarity erases neutrality and compresses ambiguity, mixed sentiment, sarcasm, and context. A prediction is a task-specific estimate, not a complete account of meaning.

### Missing comparisons

The historical experiment does not include a classical baseline, statistical confidence intervals, calibration analysis, external validation, or systematic error slices.

## Recommended validation before reuse

1. Split by `SentenceId`.
2. Add deterministic seeds and recorded environment metadata.
3. Compare against majority-class and TF-IDF baselines.
4. Report class balance and per-class error.
5. Evaluate calibration and threshold sensitivity.
6. Inspect errors involving negation, irony, short phrases, and domain shift.
7. Validate on genuinely independent data.
8. Document a human-review and rollback strategy for any deployed application.

## Ethical considerations

Sentiment systems can mistake dialect, bluntness, disagreement, or culturally specific expression for negative affect. In consequential settings, such errors can become disparate treatment. Any real deployment should begin with a concrete use case, affected-user analysis, subgroup testing where lawful and appropriate, monitoring, and a clear decision about when the model must not be used.
