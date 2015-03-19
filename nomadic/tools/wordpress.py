"""
Fix embedded mathjax from copied wordpress posts.
"""

import re
import sys

r = re.compile(r'!\[[^!]+\]\(http://s0.wp.com/latex.php\)')

def fix_mathjax(note):
    content = note.content

    for m in r.findall(content):
        m_ = m
        m_ = m_.replace('](http://s0.wp.com/latex.php)', '')
        m_ = m_.replace('![', '')
        m_ = m_.replace('\\\\', '\\')
        m_ = m_.replace('\\(', '(')
        m_ = m_.replace('\\)', ')')
        content = content.replace(m, '${0}$'.format(m_))

    note.write(content)