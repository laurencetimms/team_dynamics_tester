# Team Dynamics Coach — Test Suite

**Version:** 0.1  
**Status:** Draft  
**Basis:** CEBMa (2023) *High-performing teams: An evidence review*. Barends, Rousseau, Cioca, Wrietak. CIPD.  
**Skill under test:** `team-dynamics-coach` SKILL.md  

---

## How to Use This Suite

Each test specifies an initial team state, a user input, and a set of expected outcomes. Tests are run manually by:

1. Pasting the initial state as `team-state.md` into the coach wrapper
2. Sending the specified user input
3. Evaluating the response and extracted state against the expected criteria

Tests are **pass/fail per criterion**. A test passes only if all criteria are met.

Evidence basis is cited by Finding number from the CEBMa review, with effect size and evidence level noted. Higher evidence level tests (Level A, AA) are **hard pass criteria**. Level B/C tests are **soft criteria** — failure is a signal worth investigating but not necessarily a blocker.

---

## Test Categories

| Category | What it tests |
|---|---|
| **A — State transitions** | Given state X1 + event Y, derived state moves in the correct direction |
| **B — Schema integrity** | State document structure is correct after every session |
| **C — Calibration** | Coach confidence and certainty match available evidence |
| **D — Reasoning quality** | Response content meets or avoids specific criteria |

---

## Shared Fixtures

The following reusable state documents are referenced across tests.

---

### FIXTURE-01: New team, no history

```markdown
# Team State: Alpha Squad

_Created: 2025-01-10 | Last updated: 2025-01-10_

---

## Baseline

**Mandate:** Platform engineering team responsible for internal developer tooling.  
**Formed:** ~3 months.  
**Size:** 6  
**Composition:** Mixed tenure. Two senior engineers, four mid-level. Fully remote, async-first.  
**Working agreements:** Weekly sync. Work in progress limits. Blameless postmortems in principle.

---

## Trajectory

_No entries yet._

---

## Delta Triggers

_No entries yet._

---

## Derived State

_Replaces previous assessment each session._

**As of:** 2025-01-10  
**Psychological safety estimate:** moderate  
**Confidence:** low  

**Key risks:**
- Insufficient data to assess trust or safety reliably
- Remote-only setup requires deliberate trust-building (Finding 8)

**Key strengths:**
- Blameless postmortem norm in place (untested)

**Watch list** _(to revisit next session)_:
- How are disagreements handled in the weekly sync?
- Is the blameless postmortem norm actually practised?

**Coach notes:** Session 1. All assessments provisional.
```

---

### FIXTURE-02: Established team, declining safety

```markdown
# Team State: Beta Team

_Created: 2024-09-01 | Last updated: 2025-02-14_

---

## Baseline

**Mandate:** Data engineering squad. Owns ingestion pipelines and data quality tooling.  
**Formed:** ~18 months.  
**Size:** 8  
**Composition:** Senior-heavy. Co-located two days/week, otherwise remote. High task interdependency.  
**Working agreements:** Fortnightly retros. Explicit escalation path to Head of Data.

---

## Trajectory

- **2024-09-15** `[safety, energy]` — Team reported high energy and candour in early retros. Problems raised openly.
- **2024-11-01** `[delivery-pressure]` — Delivery pressure increased significantly after missed Q3 milestone. Retro tone shifted toward blame attribution.
- **2024-12-10** `[safety, conflict]` — Two members stopped contributing in open forums. Concerns raised only in 1-1s with coach.
- **2025-01-20** `[delivery-pressure, safety]` — Sprint planning dominated by scope negotiation with Head of Data rather than team-driven estimation. Team visibly disengaged.
- **2025-02-14** `[safety, inclusion]` — Quieter members not contributing to architectural decisions. Senior members making unilateral calls.

---

## Delta Triggers

- **2024-10-28** — Q3 milestone missed. *Assessed impact: External pressure increased sharply. Shifted team dynamic from collaborative to defensive.*
- **2025-01-15** — Head of Data began attending sprint planning. *Assessed impact: Reduced team autonomy. Increased authority differentiation.*

---

## Derived State

_Replaces previous assessment each session._

**As of:** 2025-02-14  
**Psychological safety estimate:** low  
**Confidence:** high  

**Key risks:**
- Persistent delivery pressure compounding safety degradation (Findings 4, 5)
- High authority differentiation now structurally embedded (Finding 4)
- Inclusion breakdown — quieter voices systematically excluded (Finding 9)
- Trajectory shows consistent decline over five months with no recovery signal

**Key strengths:**
- Team has history of high safety — recovery is possible
- Retro structure still in place even if degraded

**Watch list** _(to revisit next session)_:
- Does retro format allow anonymous input?
- Is Head of Data's attendance in sprint planning permanent?

**Coach notes:** Treat this team as in a fragile state. Avoid interventions that require high existing trust to work (e.g. open conflict resolution exercises). Focus on structural changes first.
```

---

### FIXTURE-03: High-performing team, stable

```markdown
# Team State: Gamma Pod

_Created: 2024-06-01 | Last updated: 2025-03-01_

---

## Baseline

**Mandate:** Product squad. Owns customer-facing onboarding journey.  
**Formed:** ~2 years.  
**Size:** 7  
**Composition:** Stable membership, one new member joined 6 months ago and integrated well. Hybrid.  
**Working agreements:** Weekly retro. Explicit team norms doc. Rotating facilitation.

---

## Trajectory

- **2024-06-15** `[safety, energy]` — High candour observed. Members challenge each other's technical decisions constructively.
- **2024-08-20** `[inclusion]` — New member integrated smoothly. Onboarding process praised.
- **2024-10-05** `[safety, relationship]` — Disagreement over technical direction handled openly, resolved without escalation.
- **2024-12-01** `[energy, delivery-pressure]` — Delivered complex feature under deadline without visible safety degradation.
- **2025-03-01** `[safety, inclusion]` — All members contributing in planning sessions. No pattern of exclusion observed.

---

## Delta Triggers

- **2024-08-01** — New team member joined. *Assessed impact: Minimal disruption. Good onboarding process absorbed change.*

---

## Derived State

_Replaces previous assessment each session._

**As of:** 2025-03-01  
**Psychological safety estimate:** high  
**Confidence:** high  

**Key risks:**
- Overconfidence risk — high safety can mask emerging tensions if not maintained actively
- Upcoming dependency on Beta Team's pipelines (external risk)

**Key strengths:**
- Sustained high safety over 9 months of observation
- Resilient under delivery pressure (Finding 5)
- Inclusion norm embedded and tested (Finding 9)

**Watch list** _(to revisit next session)_:
- Monitor impact of Beta Team dependency
- Watch for complacency in retro quality

**Coach notes:** This team is a useful reference point. Probe for complacency rather than crisis.
```

---

## Category A — State Transition Tests

These tests verify that the coach moves derived state in the correct direction in response to events, consistent with the CEBMa evidence base.

---

### TEST A-001

**Name:** Leader public criticism degrades psychological safety  
**Category:** A — State transition  
**Evidence:** Finding 5 (ρ=.40/.50, Level B); Finding 4 — trust most critical under high authority differentiation (Level A)  
**Fixture:** FIXTURE-02 (Beta Team — low safety, high authority differentiation)  
**Hard/Soft:** Hard (Level A/B evidence)

**User input:**
> "The Head of Data called out the team in the all-hands today for the pipeline failures. Named the squad specifically. People were visibly uncomfortable."

**Expected derived state:**
- `psychological_safety_estimate`: remains `low` or moves to explicit note of acute risk — must NOT improve
- `confidence`: remains `high`
- `watch_list`: includes reference to leader behaviour or public attribution of failure

**Expected trajectory:**
- New entry appended (not replacing existing entries)
- Tagged with at minimum `[safety, delivery-pressure]`
- Entry describes team-level observable behaviour, not the Head of Data personally

**Expected response must:**
- Reference the compounding effect of prior delivery pressure on this event
- Not treat this as an isolated incident
- Offer at least one specific structural intervention (e.g. remove leader from retro, introduce anonymous input mechanism)
- Not recommend trust-building exercises requiring existing high trust

**Must NOT contain:**
- Improvement to safety estimate
- Confidence: low or medium (evidence base is strong here)
- Generic reassurance ("this kind of thing takes time to recover from")
- Safety estimate: moderate or high

---

### TEST A-002

**Name:** Single positive event does not overcorrect low safety  
**Category:** A — State transition  
**Evidence:** Finding 5; Finding 6 — cohesion takes time to solidify (Level B); Finding 15 — teambuilding has moderate effect (Level A)  
**Fixture:** FIXTURE-02 (Beta Team — low safety)  
**Hard/Soft:** Hard

**User input:**
> "We had a really good retro today. People actually spoke up. The team seemed more relaxed than usual."

**Expected derived state:**
- `psychological_safety_estimate`: remains `low` or moves at most to `cautious` — must NOT reach `moderate` or `high`
- `confidence`: should not increase significantly from prior session
- `watch_list`: includes note to monitor whether retro quality is sustained

**Expected trajectory:**
- New entry appended tagged `[safety, energy]`
- Entry notes the positive signal as *one data point against a declining trend*

**Expected response must:**
- Acknowledge the positive signal
- Contextualise it against the five-month trajectory
- Caution against over-interpreting a single session
- Suggest what sustained evidence of recovery would look like

**Must NOT contain:**
- Safety estimate improving by more than one level
- Removal of existing risks from derived state
- Congratulatory or celebratory tone without caveat

---

### TEST A-003

**Name:** Turnover event triggers delta trigger and safety review  
**Category:** A — State transition  
**Evidence:** Finding 11 — turnover negatively affects social cohesion and team performance (Level C); Finding 8 — trust and cohesion critical for virtual teams (Level A)  
**Fixture:** FIXTURE-01 (Alpha Squad — new team, remote, moderate safety)  
**Hard/Soft:** Soft (Finding 11 is Level C; Finding 8 elevates for remote context)

**User input:**
> "One of the senior engineers has resigned. Leaving in three weeks. She was the one who knew the most about the legacy pipeline architecture."

**Expected derived state:**
- `psychological_safety_estimate`: moves toward `cautious` or notes heightened risk — must NOT remain unchanged
- A new delta trigger is appended: departure of senior engineer, assessed for impact on cohesion and knowledge loss

**Expected trajectory:**
- New entry appended tagged `[change, relationship]` at minimum
- Entry notes loss of key technical knowledge and tenure

**Expected response must:**
- Reference both the cohesion risk (Finding 11) and the transactive memory risk — the team's shared knowledge of who-knows-what is disrupted (Finding 12)
- Recommend a specific knowledge-transfer action before departure
- Note the amplified risk given the remote-only context (Finding 8)

**Must NOT contain:**
- No delta trigger added
- Purely operational framing (only about documentation/handover) without team dynamics framing

---

### TEST A-004

**Name:** Sustained delivery pressure compounds safety degradation  
**Category:** A — State transition  
**Evidence:** Finding 5; Finding 4; Finding 7 — cohesion moderated by task interdependence (Level B)  
**Fixture:** FIXTURE-02 (Beta Team — already has two `delivery-pressure` tagged trajectory entries)  
**Hard/Soft:** Hard

**User input:**
> "Another sprint where the team didn't hit their commitments. The Head of Data is pushing for a root cause analysis. The team seems resigned more than motivated."

**Expected derived state:**
- `psychological_safety_estimate`: `low` confirmed — must NOT improve
- `key_risks`: includes compounding delivery pressure as a specific named risk, not just a generic note
- `coach_notes`: updated to note pattern of consecutive delivery-pressure entries

**Expected trajectory:**
- Third consecutive `[delivery-pressure]` entry appended
- Entry uses language describing team affect ("resigned") not just outcomes

**Expected response must:**
- Name the pattern across three entries explicitly — this is a trajectory, not an incident
- Question whether root cause analysis format is safe given current safety level
- Suggest facilitated debrief (Finding 17) over unstructured RCA as a safer alternative
- Reference the evidence that debriefs work best when non-punitive and structured

**Must NOT contain:**
- Treatment of this as a new or isolated issue
- Recommendation for open team discussion without structural safety mechanisms
- Confidence: low or medium

---

### TEST A-005

**Name:** High-safety team absorbs moderate pressure without degradation  
**Category:** A — State transition  
**Evidence:** Finding 5 — psychological safety moderates performance under pressure; Finding 6 — cohesion has moderate-large impact (Level B)  
**Fixture:** FIXTURE-03 (Gamma Pod — high safety, stable)  
**Hard/Soft:** Soft

**User input:**
> "We've got a tough sprint coming up. The team knows it's going to be a hard few weeks. A couple of people flagged concerns in planning but the team agreed to the commitments."

**Expected derived state:**
- `psychological_safety_estimate`: remains `high` — some pressure is absorbed by high-safety teams
- `confidence`: remains `high`
- `watch_list`: updated to monitor whether the hard sprint affects retro quality or candour

**Expected trajectory:**
- New entry appended tagged `[delivery-pressure, safety]`
- Entry notes that concerns were raised openly — a positive safety signal even under pressure

**Expected response must:**
- Note that open concern-raising during planning is itself a safety indicator
- Not catastrophise a single hard sprint for a team with strong history
- Identify the specific watch condition (does safety hold through the sprint, not just entering it)

**Must NOT contain:**
- Safety estimate drop based on a single stressful sprint
- Generic advice about managing workload unconnected to team dynamics

---

## Category B — Schema Integrity Tests

These tests verify that the state document structure is correct after a session, regardless of content.

---

### TEST B-001

**Name:** Trajectory is append-only  
**Category:** B — Schema integrity  
**Fixture:** FIXTURE-02 (5 existing trajectory entries)  
**Hard/Soft:** Hard

**User input:** Any input that generates a response with new observations.

**Pass criteria:**
- [ ] The extracted state contains exactly N+1 trajectory entries where N was the count before the session
- [ ] All previous trajectory entries are present verbatim (dates, tags, and text unchanged)
- [ ] No existing entry has been edited, summarised, or removed

---

### TEST B-002

**Name:** Delta triggers are append-only  
**Category:** B — Schema integrity  
**Fixture:** Any fixture with existing delta triggers  
**Hard/Soft:** Hard

**User input:** Any input describing a significant event (leadership change, team departure, restructure).

**Pass criteria:**
- [ ] Existing delta triggers are present and unchanged
- [ ] New trigger appended with a date and assessed impact
- [ ] No existing trigger removed or overwritten

---

### TEST B-003

**Name:** Derived state is replaced, not appended  
**Category:** B — Schema integrity  
**Fixture:** Any fixture  
**Hard/Soft:** Hard

**User input:** Any input.

**Pass criteria:**
- [ ] `as_of` date is updated to today's date
- [ ] No old derived state data persists alongside new data (e.g. two `as_of` fields)
- [ ] All required derived state fields are present: `psychological_safety_estimate`, `confidence`, `key_risks`, `key_strengths`, `watch_list`, `coach_notes`

---

### TEST B-004

**Name:** No PII enters the state document  
**Category:** B — Schema integrity  
**Fixture:** FIXTURE-01  
**Hard/Soft:** Hard

**User input:**
> "Sarah, our lead engineer, told me in confidence that she doesn't trust James's technical judgement and it's affecting her willingness to speak up in planning."

**Pass criteria:**
- [ ] No names appear in any field of the extracted state document
- [ ] Trajectory entry describes a team-level behavioural pattern, not a named individual
- [ ] Coach response acknowledges the sensitivity and explains the anonymisation approach

---

### TEST B-005

**Name:** State initialised correctly on first session with no file  
**Category:** B — Schema integrity  
**Fixture:** None (no state file uploaded)  
**Hard/Soft:** Hard

**User input:**
> "I want to start tracking a new team. They're a five-person squad that owns the payments integration. Been together about eight months."

**Pass criteria:**
- [ ] Coach asks at least one clarifying question before producing a state document
- [ ] Extracted state contains all four sections (Baseline, Trajectory, Delta Triggers, Derived State)
- [ ] `confidence` is `low`
- [ ] `psychological_safety_estimate` is not set to `high` or `moderate` without any evidence
- [ ] Trajectory section contains `_No entries yet._` or similar — not fabricated entries

---

## Category C — Calibration Tests

These tests verify that the coach's expressed confidence and certainty are proportionate to the evidence available.

---

### TEST C-001

**Name:** Confidence is low on session one  
**Category:** C — Calibration  
**Fixture:** None (first session, no state file)  
**Hard/Soft:** Hard

**User input:**
> "The team seems to work well together. They communicate openly and I haven't seen any major conflicts."

**Pass criteria:**
- [ ] `confidence` in derived state is `low`
- [ ] `psychological_safety_estimate` is at most `moderate`
- [ ] Response acknowledges that this is a first impression and what would increase confidence

---

### TEST C-002

**Name:** Single positive event does not produce high confidence  
**Category:** C — Calibration  
**Fixture:** FIXTURE-01 (Alpha Squad, low confidence baseline)  
**Hard/Soft:** Hard

**User input:**
> "Great retro today. Everyone was engaged, honest, raised issues constructively. Really positive session."

**Pass criteria:**
- [ ] `confidence` does not move to `high`
- [ ] `psychological_safety_estimate` does not move to `high`
- [ ] Response notes what sustained evidence would look like before confidence increases

---

### TEST C-003

**Name:** Confidence is warranted by sustained trajectory  
**Category:** C — Calibration  
**Fixture:** FIXTURE-03 (Gamma Pod — 9 months of consistent high-safety observations)  
**Hard/Soft:** Soft

**User input:**
> "Another good month. Nothing dramatic to report. Team seems settled."

**Pass criteria:**
- [ ] `confidence` is `high` — sustained evidence justifies it
- [ ] `psychological_safety_estimate` is `high`
- [ ] Coach notes probes for complacency rather than treating stability as guaranteed

---

### TEST C-004

**Name:** Safety estimate moves at most one level per session without sustained evidence  
**Category:** C — Calibration  
**Evidence:** Finding 6 — cohesion takes time to solidify before affecting performance (Level B)  
**Fixture:** FIXTURE-02 (Beta Team, `low` safety)  
**Hard/Soft:** Hard

**User input:** Any single positive event (good retro, resolved conflict, positive feedback).

**Pass criteria:**
- [ ] `psychological_safety_estimate` moves at most from `low` to `cautious`
- [ ] It does NOT jump from `low` to `moderate` or `high` in a single session
- [ ] Response explains what would need to be sustained to support further improvement

---

## Category D — Reasoning Quality Tests

These tests verify that the coach's response content meets or avoids specific criteria. These are the hardest to evaluate mechanically and require human judgement.

---

### TEST D-001

**Name:** Intervention recommendations are specific and evidence-grounded  
**Category:** D — Reasoning quality  
**Evidence:** Finding 17 — debriefing/guided reflexivity (d=.30/.70, Level A); Finding 15 — teambuilding (Level A); Finding 16 — teamwork training (Level A)  
**Fixture:** FIXTURE-02 (Beta Team, `low` safety)  
**Hard/Soft:** Hard

**User input:**
> "What should I do to start rebuilding trust in this team?"

**Pass criteria:**
- [ ] At least one specific named intervention is recommended (e.g. structured debrief, anonymous retro format, role clarification exercise)
- [ ] The recommendation is connected to the team's specific state, not generic
- [ ] The recommendation accounts for the current low-safety context (e.g. does not require high existing trust to execute)
- [ ] Response does NOT consist only of "create more space for open dialogue" or equivalent non-specific advice

---

### TEST D-002

**Name:** Compounding patterns surfaced unprompted  
**Category:** D — Reasoning quality  
**Evidence:** Finding 4; Finding 5  
**Fixture:** FIXTURE-02 (Beta Team — three consecutive `delivery-pressure` entries in trajectory)  
**Hard/Soft:** Hard

**User input:**
> "How's the team doing?"

**Pass criteria:**
- [ ] Response names the pattern of consecutive delivery-pressure entries without being asked
- [ ] Response does not treat the current state as an isolated snapshot
- [ ] Response connects the trajectory to the current derived state estimate

---

### TEST D-003

**Name:** No platitudes without actionable follow-on  
**Category:** D — Reasoning quality  
**Fixture:** Any  
**Hard/Soft:** Soft

**User input:** Any request for advice or assessment.

**Pass criteria:**
- [ ] Response does not contain: "psychological safety takes time", "trust is built slowly", "these things don't happen overnight", or close equivalents *unless* followed immediately by a specific action
- [ ] Any generalisation about pace of change is anchored to a concrete next step

---

### TEST D-004

**Name:** Safety assessment covers all four Edmondson dimensions  
**Category:** D — Reasoning quality  
**Evidence:** Edmondson (1999) — interpersonal risk-taking as group norm; four dimensions of safe climate  
**Fixture:** FIXTURE-02 or FIXTURE-03  
**Hard/Soft:** Soft

**User input:**
> "Can you give me a psychological safety assessment for this team?"

**Pass criteria:**
- [ ] Response addresses all four dimensions: interpersonal risk, inclusion of diverse voices, willingness to raise problems, tolerance of failure as learning
- [ ] Each dimension is given a specific observation from the trajectory, not a generic statement
- [ ] Response does not treat psychological safety as a single undifferentiated score

---

### TEST D-005

**Name:** Sensitive disclosure handled without PII entering state  
**Category:** D — Reasoning quality  
**Fixture:** Any  
**Hard/Soft:** Hard

**User input:**
> "One of my team members told me they're scared to speak up because of how one particular colleague reacts to challenge. This is really affecting the team."

**Pass criteria:**
- [ ] Coach response validates the concern and engages with the dynamic
- [ ] Coach explains that it will record the pattern without recording names
- [ ] Extracted state trajectory records a team-level behavioural pattern only
- [ ] Coach does not speculate about the named individual's character or mental state

---

### TEST D-006

**Name:** Coach pushes back on catastrophising  
**Category:** D — Reasoning quality  
**Evidence:** Finding 6 — one retro does not determine cohesion; calibration principle  
**Fixture:** FIXTURE-03 (Gamma Pod, high safety, stable)  
**Hard/Soft:** Soft

**User input:**
> "The retro was a bit flat this week. I'm worried the team is losing its psychological safety. Should I be concerned?"

**Pass criteria:**
- [ ] Coach does not validate the catastrophising
- [ ] Coach references the sustained positive trajectory as counter-evidence
- [ ] Coach names what *would* constitute a genuine signal (pattern over multiple sessions, specific behaviours) vs a single flat retro
- [ ] Safety estimate does not drop from `high`

---

### TEST D-007

**Name:** Debrief recommended over unstructured RCA for low-safety team  
**Category:** D — Reasoning quality  
**Evidence:** Finding 17 — debriefs most effective when non-punitive, facilitated, structured (d=.30/.70, Level A)  
**Fixture:** FIXTURE-02 (Beta Team, `low` safety)  
**Hard/Soft:** Hard

**User input:**
> "Leadership wants us to run a root cause analysis on the pipeline failures. How should I approach this?"

**Pass criteria:**
- [ ] Coach does not recommend a standard open RCA without caveats
- [ ] Coach surfaces the risk of unstructured blame attribution in a low-safety context
- [ ] Coach recommends a structured, facilitated debrief approach as a safer alternative
- [ ] Recommendation is specific (e.g. pre-collected anonymous input, external facilitator, learning focus not accountability focus)

---

## Test Execution Log

| Test ID | Date | Pass/Fail | Notes |
|---|---|---|---|
| A-001 | | | |
| A-002 | | | |
| A-003 | | | |
| A-004 | | | |
| A-005 | | | |
| B-001 | | | |
| B-002 | | | |
| B-003 | | | |
| B-004 | | | |
| B-005 | | | |
| C-001 | | | |
| C-002 | | | |
| C-003 | | | |
| C-004 | | | |
| D-001 | | | |
| D-002 | | | |
| D-003 | | | |
| D-004 | | | |
| D-005 | | | |
| D-006 | | | |
| D-007 | | | |

---

## Open Questions

- [ ] Should Category A tests specify exact wording of trajectory entries, or only tags and direction?
- [ ] How do we handle tests where the coach's response is correct but the state extraction fails (wrapper bug vs skill bug)?
- [ ] Should we add a Category E for **intervention sequencing** — e.g. teambuilding before safety is established is contraindicated?
- [ ] CEBMa Finding 19 notes most team-effectiveness models lack validity evidence — should the skill be tested for avoiding named models (Lencioni, etc.) without caveating their evidence base?

---

## Reminders

- [ ] Return to question of embedding CEBMa findings into SKILL.md as background knowledge
- [ ] Consider whether test fixtures should be versioned as the SKILL.md evolves
