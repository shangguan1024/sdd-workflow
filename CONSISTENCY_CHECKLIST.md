# Documentation Consistency Checklist

## Source of Truth

`SKILL.md` is the core definition for:

- Plugin path and setup.
- Tool and CLI fallback order.
- Phase overview and gate protocol.
- Artifact contract and compatibility aliases.
- Recovery rules.

Other files must extend these details, not contradict them.

## Consistency Checks

### Plugin Pairing

- [ ] `SKILL.md`, `USAGE.md`, and `README.md` mention `E:/workspace/coding/tools/sdd-workflow-plugin`.
- [ ] Setup uses `dist/index.js` for opencode plugin config.
- [ ] CLI fallback uses `bin/sdd.js`.
- [ ] No current file claims the plugin is unavailable or nonexistent.

### Tool Names

- [ ] Plugin tools use underscores: `sdd_init`, `sdd_start`, `sdd_gate`, `sdd_status`, `sdd_refresh`, `sdd_complete`.
- [ ] CLI commands use spaces: `sdd init`, `sdd start`, `sdd gate`, `sdd status`, `sdd refresh`, `sdd complete`.
- [ ] Gate approval requires explicit user confirmation before `approve`.

### Phase Numbering

- [ ] Human workflow uses Phase 0-6.
- [ ] Plugin internal Research phase `-1` is documented.
- [ ] Gate commands use destination phase numbers.

### Artifacts

- [ ] Canonical design file is `docs/features/<feature>/design.md`.
- [ ] `design-doc.md` is documented as a compatibility alias.
- [ ] Canonical plan file is `docs/features/<feature>/task_plan.md`.
- [ ] `implementation-plan.md` is documented as a compatibility alias.
- [ ] `findings.md` phase summary markers are documented for plugin compression.
- [ ] `.sdd/state.json` is never edited manually.

### Visualization Strategy

- [ ] PlantUML is used for interaction diagrams.
- [ ] Mermaid is used for flowcharts and state diagrams.
- [ ] No guide recommends Mermaid sequence diagrams for interactions.

## Validation Commands

```bash
rg -n "documentation-only|does not provide `sdd|Plugin references \\(npm package does not exist\\)" . --glob "*.md" --glob "!CHANGELOG.md" --glob "!CONSISTENCY_CHECKLIST.md"
rg -n "sequenceDiagram|Mermaid Sequence|docs/specs|docs/plans" . --glob "*.md" --glob "!CONSISTENCY_CHECKLIST.md"
rg -n "design-doc.md|implementation-plan.md|task_plan.md|design.md" SKILL.md USAGE.md phases-reference.md design-doc-template.md templates/task_plan_template.md
```

Expected result: active docs describe plugin-backed workflow, and compatibility aliases are explicit.
