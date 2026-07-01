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

If `primertran` only works after activating `.venv`, add the virtual
environment's `bin` directory to your shell path:

```bash
echo 'export PATH="/Volumes/Software/Code/primertran/.venv/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

After that, `primertran` can be run from any directory.

Install test dependencies:

```bash
pip install -e './code[dev]'
pytest code/tests
```
