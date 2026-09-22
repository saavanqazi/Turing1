#!/usr/bin/env python3
"""annotate_rollout.py — add the delivery-format fields to a copied harbor trial.

Usage:
    python3 tools/annotate_rollout.py task/evaluations/difficulty/r1 [r2 ...]

For each trial folder it reads verifier/reward.json (or reward.txt) and the
agent's results.json if the trial kept one, then ADDS to result.json:
    "model": "GLM-5.2"
    "overall_pass": <reward == 1.0>
    "final_answer": <parsed results.json the agent wrote, or null>
    "reward": <float>
    "judge": {"type": "deterministic file_check", "judge_model": null}
Harbor's own fields are never changed. Re-running is idempotent.
"""
import json
import sys
from pathlib import Path


def reward_of(trial: Path) -> float:
    rj = trial / "verifier" / "reward.json"
    if rj.is_file():
        data = json.loads(rj.read_text())
        if isinstance(data, dict):
            return float(data.get("reward", next(iter(data.values()))))
        return float(data)
    rt = trial / "verifier" / "reward.txt"
    return float(rt.read_text().strip())


def final_answer_of(trial: Path):
    for cand in (trial / "final_answer.json", trial / "agent" / "results.json",
                 trial / "artifacts" / "results.json"):
        if cand.is_file():
            try:
                return json.loads(cand.read_text())
            except json.JSONDecodeError:
                return cand.read_text()
    return None


def main(paths):
    for p in paths:
        trial = Path(p)
        result_path = trial / "result.json"
        result = json.loads(result_path.read_text())
        reward = reward_of(trial)
        result["model"] = "GLM-5.2"
        result["overall_pass"] = reward == 1.0
        result["final_answer"] = final_answer_of(trial)
        result["reward"] = reward
        result["judge"] = {"type": "deterministic file_check", "judge_model": None}
        result_path.write_text(json.dumps(result, indent=4) + "\n")
        print(f"{trial}: reward={reward} overall_pass={result['overall_pass']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
