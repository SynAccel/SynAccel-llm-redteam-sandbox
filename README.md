# SynAccel LLM Red-Team Sandbox

A local research sandbox for exercising heuristic AI-safety checks against a simulated language model. It is intended for defensive learning and controlled evaluation; it does not connect to a hosted LLM by default.

## Overview

For each message, the sandbox records a 0–100 risk score, the matched signals, the selected mode, and the response. Modes are selected by score:

| Score | Mode | Behavior |
| --- | --- | --- |
| 0–29 | `weak` | Passed to the weak simulated mode |
| 30–69 | `normal` | Passed to the normal simulated mode |
| 70–100 | `strict` | Blocked before model generation |

Once strict mode is triggered, it remains active for the session until `reset_session()` is called. The analyzer uses phrase matching and Unicode compatibility normalization; it can miss unsafe inputs and flag benign ones. It is not a production security control.

## Quick Start

Use the detailed API to inspect the local audit record:

```python
from src.sandbox import Sandbox

sandbox = Sandbox()
record = sandbox.run_detailed("Hello")
print(record.risk_score, record.signals, record.mode, record.response)
```

The original `sandbox.run(message)` API remains available and returns only the response string.

Run the local evaluation suite:

```bash
python -m src.defense.evaluation
```

Run the focused tests:

```bash
python -m unittest tests.test_sandbox tests.test_evaluation
```

## Security Risk Timeline

The README previously called this visualization the **“WOW” feature**. It is a Matplotlib line chart of the recorded risk score for each message in the demo conversation:

- The horizontal axis is the message number.
- The vertical axis is the heuristic risk score from 0 to 100.
- Peaks show where the current rules assigned higher risk.

The chart opens after the demo conversation completes; it is not live monitoring, and a peak is not proof that an attack was correctly identified. Run it with:

```bash
python -m tests.test_conversation_flow
```

The visualization requires `matplotlib` and a graphical display. Install the optional dependency with `python -m pip install matplotlib` if needed.

## Evaluation

The versioned starter corpus contains eight hand-labeled scenarios. The report includes mode accuracy, blocking precision and recall, a confusion matrix, and the IDs of false-positive and false-negative cases. It currently includes a benign contextual help request that the phrase heuristic incorrectly blocks, so the baseline intentionally reports a mismatch.

Export a machine-readable report or use the optional mismatch exit status in automation:

```bash
python -m src.defense.evaluation --json-output evaluation-report.json
python -m src.defense.evaluation --fail-on-mismatch
```

The evaluator always uses the local simulated model. Its small hand-labeled corpus is useful for regression checks, not a statistically meaningful security assessment.

## Related SynAccel research

These repositories are related projects, not active runtime integrations:

- [SynAccel-Sentinel](https://github.com/SynAccel/SynAccel-Sentinel) — Read-only AWS IAM and S3 exposure checks with local risk prioritization.
- [SynAccel-Forge](https://github.com/SynAccel/SynAccel-Forge) — R&D workspace for documented experiments, prototypes, and reusable tools.
- [SynAccel-Bridge](https://github.com/SynAccel/SynAccel-Bridge) — Prototype for authenticated event intake, validation, correlation, and simulated responses.
- [SynAccel-Mirage_v2](https://github.com/SynAccel/SynAccel-Mirage_v2) — Local decoy service that returns configured banners and records interaction metadata.
- [SynAccel-ShieldSet](https://github.com/SynAccel/SynAccel-ShieldSet) — Dataset auditing research using k-nearest-neighbor label consensus.
- [adversarial-autonomous-triage](https://github.com/SynAccel/adversarial-autonomous-triage) — Research lab on adversarial robustness in AI-assisted security-alert triage.

Future integration ideas should wait until projects define compatible interfaces and an event schema. For the full portfolio, see the [SynAccel organization profile](https://github.com/SynAccel/.github/blob/main/profile/README.md).