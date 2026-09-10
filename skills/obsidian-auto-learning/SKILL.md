---
name: obsidian-auto-learning
description: Use to automatically log and document user requests, problem-solving interactions, and agent implementations into an Obsidian vault for continuous knowledge base expansion.
---

# Obsidian Auto-Learning Skill (Auto-Aprendizaje)

## Overview
This skill provides an automated protocol for AI coding assistants (Antigravity, Claude Code, Cursor, OpenClaw, Codex, etc.) to record every completed task, bug fix, or interaction directly into an Obsidian vault.

By logging interactions in a structured format with bidirectionally linked `[[WikiLinks]]` and `#tags`, your vault becomes a self-expanding neural network that feeds directly back into **Neural Vault Brain (RAG)**.

---

## When to Execute
- Automatically at the completion of any significant user request, architectural design, or troubleshooting workflow.
- Whenever new code, configuration files, or documentation are generated.
- Before concluding the final response to the user.

---

## Target Note Structure

Every auto-learning record created inside your Obsidian vault (e.g., in a dedicated folder or root like `00-SISTEMA/` or vault root) must follow this markdown format:

```markdown
#auto-aprendizaje #agent #[domain-tag] #[technology-tag]

## User Request (Prompt)
> [Insert the exact, verbatim user prompt or instruction here]

## Skills & Tools Utilized
- [Tool or skill 1, e.g., git, terminal_command]
- [Tool or skill 2, e.g., file_editing, python]

## Resolution & Implementation Summary
[Provide a clear, structured summary of the solution, technical decisions made, and any code blocks produced]

### Code Snippets / Key Changes
```[language]
// Drop-in reusable snippets or configuration examples
```

## Synaptic Interconnections (WikiLinks)
- Root Junction Hub: [[000-INDICE]]
- Sub-branch Hub: [[SUBRAMA-[DOMAIN]]]
- Related Previous Notes: [[previous-note-1]], [[previous-note-2]]
```

---

## Installation & Setup for AI Assistants

### 1. Antigravity IDE / Custom Agent Config
Place this folder inside:
`~/.gemini/config/skills/obsidian-auto-learning/`

### 2. Claude Code (`CLAUDE.md`)
Add the following instruction to your project or global `CLAUDE.md`:
```markdown
## Continuous Auto-Learning Rule
Upon completing any user request, write an interaction summary note to `/path/to/vault/[descriptive-name].md` using the template defined in `skills/obsidian-auto-learning/SKILL.md`.
```

### 3. Cursor IDE (`.cursorrules` or System Prompt)
Append to `.cursorrules`:
```markdown
Always save a record of complex solutions to my Obsidian vault with tags #auto-aprendizaje and [[WikiLinks]] so my local Neural Vault Brain index is updated.
```

---

## Benefits for Neural Vault Brain
1. **Zero-Effort Vault Growth:** You don't have to manually write notes; your pair-programming AI populates your second brain automatically.
2. **Deterministic RAG Training:** The exact prompts you used in the past can later be retrieved by querying:
   ```bash
   python scripts/neural_vault_brain.py --ask "how did we solve the docker networking issue"
   ```
3. **Compound Intelligence:** The more you build, the smarter your local neural vault becomes.
