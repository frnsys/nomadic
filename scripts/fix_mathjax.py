# Fix embedded mathjax from copied wordpress posts.

import re
import sys

filename = sys.argv[1]

r = re.compile(r'!\[[^!]+\]\(http://s0.wp.com/latex.php\)')

with open(filename, 'r') as f:
    text = f.read()

    for m in r.findall(text):
        m_ = m
        m_ = m_.replace('](http://s0.wp.com/latex.php)', '')
        m_ = m_.replace('![', '')
        m_ = m_.replace('\\\\', '\\')
        m_ = m_.replace('\\(', '(')
        m_ = m_.replace('\\)', ')')
        text = text.replace(m, '::{0}::'.format(m_))

with open(filename, 'w') as f:
    f.write(text)