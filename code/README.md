# PrimerTran Package

This directory contains the Python package for PrimerTran.

For user-facing installation and usage instructions, see the repository root [`README.md`](../README.md).

## Development

```bash
cd ..
python3 -m venv .venv
source .venv/bin/activate
pip install -e './code[dev]'
```

Run:

```bash
primertran
```

Run tests:

```bash
pytest code/tests
```

## Configuration

PrimerTran stores local configuration at:

```text
~/.primertran/config.toml
```
