# PrimerTran

PrimerTran is an English-to-Chinese AI translation CLI with a Claude Code inspired terminal interface.

It is built for quick translation, short explanations, long pasted text, and technical English such as CLI output, API docs, errors, and source comments.

## Features

- English to Simplified Chinese translation
- Streaming output
- Long input folding by character count
- Chunked translation with per-section explanations
- Claude Code style prompt, mascot banner, and session commands
- DeepSeek provider support

## Install

Install the latest release from GitHub:

```bash
pip install 'git+https://github.com/Aeromtrich/primertran.git@v0.1.0#subdirectory=code'
```

Run:

```bash
primertran
```

On first launch, PrimerTran asks for a DeepSeek API key and saves it to:

```text
~/.primertran/config.toml
```

## Usage

Paste or type English text, then press Enter. Long input is folded in the prompt as a character count, then printed into the session history before translation starts.

```text
› 1287c
```

The current release uses DeepSeek models:

```text
deepseek-v4-flash
deepseek-v4-pro
```

## Commands

```text
/help      show commands
/clear     start a fresh session
/key       update API key
/provider  switch provider
/model     switch model
/style     switch output style
/config    show config
/reset     reset local config
/multi     multi-line input, finish with /end
/exit      quit
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e './code[dev]'
```

Run from source:

```bash
primertran
```

Run tests:

```bash
pytest code/tests
```

The Python package lives in [`code/`](code/), and the product plan lives in [`doc/`](doc/).
