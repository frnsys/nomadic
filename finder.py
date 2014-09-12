import re
from nomadic import nomadic
import click

r = re.compile(r'(?<!\!)\[.*\]\(`?(_resources/[^`\(\)]+pdf)`?\)')

# finds notes with embedded local pdfs
for note in nomadic.rootbook.notes:
    if r.search(note.content):
        print(note.path.abs)
        #click.edit(filename=note.path.abs)