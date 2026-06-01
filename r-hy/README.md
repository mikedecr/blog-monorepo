# r-hy

Hy translations of Python translations of R functions.

## Setup

```sh
uv sync
uv run setup-hy
uv run quarto render index.qmd --to hugo-md

`setup-hy` registers the Hy Jupyter kernel in the virtual environment so quarto can execute the Hy code blocks during render.
