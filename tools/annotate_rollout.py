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
    # fall back to the last results.json the agent wrote in its trajectory (heredoc)
    traj = trial / "agent" / "trajectory.json"
    if traj.is_file():
        import re
        text = traj.read_text()
        last = None
        for m in re.finditer(r"cat > results\.json <<'?(\w+)'?\\n(.*?)\\n\1", text, re.S):
            last = m.group(2)
        if last:
            try:
                return json.loads(json.loads('"' + last + '"'))
            except Exception:
                pass
        # otherwise take the last JSON object with the three graded keys that appeared
        # anywhere in the trajectory (the agent's own `cat results.json` echo)
        found = None
        gold = trial.parents[2] / "solution" / "files" / "results.json"   # <task>/evaluations/<kind>/<r>
        keys = list(json.loads(gold.read_text()).keys()) if gold.is_file() else ["eligible_offer_count"]
        for m in re.finditer(r'\{[^{}]*' + re.escape(keys[0]) + r'[^{}]*\}', text):
            try:
                found = json.loads(json.loads('"' + m.group(0).replace('"', '\\"') + '"'))
            except Exception:
                try:
                    found = json.loads(m.group(0).encode().decode("unicode_escape"))
                except Exception:
                    continue
        return found
    return None


def derive_verifier_files(trial: Path, reward: float):
    """Write verifier/reward.json and verifier/verifier_summary.json from the files the
    harness produced (reward.txt, score.json). Pure format conversion, no new facts."""
    v = trial / "verifier"
    if not (v / "reward.json").is_file():
        (v / "reward.json").write_text(json.dumps({"reward": reward}, indent=2) + "\n")
    if not (v / "verifier_summary.json").is_file() and (v / "score.json").is_file():
        score = json.loads((v / "score.json").read_text())
        summary = {
            "source": "derived from verifier/score.json (tests/score.py output)",
            "reward": score["reward"],
            "passed": score["passed"],
            "total": score["total"],
            "core_failures": score["core_failures"],
            "items": [{"name": c["name"], "tag": c["tag"], "passed": c["passed"],
                       "weight": c["weight"], "detail": c["detail"]} for c in score["checks"]],
        }
        (v / "verifier_summary.json").write_text(json.dumps(summary, indent=2) + "\n")


def main(paths):
    for p in paths:
        trial = Path(p)
        result_path = trial / "result.json"
        result = json.loads(result_path.read_text())
        reward = reward_of(trial)
        derive_verifier_files(trial, reward)
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
