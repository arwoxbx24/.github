# ADR-001: GitHub Actions Optimization — arwoxbx24 org
Status: Accepted
Date: 2026-04-03
Issue: arwoxbx24/.github#10

## Context

CI runs triggered on every push/PR regardless of changed files.
Already completed: protect.yml weekly cron (PR#11), cleanup-plans.yml cron removed (PR#862), whisper-voice paths filter (PR#2).
Four optimization types remain pending architectural approval.

## Options Evaluated

### 1. telegram-ai-bot/main.yml — Docker GHA cache + paths filter

| Option | Description |
|--------|-------------|
| A | No change — full build on every push |
| B | Add GHA cache only |
| C | Add GHA cache + paths filter (proposed) |

Decision: APPROVED — Option C.

Conditions:
- paths filter MUST include: `Dockerfile`, `docker-compose*.yml`, `requirements*.txt`, `pyproject.toml`, `package*.json` in addition to source dirs
- Use `cache-to: type=gha,mode=min` unless build exceeds 3 min (mode=max consumes 2-4 GB of org 10 GB cache limit)

Risk: LOW. Cache miss = full build, not failure. paths omission of manifests = stale image risk (MED if missed).

---

### 2. security-scan.yml (claude-projects) — paths filter [**.py, **.js, **.ts]

| Option | Description |
|--------|-------------|
| A | No change |
| B | paths filter to code files only (proposed) |
| C | paths-ignore on docs/markdown only |

Decision: REJECTED — Option B. APPROVED — Option C.

Rationale: Security scanners must cover `package.json`, `requirements.txt`, `poetry.lock`, `*.yml` (supply chain), `Dockerfile`. Narrowing to `**.py/js/ts` silently skips dependency manifest changes — a known supply-chain attack vector.

Safe alternative (paths-ignore):
```yaml
paths-ignore:
  - '**.md'
  - '**.txt'
  - 'docs/**'
  - '.github/ISSUE_TEMPLATE/**'
```

Risk of original proposal: MED. Dependency vulnerabilities introduced via lock file changes would not trigger scan.

---

### 3. validate.yml (client-video-transcription) — paths filter [admin/**, tests/**]

| Option | Description |
|--------|-------------|
| A | No change |
| B | paths filter admin + tests only (proposed) |
| C | paths filter admin + tests + shared modules + manifests |

Decision: CONDITIONALLY APPROVED — Option C (expanded filter).

Conditions:
- Add shared module dirs (`src/**`, `lib/**`, `app/**` — verify actual structure)
- Add `requirements*.txt`, `pyproject.toml`, `package*.json`
- Verify validate.yml does NOT use self-hosted runners (transcription deploy runners are protected per project constraints)
- client-video-transcription is production: regression risk is elevated; confirm self-contained admin dir before narrowing

Risk: MED if Option B applied as-is (shared library changes skipped). LOW with Option C.

---

### 4. freelancer-guard.yml x4 repos — paths-ignore [*.md, *.txt, *.png]

| Option | Description |
|--------|-------------|
| A | No change |
| B | paths-ignore docs/images (proposed) |
| C | Org-level workflow template with shared filter |

Decision: APPROVED — Option B, with note toward Option C.

Conditions:
- Verify no `.txt` file serves as config/seed data in any of the 4 repos
- `paths-ignore` does not suppress `workflow_dispatch` — manual runs unaffected
- Preferred: consolidate via org `.github` workflow template to prevent 4-repo drift

Risk: LOW.

## Summary

| Workflow | Decision | Condition |
|---|---|---|
| telegram-ai-bot/main.yml | APPROVED | Expand paths filter to include Dockerfiles + manifests; cache mode=min default |
| security-scan.yml | REJECTED as specified / APPROVED as paths-ignore | Never narrow security scan to code extensions only |
| validate.yml | CONDITIONALLY APPROVED | Expand filter; verify no self-hosted runner dependency |
| freelancer-guard.yml x4 | APPROVED | Verify no .txt config files; prefer org template |

## Consequences

Positive:
- Reduced unnecessary runner minutes (est. 40-60% reduction on doc-only PRs)
- Docker layer cache cuts telegram-ai-bot build time on cache hit

Negative:
- paths filter maintenance burden: new source dirs must be added to filter manually
- GHA cache consumes org 10 GB budget; monitor via Actions cache settings

Non-functional requirements confirmed:
- Deploy workflows: NOT touched by any of the 4 optimizations
- Self-hosted runners (transcription deploy): NOT referenced in any proposal
