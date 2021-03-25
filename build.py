#!/usr/bin/env python3
import string

with open("game.py") as f:
    game_str = f.read()

with open("style.css") as f:
    style_str = f.read()

with open("index.html.template") as f:
    template_str = f.read()

t = string.Template(template_str)
out_str = t.substitute(python_code=game_str, style_sheet=style_str)

with open("index.html", "w") as f:
    f.write(out_str)
