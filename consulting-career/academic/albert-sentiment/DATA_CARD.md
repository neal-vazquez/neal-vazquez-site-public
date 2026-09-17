# Data Card

## Dataset

This project uses `train.tsv` from Kaggle's [Sentiment Analysis on Movie Reviews](https://www.kaggle.com/competitions/sentiment-analysis-on-movie-reviews/data) competition. The file contains phrase-level labels derived from the Stanford Sentiment Treebank.

This corrects an earlier README description that named the IMDB 50K review dataset. The notebook itself has always loaded the Kaggle `train.tsv` schema described here.

## Schema

| Field | Meaning |
|---|---|
| `PhraseId` | Identifier for a phrase |
| `SentenceId` | Identifier for the source sentence |
| `Phrase` | Phrase text |
| `Sentiment` | Ordinal sentiment label from 0 through 4 |

## Label transformation

The notebook converts the original five-class target into binary sentiment:

| Original label | Meaning in this project | Binary label |
|---:|---|---:|
| 0 | Negative | 0 |
| 1 | Somewhat negative | 0 |
| 2 | Neutral | Excluded |
| 3 | Somewhat positive | 1 |
| 4 | Positive | 1 |

Removing neutral phrases makes the classification boundary cleaner, but also changes the task. The resulting metric does not describe five-class sentiment classification and does not measure the model's ability to recognize neutrality.

## Historical split

The notebook creates an 80/20 row-level split with `pandas.DataFrame.sample(frac=0.8, random_state=42)`.

Because many phrases share a `SentenceId`, a row-level split can distribute related fragments from one source sentence across training and held-out data. This is a credible leakage risk and may inflate measured performance.

## Recommended split

A stronger evaluation should group by `SentenceId` so every phrase from a source sentence remains in exactly one partition. It should also reserve a validation set for model selection and preserve the test set for one final evaluation.

## Data quality considerations

- Phrases vary substantially in length and information content.
- Short fragments can be ambiguous outside their source sentence.
- Sentiment labels reflect annotator judgments, not objective emotional truth.
- Neutral examples are removed, narrowing the domain.
- Review language can encode cultural, temporal, and genre-specific patterns.
- The dataset is a benchmark and does not represent every audience or writing context.

## Access and governance

The dataset is not included in this repository. Obtain it from Kaggle and review the source dataset's current terms before redistribution or commercial use. Do not commit `train.tsv`, derived copies, trained weights, or local credentials to the repository.
