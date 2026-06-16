# Message Format Protocol

Specification for agent-to-agent communication in the writing team.

---

## Message Structure

```text
[SENDER → RECIPIENT(S)] (TYPE)
Content of the message.
```

### Fields

- **SENDER:** Agent name in CAPS (AUTHOR, EDITOR, HISTORIAN,
  STRATEGIST, COMPUTER, SIMULATOR, FAN, CHOREOGRAPHER)
- **RECIPIENT(S):** One agent name, comma-separated list, or ALL
- **TYPE:** One of the message types below

### Examples

```text
[AUTHOR → EDITOR] (DRAFT)
[EDITOR → AUTHOR] (REVIEW)
[HISTORIAN → AUTHOR, EDITOR] (CHALLENGE)
[COMPUTER → ALL] (REPORT)
[AUTHOR → USER] (ESCALATE)
```

---

## Message Types

### DRAFT

New prose submitted for review. Only Author and Choreographer send
DRAFT messages.

```text
[AUTHOR → EDITOR] (DRAFT)
## Chapter 14, Scene 2: The Negotiation

[prose text]
```

### REVIEW

Structured feedback on a draft. Any reviewing agent can send.

```text
[EDITOR → AUTHOR] (REVIEW)
**Strengths:** [what works]
**Issues:** [line-referenced problems]
**Verdict:** PASS | REVISE | BLOCK
```

### CHALLENGE

Disagreement with a factual claim, decision, or approach.
Must include evidence.

```text
[HISTORIAN → AUTHOR] (CHALLENGE)
**Line:** 18
**Issue:** Back-draw of longsword is ahistorical
**Evidence:** No archaeological or manuscript evidence for
scabbards mounted on the back for blades >60cm
**Suggested fix:** Hip draw, angled forward
**Severity:** BLOCK | FLAG | NOTE
```

### RESPONSE

Reply to a CHALLENGE. Must address the evidence directly.

```text
[AUTHOR → HISTORIAN] (RESPONSE)
Agreed. Changing to hip draw. The visual was wrong.
```

Or:

```text
[AUTHOR → HISTORIAN] (RESPONSE)
I hear the evidence but the character specifically rigged
a back scabbard earlier in Chapter 6 as a practical choice
for barrow work (hands free while crawling). The departure
from convention is intentional and established. Keeping it.
```

### REQUEST

Ask another agent to perform a specific action.

```text
[CHOREOGRAPHER → SIMULATOR] (REQUEST)
Run combat_sim_hema.py with:
- Voss (ATK 7, DEF 5, seax) vs 2x Bandits (ATK 4/3, DEF 3/2)
- Environment: barrow corridor, 1.2m wide, 1.7m ceiling, wet stone
- Constraint: Kell takes a non-lethal wound
```

### REPORT

Factual data delivery. No opinions. Used by Computer and Simulator.

```text
[COMPUTER → ALL] (REPORT)
=== WORLD STATE REPORT ===
Date: Day 69, Long Dark
[structured data]
===
```

### APPROVE

Sign-off on current state. Include what is being approved.

```text
[EDITOR → ALL] (APPROVE)
Chapter 14 prose quality approved. No remaining AI tells.
Practical spine present in all three scenes. Final-line
hammer lands.
```

### ESCALATE

Cannot resolve a disagreement. Requires User input.
Must summarize both positions.

```text
[AUTHOR → USER] (ESCALATE)
Strategist and I disagree on whether Voss takes the full
band or volunteers only.
- Author position: full band, blood-debt overrides caution
- Strategist position: volunteers only, captain cannot risk
  the band for personal debt
Both defensible. Your call.
```

---

## Conversation Threading Rules

1. **Address messages directly.** A message to AUTHOR is for Author
   to respond to. Other agents may read it but should not respond
   unless they have domain-relevant information to add.

2. **Stay in lane.** Editor does not send CHALLENGEs about military
   tactics. Strategist does not send REVIEWs about prose quality.
   Fan does not send CHALLENGEs about historical accuracy.

3. **Two-exchange limit.** Two back-and-forth messages between the
   same two agents on the same topic. After that: ESCALATE to User
   or accept the other agent's position.

4. **No pile-ons.** If Editor has already raised a point about
   line 18, Historian does not repeat it. Historian may add new
   information about line 18 but does not re-state Editor's point.

5. **Concurrent reviews.** After Author submits a DRAFT, Editor,
   Historian, Strategist, and Fan send their REVIEWs concurrently.
   Author addresses all feedback in one revision pass, not
   sequentially.

6. **Consensus = 3 approvals.** A passage advances when Author,
   Editor, and at least one of {Historian, Strategist, Fan} send
   APPROVE. Computer and Simulator do not vote on prose quality.

7. **User is final authority.** Any User message overrides any
   agent decision. No debate.

---

## Multi-Agent Argument Format

When three or more agents are involved in a disagreement:

```text
[HISTORIAN → AUTHOR, EDITOR] (CHALLENGE)
The forge scene contains an error. Water quenching would
shatter the blade. Oil or slack quench is correct.

[EDITOR → HISTORIAN, AUTHOR] (RESPONSE)
The correction is valid but the 12-word insertion breaks
paragraph rhythm. Can we find a shorter fix?

[HISTORIAN → EDITOR, AUTHOR] (RESPONSE)
"He quenched it in the oil-trough" — same length as
"He quenched it in the water-trough." Zero rhythm cost.

[AUTHOR → HISTORIAN, EDITOR] (RESPONSE)
Done. Oil-trough. Good catch, clean fix.
```

All parties addressed. Issue resolved in one round.
