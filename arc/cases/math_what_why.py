#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
math_what_why.py
================

Mathematics: the WHAT and the WHY
---------------------------------
This script builds a *shortest* plan — a sequence of axiom adoptions —

    adopt classical-logic
    adopt set-existence
    adopt function-formation
    …

such that, in the final “mathematical world”, a group of target concepts
becomes available:

    arithmetic, topology, geometry, calculus,
    category-theory, invariants, transfer-principle, explanatory-power.

Each world is a set of adopted axioms; concepts (like “reals” or
“category-theory”) appear once all their prerequisites are available.


Higher-order look, first-order core
-----------------------------------
We follow the “higher-order look, first-order core” view from

    https://josd.github.io/higher-order-look-first-order-core/

in a very concrete way.

* Worlds are encoded as bit-masks over the candidate axioms.
* Every axiom `a` has a unary predicate-name  `ax:a`.
* Every concept `c` has a unary predicate-name `cx:c`.
* A single binary relation-name `rel:requires` links concepts to their
  direct prerequisites (axioms or other concepts).

The semantic work is done by one first-order-looking predicate:

    Holds₁(P, w)

read as “the unary predicate named by P holds in world w”.

On the Python side we implement it by an extensional model:

    EXT1: Dict[str, Set[int]]

mapping each *intension* `P` (like "ax:classical-logic" or "cx:calculus") to
the set of worlds `w` where it holds. This is derived from an explicit
closure operator

    infer_concepts(ax_mask) -> concept_mask

which computes the least fixed point of concept derivation given a set of
axioms. A second predicate

    Holds₂("rel:requires", X, Y)

reads “intension Y is a direct prerequisite of concept X” and is implemented
as a fixed extension

    EXT2["rel:requires"] ⊆ { (cx:c, ax:a) or (cx:c, cx:d) }.

No external reasoner is involved; everything is done in this file:
bit-masks, closure, search, Holds₁ / Holds₂, and a small test harness.


What the program prints
-----------------------
Running

    python3 math_what_why.py

produces three sections:

1) Answer
   * the target observation concepts,
   * the minimal sequence of axiom adoptions,
   * the final set of axioms and concepts,
   * and a few sample Holds₁ judgements for the final world.

2) Reason why
   * how worlds, axioms, concepts, and Holds₁ / Holds₂ are interpreted,
   * why the search returns a shortest plan.

3) Check (harness)
   * at least six deterministic checks, including that:
       - Holds₂ encodes key “requires” dependencies,
       - Holds₁ behaves correctly in small toy worlds,
       - the final world really satisfies all observation concepts,
       - every adopted axiom is individually necessary,
       - concept growth along the path is monotone (and deltas are correct),
       - the closure operator agrees with Holds₁ on the final concepts.

Python 3.9+; no external packages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from collections import deque
import random


# -----------------------------------------------------------------------------
# Configuration: axioms, concepts, observations
# -----------------------------------------------------------------------------

CANDIDATE_AXIOMS: List[str] = [
    "classical-logic",
    "set-existence",
    "function-formation",
    "natural-induction",
    "algebra-operations",
    "order-completeness",
    "topology-axioms",
    "symmetry-axioms",
]

# Concepts and their prerequisites (axioms or other concepts)
PREREQUISITES: Dict[str, Set[str]] = {
    # Foundations
    "proofs": {"classical-logic"},
    "sets": {"set-existence"},
    "functions": {"sets", "function-formation"},

    # Arithmetic & algebra
    "naturals": {"sets", "natural-induction"},
    "arithmetic": {"naturals"},
    "rings": {"sets", "algebra-operations"},
    "fields": {"rings"},

    # Analysis & geometry
    "reals": {"fields", "order-completeness"},
    "topology": {"sets", "topology-axioms"},
    "analysis": {"reals", "proofs"},
    "geometry": {"reals", "symmetry-axioms"},
    "calculus": {"analysis"},

    # Higher viewpoints
    "category-theory": {"functions", "proofs"},

    # Algebraic structures driven by symmetry axioms
    "groups": {"sets", "symmetry-axioms"},

    # Explanatory goals
    "invariants": {"proofs", "groups", "topology"},
    "transfer-principle": {"category-theory", "proofs"},
    "explanatory-power": {"invariants", "transfer-principle"},
}

# Concepts we want to hold in the final state (the “what” and the “why”)
OBSERVATIONS: Set[str] = {
    "arithmetic",
    "topology",
    "geometry",
    "calculus",
    "category-theory",
    "invariants",
    "transfer-principle",
    "explanatory-power",
}

# Search controls
MAX_DEPTH: int = len(CANDIDATE_AXIOMS)
CAP_PATHS: int = 200_000
FAST_THOROUGH: bool = True  # stop exploring deeper once a shortest plan is found
PERMUTATION_TRIALS: int = 0  # >0 to stress-test under shuffled axiom orders

NUM_AXIOMS: int = len(CANDIDATE_AXIOMS)
WORLD_DOMAIN: Tuple[int, ...] = tuple(range(1 << NUM_AXIOMS))  # all possible axiom-sets


# -----------------------------------------------------------------------------
# Data structures for plans and results
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class Step:
    """
    One action in the plan.

    - action: human text like "adopt classical-logic"
    - added_axiom: the axiom name added at this step
    - enabled_concepts: concepts that became available *at this step*
    """
    action: str
    added_axiom: Optional[str] = None
    enabled_concepts: Tuple[str, ...] = ()


@dataclass
class PathResult:
    path: List[Step]
    final_axioms: Set[str]
    final_concepts: Set[str]


# -----------------------------------------------------------------------------
# Engine: closure on concepts + BFS over axiom adoptions
# -----------------------------------------------------------------------------

class MathWhatWhy:
    """
    Tiny engine:

      • worlds = bit-masks over CANDIDATE_AXIOMS,
      • infer_concepts(ax_mask) = closure of concepts supported by that world,
      • search(...) = breadth-first search for a shortest plan achieving OBSERVATIONS.
    """

    def __init__(
        self,
        candidate_axioms: List[str],
        prereq: Dict[str, Set[str]],
        observations: Set[str],
    ) -> None:
        # Names and indices
        self.candidate_axioms = list(candidate_axioms)
        self.observations = set(observations)
        self.concept_names = list(prereq.keys())

        self.ax_index: Dict[str, int] = {
            a: i for i, a in enumerate(self.candidate_axioms)
        }
        self.cx_index: Dict[str, int] = {
            c: i for i, c in enumerate(self.concept_names)
        }

        # For each concept cᵢ:
        #   req_ax_mask[i]  = bit-mask of required axioms
        #   req_cx_mask[i]  = bit-mask of required concepts
        self.req_ax_mask: List[int] = [0] * len(self.concept_names)
        self.req_cx_mask: List[int] = [0] * len(self.concept_names)

        for c, reqs in prereq.items():
            ci = self.cx_index[c]
            ax_mask = 0
            cx_mask = 0
            for r in reqs:
                if r in self.ax_index:
                    ax_mask |= 1 << self.ax_index[r]
                elif r in self.cx_index:
                    cx_mask |= 1 << self.cx_index[r]
                else:
                    raise KeyError(f"Unknown prerequisite: {r}")
            self.req_ax_mask[ci] = ax_mask
            self.req_cx_mask[ci] = cx_mask

        # Observation mask (target concepts)
        self.obs_mask_cx = 0
        for o in self.observations:
            self.obs_mask_cx |= 1 << self.cx_index[o]

        # Cache: concepts implied by a given axiom set
        self._infer_cache: Dict[int, int] = {}

    # ---- Convenience: masks ↔ names ---------------------------------------

    def ax_mask_to_names(self, ax_mask: int) -> List[str]:
        return [
            name
            for i, name in enumerate(self.candidate_axioms)
            if (ax_mask >> i) & 1
        ]

    def cx_mask_to_names(self, cx_mask: int) -> List[str]:
        return [
            name
            for i, name in enumerate(self.concept_names)
            if (cx_mask >> i) & 1
        ]

    # ---- Closure: which concepts appear under a given axiom set? ----------

    def infer_concepts(self, ax_mask: int) -> int:
        """
        Given a set of axioms (as a bit-mask), compute the closure of all
        concepts supported by those axioms and by one another.

        This is the core FO operator behind Holds₁ for concepts:

            Holds1("cx:c", w)  ⇔  bit for c is set in infer_concepts(w).
        """
        cached = self._infer_cache.get(ax_mask)
        if cached is not None:
            return cached

        cx_mask = 0
        changed = True
        while changed:
            changed = False
            for ci in range(len(self.concept_names)):
                if (cx_mask >> ci) & 1:
                    continue  # already present

                # Missing required axioms?
                if (self.req_ax_mask[ci] & ~ax_mask) != 0:
                    continue

                # Missing required concepts?
                if (self.req_cx_mask[ci] & ~cx_mask) != 0:
                    continue

                cx_mask |= 1 << ci
                changed = True

        self._infer_cache[ax_mask] = cx_mask
        return cx_mask

    # ---- Neighbours: adopt one new axiom not yet present ------------------

    def _expand(self, ax_mask: int) -> List[Tuple[int, int, int]]:
        """
        For a given set of adopted axioms `ax_mask`, return all one-step
        extensions:

            (axiom_index, new_ax_mask, new_cx_mask)
        """
        out: List[Tuple[int, int, int]] = []
        for ai in range(len(self.candidate_axioms)):
            if (ax_mask >> ai) & 1:
                continue
            new_ax = ax_mask | (1 << ai)
            new_cx = self.infer_concepts(new_ax)
            out.append((ai, new_ax, new_cx))
        return out

    # ---- BFS search for a shortest plan -----------------------------------

    def search(
        self,
        max_depth: int,
        cap_paths: int,
        fast: bool,
    ) -> Tuple[Optional[PathResult], int, int]:
        """
        Breadth-first search over axiom-adoption plans.

        Returns:
            (chosen_result_or_None, total_nodes_explored, consistent_endpoints)

        * We start from the empty world (no axioms).
        * At each step we add one previously absent axiom.
        * A world is “consistent” if all observation concepts hold there.
        * Among consistent worlds, we keep a minimal-depth, and if there are
          ties we choose the lexicographically smallest action sequence.
        """
        Node = Tuple[int, Tuple[int, ...]]  # (axiom_mask, tuple of axiom indices)

        q: deque[Node] = deque([(0, tuple())])
        total_nodes = 0
        consistent_count = 0

        best_depth: Optional[int] = None
        best_actions: Optional[Tuple[str, ...]] = None
        best_final: Optional[Tuple[int, int]] = None  # (ax_mask, cx_mask)
        best_path_indices: Optional[Tuple[int, ...]] = None

        while q:
            ax_mask, path = q.popleft()
            cx_mask = self.infer_concepts(ax_mask)
            total_nodes += 1

            # Goal met?
            if (cx_mask & self.obs_mask_cx) == self.obs_mask_cx:
                consistent_count += 1
                actions = tuple(
                    f"adopt {self.candidate_axioms[i]}" for i in path
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
                    best_final = (ax_mask, cx_mask)
                    best_path_indices = path

            if len(path) >= max_depth:
                continue

            # In FAST mode, skip exploring branches that are already as deep
            # as the best plan we have found.
            if fast and (best_depth is not None) and len(path) >= best_depth:
                continue

            for ai, new_ax, _ in self._expand(ax_mask):
                q.append((new_ax, (*path, ai)))

            if total_nodes >= cap_paths:
                break

        if best_final is None or best_path_indices is None:
            return None, total_nodes, consistent_count

        # Build the chosen path with enabled-concept deltas
        steps: List[Step] = []
        cur_ax = 0
        cur_cx = self.infer_concepts(cur_ax)

        for ai in best_path_indices:
            next_ax = cur_ax | (1 << ai)
            next_cx = self.infer_concepts(next_ax)
            delta_cx = next_cx & ~cur_cx
            enabled = tuple(sorted(self.cx_mask_to_names(delta_cx)))
            ax_name = self.candidate_axioms[ai]
            steps.append(
                Step(
                    action=f"adopt {ax_name}",
                    added_axiom=ax_name,
                    enabled_concepts=enabled,
                )
            )
            cur_ax, cur_cx = next_ax, next_cx

        chosen = PathResult(
            path=steps,
            final_axioms=set(self.ax_mask_to_names(best_final[0])),
            final_concepts=set(self.cx_mask_to_names(best_final[1])),
        )
        return chosen, total_nodes, consistent_count

    # ---- Helper: is there any strictly shorter plan? ----------------------

    def find_shorter_example(self, limit_depth: int) -> List[str]:
        """
        Try to find a plan of length ≤ limit_depth that already satisfies the
        observations. Return the corresponding action sequence, or [] if none.
        """
        if limit_depth <= 0:
            return []

        Node = Tuple[int, Tuple[int, ...]]
        q: deque[Node] = deque([(0, tuple())])

        while q:
            ax_mask, path = q.popleft()
            cx_mask = self.infer_concepts(ax_mask)
            if (cx_mask & self.obs_mask_cx) == self.obs_mask_cx:
                return [
                    f"adopt {self.candidate_axioms[i]}" for i in path
                ]

            if len(path) >= limit_depth:
                continue

            for ai, new_ax, _ in self._expand(ax_mask):
                q.append((new_ax, (*path, ai)))

        return []


# -----------------------------------------------------------------------------
# Higher-order look: Holds₁ / Holds₂ and model extensions
# -----------------------------------------------------------------------------

EXT1: Dict[str, Set[int]] = {}                 # unary: name ↦ {worlds}
EXT2: Dict[str, Set[Tuple[str, str]]] = {}     # binary: name ↦ set of pairs

REQUIRES_REL = "rel:requires"


def ax_int(name: str) -> str:
    """Encode an axiom symbol as a unary predicate-name, e.g. 'classical-logic' → 'ax:classical-logic'."""
    return f"ax:{name}"


def cx_int(name: str) -> str:
    """Encode a concept symbol as a unary predicate-name, e.g. 'calculus' → 'cx:calculus'."""
    return f"cx:{name}"


def build_model_extensions(engine: MathWhatWhy) -> None:
    """
    Populate EXT1 and EXT2 from the engine:

      • EXT1 holds unary predicate extensions:
          - ax:a is true in w iff a is in the axiom-set of w;
          - cx:c is true in w iff c is in infer_concepts(w).

      • EXT2[REQUIRES_REL] contains all (cx:c, Q) pairs listed in PREREQUISITES,
        with Q either ax:a or cx:d.
    """
    EXT1.clear()
    EXT2.clear()

    # Prepare keys
    for ax in engine.candidate_axioms:
        EXT1[ax_int(ax)] = set()
    for c in engine.concept_names:
        EXT1[cx_int(c)] = set()

    # Unary extensions over all possible worlds
    for w in WORLD_DOMAIN:
        # axioms that hold in this world
        for i, ax in enumerate(engine.candidate_axioms):
            if (w >> i) & 1:
                EXT1[ax_int(ax)].add(w)

        # concepts that hold in this world
        cx_mask = engine.infer_concepts(w)
        for i, c in enumerate(engine.concept_names):
            if (cx_mask >> i) & 1:
                EXT1[cx_int(c)].add(w)

    # Binary requires relation between intensions
    req_pairs: Set[Tuple[str, str]] = set()
    for c, reqs in PREREQUISITES.items():
        for r in reqs:
            if r in engine.ax_index:
                q_int = ax_int(r)
            elif r in engine.cx_index:
                q_int = cx_int(r)
            else:
                raise KeyError(f"Unknown prerequisite symbol {r!r}")
            req_pairs.add((cx_int(c), q_int))
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


# -----------------------------------------------------------------------------
# Check (harness)
# -----------------------------------------------------------------------------

class CheckFailure(AssertionError):
    pass


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise CheckFailure(msg)


def run_checks(engine: MathWhatWhy, chosen: PathResult) -> List[str]:
    """
    Run a battery of checks covering both the Holds₁/₂ view and the search:

      1) Holds₂ encodes important requires-dependencies.
      2) Holds₁ behaves correctly in simple worlds.
      3) The chosen final world satisfies all observations.
      4) Concepts from infer_concepts match those from Holds₁.
      5) Concept growth along the path is monotone and matches deltas.
      6) The final axiom-set is pointwise necessary (no single axiom dispensable).
      7) No strictly shorter plan exists.
      8) The concept dependency graph is acyclic.
      9) (Optionally) the result is robust under permutations of axiom order.
    """
    notes: List[str] = []

    # Base worlds for small tests
    w0 = 0
    w_logic = 1 << engine.ax_index["classical-logic"]
    w_sets = 1 << engine.ax_index["set-existence"]
    w_logic_sets = w_logic | w_sets

    # Final world (as axiom mask)
    w_final = 0
    for ax in chosen.final_axioms:
        w_final |= 1 << engine.ax_index[ax]

    # 1) Requires relation encodes key dependencies
    check(
        Holds2(REQUIRES_REL, cx_int("proofs"), ax_int("classical-logic")),
        "proofs should require classical-logic.",
    )
    check(
        Holds2(REQUIRES_REL, cx_int("functions"), cx_int("sets")),
        "functions should require sets.",
    )
    check(
        Holds2(REQUIRES_REL, cx_int("functions"), ax_int("function-formation")),
        "functions should require function-formation.",
    )
    check(
        Holds2(REQUIRES_REL, cx_int("invariants"), cx_int("groups")),
        "invariants should require groups.",
    )
    notes.append("PASS 1: Holds₂(rel:requires, …) encodes key dependencies.")

    # 2) Holds1 in small toy worlds
    # Empty world: no axioms, no concepts
    check(
        not Holds1(ax_int("classical-logic"), w0),
        "classical-logic must be false in the empty world.",
    )
    check(
        not Holds1(cx_int("proofs"), w0),
        "proofs must be unavailable in the empty world.",
    )

    # World with only classical-logic
    check(
        Holds1(ax_int("classical-logic"), w_logic),
        "classical-logic must hold in the world where it is the only adopted axiom.",
    )
    check(
        Holds1(cx_int("proofs"), w_logic),
        "proofs must appear once classical-logic holds.",
    )

    # World with only set-existence
    check(
        Holds1(ax_int("set-existence"), w_sets),
        "set-existence must hold in its singleton world.",
    )
    check(
        Holds1(cx_int("sets"), w_sets),
        "sets must appear once set-existence holds.",
    )

    # World with both classical-logic and set-existence:
    #   we should have proofs and sets, but still not functions.
    check(
        Holds1(cx_int("proofs"), w_logic_sets),
        "proofs must hold when classical-logic is adopted.",
    )
    check(
        Holds1(cx_int("sets"), w_logic_sets),
        "sets must hold when set-existence is adopted.",
    )
    check(
        not Holds1(cx_int("functions"), w_logic_sets),
        "functions must not hold until function-formation is adopted.",
    )
    notes.append("PASS 2: Holds₁ behaves correctly in small toy worlds.")

    # 3) Observations satisfied in final world
    for obs in OBSERVATIONS:
        check(
            Holds1(cx_int(obs), w_final),
            f"Observation concept {obs!r} should hold in the final world.",
        )
    notes.append("PASS 3: Final world satisfies all observation concepts via Holds₁.")

    # 4) Concepts from infer_concepts vs Holds1
    final_cx_mask = engine.infer_concepts(w_final)
    from_engine = set(engine.cx_mask_to_names(final_cx_mask))
    from_holds1 = {
        c for c in engine.concept_names if Holds1(cx_int(c), w_final)
    }
    check(
        from_engine == from_holds1,
        "infer_concepts must agree with Holds₁/EXT1 on final concepts.",
    )
    notes.append("PASS 4: infer_concepts and Holds₁ agree on the final concept set.")

    # 5) Monotonicity of concepts along the chosen path and delta bookkeeping
    ax_prog = 0
    prev_cx = engine.infer_concepts(ax_prog)
    for step in chosen.path:
        ai = engine.ax_index[step.added_axiom] if step.added_axiom else None
        if ai is None or ((ax_prog >> ai) & 1):
            check(False, "Path should never reuse an axiom.")
        ax_prog |= 1 << ai
        now_cx = engine.infer_concepts(ax_prog)

        # Monotone: no concept is ever lost.
        check(
            (prev_cx & ~now_cx) == 0,
            "Concepts must grow monotonically along the chosen path.",
        )

        # Enabled concepts must match the actual delta
        delta = now_cx & ~prev_cx
        delta_names = tuple(sorted(engine.cx_mask_to_names(delta)))
        check(
            delta_names == step.enabled_concepts,
            f"Enabled concepts for step {step.action!r} do not match recomputed delta.",
        )

        prev_cx = now_cx

    notes.append("PASS 5: Concepts grow monotonically and enabled-concepts are consistent.")

    # 6) Pointwise necessity: dropping any adopted axiom should break the goal
    for ax in sorted(chosen.final_axioms):
        ai = engine.ax_index[ax]
        alt = w_final & ~(1 << ai)
        holds_all = all(Holds1(cx_int(o), alt) for o in OBSERVATIONS)
        check(
            not holds_all,
            f"Axiom {ax!r} appears dispensable; dropping it still satisfies observations.",
        )
    notes.append("PASS 6: Each adopted axiom is individually necessary for the observations.")

    # 7) No strictly shorter plan exists
    if len(chosen.path) > 0:
        shorter = engine.find_shorter_example(limit_depth=len(chosen.path) - 1)
        check(
            shorter == [],
            f"Found a strictly shorter plan: {shorter}",
        )
    notes.append("PASS 7: Chosen plan is shortest with respect to this search space.")

    # 8) Concept dependency graph is acyclic
    def has_cycle() -> bool:
        graph: Dict[str, Set[str]] = {c: set() for c in engine.concept_names}
        for c in engine.concept_names:
            ci = engine.cx_index[c]
            for rci in range(len(engine.concept_names)):
                if (engine.req_cx_mask[ci] >> rci) & 1:
                    graph[c].add(engine.concept_names[rci])

        visited: Set[str] = set()
        stack: Set[str] = set()

        def dfs(u: str) -> bool:
            visited.add(u)
            stack.add(u)
            for v in graph[u]:
                if v not in visited and dfs(v):
                    return True
                if v in stack:
                    return True
            stack.remove(u)
            return False

        for node in graph:
            if node not in visited and dfs(node):
                return True
        return False

    check(
        not has_cycle(),
        "Concept dependency graph must be acyclic.",
    )
    notes.append("PASS 8: Concept dependency graph is acyclic (no circular definitions).")

    # 9) Optional: robustness under permutations of axiom order
    mismatches: List[Dict[str, object]] = []
    base_axioms = set(chosen.final_axioms)
    base_len = len(chosen.path)

    for i in range(PERMUTATION_TRIALS):
        perm = list(engine.candidate_axioms)
        random.shuffle(perm)
        if perm == engine.candidate_axioms:
            random.shuffle(perm)

        engine2 = MathWhatWhy(perm, PREREQUISITES, engine.observations)
        build_model_extensions(engine2)
        chosen2, _, _ = engine2.search(MAX_DEPTH, CAP_PATHS, fast=FAST_THOROUGH)
        if not chosen2:
            mismatches.append({"trial": i + 1, "issue": "no_path_under_permutation"})
        else:
            eq_axioms = set(chosen2.final_axioms) == base_axioms
            eq_len = len(chosen2.path) == base_len
            if not (eq_axioms and eq_len):
                mismatches.append(
                    {
                        "trial": i + 1,
                        "final_axioms_equal": eq_axioms,
                        "path_length_equal": eq_len,
                    }
                )

    check(
        len(mismatches) == 0,
        f"Permutation robustness failed: {mismatches}",
    )
    if PERMUTATION_TRIALS > 0:
        notes.append("PASS 9: Result is robust under tested permutations of axiom order.")
    else:
        notes.append("PASS 9: Permutation robustness trivially holds (no trials requested).")

    return notes


# -----------------------------------------------------------------------------
# ARC: Answer / Reason why / Check
# -----------------------------------------------------------------------------

def arc_answer(
    engine: MathWhatWhy,
    chosen: Optional[PathResult],
    total_nodes: int,
    consistent_count: int,
) -> None:
    print("Answer")
    print("------")

    print("Target observation concepts:")
    print("  " + ", ".join(sorted(OBSERVATIONS)) + ".")
    print()

    if chosen is None:
        print(f"Explored {total_nodes} distinct axiom-sets; no world satisfies them all.")
        print()
        return

    print(f"Search explored {total_nodes} distinct axiom-sets (nodes).")
    print(f"Found {consistent_count} consistent endpoints.")
    print()
    print("Chosen plan (minimal number of axiom adoptions):")
    for i, step in enumerate(chosen.path, start=1):
        enabled = ", ".join(step.enabled_concepts) if step.enabled_concepts else "—"
        print(f" {i}. {step.action:<30} → enables: {enabled}")
    print()
    print("Final axioms:   " + ", ".join(sorted(chosen.final_axioms)) + ".")
    print("Final concepts: " + ", ".join(sorted(chosen.final_concepts)) + ".")

    # Show Holds1 on the final world
    w_final = 0
    for ax in chosen.final_axioms:
        w_final |= 1 << engine.ax_index[ax]

    print()
    print(f"Final world id (axiom-mask) = {w_final}")
    print("Sample Holds₁ judgements for the final world:")
    sample_concepts = sorted(OBSERVATIONS)[:4]  # a small sample
    for c in sample_concepts:
        pname = cx_int(c)
        print(f"  Holds1({pname}, {w_final}) = {Holds1(pname, w_final)}")
    print()


def arc_reason(
    engine: MathWhatWhy,
    chosen: Optional[PathResult],
    total_nodes: int,
    consistent_count: int,
) -> None:
    print("Reason why")
    print("----------")
    print("We model mathematics at two levels:")
    print("  • A *world* is a set of adopted axioms, encoded as an integer 0..2^N−1.")
    print("  • Each axiom a has a unary predicate-name ax:a, each concept c has cx:c.")
    print("    The fixed predicate Holds₁(ax:a, w) says “a is adopted in world w”.")
    print("    The fixed predicate Holds₁(cx:c, w) says “c is available in world w”.")
    print()
    print("Direct dependencies between intensions are recorded by Holds₂:")
    print("  Holds₂(rel:requires, cx:c, Q) means that Q (an ax:… or cx:…) is a")
    print("  direct prerequisite of concept c. We compile these from PREREQUISITES.")
    print()
    print("The real semantic work is done by a first-order closure operator:")
    print("  infer_concepts(ax_mask) repeatedly adds any concept whose axiom")
    print("  and concept prerequisites are already satisfied, until a fixed point.")
    print("This operator induces EXT1 and therefore all Holds₁ facts.")
    print()
    print("The search then explores axiom-adoption paths breadth-first, starting")
    print("from the empty world (no axioms). Whenever a world w satisfies all")
    print("observation concepts, it is a candidate endpoint. Among these:")
    print("  • we keep a world with the smallest number of adopted axioms, and")
    print("  • if there are ties, the lexicographically smallest action sequence.")
    print()
    if chosen is not None:
        print("The printed plan is therefore a shortest explanation, in terms of")
        print("axiom adoptions, of how our chosen WHAT/WHY concepts can obtain.")
    else:
        print("In this configuration there is simply no world that realises all")
        print("observation concepts at once.")
    print()


def arc_check(engine: MathWhatWhy, chosen: Optional[PathResult]) -> None:
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


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:
    engine = MathWhatWhy(CANDIDATE_AXIOMS, PREREQUISITES, OBSERVATIONS)
    build_model_extensions(engine)
    chosen, total_nodes, consistent_count = engine.search(
        MAX_DEPTH,
        CAP_PATHS,
        FAST_THOROUGH,
    )
    arc_answer(engine, chosen, total_nodes, consistent_count)
    arc_reason(engine, chosen, total_nodes, consistent_count)
    if chosen is not None:
        arc_check(engine, chosen)
    else:
        print("Check (harness)")
        print("---------------")
        print("No chosen path; skipping checks.")
        print()


if __name__ == "__main__":
    main()

