from __future__ import print_function

import logging
log = logging.getLogger('main')

import sys
import time
import string
import struct
import argparse
import hmac, hashlib

from cli import CommandLineInterface

import nfc
import nfc.clf
import nfc.ndef

def add_show_parser(parser):
    pass

def add_dump_parser(parser):
    parser.add_argument(
        "-o", dest="output", metavar="FILE",
        type=argparse.FileType('w'), default="-",
        help="save ndef to FILE (writes binary data)")
        
def add_load_parser(parser):
    parser.add_argument(
        "input", metavar="FILE", type=argparse.FileType('r'),
        help="ndef data file ('-' reads from stdin)")

class TagTool(CommandLineInterface):
    def __init__(self):
        parser = ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="")
        parser.add_argument(
            "-p", dest="authenticate", metavar="PASSWORD",
            help="unlock with password if supported")
        subparsers = parser.add_subparsers(
            title="commands", dest="command")
        add_show_parser(subparsers.add_parser(
                'show', help='pretty print ndef data'))
        add_dump_parser(subparsers.add_parser(
                'dump', help='read ndef data from tag'))
        add_load_parser(subparsers.add_parser(
                'load', help='write ndef data to tag'))
        
        self.rdwr_commands = {"show": self.show_tag,
                              "dump": self.dump_tag,
                              "load": self.load_tag,}
    
        super(TagTool, self).__init__(
            parser, groups="rdwr card dbg clf")

    def on_rdwr_startup(self, targets):
        if self.options.command in self.rdwr_commands.keys():
            print("** waiting for a tag **", file=sys.stderr)
            return targets

    def on_rdwr_connect(self, tag):
        if self.options.authenticate is not None:
            if len(self.options.authenticate) > 0:
                key, msg = self.options.authenticate, tag.identifier
                password = hmac.new(key, msg, hashlib.sha256).digest()
            else:
                password = "" # use factory default password
            result = tag.authenticate(password)
            if result is False:
                print("Access Denied")
                return False
            if result is None:
                print(tag)
                print("Unauthoriesed Personnel")
                return False
            
        self.rdwr_commands[self.options.command](tag)
        return self.options.wait or self.options.loop
    
    def on_card_startup(self, target):
        if self.options.command == "emulate":
            target = self.prepare_tag(target)
            print("** waiting for a reader **", file=sys.stderr)
            return target

    def on_card_connect(self, tag):
        log.info("tag activated")
        return self.emulate_tag_start(tag)

    def on_card_release(self, tag):
        log.info("tag released")
        self.emulate_tag_stop(tag)
        return True

    def show_tag(self, tag):
        print(tag)
        
        if tag.ndef:
            print("NDEF Capabilities:")
            print("  readable  = %s" % ("no","yes")[tag.ndef.is_readable])
            print("  writeable = %s" % ("no","yes")[tag.ndef.is_writeable])
            print("  capacity  = %d byte" % tag.ndef.capacity)
            print("  message   = %d byte" % tag.ndef.length)
            if tag.ndef.length > 0:
                print("NDEF Message:")
                print(tag.ndef.message.pretty())
        
        if self.options.verbose:
            print("Memory Dump:")
            print('  ' + '\n  '.join(tag.dump()))

    def dump_tag(self, tag):
        if tag.ndef:
            data = tag.ndef.message
            if self.options.output.name == "<stdout>":
                self.options.output.write(str(data).encode("hex"))
                if self.options.loop:
                    self.options.output.write('\n')
                else:
                    self.options.output.flush()
            else:
                self.options.output.write(str(data))

    def load_tag(self, tag):
        try: self.options.data
        except AttributeError:
            self.options.data = self.options.input.read()
            try: self.options.data = self.options.data.decode("hex")
            except TypeError: pass

        if tag.ndef is None:
            print("NDEF Tag Denied")
            return

        if not tag.ndef.is_writeable:
            print("Tag is not writeable")
            return

        new_ndef_message = nfc.ndef.Message(self.options.data)
        if new_ndef_message == tag.ndef.message:
            print("The Tag already contains the message to write.")
            return

        if len(str(new_ndef_message)) > tag.ndef.capacity:
            print("The new message exceeds the Tag's capacity.")
            return
        
        print("Old message:")
        print(tag.ndef.message.pretty())
        tag.ndef.message = new_ndef_message
        print("New message:")
        print(tag.ndef.message.pretty())

    def format_tag(self, tag):
        if (self.options.tagtype != "any" and
            self.options.tagtype[2] != tag.type[4]):
            print("This is not a Type {0} Tag but you said so."
                  .format(self.options.tagtype[2]))
            return

        if self.options.version is None:
            version = {'Type1Tag': 0x12, 'Type2Tag': 0x12,
                       'Type3Tag': 0x10, 'Type4Tag': 0x30}[tag.type]
        else: version = self.options.version
            
        formatted = tag.format(version=version, wipe=self.options.wipe)

        if formatted is True:
            {'tt1': self.format_tt1_tag, 'tt2': self.format_tt2_tag,
             'tt3': self.format_tt3_tag, 'tt4': self.format_tt4_tag,
             'any': lambda tag: None}[self.options.tagtype](tag)
            print("Formatted %s" % tag)
            if tag.ndef:
                print("  readable  = %s" % ("no","yes")[tag.ndef.is_readable])
                print("  writeable = %s" % ("no","yes")[tag.ndef.is_writeable])
                print("  capacity  = %d byte" % tag.ndef.capacity)
                print("  message   = %d byte" % tag.ndef.length)
        elif formatted is None:
            print("Sorry, this tag can not be formatted.")
        else:
            print("Sorry, I could not format this tag.")

    def format_tt2_tag(self, tag):
        pass

    def protect_tag(self, tag):
        print(tag)
        
        if self.options.password is not None:
            if len(self.options.password) >= 8:
                print("generating diversified key from password")
                key, msg = self.options.password, tag.identifier
                password = hmac.new(key, msg, hashlib.sha256).digest()
            elif len(self.options.password) == 0:
                print("using factory default key for password")
                password = ""
            else:
                print("A password should be at least 8 characters.")
                return
            
        result = tag.protect(password, self.options.unreadable,
                             self.options.protect_from)
        if result is True:
            print("This tag is now protected.")
        elif result is False:
            print("Failed to protect this tag.")
        elif result is None:
            print("Sorry, but this tag can not be protected.")

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgparseError(self.prog, message)

if __name__ == '__main__':
    try:
        TagTool().run()
    except ArgparseError as e:
        prog = e.args[1].split()
    else:
        sys.exit(0)

    if len(prog) == 1:
        sys.argv = sys.argv + ['show']
    elif prog[-1] == "format":
        sys.argv = sys.argv + ['any']

    try:
        TagTool().run()
    except ArgparseError as e:
        print(e, file=sys.stderr)
