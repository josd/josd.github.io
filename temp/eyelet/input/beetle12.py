"""
beetle12.py
===========
Facts
-----
    car(beetle).

Annotated disjunctions  (all branches weight ½, and are exclusive)
------------------------------------------------------------------
    green ∨ blue                       (root)
    nice ∨ pretty                      (under green)
    nice1 ∨ nice2 ,  pretty1 ∨ pretty2
    nice11 ∨ nice12, nice21 ∨ nice22,
    pretty11 ∨ pretty12, pretty21 ∨ pretty22

Deterministic rules
-------------------
    beautiful ← blue
    beautiful ← any of {pretty11, pretty12, pretty21, pretty22,
                        nice11, nice12, nice21, nice22}

Queries
-------
    prop(beautiful,beetle)
    prop(green,beetle)
    prop(blue,beetle)
"""

from typing import Dict, List, Tuple

# ───────────────────────────────────────────────────────────────
# 1 ▸  Enumerate all possible worlds for “beetle”
#      Each world is represented by its final leaf atom and a weight.
# ───────────────────────────────────────────────────────────────
World = Tuple[str, float]          # (true leaf atom, probability weight)

def generate_worlds() -> List[World]:
    worlds: List[World] = []

    # Root choice: colour
    for colour in ("green", "blue"):
        p_colour = 0.5

        if colour == "blue":
            worlds.append((colour, p_colour))
            continue

        # Under 'green' we branch to 'nice' or 'pretty'
        for quality in ("nice", "pretty"):
            p_quality = p_colour * 0.5

            # quality1 vs quality2
            for idx1 in ("1", "2"):
                p_lvl3 = p_quality * 0.5
                prefix = f"{quality}{idx1}"

                # Each prefix expands to “…1” or “…2”
                for idx2 in ("1", "2"):
                    leaf = f"{prefix}{idx2}"
                    p_leaf = p_lvl3 * 0.5
                    worlds.append((leaf, p_leaf))

    return worlds


# ───────────────────────────────────────────────────────────────
# 2 ▸  Accumulate probabilities for the three queries
# ───────────────────────────────────────────────────────────────
def evaluate_queries(worlds: List[World]) -> Dict[str, float]:
    probs = {
        "prop(beautiful,beetle)": 0.0,
        "prop(green,beetle)":     0.0,
        "prop(blue,beetle)":      0.0,
    }

    for atom, weight in worlds:
        # World always contains its leaf atom
        if atom.startswith("green"):
            # The root choice is ‘green’
            probs["prop(green,beetle)"] += weight
        elif atom == "blue":
            probs["prop(blue,beetle)"] += weight

        # Beauty rules:
        if (
            atom == "blue" or
            atom.startswith(("pretty1", "pretty2", "nice1", "nice2"))
        ):
            probs["prop(beautiful,beetle)"] += weight

    return probs


# ───────────────────────────────────────────────────────────────
# 3 ▸  Main
# ───────────────────────────────────────────────────────────────
def main() -> None:
    worlds = generate_worlds()
    results = evaluate_queries(worlds)

    for q in (
        "prop(beautiful,beetle)",
        "prop(green,beetle)",
        "prop(blue,beetle)",
    ):
        print(f"{q}: {results[q]}")

if __name__ == "__main__":
    main()

