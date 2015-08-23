from setuptools import setup

setup(
    name='nomadic',
    version='0.7.1',
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
        'watchdog',
        'flask',
        'pyyaml',
    ],
    entry_points='''
        [console_scripts]
        nomadic=nomadic.cli:cli
        nomadic-t=nomadic.tools:tools
        nomadic-d=nomadic.daemon:daemon
    ''',

    # Note: this also requires flask-socketio and py-gfm.
    # These should be installed from git:
    # pip install git+git://github.com/dart-lang/py-gfm
    # pip install git+git://github.com/ftzeng/Flask-SocketIO
)