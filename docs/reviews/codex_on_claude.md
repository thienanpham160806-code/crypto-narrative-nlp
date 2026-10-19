# Codex review of Claude NLP

Reviewed 2026-10-16 on shared `dev`; read-only review of NLP and ingestion. Files may continue changing concurrently. This review does not certify publication accuracy or independent sentiment labels.

## Blocker

- **Conditional blocker: LLM features on test are not prohibited in code.** `src/features/doc_scores.py:79` calls LLM labels for all English canonical documents when enabled; `src/features/doc_scores.py:61` replaces the forecast narrative with those labels. A model with knowledge after `split.valid_end` can leak historical outcomes into test features. Keep LLM strictly in validation, or reject use outside the permitted period. Current config has `nlp.llm.enabled = false`, so the default run does not trigger this path.

## Should-fix

- **Embedding cache ignores text and model identity.** `src/features/narrative.py:57` loads vectors keyed only by `doc_id`; `src/features/narrative.py:59` decides whether to recompute from that ID. Changing article text, body truncation or embedding model reuses stale vectors, possibly from a prior experiment. Include text hash, model/revision and preprocessing version; test invalidation.
- **FinBERT cache ignores model identity.** `src/features/finbert.py:31` reuses `(doc_id, sha)` although the stored record includes `model`. A changed model can silently reuse previous probabilities. Include the model revision and inference settings in the cache key.
- **Daily joins can multiply or hide articles.** `src/features/daily_index.py:41` merges without `validate='one_to_one'`; `src/features/doc_scores.py:56` also lacks merge-cardinality checks. Duplicate score rows inflate counts, while incomplete score joins can make collection gaps look like zero-news days. Reject duplicate IDs and publish scored-versus-collected coverage separately.
- **URL normalization can merge distinct articles.** `src/data/build_documents.py:29` strips every query string before URL deduplication at `src/data/build_documents.py:49`. URLs such as `/article?id=1` and `/article?id=2` become identical. Remove known tracking parameters only and preserve content identifiers.
- **Khaksar disagreement is not yet reproduced.** `src/features/daily_index.py:33` uses Antweiler–Frank label disagreement, not the daily standard deviation of sentiment (or sentiment times topic probability) described in `docs/research/FULLTEXT_lucey_khaksar.md`. Both can be useful, but name the current metric explicitly in the paper and do not present it as Khaksar's specification.

## Nit

- `src/features/narrative.py:3` says every selection uses train, while `src/features/narrative.py:97` selects K on validation perplexity. The implementation is permitted by AGENTS (no test fitting), but the docstring is inconsistent and differs from the proposed train-only coherence selection.
- `src/features/narrative.py:39` truncates body text to 500 characters for narrative extraction. Document this sensitivity, especially when the title and opening do not contain the main event.

## Verified paths

- `src/features/narrative.py:95`: vectorizer fit only on train; validation uses transform. LDA candidates fit train and select K on validation, never test.
- `src/features/narrative.py:78`: zero-shot `other` threshold uses the train mask. `src/features/narrative.py:115`: BERTopic fit receives train-only rows; subsequent transform applies to later rows.
- `src/data/build_documents.py:41`: publication timestamp accepted only within the documented 48-hour bound and no later than first-seen. `src/data/build_documents.py:75`: chronological stable sort precedes canonical selection, so later duplicates do not replace earlier content.
- `src/features/daily_index.py:42`: convert `public_ts_utc` to UTC before floor('D'). Canonical English news only; no Vietnamese translation or SEC mixing in daily forecasting.
- `src/features/daily_index.py:36`: `neg_accel` is computed after reindexing to a complete UTC daily grid, preserving calendar gaps rather than taking the previous observed news day.

## Limits

No live source requests, manual article timestamp verification, or sentiment ground-truth labeling were performed in this review. GKG first-seen is a conservative availability timestamp, not proof of original publication time. Frozen pretrained model provenance and cache hashes still need to accompany real-data claims.
