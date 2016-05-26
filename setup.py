from setuptools import setup

setup(
    name='nomadic',
    version='1.1.0',
    description='a lightweight note management system.',
    url='https://github.com/frnsys/nomadic',
    author='Francis Tseng',
    author_email='f@frnsys.com',
    license='GPLv3',

    packages=['nomadic'],
    install_requires=[
        'click',
        'jinja2',
        'colorama',
        'lxml',
        'gfm',
        'python-daemon',
        'watchdog',
        'flask',
        'pyyaml',
        'py-gfm',
        'html2text',
    ],
    entry_points='''
        [console_scripts]
        nomadic=nomadic.cli:cli
        nomadic-d=nomadic.daemon:daemon
    ''',
)