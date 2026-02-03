# Code Review Process

How we review code and give feedback.

---

## Philosophy

Code review is about:

1. **Catching bugs** before they reach production
2. **Sharing knowledge** across the team
3. **Maintaining quality** of the codebase
4. **Mentoring** less experienced developers

It's NOT about:

- ❌ Proving you're smarter
- ❌ Gatekeeping
- ❌ Nitpicking style preferences
- ❌ Blocking progress

---

## For Authors

### Before Requesting Review

- [ ] Self-review your changes
- [ ] All tests pass locally
- [ ] CI is green
- [ ] PR description is complete
- [ ] PR is a reasonable size (< 400 lines ideally)

### Self-Review Checklist

Ask yourself:

1. Would I understand this code in 6 months?
2. Are there any obvious bugs?
3. Did I remove debug code?
4. Are error cases handled?
5. Is the naming clear?

### Responding to Feedback

| Do | Don't |
|----|-------|
| Thank reviewers for feedback | Get defensive |
| Ask clarifying questions | Ignore comments |
| Explain your reasoning | Take it personally |
| Make requested changes promptly | Let PR go stale |

**If you disagree:**

1. Explain your reasoning
2. Suggest alternatives
3. Seek consensus
4. If stuck, escalate to tech lead

---

## For Reviewers

### Review Mindset

- Assume the author did their best
- Be constructive, not critical
- Focus on what matters
- Offer suggestions, not mandates

### Review Checklist

#### Correctness

- [ ] Does the code do what it's supposed to?
- [ ] Are edge cases handled?
- [ ] Is error handling appropriate?
- [ ] Are there any obvious bugs?

#### Design

- [ ] Does this follow our architecture?
- [ ] Is the abstraction level appropriate?
- [ ] Are there simpler alternatives?
- [ ] Is the code in the right place?

#### Maintainability

- [ ] Is the code readable?
- [ ] Are names clear and descriptive?
- [ ] Is there appropriate documentation?
- [ ] Will this be easy to modify later?

#### Testing

- [ ] Are there tests for new functionality?
- [ ] Do tests cover edge cases?
- [ ] Are tests meaningful (not just for coverage)?

#### Security

- [ ] Is input validated?
- [ ] Are there any injection vulnerabilities?
- [ ] Are secrets handled correctly?
- [ ] Are permissions checked?

---

## Giving Feedback

### Comment Types

Use prefixes to clarify intent:

| Prefix | Meaning |
|--------|---------|
| `nit:` | Minor issue, non-blocking |
| `suggestion:` | Consider this approach |
| `question:` | I don't understand this |
| `issue:` | This needs to change |
| `praise:` | This is great! |

### Examples

```markdown
<!-- Good feedback -->
nit: Consider renaming `data` to `user_response` for clarity.

suggestion: You could use `itertools.groupby` here to simplify 
this loop. Here's an example: ...

question: Why are we catching all exceptions here instead of 
specific ones?

issue: This SQL query is vulnerable to injection. Use 
parameterized queries instead.

praise: Great job on the test coverage here! The edge cases 
are well thought out.
```

```markdown
<!-- Bad feedback -->
"This is wrong."

"You should know better."

"Why didn't you just do X?"

(No comments, just approved)
```

### Feedback Dos and Don'ts

| Do | Don't |
|----|-------|
| "Consider using X because Y" | "This is wrong, use X" |
| "I found this confusing, maybe add a comment?" | "This is confusing" |
| "What do you think about X approach?" | "You should do X" |
| Ask questions to understand | Assume malice |

---

## Getting Approval

### Approval Requirements

| Change Type | Required Approvals |
|-------------|-------------------|
| Bug fix | 1 |
| Feature | 1-2 |
| Architecture change | 2 + tech lead |
| Security-related | 2 + security review |

### When to Approve

✅ Approve when:

- Logic is correct
- Tests are adequate
- Code is maintainable
- No security issues

### When to Request Changes

❌ Request changes when:

- There are bugs
- Tests are missing for new functionality
- There are security vulnerabilities
- The approach is fundamentally flawed

### When to Comment (not block)

💬 Comment only when:

- Minor style issues
- Suggestions for improvement
- Questions that aren't blocking

---

## Review Timeline

| Metric | Target |
|--------|--------|
| First response | < 4 hours |
| Complete review | < 24 hours |
| Re-review after changes | < 4 hours |

**Tips for faster reviews:**

- Keep PRs small
- Write clear descriptions
- Tag the right reviewers
- Review others' PRs promptly (karma!)

---

## Resolving Disagreements

### Escalation Path

1. **Discuss in PR comments** — Explain perspectives
2. **Move to synchronous conversation** — Slack/call
3. **Bring in third opinion** — Another team member
4. **Escalate to tech lead** — For final decision

### Decision Guidelines

Consider:

- Project consistency
- Long-term maintenance
- Team conventions
- Performance implications

When in doubt, **document the decision** for future reference.

---

## Special Cases

### Large PRs

If a PR is too large:

1. Ask if it can be split
2. Review in logical chunks
3. Schedule dedicated review time
4. Consider pair review

### Urgent Fixes

For hotfixes:

1. Expedite review (ping in Slack)
2. Focus on correctness only
3. Create follow-up issues for improvements
4. Post-incident, do thorough review

### Junior Developer PRs

- Be more detailed in feedback
- Explain the "why" not just the "what"
- Acknowledge what's done well
- Offer to pair on complex changes

---

## Tools

### GitHub Features

- **Suggested changes**: Propose exact code changes
- **Review comment threads**: Keep discussions organized
- **Request changes**: Block merge until addressed
- **Approve**: Give the green light

### Automated Checks

These should pass before human review:

- [ ] Tests
- [ ] Linting (ruff, eslint)
- [ ] Formatting (black, prettier)
- [ ] Type checking (mypy, tsc)
- [ ] Security scan
