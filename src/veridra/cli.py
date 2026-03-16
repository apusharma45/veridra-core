import typer
from rich import print

app = typer.Typer()

@app.command()
def run(file: str):
    """
    Run a Veridra evaluation suite.
    """
    print(f"[bold green]Running suite:[/bold green] {file}")

@app.command()
def validate(file: str):
    """
    Validate a test suite file.
    """
    print(f"[bold blue]Validating suite:[/bold blue] {file}")

def main():
    app()

if __name__ == "__main__":
    main()