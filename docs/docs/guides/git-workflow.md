# Git Workflow

How we use Git for version control.

---

## Overview

We use a simplified Git workflow based on GitHub Flow:

```
main ─────●─────●─────●─────●─────●─────▶
          │     ▲     │     ▲
          │     │     │     │
feature ──●─────┘     │     │
                      │     │
bugfix ───────────────●─────┘
```

- `main` is always deployable
- All work happens in feature branches
- Changes get in via Pull Requests
- PRs require review before merge

---

## Branching Strategy

### Branch Naming

```
<type>/<short-description>
```

| Type | Use For |
|------|---------|
| `feature/` | New features |
| `bugfix/` | Bug fixes |
| `hotfix/` | Urgent production fixes |
| `refactor/` | Code refactoring |
| `docs/` | Documentation changes |

**Examples:**

```bash
feature/user-authentication
bugfix/order-calculation-error
hotfix/security-vulnerability
refactor/payment-service
docs/api-documentation
```

### Creating a Branch

```bash
# Update main first
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/my-feature
```

### Branch Lifetime

- **Maximum**: 1 week
- **Ideal**: 1-3 days

Long-lived branches = merge conflicts. Keep branches short.

---

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Restructuring code |
| `test` | Adding tests |
| `chore` | Maintenance tasks |
| `perf` | Performance improvement |

### Rules

1. **Subject line**: Max 50 characters
2. **Body**: Wrap at 72 characters
3. **Imperative mood**: "Add feature" not "Added feature"
4. **No period** at end of subject

### Examples

```bash
# Simple change
git commit -m "feat(auth): add password reset endpoint"

# With body
git commit -m "fix(orders): correct total calculation

The discount was being applied before tax instead of after.
This caused orders to have incorrect totals when both
discount and tax were present.

Fixes #123"
```

### Bad Examples

```bash
# ❌ Too vague
git commit -m "fix stuff"

# ❌ No type
git commit -m "added new feature"

# ❌ Past tense
git commit -m "feat: added login page"

# ❌ Too long
git commit -m "feat(auth): add the ability for users to reset their passwords via email link"
```

---

## Pull Requests

### Before Opening a PR

```bash
# Rebase on latest main
git fetch origin
git rebase origin/main

# Run tests
pytest

# Check formatting
black --check .
ruff check .
```

### PR Title

Same format as commit messages:

```
feat(auth): add OAuth2 login support
```

### PR Description Template

```markdown
## What

Brief description of what this PR does.

## Why

Why is this change needed? Link to issue if applicable.

## How

Technical approach taken.

## Testing

- [ ] Unit tests added
- [ ] Manual testing done
- [ ] Edge cases considered

## Screenshots

(If UI changes)
```

### PR Size

| Lines Changed | Rating |
|---------------|--------|
| 0-100 | ✅ Great |
| 100-300 | ✅ Good |
| 300-500 | ⚠️ Large |
| 500+ | ❌ Too big |

**Large PRs are hard to review.** Break them up when possible.

### Getting Reviews

1. Assign 1-2 reviewers
2. Add relevant labels
3. Link related issues
4. Self-review first (catch obvious issues)

---

## Merging

### Merge Strategy

We use **Squash and Merge**:

- Multiple commits become one
- Cleaner main branch history
- Easier to revert if needed

### Before Merging

- [ ] All CI checks pass
- [ ] At least 1 approval
- [ ] No unresolved comments
- [ ] Branch is up-to-date with main

### After Merging

```bash
# Delete local branch
git branch -d feature/my-feature

# Prune remote tracking
git fetch --prune
```

---

## Handling Conflicts

### Prevention

- Keep branches short-lived
- Pull main frequently
- Communicate with team about shared files

### Resolution

```bash
# Update your branch
git fetch origin
git rebase origin/main

# If conflicts:
# 1. Fix conflicts in each file
# 2. Stage fixed files
git add <file>

# 3. Continue rebase
git rebase --continue

# 4. Force push (your branch only!)
git push --force-with-lease
```

> ⚠️ **Never force push to `main`**

---

## Hotfixes

For urgent production issues:

```bash
# Create hotfix branch from main
git checkout main
git pull
git checkout -b hotfix/critical-bug

# Make fix
# ...

# Open PR with [HOTFIX] prefix
# Get expedited review
# Merge to main
# Deploy immediately
```

---

## Best Practices

### Do

- ✅ Commit early and often
- ✅ Write meaningful commit messages
- ✅ Keep PRs focused and small
- ✅ Rebase before opening PR
- ✅ Respond to review comments promptly

### Don't

- ❌ Commit directly to main
- ❌ Use `git push --force` on shared branches
- ❌ Leave PRs open for weeks
- ❌ Ignore failing CI checks
- ❌ Merge your own PR without review

---

## Useful Commands

```bash
# See branch history
git log --oneline --graph -20

# See what's changed
git diff main...HEAD

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Stash changes temporarily
git stash
git stash pop

# Interactive rebase (cleanup commits)
git rebase -i HEAD~3

# Find which commit broke something
git bisect start
git bisect bad
git bisect good <commit>
```
