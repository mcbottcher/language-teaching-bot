---
description: Stage all changes and commit using conventional commits style (type: short description)
---

Stage and commit the current changes using this project's conventional commit style.

## Commit message format

```
type: short description
```

- All lowercase, no period at the end
- Keep the description concise (under 72 characters)
- Choose the type that best fits the change:
  - `feat` — new content or feature
  - `fix` — correcting something broken or wrong
  - `ci` — changes to CI/CD pipelines or GitHub Actions
  - `docs` — changes to documentation tooling/config (not content)
  - Or a topic name like `ansible`, `ros2`, etc. for content-specific changes

## Steps

1. Run `git status` and `git diff` to understand what changed
2. Run `git add` for the relevant files (prefer specific files over `git add -A`)
3. Propose a commit message following the format above
4. Use `AskUserQuestion` to confirm with the proposed message as the question,
   offering `Yes, commit` and `No, cancel` as options. The user can also use
   "Other" to provide a custom commit message.
5. If confirmed (or a custom message provided), run `git commit -m "<message>"`.
   If cancelled, do nothing.
