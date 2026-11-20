"""Convert a '# %%' / '# %% [markdown]' script into a Colab notebook."""
import json, sys, ast
src, out = sys.argv[1], sys.argv[2]
cells, kind, buf = [], None, []
def flush():
    if kind is None: return
    text = "\n".join(buf).strip("\n")
    if not text: return
    if kind == "md":
        text = "\n".join(l[2:] if l.startswith("# ") else l.lstrip("#") for l in text.splitlines())
        cells.append({"cell_type": "markdown", "metadata": {}, "source": text.splitlines(True)})
    else:
        if not text.startswith("!"): ast.parse(text)
        cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": text.splitlines(True)})
for line in open(src).read().splitlines():
    if line.startswith("# %%"):
        flush(); kind = "md" if "[markdown]" in line else "code"; buf = []
    else:
        buf.append(line)
flush()
nb = {"nbformat": 4, "nbformat_minor": 5, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}}, "cells": cells}
json.dump(nb, open(out, "w"), indent=1)
print("wrote", out, len(cells), "cells")
