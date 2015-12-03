import subprocess
from collections import defaultdict
from nomadic import conf


class MissingDependencyException(Exception):
    pass


def search(query):
    """searches for `query` in the notes.
    returns::

        {
            note_path: [
                (text, [(start, end), ...]),
            ...],
            ...
        }

    """
    notes_path = conf.ROOT
    note_path = None
    matches = defaultdict(list)

    try:
        # -S        smart case
        # -C n      n lines of before/after context
        # --ackmate more easily parseable format
        proc = subprocess.Popen(['ag', '-S', '-C 0', '--ackmate',
                                 '--ignore=*.pdf', query, notes_path],
                                stdout=subprocess.PIPE)

        while True:
            byte_line = proc.stdout.readline()
            line = byte_line.decode('utf-8').strip()
            if not line and proc.poll() is not None:
                break

            # line == '--' separates results from the same file
            # line == '' separates different files
            elif line == '--' or not line:
                continue

            # filenames are preceded with ':'
            elif line[0] == ':':
                note_path = line[1:].replace(notes_path, '').strip('/')

            # parse the result lines
            else:
                match_info, match = byte_line.split(b':', 1)
                match_locations = []
                if b';' in match_info:
                    line_num, match_locs = match_info.split(b';')
                    for mloc in match_locs.split(b','):
                        start, end = mloc.split(b' ')
                        match_locations.append((int(start), int(end)))

                # match locations are for the byte string,
                # so don't decode the match
                matches[note_path].append((match, match_locations))
        return matches

    except FileNotFoundError:
        raise MissingDependencyException('The silver searcher (ag) is not installed')


def search_pdf(query, window):
    """search through pdfs.
    does not give us positions of locations in the match.
    """
    notes_path = conf.ROOT
    matches = defaultdict(list)
    try:
        # -i        case insensitive
        # -R        recursive search
        # -C n      num of chars for context
        # -Z        use null bytes as filename/content separator
        proc = subprocess.Popen(['pdfgrep', '-i', '-R', '-Z', '-C {}'.format(window),
                                query, notes_path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)

        while True:
            line = proc.stdout.readline().strip()
            if not line and proc.poll() is not None:
                break
            print(line)
            note_path, match = line.split(b'\x00', 1)
            note_path = note_path.decode('utf-8').replace(notes_path, '').strip('/')
            matches[note_path].append(match.decode('utf-8'))
        return matches
    except FileNotFoundError:
        raise MissingDependencyException('pdfgrep is not installed')
