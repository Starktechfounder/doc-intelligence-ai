# M06 --- Evaluation and Regression Tests

## Objective

Measure retrieval and answer quality with repeatable test cases instead
of relying on anecdotal demos.

## Scope

-   Small version-controlled evaluation corpus
-   Retrieval relevance metrics
-   Answer faithfulness and citation checks
-   Latency and optional cost tracking
-   Regression report

## Tasks

1.  Build representative questions from the sample documents.
2.  Label expected relevant source chunks or documents.
3.  Calculate retrieval metrics such as Recall@k and Mean Reciprocal
    Rank where applicable.
4.  Create answer checks for citation validity and evidence support.
5.  Separate deterministic automated tests from model-based evaluations.
6.  Track latency and model/provider errors without logging secrets or
    full private documents.
7.  Record baseline results before changing retrieval or prompts.
8.  Document how to reproduce the evaluation.

## Acceptance criteria

-   [ ] Evaluation data is version-controlled and contains no private
    information.
-   [ ] Retrieval metrics are computed reproducibly.
-   [ ] Citation validity is checked automatically.
-   [ ] Model-dependent evaluation limitations are stated.
-   [ ] A baseline report can be regenerated.
-   [ ] Regressions are visible and investigated.

## Deliverables

Evaluation dataset, scripts/tests, metrics report, and reproduction
instructions.

## Evidence to record

Dataset version, commands, metrics, sample failure analysis, and changes
from baseline.

## Risks

Overfitting to a tiny dataset, subjective answer scoring, and
non-deterministic model outputs.
