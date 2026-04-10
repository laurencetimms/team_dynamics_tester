# Team Dynamics Coach

A longitudinal team dynamics coaching tool built on Claude, with a structured state document, evidence-grounded reasoning, and a test suite derived from the CEBMa (2023) high-performing teams evidence review.

## What This Is

A Claude skill (`SKILL.md`) that coaches team dynamics over time using a persistent markdown state document. The coach tracks psychological safety, trust, cohesion, and cognitive states across sessions, grounded in the scientific literature on team effectiveness.

Key design principles:
- **Longitudinal** — team state accumulates across sessions via an append-only trajectory log
- **Evidence-grounded** — reasoning and interventions tied to CEBMa (2023) findings
- **Privacy-first** — no PII, no names, no verbatim quotes in state documents
- **Testable** — a structured test suite verifies coach behaviour against expected state transitions

## Repo Structure

```
team_dynamics/
├── skill/
│   └── SKILL.md                  # The team dynamics coach skill
├── fixtures/
│   ├── fixture-01-new-team.md    # New remote team, session 1
│   ├── fixture-02-declining-safety.md  # Established team, declining safety
│   └── fixture-03-high-performing.md  # High-performing stable team
├── tests/
│   ├── test-suite.md             # Full test suite specification
│   └── results/                  # Test execution logs (append only)
├── wrapper/
│   └── TeamDynamicsCoach.jsx     # React wrapper for Claude.ai artifacts
└── harness/
    ├── run_tests.py              # Python test runner
    ├── requirements.txt
    └── .env.example
```

## Getting Started

### Running the Wrapper

Paste the contents of `wrapper/TeamDynamicsCoach.jsx` into a Claude.ai conversation and ask Claude to render it as a React artifact. Upload a fixture file or `team-state.md` from a previous session to continue.

### Running the Test Harness

```bash
cd harness
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
pip install -r requirements.txt
python run_tests.py
```

Results are written to `tests/results/` with a timestamp.

### Using the Skill Standalone

Copy `skill/SKILL.md` into a Claude.ai conversation system prompt or use it as a skill file. Upload a fixture as `team-state.md` to give the coach starting context.

## Evidence Basis

CEBMa (2023) *High-performing teams: An evidence review.* Barends, Rousseau, Cioca, Wrietak. CIPD. [cipd.org](https://cipd.org/en/knowledge/evidence-reviews/high-performing-teams)

Key findings informing the coach:
- Finding 5: Psychological safety → team performance (ρ=.40/.50, Level B)
- Finding 3/4: Intra-team trust (ρ=.30/.40, Level A)
- Finding 11: Turnover → cohesion degradation (Level C)
- Finding 12: Cognitive consensus, information sharing (Level AA)
- Finding 17: Debriefing/guided reflexivity (d=.30/.70, Level A)

## State Document Format

The coach reads and writes a `team-state.md` file with four sections:

- **Baseline** — team mandate, composition, working agreements (set once)
- **Trajectory** — append-only dated observation log with tags
- **Delta Triggers** — append-only log of significant events
- **Derived State** — current assessment, replaced each session

## Notes

- The coach never stores names, verbatim quotes, or PII
- Trajectory and Delta Triggers are append-only — history is never deleted
- Derived State is replaced in full each session
- Confidence levels reflect evidence available, not optimism
