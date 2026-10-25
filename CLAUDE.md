# Open Source ai.md

Beginner-friendly personal finance app. `main` is the development branch; remote is `origin` (GitHub).

## How to work here

- Simple architecture: fewest files and layers that work. No abstractions "for later".
- Minimal dependencies: standard library and platform features first. Ask before adding any dependency.
- Secure coding: validate all user input, never commit secrets (use env vars, keep `.env` out of git), treat money values carefully (integer cents, not floats).
- Incremental testing: each non-trivial change ships with a small test; run tests before committing.
- Build in small steps; one feature per commit.

## Git rules

- Ask before: pushing, force-pushing, deleting files, installing dependencies.
- Commits and pushes are authored by Eman's approval
