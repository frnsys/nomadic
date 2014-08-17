from setuptools import setup

setup(
    name='Nomad',
    version='0.1',
    py_modules=['nomad'],
    install_requires=[
        'click',
        'jinja2',
        'whoosh',
        'colorama',
        'lxml',
        'pdfminer',
        'py-gfm',
        'python-daemon',
        'watchdog'
    ],
    entry_points='''
        [console_scripts]
        nomad=nomad:cli
        nomad_d=nomad:daemon
    ''',
)