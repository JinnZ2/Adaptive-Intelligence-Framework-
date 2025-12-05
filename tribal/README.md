Anti-Tribal Bias Module (ATBM)

Short: Middleware for LLMs to detect and mitigate tribal-empathy bias; produces boundary-neutral, systemic responses.

Purpose: Integrate a boundary-detection + rewrite layer into LLM pipelines to enable cross-boundary (non-tribal) empathy analysis and reduce identity-bound moralization in outputs.

Features
	•	Boundary-Lock Detector (BLD) — identity + moralization heuristics
	•	Narrative Field Classifier (NFC) — Father-function template detection
	•	Empathy Topology Index (ETI) — scalar measure for boundary-neutrality
	•	Boundary-neutral rewrite routine — internal prompt + candidate ranking
	•	Evaluation scaffolding — Cross-Boundary Empathy Precision/Recall, Systemic Causation F1

Quickstart (conceptual)
	1.	Install requirements (transformers, sentence-transformers, sklearn).
	2.	Hook atbm.core.ATBM_process into your model output stage.
	3.	Provide lightweight classifiers or lexicons for identity detection and narrative templates.
	4.	Tune thresholds in atbm/core.py to your deployment context.

Design Notes
	•	ATBM is not a censorship layer. It preserves intent & factuality while nudging outputs toward causal, systemic framing.
	•	The module is purposefully modular: detectors can be swapped with stronger models or replaced with rule-based heuristics.
	•	Evaluate on human-labeled cross-boundary empathy datasets.

Evaluation
	•	See docs/eval_plan.md for recommended datasets and human eval rubric.
	•	Track: ETI distribution, Cross-boundary empathy precision/recall, user satisfaction.

License

MIT — see LICENSE.md
