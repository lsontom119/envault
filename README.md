# envault

A CLI tool to securely manage and sync environment variables across dev environments.

---

## Installation

```bash
pip install envault
```

Or with pipx:

```bash
pipx install envault
```

---

## Usage

Initialize a new vault in your project:

```bash
envault init
```

Add and retrieve environment variables:

```bash
envault set API_KEY "your-secret-key"
envault get API_KEY
```

Sync variables across environments:

```bash
envault push --env production
envault pull --env production
```

Export variables to a `.env` file:

```bash
envault export > .env
```

---

## Why envault?

- 🔒 Secrets are encrypted at rest
- 🔄 Sync across machines and teammates instantly
- 🧩 Works with any stack — no lock-in
- ⚡ Simple, fast CLI interface

---

## License

MIT © [envault contributors](https://github.com/envault/envault)