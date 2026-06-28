# AstroLyrica build tracks

This document groups future work into coherent tracks so Codex tasks can target one area at a time without losing the larger project shape.

## Track 1 — Symbolic Data Architecture

**Goal:** make the symbolic database richer and more relational.

This track expands the human-editable YAML data that gives AstroLyrica its interpretive specificity. Work may include planets, signs, houses, aspects, conditions, combinations, commonplace images, voices, and forms. Changes should preserve symbolic nuance, relational interpretation, originality guardrails, and clear validation rules.

## Track 2 — Prompt Assembly Engine

**Goal:** improve `src/build_prompt.py` into a robust local prompt compiler.

This track strengthens local prompt generation without adding LLM API calls. Work may include experiment controls, combination matching, optional sections, support for multiple experiments, and clearer output paths. Generated prompt files should be updated whenever generator behavior changes.

## Track 3 — Experiment Runner

**Goal:** run many local experiments without manually changing paths.

This track adds workflow tools for discovering `experiments/*.yaml`, generating prompts in batches, enforcing output naming conventions, and producing summaries that make local experimentation easier to review.

## Track 4 — Scriptorium UI

**Goal:** create a minimal local web interface for selecting astrology inputs and generating assembled prompts.

This track is for a lightweight local preview and selection interface, not a full application. It should avoid authentication, payments, social posting, and production publishing features unless those are explicitly requested later.

## Track 5 — Starweather Publishing Prep

**Goal:** prepare a future daily output workflow.

This track may introduce metadata, schedule fields, and platform-specific formatting needed for future publishing review. It should not perform real posting, call platform APIs, or automate social publishing unless explicitly requested.
