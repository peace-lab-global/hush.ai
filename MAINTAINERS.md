# Maintainers

## Roles

| Name | GitHub | Areas |
|------|--------|-------|
| _TBD_ | — | — |

To add or change maintainers, open a pull request updating this table after consensus with existing maintainers.

## Security contact

- **Preferred:** [GitHub Security Advisories](https://github.com/peace-lab-global/hush.ai/security/advisories) (private reports).
- Details: [SECURITY.md](SECURITY.md).

## Documentation

User-facing documentation lives under [docs/](docs/README.md)（配置、CLI、架构、锚点索引）。行为或 **对话模式** 变更时，请同步 [README.md](README.md)、[docs/configuration.md](docs/configuration.md)（含模式表与别名）及 [CHANGELOG.md](CHANGELOG.md)。

## Releases

1. Update [CHANGELOG.md](CHANGELOG.md) and bump `hushai.__version__` in [hushai/__init__.py](hushai/__init__.py) on the release branch as appropriate.
2. Create an annotated tag: `git tag -a v0.x.y -m "Release v0.x.y"` and push `v*` to the default branch.
3. The [Release workflow](.github/workflows/release.yml) builds sdist/wheel and uploads them to a **GitHub Release** with generated notes.

**PyPI:** publishing is not wired in CI by default. Options:

- Configure [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) for this repository and extend the workflow; or
- Publish manually after `python -m build` using `twine upload dist/*` with appropriate credentials.
