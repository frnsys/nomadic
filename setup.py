from sys import platform
from setuptools import setup

setup(
    name='nomadic',
    version='0.4.0',
    description='a lightweight note management system.',
    url='https://github.com/ftzeng/nomadic',
    author='Francis Tseng',
    author_email='f@frnsys.com',
    license='GPLv3',

    packages=['nomadic'],
    install_requires=[
        'click',
        'jinja2',
        'whoosh',
        'colorama',
        'lxml',
        'pdfminer',
        'gfm',
        'python-daemon',
        'watchdog'
    ],
    entry_points='''
        [console_scripts]
        nomadic=nomadic.cli:cli
        nomadic-d=nomadic.daemon:daemon
    ''',
)