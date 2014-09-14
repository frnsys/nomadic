import re
from nomadic import nomadic
import click

for note in nomadic.rootbook.notes:
    if not note.content:
        print(note.path.abs)
        #click.edit(filename=note.path.abs)