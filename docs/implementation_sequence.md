# Recommended implementation sequence

AstroLyrica should grow from stable local foundations toward richer automation. The recommended order is:

1. **Stabilize operating docs.** Keep `AGENTS.md`, build tracks, roadmap notes, and implementation guidance current so future Codex tasks can work from repository context instead of pasted prompts.
2. **Enrich `data/combinations.yaml` schema.** Make relational symbolic interpretation more expressive before adding larger workflow layers.
3. **Add experiment controls.** Extend local prompt assembly with clearer knobs, optional sections, and repeatable configuration.
4. **Add a batch experiment runner.** Discover `experiments/*.yaml`, generate prompts without manual path edits, and write predictable outputs and summaries.
5. **Add a local prompt preview UI.** Build the first Scriptorium surface as a minimal local interface for choosing inputs and previewing assembled prompts.
6. **Only then consider API calls or publishing automation.** LLM API calls, social posting, publishing automation, payment, authentication, and user accounts should remain out of scope unless explicitly requested.
