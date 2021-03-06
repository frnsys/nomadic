# nomadic

---

9/1/2016: I'm no longer maintaining `nomadic`. The tool I use now for managing my Markdown notes is [`nom`](https://github.com/frnsys/nom), which is basically `nomadic` without the web interface (I didn't use it much).

---

![](screenshots/01.png)
(more screenshots at the end)

`nomadic`...

- is a simple daemon/web service that makes managing notes nicer.
- supports a simple directory structure of markdown, txt, and pdf notes and any other files which are referenced from them.
- provides an easier way of searching through and browsing those files through either the command line or a simple web interface.

For example, you might have a folder like this:

    notes
    ├── math
    │   ├── my math notes.md
    │   └── assets
    │       └── some image.png
    ├── programming
    │   └── scala guide.md
    └── some note.md

I recommend using `nomadic` with [SyncThing](https://syncthing.net/) to keep
notes synced across devices. With this setup, `nomadic` becomes a decentralized,
simplified alternative to Evernote and other note-taking services.

Since `nomadic` runs a small server for browsing files, you can access your notes remotely that way as well.

---

## Features

- Supports __GitHub-Flavored__ markdown
- Supports __MathJax__ syntax
- Supports __references to images__ and other files, and will automatically update those references if the files are moved
- __Full-text search__ (across txt, markdown, and even pdf files)
- A tool for __saving copied html as markdown__ (external images are automatically saved locally)
- Serves __a browsable site of all your notes__
- Complete __command-line interface__
- Export notes as portable __presentations__ or as standalone html documents

---

## Setup

### Installation

    $ git clone https://github.com/frnsys/nomadic.git
    $ cd nomadic
    $ pip install .

    # install front-end packages
    $ cd nomadic/server/assets/
    $ bower install

    # build the highlight.js library
    $ cd static/vendor/highlight.js
    $ npm install
    # ...with all languages
    $ node tools/build.js
    # ...or with only specific languages
    $ node tools/build.js python ruby javascript scala java bash http sql cs cpp css json objectivec xml markdown apache nginx

    # install search dependencies
    # ubuntu:
    $ sudo apt-get install silversearcher-ag
    # osx:
    $ brew install the_silver_searcher

If you wish to use `nomadic clip` (to convert clipboard HTML into markdown notes) on OSX, you also need the following:

    $ pip install pyobjc

If you wish to be able to search through PDFs, you also need the following:

    # ubuntu (package manager's version may be out of date, must be >= 1.4):
    $ sudo apt-get install libpoppler-cpp-dev
    $ git clone https://gitlab.com/pdfgrep/pdfgrep.git /tmp/pdfgrep
    $ cd /tmp/pdfgrep
    $ bash autogen.sh
    $ ./configure
    $ make
    $ sudo make install

    # osx
    $ brew install pdfgrep

### Configuration
Create a config file (optional) at `~/.nomadic` in YAML format. See [Configuration](#configuration) for more details.
If you don't create this config file, `nomadic` will create one for you.


### The Daemon
The daemon watches your notes directory and automatically updates the index as they change.
It will also automatically update references to other notes as they change.

The daemon also runs a small server which allows for
easy browsing/searching through notes as well as a quick way
of previewing notes as you work on them.

#### To get the `nomadic` daemon to run automatically on startup...

##### Linux (Upstart)
If you're on a Linux distro that uses Upstart, you can do:

    $ sudo cp scripts/nomadic.conf /etc/init/nomadic.conf

Then to start the daemon right away:

    $ sudo start nomadic

##### OSX
If you're on OSX, you can do:

    $ cp scripts/com.nomadic.plist ~/Library/LaunchAgents/com.nomadic.plist

Then you can start the daemon right away:

    $ launchctl load ~/Library/LaunchAgents/com.nomadic.plist

---

## Configuration
`nomadic` checks for a configuration at `~/.nomadic`. If you
start `nomadic` without a config, one will be created for you.

For example:

```yaml
root: ~/notes
```

Whenever you change this file, you must restart the `nomadic` daemon:

    # Linux (Upstart)
    $ sudo restart nomadic

    # OSX (there might be a better way)
    $ pkill -f nomadic-d; launchctl start com.nomadic

### Custom CSS
You can specify a custom stylesheet to override the default one.
In your config, specify the path to that stylesheet:

```yaml
...
override_stylesheet: ~/path/to/my/styles.css
...
```

---

## Usage
Run the `nomadic` daemon if it isn't running already.

    $ nomadic-d

Primary interaction with `nomadic` is through
the command line.

    $ nomadic --help

    Usage: nomadic [OPTIONS] COMMAND [ARGS]...

    Options:
    --help  Show this message and exit.

    Commands:
    browse   browse notes via the web interface
    clean    remove unreferenced asset folders
    clip     convert html in the clipboard to markdown
    export   export a note to html
    new      create a new note
    search   search through notes

### Browsing notes
You can browse this notes site by running:

    $ nomadic browse

which opens up the root directory ('notebook') in your default web browser.

You can immediately jump to a specific notebook by passing its name in:

    $ nomadic browse economics

If the specified name matches multiple notebooks,
you'll be given the option to select the right one.

### Searching notes
You can search through your notes by running:

    $ nomadic search <query>

This will present a list of results, along with snippets where the
keyword was found, for you to choose from.

`nomadic` can search through markdown, txt, and pdf files.

### Adding other files (images, etc)
If you are going to be referencing other files in your notes,
you should put them in a directory called `assets` in
that note's notebook directory. `nomadic` recognizes these
directories and handles them specially.

### Exporting notes
You can export a note to a standalone html document pretty easily.

For example:

    $ nomadic export path/to/some_note.md path/to/export/to

This compiles the note to the specified folder, copying over images.

If you will be making changes to the note, you can specify `--watch` to recompile the note when it changes.

#### Presentations

Similarly, you can export a note as a standalone html presentation:

    $ nomadic export --presentation path/to/some_note.md path/to/export/to

The compiled HTML includes a script which breaks the note into slides according
to `<hr>` tags (specified in markdown as `---`, `***`, or `___`). Slides resize to take
up the full window height, and any slides that are too tall are automatically scaled down.
You can use the up/down arrow keys to navigate.

### Tips

- You can view the 20 most recently modified notes using the `/recent/` path in the web browser.

---

## Development

    $ git clone https://github.com/frnsys/nomadic.git
    $ cd nomadic
    $ pip install --editable .

This installs the package locally, allowing you to work on it and test it easily.

To run the included tests:

    $ pip install nose
    $ nosetests test

## Screenshots

#### blockquotes and images
![](scrots/01.png)

#### embedded pdfs
![](scrots/02.png)

#### you can copy and paste articles easily through the web editor
![](scrots/03.png)

#### highlighting support
![](scrots/04.png)

#### nice images
![](scrots/05.png)

#### code and mathjax galore
![](scrots/06.png)

#### list and filter your notebooks
![](scrots/07.png)

#### search your notes
![](scrots/08.png)