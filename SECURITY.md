# Security

## Supported versions

Security fixes are applied on the **default branch** (typically `main`). Prefer the latest tag when deploying; see [CHANGELOG.md](CHANGELOG.md) and [MAINTAINERS.md](MAINTAINERS.md) for release practices.

## Reporting a vulnerability

**Do not** file public issues for undisclosed security vulnerabilities.

Report privately:

1. **[GitHub Security Advisories](https://github.com/peace-lab-global/hush.ai/security/advisories)** — **Security** → **Advisories** → **Report a vulnerability** (preferred when enabled).
2. Email addresses listed in [MAINTAINERS.md](MAINTAINERS.md), subject prefix **`[SECURITY]`**, if email is listed.

Include:

- Clear description and impact
- Steps to reproduce (PoC if safe to share)
- Affected versions or commit SHA, if known

We aim to acknowledge within a few business days and coordinate disclosure after a fix is available.

## Data handling and trust boundaries

- **Prompts and replies** are sent to the API endpoint you configure (`OPENAI_BASE_URL` or vendor default). Treat that provider’s terms and privacy policy as applicable.
- **Secrets** (`LLM_APPKEY`, optional `llm_appkey` in a file) must never be committed to git or pasted into logs. The CLI does not print API keys; avoid `DEBUG` logging that could leak headers from third-party libraries.
- **`pua` (anti-manipulation drill) mode** is an **educational** feature: the model may output a single fictional line resembling manipulative speech. It is **not** therapy, crisis counseling, or legal advice. Do not rely on it for real-world safety decisions. Avoid putting highly identifying or sensitive personal details in prompts. If you are in immediate danger, contact local emergency services or trusted support channels.

## Secure usage

- Prefer **environment variables** or a **secrets manager** for `LLM_APPKEY`.
- If you store `llm_appkey` in a JSON file, restrict permissions (e.g. Unix `chmod 600`) and do not share the file.
- Use **least-privilege** API keys; rotate if exposed.
- For `OPENAI_BASE_URL`, use **HTTPS** and only endpoints you trust.

## Dependency scanning

CI may run **`pip-audit`** (informational). Locally, after `pip install -e ".[dev]"`:

```bash
python -m pip install pip-audit
python -m pip_audit
```

Review and upgrade dependencies as appropriate for your threat model.
