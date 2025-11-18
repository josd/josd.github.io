#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
library_and_path.py
===================

Overview
--------
This script is a self-contained Python reconstruction of the Brains example
“library-and-path”. It searches for a *short* sequence of “law adoptions”

    stabilize gravity-stable
    stabilize atoms-stable
    ...

such that, in the final world, a set of high-level features (galaxies, life,
culture, …) all hold.

We have three ingredients:

  1. A small *library* of candidate laws (e.g. "gravity-stable",
     "chemistry-stable", …).

  2. Feature-precondition rules saying which laws/features support which
     other features, e.g.:

         stars  ←  gravity-stable
         life   ←  stars ∧ carbon-chemistry
         mind   ←  life
         culture ← language ∧ many-minds
         …

  3. A set of observation features that must hold in the final world, here:

         { galaxies, carbon-chemistry, life, mind,
           language, many-minds, culture }.


Worlds and search space
-----------------------
A *world* is a subset of the candidate laws. Implementation-wise we encode
worlds by a bit-mask:

  • 0b00000000  = empty world (no laws adopted yet),
  • 0b00000001  = only "gravity-stable" adopted,
  • 0b00000011  = "gravity-stable" and "atoms-stable" adopted, etc.

The search space consists of all finite sequences of law adoptions, starting
from the empty world and always adding a previously absent law. A breadth-first
search (BFS) explores these law-sets and keeps the first world that satisfies
all observation features, preferring:

  1. minimal number of law adoptions, and
  2. among those, lexicographically smallest action sequence
     (so the result is deterministic).


Higher-order look, first-order core
-----------------------------------
Conceptually we follow the “higher-order look, first-order core” story:

  • Intensions (predicate names) are ordinary first-order objects:
      - for each law ℓ we have a unary predicate-name  law:ℓ
      - for each feature f we have a unary predicate-name  feat:f

  • Worlds are first-order objects (our bit-masks 0..2^N−1).

  • A *single* first-order predicate ties names to their extensions:

        Holds₁(P, w)

    meaning: “the unary predicate named by P holds in world w”.

    - If P = law:ℓ, this means “ℓ ∈ world(w)” (the law is adopted there).
    - If P = feat:f, this means “all prerequisites of feature f are already
      satisfied in w”, and we compute this via a monotone closure operator.

  • Direct preconditions between intensions are captured by a binary relation:

        Holds₂(rel:requires, feat:f, Q)

    meaning: “the intension Q is listed as a direct prerequisite of f”
    (Q can itself be a law:… or a feat:… name).

On the Python side we implement:

  • a tiny engine that, given a law-mask `w`, computes the fixed point of all
    features supported by that world;
  • a precomputed model:

        EXT1: Dict[str, Set[int]]

    mapping each unary predicate-name (laws and features) to the set of worlds
    where it holds, so that:

        Holds1(P, w)  ⇔  w ∈ EXT1[P]

  • and a binary extension:

        EXT2["rel:requires"] ⊆ { (feat:f, Q) }

    so that:

        Holds2("rel:requires", feat:f, Q)  ⇔  (feat:f, Q) ∈ EXT2["rel:requires"].

This realizes the Hayes–Menzel “Holdsₙ” trick in a small, concrete setting.


What the script prints
----------------------
When run as a script:

    python library_and_path.py

it prints three ARC-style sections:

  1. Answer
     • the minimal sequence of law adoptions,
     • the final laws and features,
     • and a sample of Holds₁ evaluations in the final world.

  2. Reason why
     • a prose explanation of the Holds₁ / Holds₂ view,
     • and how the BFS search uses that FO core.

  3. Check (harness)
     • at least six independent tests checking that:
         - Holds₂ correctly encodes prerequisites,
         - Holds₁ behaves as expected in small “toy” worlds,
         - the chosen final world really satisfies all observations,
         - each adopted law is individually necessary,
         - feature growth is monotone along the path and matches the
           recorded deltas,
         - and the closure operator agrees with Holds₁ on the final features.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from collections import deque


# ──────────────────────────────────────────────────────────────
# Configuration: laws, feature rules, observations
# ──────────────────────────────────────────────────────────────

CANDIDATE_LAWS: List[str] = [
    "gravity-stable",
    "atoms-stable",
    "chemistry-stable",
    "electroweak-stable",
    "inflationary-dynamics",
    "magnetism-stable",
    "communication-stable",
    "population-dynamics",
]

PREREQUISITES: Dict[str, Set[str]] = {
    "stars": {"gravity-stable"},
    "galaxies": {"gravity-stable"},
    "carbon-chemistry": {"atoms-stable", "chemistry-stable"},
    "life": {"stars", "carbon-chemistry"},
    "mind": {"life"},
    "language": {"mind", "communication-stable"},
    "many-minds": {"mind", "population-dynamics"},
    "culture": {"language", "many-minds"},
    "observers": {"mind"},
}

# Observation features that must hold in the final world
OBSERVATIONS: Set[str] = {
    "galaxies",
    "carbon-chemistry",
    "life",
    "mind",
    "language",
    "many-minds",
    "culture",
}

MAX_DEPTH = len(CANDIDATE_LAWS)
CAP_PATHS = 200_000
FAST_THOROUGH = True  # BFS, but stop exploring branches that are no shorter

NUM_LAWS = len(CANDIDATE_LAWS)
WORLD_DOMAIN = tuple(range(1 << NUM_LAWS))  # all possible law-sets


# ──────────────────────────────────────────────────────────────
# Data structures for paths and results
# ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Step:
    """One step in a law-adoption path."""
    action: str
    added_law: Optional[str] = None
    enabled_features: Tuple[str, ...] = ()


@dataclass
class PathResult:
    """A complete path plus the final laws and features it yields."""
    path: List[Step]
    final_laws: Set[str]
    final_features: Set[str]


# ──────────────────────────────────────────────────────────────
# Core engine: closure on features + BFS search
# ──────────────────────────────────────────────────────────────

class LibraryAndPath:
    """
    Tiny engine:

      - law-sets are represented as bit-masks over CANDIDATE_LAWS,
      - feature-preconditions are compiled to law- and feature-masks,
      - infer_features performs a monotone fixed-point computation,
      - search runs BFS over law adoption paths.
    """

    def __init__(self, candidate_laws, prereq, observations):
        self.candidate_laws = list(candidate_laws)
        self.observations = set(observations)

        # Features are exactly the keys of PREREQUISITES
        self.feature_names = list(prereq.keys())

        # Indices for bit-masks
        self.law_index: Dict[str, int] = {
            law: i for i, law in enumerate(self.candidate_laws)
        }
        self.feat_index: Dict[str, int] = {
            feat: i for i, feat in enumerate(self.feature_names)
        }

        # For each feature fᵢ:
        #   req_law_mask[i]  = bit-mask of required laws
        #   req_feat_mask[i] = bit-mask of required features
        self.req_law_mask: List[int] = [0] * len(self.feature_names)
        self.req_feat_mask: List[int] = [0] * len(self.feature_names)

        for feat, reqs in prereq.items():
            fi = self.feat_index[feat]
            law_mask = 0
            feat_mask = 0
            for r in reqs:
                if r in self.law_index:
                    law_mask |= 1 << self.law_index[r]
                elif r in self.feat_index:
                    feat_mask |= 1 << self.feat_index[r]
                else:
                    raise KeyError(f"Unknown prerequisite: {r}")
            self.req_law_mask[fi] = law_mask
            self.req_feat_mask[fi] = feat_mask

        # Observations as a feature bit-mask
        self.obs_mask_feat = 0
        for o in self.observations:
            self.obs_mask_feat |= 1 << self.feat_index[o]

        # Memo cache for infer_features
        self._infer_cache: Dict[int, int] = {}

    # ── Helpers for pretty-printing masks ─────────────────────

    def law_mask_to_names(self, mask: int) -> List[str]:
        return [
            name
            for i, name in enumerate(self.candidate_laws)
            if (mask >> i) & 1
        ]

    def feat_mask_to_names(self, mask: int) -> List[str]:
        return [
            name
            for i, name in enumerate(self.feature_names)
            if (mask >> i) & 1
        ]

    # ── Closure operator: law-mask → feature-mask ─────────────

    def infer_features(self, law_mask: int) -> int:
        """
        Given a set of laws (as a bit-mask), compute the closure of all features
        supported by those laws and by one another.

        This is the FO core underlying Holds₁ for features:

            Holds1("feat:f", w)  ⇔  the bit for f is set in infer_features(w).
        """
        cached = self._infer_cache.get(law_mask)
        if cached is not None:
            return cached

        feat_mask = 0
        changed = True
        while changed:
            changed = False
            for fi in range(len(self.feature_names)):
                if (feat_mask >> fi) & 1:
                    continue  # already have this feature

                # Check if all required laws are present
                if (self.req_law_mask[fi] & ~law_mask) != 0:
                    continue

                # Check if all required features are present
                if (self.req_feat_mask[fi] & ~feat_mask) != 0:
                    continue

                # All prerequisites satisfied: add this feature
                feat_mask |= 1 << fi
                changed = True

        self._infer_cache[law_mask] = feat_mask
        return feat_mask

    # ── Neighbour generation for BFS ──────────────────────────

    def _expand(self, law_mask: int) -> List[Tuple[int, int, int]]:
        """
        From the current law-mask, generate all children by adding one new law.
        Returns a list of triples (law_index, new_law_mask, new_feat_mask).
        """
        out: List[Tuple[int, int, int]] = []
        for li in range(len(self.candidate_laws)):
            if (law_mask >> li) & 1:
                continue  # already adopted
            new_law_mask = law_mask | (1 << li)
            new_feat_mask = self.infer_features(new_law_mask)
            out.append((li, new_law_mask, new_feat_mask))
        return out

    # ── BFS search for minimal law-adoption path ──────────────

    def search(
        self,
        max_depth: int,
        cap_paths: int,
        fast: bool,
    ) -> Tuple[Optional[PathResult], int, int]:
        """
        BFS over law-adoption sequences:

          • starts from the empty world (no laws),
          • at each step adds one previously absent law,
          • checks whether observations hold in the resulting world,
          • keeps a best (shortest, then lexicographically smallest) path.

        Returns (chosen_result_or_None, total_nodes, consistent_endpoints).
        """
        Node = Tuple[int, Tuple[int, ...]]  # (law_mask, path_of_indices)

        queue = deque([ (0, tuple()) ])
        total_nodes = 0
        consistent_count = 0

        best_depth: Optional[int] = None
        best_actions: Optional[Tuple[str, ...]] = None
        best_final: Optional[Tuple[int, int]] = None  # (law_mask, feat_mask)
        best_path: Optional[Tuple[int, ...]] = None

        while queue:
            law_mask, path = queue.popleft()
            feat_mask = self.infer_features(law_mask)
            total_nodes += 1

            # Does this world satisfy all observation features?
            if (feat_mask & self.obs_mask_feat) == self.obs_mask_feat:
                consistent_count += 1
                actions = tuple(
                    f"stabilize {self.candidate_laws[i]}"
                    for i in path
                )

                if (
                    best_depth is None
                    or len(path) < best_depth
                    or (
                        len(path) == best_depth
                        and (best_actions is None or actions < best_actions)
                    )
                ):
                    best_depth = len(path)
                    best_actions = actions
                    best_final = (law_mask, feat_mask)
                    best_path = path

            # Stop expanding this node if we already used up the depth budget
            if len(path) >= max_depth:
                continue

            # If we already have a solution of depth d, there is no point in
            # exploring branches that are at or beyond depth d.
            if fast and (best_depth is not None) and len(path) >= best_depth:
                continue

            for li, new_law_mask, _ in self._expand(law_mask):
                queue.append((new_law_mask, (*path, li)))

            if total_nodes >= cap_paths:
                break

        if best_final is None or best_path is None:
            return None, total_nodes, consistent_count

        # Reconstruct the chosen path with enabled-features at each step
        steps: List[Step] = []
        cur_law = 0
        cur_feat = self.infer_features(cur_law)

        for li in best_path:
            next_law = cur_law | (1 << li)
            next_feat = self.infer_features(next_law)
            delta = next_feat & ~cur_feat
            enabled = tuple(sorted(self.feat_mask_to_names(delta)))
            lname = self.candidate_laws[li]
            steps.append(
                Step(
                    action=f"stabilize {lname}",
                    added_law=lname,
                    enabled_features=enabled,
                )
            )
            cur_law, cur_feat = next_law, next_feat

        chosen = PathResult(
            path=steps,
            final_laws=set(self.law_mask_to_names(best_final[0])),
            final_features=set(self.feat_mask_to_names(best_final[1])),
        )
        return chosen, total_nodes, consistent_count

    def find_shorter_example(self, limit_depth: int) -> List[str]:
        """
        Try to find any path with depth ≤ limit_depth that satisfies
        the observations. Returns the action sequence, or [] if none.
        """
        if limit_depth <= 0:
            return []

        Node = Tuple[int, Tuple[int, ...]]
        queue = deque([ (0, tuple()) ])

        while queue:
            law_mask, path = queue.popleft()
            feat_mask = self.infer_features(law_mask)
            if (feat_mask & self.obs_mask_feat) == self.obs_mask_feat:
                return [
                    f"stabilize {self.candidate_laws[i]}"
                    for i in path
                ]

            if len(path) >= limit_depth:
                continue

            for li, new_law_mask, _ in self._expand(law_mask):
                queue.append((new_law_mask, (*path, li)))

        return []


# ──────────────────────────────────────────────────────────────
# Higher-order look: Holds₁ / Holds₂ and model extensions
# ──────────────────────────────────────────────────────────────

EXT1: Dict[str, Set[int]] = {}              # unary extensions: name ↦ {worlds}
EXT2: Dict[str, Set[Tuple[str, str]]] = {}  # binary extensions: name ↦ {(x,y)}

REQUIRES_REL = "rel:requires"


def law_int(name: str) -> str:
    """Turn a law identifier into a unary predicate-name, e.g. 'gravity-stable' → 'law:gravity-stable'."""
    return f"law:{name}"


def feat_int(name: str) -> str:
    """Turn a feature identifier into a unary predicate-name, e.g. 'life' → 'feat:life'."""
    return f"feat:{name}"


def build_model_extensions(engine: LibraryAndPath) -> None:
    """
    Populate EXT1 and EXT2 from the engine:

      • EXT1 holds unary predicate extensions:
          - each law:ℓ is true in w iff ℓ is in the law-set of w
          - each feat:f is true in w iff f is in infer_features(w)

      • EXT2[REQUIRES_REL] contains all (feat:f, Q) pairs listed in PREREQUISITES.
    """
    EXT1.clear()
    EXT2.clear()

    # Initialize keys
    for law in engine.candidate_laws:
        EXT1[law_int(law)] = set()
    for feat in engine.feature_names:
        EXT1[feat_int(feat)] = set()

    # Unary extensions over all possible worlds
    for w in WORLD_DOMAIN:
        # laws that hold in this world
        for i, law in enumerate(engine.candidate_laws):
            if (w >> i) & 1:
                EXT1[law_int(law)].add(w)

        # features that hold in this world
        feat_mask = engine.infer_features(w)
        for i, feat in enumerate(engine.feature_names):
            if (feat_mask >> i) & 1:
                EXT1[feat_int(feat)].add(w)

    # Binary "requires" relation between intensions
    req_pairs: Set[Tuple[str, str]] = set()
    for feat, reqs in PREREQUISITES.items():
        for r in reqs:
            if r in engine.law_index:
                r_int = law_int(r)
            elif r in engine.feat_index:
                r_int = feat_int(r)
            else:
                raise KeyError(f"Unknown prerequisite symbol {r!r}")
            req_pairs.add((feat_int(feat), r_int))
    EXT2[REQUIRES_REL] = req_pairs


def Holds1(pname: str, world: int) -> bool:
    """
    Unary Holds₁ predicate:

        Holds1(P, w)

    is true exactly when world `w` is in the extension EXT1[P].
    """
    return world in EXT1.get(pname, set())


def Holds2(rname: str, x: str, y: str) -> bool:
    """
    Binary Holds₂ predicate:

        Holds2(R, x, y)

    is true exactly when the pair (x, y) is in the extension EXT2[R].
    """
    return (x, y) in EXT2.get(rname, set())


# ──────────────────────────────────────────────────────────────
# Check (harness)
# ──────────────────────────────────────────────────────────────

class CheckFailure(AssertionError):
    pass


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise CheckFailure(msg)


def run_checks(engine: LibraryAndPath, chosen: PathResult) -> List[str]:
    """
    Run a small battery of tests that exercise the FO core and the search:

      1) Holds₂ encodes key prerequisites.
      2) Holds₁ behaves correctly in tiny worlds.
      3) The chosen final world satisfies all observations.
      4) Each adopted law is individually necessary.
      5) Feature growth along the path is monotone (and matches deltas).
      6) The closure operator agrees with Holds₁ on the final features.
    """
    notes: List[str] = []

    # Base worlds
    w0 = 0
    w_grav = 1 << engine.law_index["gravity-stable"]

    # Final world (as law-mask)
    w_final = 0
    for law in chosen.final_laws:
        w_final |= 1 << engine.law_index[law]

    # 1) Requires relation encodes key dependencies
    check(
        Holds2(REQUIRES_REL, feat_int("stars"), law_int("gravity-stable")),
        "stars should require gravity-stable.",
    )
    check(
        Holds2(REQUIRES_REL, feat_int("life"), feat_int("stars")),
        "life should require stars.",
    )
    check(
        Holds2(REQUIRES_REL, feat_int("life"), feat_int("carbon-chemistry")),
        "life should require carbon-chemistry.",
    )
    notes.append("PASS 1: 'requires' relation encodes basic feature prerequisites.")

    # 2) Holds1 for simple worlds
    check(
        not Holds1(law_int("gravity-stable"), w0),
        "gravity-stable must be false in the empty world.",
    )
    check(
        Holds1(law_int("gravity-stable"), w_grav),
        "gravity-stable must hold in the single-law world.",
    )
    check(
        Holds1(feat_int("stars"), w_grav),
        "stars must appear once gravity-stable holds.",
    )
    check(
        Holds1(feat_int("galaxies"), w_grav),
        "galaxies must appear once gravity-stable holds.",
    )
    check(
        not Holds1(feat_int("life"), w_grav),
        "life must not appear with gravity alone.",
    )
    notes.append("PASS 2: Holds1 behaves correctly for laws/features in tiny worlds.")

    # 3) Observations satisfied in final world
    for obs in OBSERVATIONS:
        check(
            Holds1(feat_int(obs), w_final),
            f"Observation feature {obs!r} should hold in the final world.",
        )
    notes.append("PASS 3: Final world satisfies all observation features via Holds1.")

    # 4) Final law set is pointwise necessary (no single law is dispensable)
    for law in sorted(chosen.final_laws):
        li = engine.law_index[law]
        alt = w_final & ~(1 << li)
        holds_all = all(Holds1(feat_int(o), alt) for o in OBSERVATIONS)
        check(
            not holds_all,
            f"Law {law!r} appears dispensable; dropping it still satisfies observations.",
        )
    notes.append("PASS 4: Each adopted law is individually necessary for the observations.")

    # 5) Monotonicity of feature growth along chosen path
    cur_mask = 0
    prev_feats = engine.infer_features(cur_mask)
    for step in chosen.path:
        li = engine.law_index[step.added_law]  # type: ignore[arg-type]
        cur_mask |= 1 << li
        now_feats = engine.infer_features(cur_mask)

        # Monotone: no feature is ever lost
        check(
            (prev_feats & ~now_feats) == 0,
            "Features must be monotone along the chosen path.",
        )

        # Enabled-features bookkeeping matches the actual delta
        delta = now_feats & ~prev_feats
        delta_names = tuple(sorted(engine.feat_mask_to_names(delta)))
        check(
            delta_names == step.enabled_features,
            f"Enabled-features for step {step.action!r} do not match recomputed delta.",
        )
        prev_feats = now_feats

    notes.append("PASS 5: Features grow monotonically and enabled-features are consistent.")

    # 6) Engine vs Holds1 agreement on final features
    final_feat_mask = engine.infer_features(w_final)
    feats_from_engine = set(engine.feat_mask_to_names(final_feat_mask))
    feats_from_holds1 = {
        feat for feat in engine.feature_names if Holds1(feat_int(feat), w_final)
    }
    check(
        feats_from_engine == feats_from_holds1,
        "Engine.infer_features must agree with Holds1/EXT1 on final features.",
    )
    notes.append("PASS 6: infer_features and Holds1 agree on the final feature set.")

    return notes


def arc_answer(
    engine: LibraryAndPath,
    chosen: Optional[PathResult],
    total_nodes: int,
    consistent_count: int,
) -> None:
    """Print the main answer: path, final laws/features, and Holds₁ view."""
    print("Answer")
    print("------")

    if chosen is None:
        print("No path of law adoptions satisfies the observations.")
        print()
        return

    print("Target observations:")
    print("  " + ", ".join(sorted(OBSERVATIONS)) + ".")
    print()
    print(f"Search explored {total_nodes} distinct law-sets (nodes).")
    print(f"Found {consistent_count} consistent endpoints.")
    print()
    print("Chosen path (minimal number of law adoptions):")
    for i, step in enumerate(chosen.path, start=1):
        enabled = ", ".join(step.enabled_features) if step.enabled_features else "—"
        print(f" {i}. {step.action:<30} → enables: {enabled}")
    print()
    print("Final laws:     " + ", ".join(sorted(chosen.final_laws)) + ".")
    print("Final features: " + ", ".join(sorted(chosen.final_features)) + ".")

    # Show Holds1 on the final world
    w_final = 0
    for law in chosen.final_laws:
        w_final |= 1 << engine.law_index[law]

    print()
    print(f"Final world id (law-mask) = {w_final}")
    print("Via Holds₁ we have:")
    for obs in sorted(OBSERVATIONS):
        pname = feat_int(obs)
        print(f"  Holds1({pname}, {w_final}) = {Holds1(pname, w_final)}")
    print()


def arc_reason(
    engine: LibraryAndPath,
    chosen: Optional[PathResult],
    total_nodes: int,
    consistent_count: int,
) -> None:
    """Explain the modeling choices and the BFS selection criterion."""
    print("Reason why")
    print("----------")
    print("We imagine a tiny 'library' of candidate laws and a space of worlds:")
    print("  • Worlds are subsets of CANDIDATE_LAWS, encoded as integers 0..2^N−1.")
    print("  • Each law ℓ gives a unary predicate-name law:ℓ.")
    print("  • Each emergent feature f gives a unary predicate-name feat:f.")
    print()
    print("The higher-order-looking predicates are interpreted by a fixed FO core:")
    print("  • Holds₁(P, w)  — the unary predicate named by P holds in world w.")
    print("      - if P = law:ℓ, this means 'ℓ is among the laws of w';")
    print("      - if P = feat:f, this means 'f is supported by all its prerequisites in w'.")
    print("  • Holds₂(rel:requires, feat:f, Q)  — the intension Q is a direct prerequisite of f.")
    print()
    print("Implementation-wise, the FO core is a closure operator on features:")
    print("  starting from a law-mask, we repeatedly add any feature whose law")
    print("  and feature prerequisites are already satisfied, until a fixed point.")
    print()
    print("The search then explores law-adoption paths breadth-first from the empty world.")
    print("Whenever a world w satisfies all observation features O (i.e.")
    print("  for every o in O: Holds1(feat:o, w) is true), it is a candidate endpoint.")
    print("Among all such endpoints we keep one with:")
    print("  • minimal path length (fewest adoptions), and")
    print("  • if there are ties, lexicographically smallest action sequence.")
    print()
    if chosen is not None:
        print("The printed plan is therefore a shortest explanation, in terms of")
        print("law adoptions, of how our observation-set can obtain given this library.")
    else:
        print("In this configuration there happens to be no such world (no chosen path).")
    print()


def arc_check(engine: LibraryAndPath, chosen: Optional[PathResult]) -> None:
    """Run and report the harness checks."""
    print("Check (harness)")
    print("---------------")
    if chosen is None:
        print("No chosen path; skipping checks.")
        print()
        return
    try:
        notes = run_checks(engine, chosen)
    except CheckFailure as e:
        print("FAIL:", e)
        raise
    else:
        for line in notes:
            print(line)
        print("All checks passed.")
    print()


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def main() -> None:
    engine = LibraryAndPath(CANDIDATE_LAWS, PREREQUISITES, OBSERVATIONS)
    build_model_extensions(engine)
    chosen, total_nodes, consistent_count = engine.search(
        MAX_DEPTH,
        CAP_PATHS,
        FAST_THOROUGH,
    )
    arc_answer(engine, chosen, total_nodes, consistent_count)
    arc_reason(engine, chosen, total_nodes, consistent_count)
    arc_check(engine, chosen)


if __name__ == "__main__":
    main()

