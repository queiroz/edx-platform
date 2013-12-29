import os, sys, logging
from unittest import TestCase

import polib

from config import LOCALE_DIR
from execute import call
from converter import Converter


def test_po_files(root=LOCALE_DIR):
    """
    This is a generator. It yields all of the .po files under root, and tests each one.
    """
    log = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    for dirpath, __, filenames in os.walk(root):
        for name in filenames:
            __, ext = os.path.splitext(name)
            if ext.lower() == '.po':
                filename = os.path.join(dirpath, name)
                yield msgfmt_check_po_file, filename, log
                yield check_messages, filename


def msgfmt_check_po_file(filename, log):
    """
    Call GNU msgfmt -c on each .po file to validate its format.
    Any errors caught by msgfmt are logged to log.
    """
    # Use relative paths to make output less noisy.
    rfile = os.path.relpath(filename, LOCALE_DIR)
    out, err = call(['msgfmt', '-c', rfile], working_directory=LOCALE_DIR)
    if err != '':
        log.info('\n' + out)
        log.warn('\n' + err)
    assert not err


def tags_in_string(msg):
    """
    Return the set of tags in a message string.

    Skips the HTML entity tags, since those might be translated differently.

    """
    __, tags = Converter().detag_string(msg)
    return set(t for t in tags if not t.startswith("&"))


def check_messages(filename):
    """
    Checks messages in various ways:

    Translations must have the same slots as the English.  The translation
    must not be empty.

    """
    # Don't check English files.
    if "/locale/en/" in filename:
        return

    problems = False
    pomsgs = polib.pofile(filename)
    for msg in pomsgs:
        if msg.msgid_plural:
            # Skip plurals, I don't know how the tags relate.
            continue
        if not msg.msgstr:
            print "Empty message for %r" % (msg.msgid,)
            problems = True
        if tags_in_string(msg.msgid) != tags_in_string(msg.msgstr):
            print "Different tags in %r and %r" % (msg.msgid, msg.msgstr)
            problems = True

    assert not problems
