# Contributing

Thanks for taking the time. These projects are built and maintained by one person, so small, focused contributions land fastest.

## Before you start

- **Bugs and ideas:** open an issue first using the templates, so we can agree on the approach before you write code.
- **Security problems:** don't open a public issue. See [SECURITY.md](SECURITY.md).

## Workflow

1. Fork and branch from `dev` (or `main` if the repo has no `dev` branch): `feat/short-name` or `fix/short-name`.
2. Keep commits in [Conventional Commits](https://www.conventionalcommits.org/) form: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`.
3. Python projects: add or update `pytest` tests. Nothing merges to `main` without passing tests.
4. Open a pull request into `dev` and fill in the template.

## House style

- Prefer the standard library and zero-dependency solutions; justify any new dependency in the PR.
- UI work uses the TheBooleanJulian design tokens (`brand/tokens.css` where present) rather than new colours or fonts.
- Text between `<!-- tbj:… -->` markers in READMEs is generated centrally — edits there are overwritten.

## Licensing of contributions

Most repositories are dual licensed (AGPLv3 + commercial). By contributing, you agree your contribution is licensed under the repository's public licence and that the maintainer may also offer it under the commercial licence.
