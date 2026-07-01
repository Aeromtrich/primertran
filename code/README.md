# PrimerTran

PrimerTran is a terminal AI agent focused on English to Simplified Chinese translation and short explanations.

## Install for development

```bash
cd code
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

```bash
primertran
```

On first launch, PrimerTran asks for a DeepSeek API key and saves config to:

```text
~/.primertran/config.toml
```

## Commands

- `/help` show commands
- `/exit` or `/quit` exit
- `/clear` clear screen and show banner
- `/key` set API key
- `/provider` show provider
- `/model` switch model
- `/style` switch output style
- `/config` show masked config
- `/reset` reset local config
- `/multi` paste multi-line input, finish with `/end`
