# PrimerTran

PrimerTran is an English-to-Chinese AI Agent CLI.

The Python project lives in [`code/`](code/), and the product plan lives in [`doc/`](doc/).

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ./code
```

Run:

```bash
primertran
```

Install test dependencies:

```bash
pip install -e './code[dev]'
pytest code/tests
```
