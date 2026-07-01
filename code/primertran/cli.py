from __future__ import annotations

import typer

from primertran.repl import run_repl

app = typer.Typer(
    add_completion=False,
    help="PrimerTran English -> Chinese translation agent.",
)


@app.callback(invoke_without_command=True)
def main() -> None:
    run_repl()


if __name__ == "__main__":
    app()
