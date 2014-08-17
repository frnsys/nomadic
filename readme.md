# Nomad

I wasn't able to find a satisfactory way to use Evernote in Linux,
which led me to reconsider my Evernote usage in general.

Nomad leverages other tools I use daily to create a replacement
for my Evernote usage.

Nomad supports a simple directory structure of HTML, Markdown, txt, and
pdf notes and any other files which may need to be referenced. Nomad
provides an easier way of searching through and browsing those files.

For example:
```
notes
├── economics
│   ├── more economics notes.pdf
│   ├── my economics notes.md
│   └── my economics notes.resources
│       └── some image.png
├── programming
│   └── scala guide.html
└── some note.md
```

Here are some useful tools to go with Nomad:
* [BitTorrent Sync](www.bittorrent.com/sync) to keep notes synced across devices.
* [Vim](http://www.vim.org/) with:
    * [vim-instant-markdown](https://github.com/suan/vim-instant-markdown) to have live previews
    of Markdown files as you edit them.
    * my fork of the [instant-markdown-d](https://github.com/ftzeng/instant-markdown-d) backend for
    vim-instant-markdown (supports MathJax and relative image references)

---

## Setup
```bash
$ git clone https://github.com/ftzeng/nomad.git
$ cd nomad
$ pip install .
```

Create a config file (optional) at `~/.nomad` in JSON format.
For example:
```json
{
    "notes_dir": "~/Notes"
}
```
If you don't create this config file, `nomad` will create one for
you.

There's also an additional script which will setup
the dependencies for `vim-instant-markdown`.
```bash
$ ./setup.sh
```

---

## Usage
Run the `nomad` daemon.

```bash
$ nomad_d
```

The daemon watches your notes directory and automatically updates
the index and compiles notes when they change.
It will also automatically update references to other notes as they
change.

Primary interaction with `nomad` is through
the command line.

```bash
$ nomad --help

Usage: nomad [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  browse  Browse through notes via a web browser.
  build   Manually re-build the browsable tree.
  index   Manually update or reset the note index.
  search  Search through notes.
```

### Browsing notes
The Nomad daemon compiles your notes into a browsable local
HTML structure as they change.

It compiles only HTML and Markdown notes.

References to local files are made relative
to the build directory, so no
extra files are redundantly copied over.

You can browse this structure by running:
```bash
$ nomad browse
```
which opens up the root directory ('notebook') in your
default web browser.

You can immediately jump to a specific notebook by
passing its name in:
```bash
$ nomad browse economics
```

If the specified name matches multiple notebooks,
you'll be given the option to select the right one.

### Searching notes
The Nomad daemon will maintain a search index
for your notes as you update them.

You can search through your notes by running:
```bash
$ nomad search <query>
```

This will present a list of results, along with snippets where the
keyword was found, for you to choose from.

The search feature can search through HTML, Markdown, txt, and pdf
files.

---

## Development
```bash
$ git clone https://github.com/ftzeng/nomad.git
$ cd nomad
$ pip install --editable .
```

This installs the package locally, allowing you to work on it and test
it easily.

To run the included tests:
```bash
$ pip install nose
$ nosetests test
```

---

## To Do
* setup daemon to start on startup in osx/ubuntu
* better css stylesheet

---

## Acknowledgements
The CSS stylesheet used for the compiled notes is from [here](https://gist.github.com/tuzz/3331384).