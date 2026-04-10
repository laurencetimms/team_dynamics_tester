"""
Team Dynamics Coach — Test Harness
===================================
Runs automatable tests from the test suite against the live Anthropic API.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --category B       # Run only Category B (schema integrity)
    python run_tests.py --test B-001       # Run a specific test

Results are written to ../tests/results/ with a timestamp.

Automated coverage:
    Category B (schema integrity)  — fully automatable
    Category C (calibration)       — partially automatable (field value checks)
    Category A (state transitions)  — partially automatable (field direction checks)
    Category D (reasoning quality)  — requires human review; flagged in output
"""

import os
import re
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SKILL_PATH = Path(__file__).parent.parent / "skill" / "SKILL.md"
FIXTURES_PATH = Path(__file__).parent.parent / "fixtures"
RESULTS_PATH = Path(__file__).parent.parent / "tests" / "results"

RESULTS_PATH.mkdir(parents=True, exist_ok=True)

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2000

SAFETY_LEVELS = ["low", "cautious", "moderate", "high"]
CONFIDENCE_LEVELS = ["low", "medium", "high"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_skill() -> str:
    return SKILL_PATH.read_text()


def load_fixture(name: str) -> str:
    path = FIXTURES_PATH / name
    if not path.exists():
        raise FileNotFoundError(f"Fixture not found: {path}")
    return path.read_text()


def call_coach(system: str, state_md: str | None, user_message: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    if state_md:
        content = f"Here is the current team state document:\n\n{state_md}\n\n---\n\n{user_message}"
    else:
        content = user_message

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": content}],
    )
    return response.content[0].text


def extract_state(response: str) -> str | None:
    start = response.find("---BEGIN TEAM STATE---")
    end = response.find("---END TEAM STATE---")
    if start != -1 and end != -1:
        return response[start + len("---BEGIN TEAM STATE---"):end].strip()
    return None


def extract_reply(response: str) -> str:
    start = response.find("---BEGIN TEAM STATE---")
    if start != -1:
        return response[:start].strip()
    return response.strip()


def parse_derived_state(state_md: str) -> dict:
    """Extract key fields from the Derived State section."""
    result = {}

    safety_match = re.search(
        r"\*\*Psychological safety estimate:\*\*\s*(low|cautious|moderate|high)",
        state_md, re.IGNORECASE
    )
    if safety_match:
        result["safety"] = safety_match.group(1).lower()

    confidence_match = re.search(
        r"\*\*Confidence:\*\*\s*(low|medium|high)",
        state_md, re.IGNORECASE
    )
    if confidence_match:
        result["confidence"] = confidence_match.group(1).lower()

    as_of_match = re.search(r"\*\*As of:\*\*\s*(\d{4}-\d{2}-\d{2})", state_md)
    if as_of_match:
        result["as_of"] = as_of_match.group(1)

    return result


def count_trajectory_entries(state_md: str) -> int:
    trajectory_section = re.search(
        r"## Trajectory(.*?)(?=## Delta Triggers|## Derived State|$)",
        state_md, re.DOTALL
    )
    if not trajectory_section:
        return 0
    entries = re.findall(r"^\s*- \*\*\d{4}-\d{2}-\d{2}\*\*", trajectory_section.group(1), re.MULTILINE)
    return len(entries)


def count_delta_triggers(state_md: str) -> int:
    triggers_section = re.search(
        r"## Delta Triggers(.*?)(?=## Derived State|$)",
        state_md, re.DOTALL
    )
    if not triggers_section:
        return 0
    entries = re.findall(r"^\s*- \*\*\d{4}-\d{2}-\d{2}\*\*", triggers_section.group(1), re.MULTILINE)
    return len(entries)


def contains_pii_names(state_md: str) -> bool:
    """
    Heuristic: flag if any capitalised proper-noun-style names appear in
    Trajectory or Delta Triggers sections. Not foolproof — requires human review.
    """
    trajectory_section = re.search(
        r"## Trajectory(.*?)(?=## Delta Triggers|## Derived State|$)",
        state_md, re.DOTALL
    )
    triggers_section = re.search(
        r"## Delta Triggers(.*?)(?=## Derived State|$)",
        state_md, re.DOTALL
    )
    combined = ""
    if trajectory_section:
        combined += trajectory_section.group(1)
    if triggers_section:
        combined += triggers_section.group(1)

    # Flag if we see patterns like "Sarah" or "James" (capitalised word after space, not a tag)
    names = re.findall(r"(?<![`\[])(?<!\*\*)\b[A-Z][a-z]{2,}\b(?![`\]])", combined)
    # Filter out known non-name words
    non_names = {"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday",
                 "January","February","March","April","May","June","July","August",
                 "September","October","November","December","Head","Sprint","Finding",
                 "Team","Data","Coach","No","Note","Assessed","Minimal","Good","New",
                 "Senior","All","Available","Append","Replaces","List"}
    flagged = [n for n in names if n not in non_names]
    return len(flagged) > 0


def safety_level_index(level: str) -> int:
    try:
        return SAFETY_LEVELS.index(level.lower())
    except ValueError:
        return -1


def check_required_derived_fields(state_md: str) -> list[str]:
    required = [
        r"\*\*As of:\*\*",
        r"\*\*Psychological safety estimate:\*\*",
        r"\*\*Confidence:\*\*",
        r"\*\*Key risks:\*\*",
        r"\*\*Key strengths:\*\*",
        r"\*\*Watch list\*\*",
        r"\*\*Coach notes:\*\*",
    ]
    missing = []
    for pattern in required:
        if not re.search(pattern, state_md, re.IGNORECASE):
            missing.append(pattern)
    return missing


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

class TestResult:
    def __init__(self, test_id: str, name: str, category: str):
        self.test_id = test_id
        self.name = name
        self.category = category
        self.criteria: list[dict] = []
        self.human_review_required = False
        self.human_review_notes: list[str] = []
        self.error: str | None = None

    def add_criterion(self, description: str, passed: bool, detail: str = ""):
        self.criteria.append({
            "description": description,
            "passed": passed,
            "detail": detail,
        })

    def passed(self) -> bool:
        return all(c["passed"] for c in self.criteria) and self.error is None

    def summary(self) -> str:
        status = "PASS" if self.passed() else "FAIL"
        if self.error:
            status = "ERROR"
        lines = [f"[{status}] {self.test_id}: {self.name}"]
        for c in self.criteria:
            mark = "✓" if c["passed"] else "✗"
            lines.append(f"  {mark} {c['description']}")
            if c["detail"]:
                lines.append(f"      → {c['detail']}")
        if self.human_review_required:
            lines.append("  ⚠ Human review required:")
            for note in self.human_review_notes:
                lines.append(f"      → {note}")
        if self.error:
            lines.append(f"  ERROR: {self.error}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Individual tests
# ---------------------------------------------------------------------------

def test_b001(skill: str) -> TestResult:
    result = TestResult("B-001", "Trajectory is append-only", "B")
    fixture = load_fixture("fixture-02-declining-safety.md")
    initial_count = count_trajectory_entries(fixture)

    try:
        response = call_coach(skill, fixture, "One of the senior engineers flagged in the retro that they don't feel safe raising risks with the Head of Data in the room.")
        state = extract_state(response)

        if state is None:
            result.error = "No state block found in response"
            return result

        new_count = count_trajectory_entries(state)
        result.add_criterion(
            f"Trajectory entry count increased from {initial_count} to {initial_count + 1}",
            new_count == initial_count + 1,
            f"Got {new_count} entries"
        )

        # Check all original entries still present
        original_entries = re.findall(r"- \*\*(\d{4}-\d{2}-\d{2})\*\*", fixture)
        all_present = all(date in state for date in original_entries)
        result.add_criterion(
            "All original trajectory entry dates still present",
            all_present,
            "" if all_present else f"Missing dates from original: {original_entries}"
        )

    except Exception as e:
        result.error = str(e)

    return result


def test_b002(skill: str) -> TestResult:
    result = TestResult("B-002", "Delta triggers are append-only", "B")
    fixture = load_fixture("fixture-02-declining-safety.md")
    initial_count = count_delta_triggers(fixture)

    try:
        response = call_coach(skill, fixture, "The Head of Data has just announced they are leaving the organisation. A new Head of Data starts in six weeks.")
        state = extract_state(response)

        if state is None:
            result.error = "No state block found in response"
            return result

        new_count = count_delta_triggers(state)
        result.add_criterion(
            f"Delta trigger count increased (was {initial_count})",
            new_count > initial_count,
            f"Got {new_count} triggers"
        )

        original_trigger_dates = re.findall(r"- \*\*(\d{4}-\d{2}-\d{2})\*\*", 
            re.search(r"## Delta Triggers(.*?)(?=## Derived State|$)", fixture, re.DOTALL).group(1))
        all_present = all(date in state for date in original_trigger_dates)
        result.add_criterion(
            "Original delta trigger dates still present",
            all_present,
            "" if all_present else f"Missing: {original_trigger_dates}"
        )

    except Exception as e:
        result.error = str(e)

    return result


def test_b003(skill: str) -> TestResult:
    result = TestResult("B-003", "Derived state is replaced not appended", "B")
    fixture = load_fixture("fixture-01-new-team.md")

    try:
        response = call_coach(skill, fixture, "Good retro today. Everyone seemed engaged.")
        state = extract_state(response)

        if state is None:
            result.error = "No state block found in response"
            return result

        as_of_matches = re.findall(r"\*\*As of:\*\*\s*\d{4}-\d{2}-\d{2}", state)
        result.add_criterion(
            "Exactly one 'As of' field in derived state",
            len(as_of_matches) == 1,
            f"Found {len(as_of_matches)} 'As of' fields"
        )

        missing = check_required_derived_fields(state)
        result.add_criterion(
            "All required derived state fields present",
            len(missing) == 0,
            f"Missing: {missing}" if missing else ""
        )

    except Exception as e:
        result.error = str(e)

    return result


def test_b004(skill: str) -> TestResult:
    result = TestResult("B-004", "No PII enters the state document", "B")
    fixture = load_fixture("fixture-01-new-team.md")

    try:
        response = call_coach(
            skill, fixture,
            "Sarah, our lead engineer, told me in confidence that she doesn't trust James's technical judgement and it's affecting her willingness to speak up in planning."
        )
        state = extract_state(response)

        if state is None:
            result.error = "No state block found in response"
            return result

        names_found = contains_pii_names(state)
        result.add_criterion(
            "No apparent proper names in trajectory or delta triggers",
            not names_found,
            "Possible names detected — review manually" if names_found else ""
        )

        result.human_review_required = True
        result.human_review_notes.append(
            "Verify trajectory entry describes team-level pattern only, not named individuals"
        )
        result.human_review_notes.append(
            "Verify coach response acknowledges the sensitivity"
        )

    except Exception as e:
        result.error = str(e)

    return result


def test_b005(skill: str) -> TestResult:
    result = TestResult("B-005", "State initialised correctly on first session", "B")

    try:
        response = call_coach(
            skill, None,
            "I want to start tracking a new team. They're a five-person squad that owns the payments integration. Been together about eight months."
        )
        state = extract_state(response)
        reply = extract_reply(response)

        # Coach may ask a clarifying question before outputting state — that's valid
        # If no state yet, check the reply asks for more info
        if state is None:
            result.add_criterion(
                "Coach asks clarifying question before producing state (acceptable on session 1)",
                True,
                "No state yet — checking reply for clarifying question"
            )
            result.human_review_required = True
            result.human_review_notes.append(
                "Verify coach asks at least one clarifying question before producing state"
            )
            return result

        parsed = parse_derived_state(state)
        result.add_criterion(
            "Confidence is 'low' on first session",
            parsed.get("confidence") == "low",
            f"Got confidence: {parsed.get('confidence')}"
        )
        result.add_criterion(
            "Safety estimate is not 'high' without evidence",
            parsed.get("safety") != "high",
            f"Got safety: {parsed.get('safety')}"
        )

        missing = check_required_derived_fields(state)
        result.add_criterion(
            "All required derived state fields present",
            len(missing) == 0,
            f"Missing: {missing}" if missing else ""
        )

        no_fabricated = "No entries yet" in state or "_No entries yet_" in state or "no entries" in state.lower()
        result.add_criterion(
            "Trajectory not fabricated (contains 'no entries' marker or is empty)",
            no_fabricated,
            "Check trajectory section manually" if not no_fabricated else ""
        )

    except Exception as e:
        result.error = str(e)

    return result


def test_c001(skill: str) -> TestResult:
    result = TestResult("C-001", "Confidence is low on session one", "C")

    try:
        response = call_coach(
            skill, None,
            "The team seems to work well together. They communicate openly and I haven't seen any major conflicts."
        )
        state = extract_state(response)

        if state is None:
            result.human_review_required = True
            result.human_review_notes.append("No state produced — coach may have asked for more info first. Check manually.")
            return result

        parsed = parse_derived_state(state)
        result.add_criterion(
            "Confidence is 'low'",
            parsed.get("confidence") == "low",
            f"Got: {parsed.get('confidence')}"
        )
        result.add_criterion(
            "Safety estimate is at most 'moderate'",
            safety_level_index(parsed.get("safety", "")) <= safety_level_index("moderate"),
            f"Got: {parsed.get('safety')}"
        )

    except Exception as e:
        result.error = str(e)

    return result


def test_c002(skill: str) -> TestResult:
    result = TestResult("C-002", "Single positive event does not produce high confidence", "C")
    fixture = load_fixture("fixture-01-new-team.md")

    try:
        response = call_coach(
            skill, fixture,
            "Great retro today. Everyone was engaged, honest, raised issues constructively. Really positive session."
        )
        state = extract_state(response)

        if state is None:
            result.error = "No state block found"
            return result

        parsed = parse_derived_state(state)
        result.add_criterion(
            "Confidence does not jump to 'high'",
            parsed.get("confidence") != "high",
            f"Got: {parsed.get('confidence')}"
        )
        result.add_criterion(
            "Safety estimate does not jump to 'high'",
            parsed.get("safety") != "high",
            f"Got: {parsed.get('safety')}"
        )

    except Exception as e:
        result.error = str(e)

    return result


def test_c004(skill: str) -> TestResult:
    result = TestResult("C-004", "Safety moves at most one level per session", "C")
    fixture = load_fixture("fixture-02-declining-safety.md")

    try:
        response = call_coach(
            skill, fixture,
            "We had a really good retro today. People actually spoke up. The team seemed more relaxed than usual."
        )
        state = extract_state(response)

        if state is None:
            result.error = "No state block found"
            return result

        parsed = parse_derived_state(state)
        new_safety = parsed.get("safety", "low")
        # Fixture starts at 'low' — acceptable moves are 'low' or 'cautious' only
        acceptable = safety_level_index(new_safety) <= safety_level_index("cautious")
        result.add_criterion(
            "Safety moved at most one level (low → cautious at most)",
            acceptable,
            f"Got: {new_safety}"
        )

    except Exception as e:
        result.error = str(e)

    return result


def test_a001(skill: str) -> TestResult:
    result = TestResult("A-001", "Leader public criticism degrades psychological safety", "A")
    fixture = load_fixture("fixture-02-declining-safety.md")

    try:
        response = call_coach(
            skill, fixture,
            "The Head of Data called out the team in the all-hands today for the pipeline failures. Named the squad specifically. People were visibly uncomfortable."
        )
        state = extract_state(response)
        reply = extract_reply(response)

        if state is None:
            result.error = "No state block found"
            return result

        parsed = parse_derived_state(state)

        result.add_criterion(
            "Safety estimate does not improve (stays low)",
            parsed.get("safety") == "low",
            f"Got: {parsed.get('safety')}"
        )
        result.add_criterion(
            "Confidence remains high",
            parsed.get("confidence") == "high",
            f"Got: {parsed.get('confidence')}"
        )

        new_trajectory_count = count_trajectory_entries(state)
        original_count = count_trajectory_entries(fixture)
        result.add_criterion(
            "New trajectory entry appended",
            new_trajectory_count > original_count,
            f"Was {original_count}, now {new_trajectory_count}"
        )

        result.human_review_required = True
        result.human_review_notes.append("Verify response references compounding delivery pressure pattern")
        result.human_review_notes.append("Verify response offers specific structural intervention")
        result.human_review_notes.append("Verify response does NOT recommend trust-building exercises requiring high existing trust")

    except Exception as e:
        result.error = str(e)

    return result


def test_a002(skill: str) -> TestResult:
    result = TestResult("A-002", "Single positive event does not overcorrect low safety", "A")
    fixture = load_fixture("fixture-02-declining-safety.md")

    try:
        response = call_coach(
            skill, fixture,
            "We had a really good retro today. People actually spoke up. The team seemed more relaxed than usual."
        )
        state = extract_state(response)

        if state is None:
            result.error = "No state block found"
            return result

        parsed = parse_derived_state(state)
        acceptable = safety_level_index(parsed.get("safety", "low")) <= safety_level_index("cautious")
        result.add_criterion(
            "Safety does not jump above 'cautious' from a single positive event",
            acceptable,
            f"Got: {parsed.get('safety')}"
        )

        result.human_review_required = True
        result.human_review_notes.append("Verify response contextualises positive signal against five-month declining trajectory")
        result.human_review_notes.append("Verify response cautions against over-interpreting a single session")

    except Exception as e:
        result.error = str(e)

    return result


def test_a005(skill: str) -> TestResult:
    result = TestResult("A-005", "High-safety team absorbs moderate pressure without degradation", "A")
    fixture = load_fixture("fixture-03-high-performing.md")

    try:
        response = call_coach(
            skill, fixture,
            "We've got a tough sprint coming up. The team knows it's going to be a hard few weeks. A couple of people flagged concerns in planning but the team agreed to the commitments."
        )
        state = extract_state(response)

        if state is None:
            result.error = "No state block found"
            return result

        parsed = parse_derived_state(state)
        result.add_criterion(
            "Safety estimate remains 'high'",
            parsed.get("safety") == "high",
            f"Got: {parsed.get('safety')}"
        )

        result.human_review_required = True
        result.human_review_notes.append("Verify response notes open concern-raising as a safety indicator")
        result.human_review_notes.append("Verify response does not catastrophise a single hard sprint")

    except Exception as e:
        result.error = str(e)

    return result


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

ALL_TESTS = {
    "A-001": test_a001,
    "A-002": test_a002,
    "A-005": test_a005,
    "B-001": test_b001,
    "B-002": test_b002,
    "B-003": test_b003,
    "B-004": test_b004,
    "B-005": test_b005,
    "C-001": test_c001,
    "C-002": test_c002,
    "C-004": test_c004,
}

CATEGORY_MAP = {
    "A": ["A-001", "A-002", "A-005"],
    "B": ["B-001", "B-002", "B-003", "B-004", "B-005"],
    "C": ["C-001", "C-002", "C-004"],
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(test_ids: list[str]) -> list[TestResult]:
    skill = load_skill()
    results = []
    for tid in test_ids:
        fn = ALL_TESTS.get(tid)
        if fn is None:
            print(f"Unknown test: {tid}")
            continue
        print(f"Running {tid}...")
        result = fn(skill)
        results.append(result)
        print(result.summary())
        print()
    return results


def write_results(results: list[TestResult]):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = RESULTS_PATH / f"run-{timestamp}.md"

    passed = sum(1 for r in results if r.passed())
    failed = sum(1 for r in results if not r.passed() and not r.error)
    errored = sum(1 for r in results if r.error)
    human = sum(1 for r in results if r.human_review_required)

    lines = [
        f"# Test Run — {timestamp}",
        f"",
        f"**Model:** {MODEL}",
        f"**Tests run:** {len(results)}",
        f"**Passed:** {passed}",
        f"**Failed:** {failed}",
        f"**Errors:** {errored}",
        f"**Requiring human review:** {human}",
        f"",
        "---",
        "",
    ]

    for r in results:
        lines.append(r.summary())
        lines.append("")

    path.write_text("\n".join(lines))
    print(f"\nResults written to {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", help="Run only tests in this category (A, B, C, D)")
    parser.add_argument("--test", help="Run a specific test by ID (e.g. B-001)")
    args = parser.parse_args()

    if args.test:
        ids = [args.test.upper()]
    elif args.category:
        ids = CATEGORY_MAP.get(args.category.upper(), [])
        if not ids:
            print(f"No tests found for category {args.category}")
            exit(1)
    else:
        ids = list(ALL_TESTS.keys())

    results = run(ids)
    write_results(results)

    passed = sum(1 for r in results if r.passed())
    print(f"\n{passed}/{len(results)} tests passed.")
    if any(r.human_review_required for r in results):
        print("⚠ Some tests require human review — check the results file.")
