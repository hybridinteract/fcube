# Engineering Standards

Welcome to our engineering documentation. This guide exists to help our team build better software by understanding **why** we make certain technical decisions, not just **how**.

---

## What This Guide Is About

Software engineering isn't just generating code—it's about solving problems in a way that's maintainable, scalable, and aligned with business needs.

This documentation covers:

- **Why** we structure code in certain ways
- **What** trade-offs we're making when we choose technologies
- **How** our decisions today affect our ability to deliver tomorrow

---

## Core Principles

### 1. Solve Real Problems

Every line of code should serve a purpose. Before writing code, we ask:
- What business problem does this solve?
- What happens if we don't build this?
- Is there a simpler solution?

Good engineering means knowing when *not* to build something.

### 2. Design Before Implementation

Software architecture is about making decisions that are hard to change later:
- How do different parts of the system communicate?
- Where do we store and process data?
- What happens when things fail?

We document these decisions because future team members (including our future selves) need to understand the reasoning.

### 3. Balance Speed and Quality

Fast delivery matters, but so does:
- **Maintainability**: Can someone else understand and modify this code?
- **Reliability**: Does it work consistently under real-world conditions?
- **Testability**: Can we verify it works without manual testing every time?

We're not aiming for perfection—we're aiming for "good enough to evolve safely."

---

## How We Work

### Standards and Frameworks

We use standardized approaches (like FCube) because:

1. **Consistency reduces cognitive load** - Team members can navigate any project without relearning patterns
2. **Automation becomes possible** - Common tasks can be automated when structure is predictable
3. **Onboarding is faster** - New team members learn one pattern, not a different approach per project

Standards aren't about limiting creativity—they're about focusing it on problems that actually need creative solutions.

### Code Reviews and Collaboration

We review each other's code not to criticize, but to:
- Share knowledge across the team
- Catch issues before they reach production
- Ensure someone besides the author understands how it works

---

## Using This Documentation

<div class="grid cards" markdown>

-   :material-floor-plan:{ .lg .middle } __Architecture__

    ---

    How we structure applications, organize code, and separate concerns.
    
    *Covers: layered architecture, modularity, separation of concerns*

    [:octicons-arrow-right-24: Architecture Guide](architecture.md)

</div>

---

## A Note on AI and Code Generation

AI tools can generate code quickly, but they can't:
- Understand your specific business context
- Make architectural decisions that affect long-term maintainability
- Know the trade-offs between different technical approaches

Our job as engineers is to use AI as a tool while remaining responsible for the **design, architecture, and business alignment** of what we build.

---

**Questions or suggestions?** This is a living document. If something is unclear or you think we should add a section, talk to the team.