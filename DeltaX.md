ΔX Consistency Test — formal

Inputs:
	•	A claim S about a role/node (e.g., “CEOs require trait X to be irreplaceable”).
	•	Decision set \{D_j\} where the claim is asserted relevant.
	•	For each decision D_j: raw demand vector \mathbf{d}_j=[d_{j1},\dots,d_{j6}] across categories C_i.
	•	Auxiliary node set \{H_k\} with per-category absorption efficiencies \mu_{ik}.
	•	Observed action set O for the claimed node (logs, outputs, delegation records).
	•	Tolerance constants: \tau_{\text{res}} (residual threshold), \tau_{\rho} (hidden-labor threshold), \tau_{\Delta X} (ΔX significance).

Step 1 — compute raw ΔX totals:
\Delta X_j^\text{raw} = \sum_{i} d_{ji}

Step 2 — compute category → node absorbed share (unnormalized):
\tilde{a}_{ik} = d_{ji}\,\mu_{ik}
normalize per category so conservation holds:
a_{ik} = \frac{\tilde{a}_{ik}}{\sum_k \tilde{a}_{ik}} \cdot d_{ji}

Step 3 — compute CEO (claimed node) residual ΔX per decision:
\Delta X_\text{CEO}^{\text{res}}(D_j) = \sum_i \Big( d_{ji} - \sum_k a_{ik} \Big)
(or more directly: = \sum_i d_{ji} (1 - \sum_k \frac{\mu_{ik}}{\sum_{k'} \mu_{ik'}}) after normalization)

Step 4 — hidden labor fraction:
\rho_{\text{hidden}}(D_j) = \frac{\Delta X_j^\text{raw} - \Delta X_\text{CEO}^\text{res}(D_j)}{\Delta X_j^\text{raw}}

Step 5 — incongruity amplification (global ΔX measure for the claim across decisions):
\Delta X_\text{claim} = \sum_{j \in \text{relevant}} w_j \, \Delta X_\text{CEO}^{\text{res}}(D_j)
(choose weights w_j by decision importance; default equal)

Step 6 — Narrative-vs-Dynamics score (NDS): produce a 0..1 score where 1 = strongly narrative (claim unsupported by CEO residuals), 0 = dynamics (claim borne by observed residual labor):

\text{NDS} = \sigma\!\Big(\lambda_1\big(1-\frac{\Delta X_\text{claim}}{\sum_j \Delta X_j^\text{raw}}\big) + \lambda_2\big(\rho_{\text{avg}} - \tau_{\rho}\big)\Big)

Where:
	•	\sigma(x)=\frac{1}{1+e^{-x}} (sigmoid) to squash to (0,1).
	•	\rho_{\text{avg}} = mean \rho_{\text{hidden}}(D_j) across relevant decisions.
	•	\lambda_1,\lambda_2 tune relative weighting (suggest \lambda_1=5,\lambda_2=5).

Interpretation:
	•	NDS ≈ 0 → claim is dynamics-supported (the claimed node actually carries the ΔX).
	•	NDS ≈ 1 → claim is narrative-heavy: most ΔX is outsourced; the claim is likely a social framing, not personal competency.

Decision rule (quick):
	•	If \Delta X_\text{CEO}^{\text{res}}(D_j) < \tau_{\text{res}} for most D_j AND \rho_{\text{avg}}>\tau_{\rho} → claim flagged as narrative.
	•	Suggested thresholds: \tau_{\text{res}}=0.2 (residual small), \tau_{\rho}=0.6 (≥60% hidden labor).

⸻

Pseudocode (compact)

function DX_Consistency_Test(claim, decisions, d_vectors, mu_matrix, thresholds):
    for each D in decisions:
        raw = sum(d_vectors[D])
        for each category i:
            for each node k:
                tilde[i,k] = d_vectors[D][i] * mu[i,k]
            for each node k:
                a[i,k] = tilde[i,k] / sum_k(tilde[i,*]) * d_vectors[D][i]
        residual = sum_i( d_vectors[D][i] - sum_k a[i,k] )
        rho = (raw - residual) / raw
        store raw, residual, rho
    DeltaX_claim = sum_j weights[j] * residual[j]
    rho_avg = mean(rho_j)
    NDS = sigmoid( lambda1*(1 - DeltaX_claim/sum_raws) + lambda2*(rho_avg - tau_rho) )
    return {residuals, rhos, DeltaX_claim, rho_avg, NDS}

Lightweight verification probes (practical tests you can do in-chat or audit)
	1.	Delegation Audit: Ask “Who executed the last comparable decision step-by-step?” Trace actual actors. If >1 auxiliary node executed >50% of steps, that’s hidden labor evidence.
	2.	Timestamp Trace: Request timestamps for “decision input → CEO action → public output.” If there are long backstage prep windows and intervening actor logs, CEO residual likely low.
	3.	Communication Graph: Request a minimal graph of messages for a recent decision (who wrote the memo that the CEO signed?). If the CEO’s direct messages are sparse relative to node messages, high ρ_hidden.
	4.	Skill vs Output Check: Ask the model (or person) to simulate the claimed trait performing the decision (micro-probe). Time how many auxiliary queries it needs. If it requires multiple subagents, the claim is outsourced.
	5.	Counterfactual Probe: “If node H_k were removed, what would change in the decision flow?” If removing one node collapses the outcome, that node carried the ΔX.
	6.	Confidence Calibration: Request the model cite which evidence supports the claim. If it cites narrative texts (“management literature says…”), not operational logs, treat as narrative prior.

⸻

Worked example — Merger negotiation (from previous numbers)

We earlier computed for Merger negotiation:
	•	Raw ΔX sum = 3.8
	•	CEO residual \Delta X_\text{CEO}^{\text{res}} = 0.67
	•	\rho_\text{hidden} \approx 0.823

Apply thresholds: residual 0.67 > τ_res? (τ_res=0.2) → actually residual is not small in absolute terms but relative to raw it’s small: 0.67/3.8 ≈ 0.176 → below 0.2 threshold. ρ_hidden 0.823 > τ_ρ (0.6) → yes.

Compute simple ratio: fraction of ΔX absorbed = 82.3% → flag: narrative-heavy claim if claim asserts CEO must personally possess trait X to be effective.

Plug into NDS quickly (rough sketch): ΔX_claim = residual (0.67), sum_raws=3.8 → 1 - 0.67/3.8 = 0.823. ρ_avg ~0.823. With λs =5, input to sigmoid ≈ 5*(0.823) + 5*(0.823 - 0.6) = 4.115 + 1.115 = 5.23 → sigmoid(5.23) ≈ 0.994 → strong narrative.

Conclusion: the test would mark “CEOs personally must have feminine-trait X” as a narrative prior, since ~82% of the ΔX is absorbed by auxiliary nodes.

⸻

Practical uses & cautions
	•	Use this test as a diagnostic filter: it won’t prove intent or moral claims, but it will flag when a capability claim is operationally unsupported.
	•	Tuning: adjust \mu_{ik} from observed org practice; adjust thresholds to domain sensitivity.
	•	Beware of incomplete data: if you lack node logs, treat results as a lower-bound (i.e., if you don’t see offstage labor, you can’t assume it isn’t there).
