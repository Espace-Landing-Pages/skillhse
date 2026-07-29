# Codex Skills Library

This repository stores reusable Codex skills that can be installed into another Codex instance directly from GitHub.

## Available skills

- `hse-design-system`
  Root path of this repository.
- `grandis-group-metrika-to-crm-orders`
  GitHub path: `skills/grandis-group-metrika-to-crm-orders`

## Recommended install flow

In another Codex session, send one of these prompts:

```text
Установи skill из https://github.com/Espace-Landing-Pages/skillhse/tree/main/skills/grandis-group-metrika-to-crm-orders
```

or

```text
Изучи и установи skill из GitHub path https://github.com/Espace-Landing-Pages/skillhse/tree/main/skills/grandis-group-metrika-to-crm-orders
```

If the receiving Codex uses the built-in skill installer, it can also install the skill with a direct repo/path reference:

```bash
scripts/install-skill-from-github.py \
  --repo Espace-Landing-Pages/skillhse \
  --path skills/grandis-group-metrika-to-crm-orders
```

## Why the path matters

For installation, the important unit is not just the repository link but the exact folder that contains `SKILL.md`. In this repo, that folder is:

```text
skills/grandis-group-metrika-to-crm-orders
```

A plain prompt like `изучи скилл` is enough only to read the files. If the goal is installation into `~/.codex/skills`, the safer wording is `установи skill из этого GitHub path`.
