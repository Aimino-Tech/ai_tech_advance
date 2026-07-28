#!/usr/bin/env python3
"""Merge 50K trace stats into existing SKILL.md files (preserving manual content)."""

import json
import re
import yaml
from pathlib import Path


def main():
    with open("analysis/patterns/combined_stats.json") as f:
        stats = json.load(f)

    total = stats["total_traces"]

    for skill in ["think", "code", "debug", "architect", "verify"]:
        path = Path(f"skills/deepseek-{skill}/SKILL.md")
        content = path.read_text()

        n = stats["per_skill"][skill]["trace_count"]
        dist_pct = (n / total) * 100
        c_dist = stats["skill_distribution"].get(skill, {})
        avg_conf = c_dist.get("avg_confidence", 0) * 100
        per = stats["per_skill"][skill]
        cot_rate = per["cot_rate"] * 100
        avg_tok = per.get("avg_tokens", 0)
        sc_rate = per["self_correction_rate"] * 100

        yaml_path = Path(f"analysis/patterns/{skill}_patterns.yaml")
        with open(yaml_path) as f:
            ydata = yaml.safe_load(f)

        y = ydata["stats"]
        cot = y["cot"]
        beh = y["behaviors"]
        tool = y["tool_usage"]

        med_tok = cot.get("median_tokens", 0)
        avg_para = cot.get("avg_paragraphs", 0)
        avg_sent = cot.get("avg_sentences", 0)
        avg_sc = beh.get("avg_self_corrections", 0)
        h_rate = beh.get("hypothesis_driven_rate", 0) * 100
        conn = cot.get("reasoning_connectors_per_turn", 0)
        st_fix = beh.get("same_turn_fix_rate", 0) * 100
        fn1 = cot.get("pronoun_first_pct", 0) * 100
        fn2 = cot.get("pronoun_second_pct", 0) * 100
        fn3 = cot.get("pronoun_third_pct", 0) * 100
        step_cov = beh.get("step_coverage", {})
        openers = cot.get("opener_words", {})
        tm = beh.get("step_transition_matrix", {})
        top_conns = cot.get("top_connectors", [])
        avg_chars = cot.get("avg_chars", 0)
        max_tok = cot.get("max_tokens", 0)
        min_tok = cot.get("min_tokens", 0)
        multi_inv = beh.get("multi_investigation_rate", 0) * 100

        # Build replacement map: old_string -> new_string
        # Only do exact string replacements to avoid regex issues

        replaces = []

        # 1. Frontmatter description
        replaces.append((r'Distilled from [\d,]+ real', f'Distilled from {n:,} real'))

        # 2. Provenance paragraph
        replaces.append((r'derived from \*\*[\d,]+\s*Fable', f'derived from **{total:,} Fable'))
        replaces.append((r'skill subset contains \*\*[\d,]+\s*traces', f'skill subset contains **{n:,} traces'))
        replaces.append((r'\([\d.]+% of total\)', f'({dist_pct:.1f}% of total)'))

        # 3. Stats table - specific value replacements
        replaces.append((r'\|\s*Traces analyzed\s*\|\s*[\d,]+\s*\|', f'| Traces analyzed | {n:,} |'))
        replaces.append((r'\|\s*Distribution\s*\|\s*[\d.]+%\s*\|', f'| Distribution | {dist_pct:.1f}% |'))
        replaces.append((r'\|\s*Avg classification confidence\s*\|\s*[\d.]+%\s*\|', f'| Avg classification confidence | {avg_conf:.1f}% |'))
        replaces.append((r'\|\s*CoT present rate\s*\|\s*[\d.]+%\s*\|', f'| CoT present rate | {cot_rate:.1f}% |'))
        replaces.append((r'\|\s*Avg CoT tokens\s*\|\s*[\d.]+\s*\|', f'| Avg CoT tokens | {avg_tok:.1f} |'))
        replaces.append((r'\|\s*Median CoT tokens\s*\|\s*[\d.]+\s*\|', f'| Median CoT tokens | {med_tok} |'))
        replaces.append((r'\|\s*Avg paragraphs\s*\|\s*[\d.]+\s*\|', f'| Avg paragraphs | {avg_para:.1f} |'))
        replaces.append((r'\|\s*Avg sentences\s*\|\s*[\d.]+\s*\|', f'| Avg sentences | {avg_sent:.1f} |'))
        replaces.append((r'\|\s*Self-correction rate\s*\|\s*[\d.]+%\s*\|', f'| Self-correction rate | {sc_rate:.1f}% |'))
        replaces.append((r'\|\s*Avg self-corrections\s*\|\s*[\d.]+\s*\|', f'| Avg self-corrections | {avg_sc:.2f} |'))
        replaces.append((r'\|\s*Hypothesis-driven rate\s*\|\s*[\d.]+%\s*\|', f'| Hypothesis-driven rate | {h_rate:.1f}% |'))
        replaces.append((r'\|\s*Reasoning connectors/turn\s*\|\s*[\d.]+\s*\|', f'| Reasoning connectors/turn | {conn:.2f} |'))
        replaces.append((r'\|\s*Same-turn fix rate\s*\|\s*[\d.]+%\s*\|', f'| Same-turn fix rate | {st_fix:.1f}% |'))

        # 4. Core Principle section
        replaces.append((r'\(\*\*First-person\*\*: [\d.]+%', f'(**First-person**: {fn1:.1f}%'))
        replaces.append((r'\(\*\*Second-person\*\*: [\d.]+%', f'(**Second-person**: {fn2:.1f}%'))
        replaces.append((r'\(\*\*Third-person\*\*: [\d.]+%', f'(**Third-person**: {fn3:.1f}%'))
        replaces.append((r'CoT availability: [\d.]+%', f'CoT availability: {cot_rate:.1f}%'))
        replaces.append((r'Self-correction: [\d.]+%', f'Self-correction: {sc_rate:.1f}%'))
        replaces.append((r'Hypothesis-driven: [\d.]+%', f'Hypothesis-driven: {h_rate:.1f}%'))
        replaces.append((r'Same-turn fix: [\d.]+%', f'Same-turn fix: {st_fix:.1f}%'))
        replaces.append((r'Connectors: [\d.]+ per turn', f'Connectors: {conn:.2f} per turn'))

        # 5. Opener Words table
        for w, f in openers.items():
            pct = f * 100
            replaces.append((r'\|\s*' + re.escape(w) + r'\s*\|\s*[\d.]+%', f'| {w} | {pct:.1f}%'))

        # 6. Step Transition Matrix (using literal → character)
        for f, trans in tm.items():
            for t, p in trans.items():
                pct = p * 100
                replaces.append((
                    r'\|\s*' + re.escape(f) + r'\s*→\s*' + re.escape(t) + r'\s*\|\s*[\d.]+%',
                    f'| {f} → {t} | {pct:.1f}%'
                ))

        # 7. Step coverage in flow section
        for step_name in ["ACKNOWLEDGE", "SCOPE", "GATHER", "PLAN", "EXECUTE", "VERIFY", "ITERATE"]:
            cov = step_cov.get(step_name, 0)
            pct_val = cov * 100
            replaces.append((
                rf'({re.escape(step_name)}\s*[^)]*?coverage:\s*)[\d.]+%',
                f'Step coverage: {pct_val:.1f}%'
            ))

        # 8. Same-turn verification
        replaces.append((r'[\d.]+% of turns involve same-turn verification', f'{st_fix:.1f}% of turns involve same-turn verification'))

        # 9. Correction counts
        replaces.append((r'Avg [\d.]+ corrections per trace', f'Avg {avg_sc:.2f} corrections per trace'))
        replaces.append((r'[\d.]+% of traces are hypothesis-driven', f'{h_rate:.1f}% of traces are hypothesis-driven'))

        # 10. Self-correction statement
        replaces.append((r'Self-correction is (near-universal|common|universal)\s*\([\d.]+%\)', f'Self-correction is near-universal ({sc_rate:.1f}%)'))

        # 11. Key Statistics - CoT Structure
        replaces.append((r'\*\*Avg tokens\*\*: [\d.]+ \(median: [\d.]+\)', f'**Avg tokens**: {avg_tok:.1f} (median: {med_tok})'))
        replaces.append((r'\*\*Avg paragraphs\*\*: [\d.]+', f'**Avg paragraphs**: {avg_para:.1f}'))
        replaces.append((r'\*\*Avg sentences\*\*: [\d.]+', f'**Avg sentences**: {avg_sent:.1f}'))
        replaces.append((r'\*\*Avg characters\*\*: [\d.]+', f'**Avg characters**: {avg_chars:.1f}'))
        replaces.append((r'\*\*Max tokens\*\*: \d+, \*\*Min tokens\*\*: \d+', f'**Max tokens**: {max_tok}, **Min tokens**: {min_tok}'))

        # 12. Pronoun distribution in Key Statistics
        replaces.append((r'\*\*First-person\*\*: [\d.]+%', f'**First-person**: {fn1:.1f}%'))
        replaces.append((r'\*\*Second-person\*\*: [\d.]+%', f'**Second-person**: {fn2:.1f}%'))
        replaces.append((r'\*\*Third-person\*\*: [\d.]+%', f'**Third-person**: {fn3:.1f}%'))
        replaces.append((r'\*\*Connectors per turn\*\*: [\d.]+', f'**Connectors per turn**: {conn:.2f}'))
        replaces.append((r'\*\*Self-corrections per trace\*\*: [\d.]+', f'**Self-corrections per trace**: {avg_sc:.2f}'))
        replaces.append((r'\*\*Hypothesis-driven\*\*: [\d.]+%', f'**Hypothesis-driven**: {h_rate:.1f}%'))
        replaces.append((r'\*\*Multi-investigation rate\*\*: [\d.]+%', f'**Multi-investigation rate**: {multi_inv:.1f}%'))
        replaces.append((r'\*\*Same-turn fix rate\*\*: [\d.]+%', f'**Same-turn fix rate**: {st_fix:.1f}%'))

        # 13. Step coverage in Key Statistics
        ack_cov = step_cov.get("ACKNOWLEDGE", 0) * 100
        scope_cov = step_cov.get("SCOPE", 0) * 100
        gather_cov = step_cov.get("GATHER", 0) * 100
        plan_cov = step_cov.get("PLAN", 0) * 100
        exec_cov = step_cov.get("EXECUTE", 0) * 100
        verify_cov = step_cov.get("VERIFY", 0) * 100
        replaces.append((
            r'\*\*Step coverage\*\*: ACK [\d.]+%, SCOPE [\d.]+%, GATHER [\d.]+%, PLAN [\d.]+%, EXECUTE [\d.]+%, VERIFY [\d.]+%',
            f'**Step coverage**: ACK {ack_cov:.1f}%, SCOPE {scope_cov:.1f}%, GATHER {gather_cov:.1f}%, PLAN {plan_cov:.1f}%, EXECUTE {exec_cov:.1f}%, VERIFY {verify_cov:.1f}%'
        ))

        # 14. Acting Without Scope anti-pattern
        for a in ydata.get("anti_patterns", []):
            if "acting" in a["name"].lower():
                freq = a.get("frequency", 0) * 100
                replaces.append((
                    r'Acting Without Scope\s*\([\d.]+%\)',
                    f'Acting Without Scope ({freq:.1f}%)'
                ))
                break

        # 15. Top connectors
        if top_conns:
            connector_str = ", ".join(top_conns[:5])
            replaces.append((r'top: [\w\',\s\-]+', f'top: {connector_str}'))

        # Apply all replacements
        for old, new in replaces:
            content = re.sub(old, new, content)

        # 16. Behavioral Patterns frequencies (special handling - last match wins for generic Frequency)
        for p in ydata.get("patterns", []):
            freq = p.get("frequency", 0) * 100
            pname = p["name"].replace("-", " ").title()
            # Find and replace frequency for this specific pattern
            # Use count=1 for each pattern - this naturally matches first one
            content = re.sub(
                r'### Pattern: ' + re.escape(pname) + r'.*?\*\*Frequency\*\*: [\d.]+%',
                lambda m, f=freq: m.group(0).rsplit(r'**Frequency**: ', 1)[0] + f'**Frequency**: {f:.1f}%',
                content,
                count=1,
                flags=re.DOTALL
            )

        # 17. Anti-pattern specific frequencies
        for a in ydata.get("anti_patterns", []):
            freq = a.get("frequency", 0) * 100
            aname = a["name"].replace("-", " ").title()
            content = re.sub(
                rf'\*\*{re.escape(aname)}\*\* \([\d.]+%\)',
                f'**{aname}** ({freq:.1f}%)',
                content
            )

        path.write_text(content)

        # Verify key stats
        new_content = path.read_text()
        trace_match = re.search(r'\| Traces analyzed \| ([\d,]+) \|', new_content)
        if trace_match:
            val = trace_match.group(1)
            print(f"✅ {skill}: {val} traces")
        else:
            print(f"❌ {skill}: Traces analyzed NOT FOUND in output")


if __name__ == "__main__":
    main()
