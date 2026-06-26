# Repository Guidelines

## Project Structure & Module Organization

This repository is a lightweight codespace template with examples and helper scripts. Source examples live in `src/`, including Python, shell, JSON, and XML files. Shell automation is under `scripts/`, with shared helpers in `scripts/lib/`. Documentation lives in `docs/`, with localized README files and changelog entries in `docs/changelog/`. GitHub metadata is in `.github/`. Tooling configuration is kept at the root, including `package.json`, `environment.yml`, and `commitlint.config.js`.

## Build, Test, and Development Commands

- `make init`: run `scripts/codespace.sh` to initialize the codespace environment.
- `conda env create -f environment.yml`: create the Python/tooling environment named `codespace`.
- `npm install`: install Node-based development tools.
- `npm run prepare`: install Husky Git hooks.
- `npm run commit`: start the Commitizen prompt for conventional commits.
- `npx lint-staged`: run staged-file formatters and linters manually.

The current `make clean`, `make compile`, `make install`, and `make sha1sum` targets are placeholders.

## Coding Style & Naming Conventions

Follow `.editorconfig`: UTF-8, LF endings, two-space indentation, final newline for most files, and trimmed trailing whitespace. Markdown preserves trailing whitespace and does not require a final newline. Prettier uses single quotes and plugins for XML, shell, SQL, and TOML. Python files should pass `ruff check` and `ruff format`; shell files should pass `shellcheck` and Prettier.

Use lowercase, descriptive file names where practical. Keep scripts executable only when they are intended to be run directly.

## Testing Guidelines

There is no dedicated test framework configured yet. For changes, run relevant linters and formatters through `npx lint-staged` or directly, for example `ruff check src` and `shellcheck scripts/*.sh scripts/lib/*.sh`. When adding tests later, place them near the code or in `tests/`, and document the command in `package.json` or `Makefile`.

## Commit & Pull Request Guidelines

Commits are checked with commitlint and should follow Conventional Commits, such as `feat: add setup script`, `fix(conf): update commitlint config`, or `docs: refresh README`. Use `npm run commit` for the guided flow. Husky runs `gitleaks git . --verbose`, `lint-staged`, and `commitlint` during commits.

Pull requests should include a concise description, linked issues when relevant, and notes about validation performed. Include screenshots only for documentation or visual changes.

## Security & Configuration Tips

Do not commit secrets. The pre-commit hook runs Gitleaks, but contributors should also inspect `.env` and generated files before staging. Keep dependency and environment changes synchronized across `package.json`, lockfiles, and `environment.yml`.
