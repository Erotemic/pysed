#!/usr/bin/env python
# -*- coding: utf-8 -*-

# main.py file is part of pysed.

# Copyright 2014-2015 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# pysed is utility that parses and transforms text

# https://github.com/dslackw/pysed

# Pysed is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import re
import sys
from pysed.__metadata__ import __prog__
from pysed.options import (
    usage,
    helps,
    version
)


class Pysed(object):
    """Pysed is a stream editor, is used to perform basic text
    transformations from a file or from pipeline. It reads text,
    line by line, from a file and replace, insert or print all
    text or specific area.
    """
    def __init__(self, args, data, filename, write):
        self.args = args
        self.pattern = ""
        self.repl = ""
        self.count = 0
        self.flag = "0"
        self.write = write
        self.filename = filename
        self.data = data.rstrip()
        self.color = ""
        self.color_def = "\x1b[0m"
        self.text = ""
        self.numlines = range(1, len(self.data.splitlines()) + 1)
        self._patternInit()
        self._extraInit()
        self._writeInit()

    def _patternInit(self):
        """Pattern initialization
        """
        if len(self.args) > 2:      # pattern
            self.pattern = self.args[1]
        if len(self.args) > 3:      # replace
            self.repl = self.args[2]

    def _extraInit(self):
        """Extra initialization
        """
        if len(self.args) > 4:      # extra
            adv = self.args[3].split("/")
            if len(adv) > 3:
                usage()
                sys.exit("{0}: {1}".format(__prog__, messageError(200, Err="")))
            if len(adv) < 3:
                adv += [''] * (3 - len(adv))
            if adv[0]:
                self.numlines = map(int, re.findall("\d+", adv[0]))
                if self.numlines == [] or self.numlines == [0]:
                    self.numlines = range(1, len(self.data.splitlines()) + 1)
            if adv[1]:
                try:
                    self.count = int(adv[1])
                except ValueError:
                    self.count = 0
            if adv[2]:
                self.flag = adv[2]

    def _writeInit(self):
        """Write initilization
        """
        if len(self.args) > 7:      # write
            self.write = self.args[7]

    def _difftext(self, text1, text2):
        import difflib
        text1_lines = text1.splitlines()
        text2_lines = text2.splitlines()
        ignore_whitespace = True
        if ignore_whitespace:
            text1_lines = [t.rstrip() for t in text1_lines]
            text2_lines = [t.rstrip() for t in text2_lines]
            ndiff_kw = dict(linejunk=difflib.IS_LINE_JUNK,
                            charjunk=difflib.IS_CHARACTER_JUNK)
        else:
            ndiff_kw = {}
        all_diff_lines = list(difflib.ndiff(text1_lines, text2_lines, **ndiff_kw))

        # if num_context_lines is None:
        diff_lines = all_diff_lines
        return diff_lines
        # else:
        #     from utool import util_list
        #     # boolean for every line if it is marked or not
        #     ismarked_list = [len(line) > 0 and line[0] in '+-?'
        #                      for line in all_diff_lines]
        #     # flag lines that are within num_context_lines away from a diff line
        #     isvalid_list = ismarked_list[:]
        #     for i in range(1, num_context_lines + 1):
        #         isvalid_list[:-i] = util_list.or_lists(isvalid_list[:-i],
        #                                                ismarked_list[i:])
        #         isvalid_list[i:]  = util_list.or_lists(isvalid_list[i:],
        #                                                ismarked_list[:-i])
        #     USE_BREAK_LINE = True
        #     if USE_BREAK_LINE:
        #         # insert a visual break when there is a break in context
        #         diff_lines = []
        #         prev = False
        #         visual_break = '\n <... FILTERED CONTEXT ...> \n'
        #         #print(isvalid_list)
        #         for line, valid in zip(all_diff_lines, isvalid_list):
        #             if valid:
        #                 diff_lines.append(line)
        #             elif prev:
        #                 if False:
        #                     diff_lines.append(visual_break)
        #             prev = valid
        #     else:
        #         diff_lines = util_list.compress(all_diff_lines, isvalid_list)

    def _highlight_diff(self, text):
        import pygments
        import pygments.lexers
        import pygments.formatters
        import pygments.formatters.terminal
        formater = pygments.formatters.terminal.TerminalFormatter(bg='dark')
        lexer = pygments.lexers.get_lexer_by_name('diff')
        return pygments.highlight(text, lexer, formater)

    def replaceText(self):
        """Replace text with new
        """
        self.regexFlags()
        count = 0
        for line in self.data.splitlines(keepends=True):
            count += 1
            if count in self.numlines:
                try:
                    newline = re.sub(self.pattern, self.repl, line, self.count,
                                     self.flag)
                    self.text += newline
                    if line != newline:
                        print('line = {!r}'.format(line))
                        print('newline = {!r}'.format(newline))
                        show_newlines = True
                        if show_newlines:
                            line = line.replace('\n', '\\n')
                            newline = newline.replace('\n', '\\n')
                        diff = self._difftext(line, newline)
                        diff_text = self._highlight_diff('\n'.join(diff))
                        print(diff_text)
                except re.error as e:
                    sys.exit("{0}: {1}".format(__prog__, messageError(
                        000, Err=e)))
            else:
                self.text += line
        self.selectPrintWrite()

    def findallText(self):
        """Find all from pattern in text
        """
        self.regexFlags()
        count = 0
        for line in self.data.splitlines():
            count += 1
            if count in self.numlines:
                try:
                    self.text += " ".join(re.findall(self.pattern, line,
                                                     self.flag))
                except (re.error, IndexError, AttributeError, TypeError) as e:
                    sys.exit("{0}: {1}".format(__prog__, messageError(
                        000, Err=e)))
        self.selectPrintWrite()

    def searchText(self):
        """Search for the first matching
        """
        self.regexFlags()
        text = ""
        count = 0
        for line in self.data.splitlines():
            count += 1
            if count in self.numlines:
                try:
                    text = re.search(self.pattern, line, self.flag)
                    if text is not None:
                        self.text += text.group(self.count)
                except (re.error, IndexError, AttributeError) as e:
                    sys.exit("{0}: {1}".format(__prog__, messageError(
                        000, Err=e)))
        self.selectPrintWrite()

    def matchText(self):
        """Matching pattern into text
        """
        self.regexFlags()
        text = ""
        count = 0
        for line in self.data.splitlines():
            count += 1
            if count in self.numlines:
                try:
                    text = re.match(self.pattern, line, self.flag)
                    if text is not None:
                        self.text += text.group(self.count)
                except (re.error, IndexError, AttributeError) as e:
                    sys.exit("{0}: {1}".format(__prog__, messageError(
                        000, Err=e)))
        self.selectPrintWrite()

    def findLines(self):
        """Find text and print line
        """
        count = 0
        for line in self.data.splitlines():
            count += 1
            if self.pattern in line:
                self.text += "{0} {1}".format(count, line + "\n")
            else:
                self.text += "{0} {1}".format("-" * len(str(count)),
                                              line + "\n")
        self.selectPrintWrite()

    def highLight(self):
        """Highlight text and print
        """
        self.colors()
        self.text = (self.data.replace(
            self.pattern, self.color + self.pattern + self.color_def))
        self.selectPrintWrite()

    def textStat(self):
        """Print text statics
        """
        lines, words = 0, 0
        chars = len(self.data.replace(" ", ""))
        blanks = len(self.data) - chars
        for line in self.data.splitlines():
            lines += 1
            words += len(re.findall(r"[\w']+", line))
        self.text = ("Lines: {0}, Words: {1}, Chars: {2}, Blanks: {3}".format(
            lines, words, chars, blanks))
        self.selectPrintWrite()

    def regexFlags(self):
        """Python regex flags
        """
        patt_flag = ""
        for i in self.flag.split("|"):
            re_patt = {
                "I": "2",
                "L": "4",
                "M": "8",
                "S": "16",
                "U": "32",
                "X": "64",
                "IGNORECASE": "2",
                "LOCALE": "4",
                "MULTILINE": "8",
                "DOTALL": "16",
                "UNICODE": "32",
                "VERBOSE": "64",
                "0": "0",
                "": ""
            }
            try:
                patt_flag += re_patt[i] + "|"
            except KeyError:
                usage()
                sys.exit("{0}: {1}".format(__prog__, messageError(
                    500, Err=self.flag)))
        if self.flag:
            self.flag = int(patt_flag[:-1])
        else:
            self.flag = 0

    def colors(self):
        """Colors dictionary
        """
        paint = {
            'black': '\x1b[30m',
            'red': '\x1b[31m',
            'green': '\x1b[32m',
            'yellow': '\x1b[33m',
            'blue': '\x1b[34m',
            'magenta': '\x1b[35m',
            'cyan': '\x1b[36m',
        }
        try:
            self.color = paint[self.repl]
        except KeyError:
            usage()
            sys.exit("{0}: {1}".format(__prog__, messageError(
                600, Err=self.repl)))

    def selectPrintWrite(self):
        """Write to file or print
        """
        if self.write:
            self.writeFile(self.text)
        else:
            diffonly = True
            if not diffonly:
                print(self.text.rstrip())

    def writeFile(self, newtext):
        """Write data to file
        """
        with open(self.filename, "w") as fo:
            for line in newtext.splitlines():
                fo.write(line + "\n")
            fo.close()
        print('wrote to ' + self.filename)


def messageError(code, Err):
    """Error messages dictionary
    """
    msg = {
        000: "error: {0}".format(Err),
        100: "error: Too few arguments",
        200: "error: Too many arguments",
        300: "error: '{0}' argument does not recognized".format(Err),
        400: "error: No such file or directory {0}".format(Err),
        500: "error: '{0}' flag doesn't exist".format(Err),
        600: "error: '{0}' color doesn't exist".format(Err)
    }
    return msg[code]


def executeArguments(args, data, filename, isWrite):
    """Execute available arguments
    """
    pysed = Pysed(args, data, filename, isWrite)
    if args[0] in ["-r", "--replace"]:
        pysed.replaceText()
    elif args[0] in ["-f", "--findall"]:
        pysed.findallText()
    elif args[0] in ["-s", "--search"]:
        pysed.searchText()
    elif args[0] in ["-m", "--match"]:
        pysed.matchText()
    elif args[0] in ["-l", "--lines"]:
        pysed.findLines()
    elif args[0] in ["-g", "--highlight"]:
        pysed.highLight()
    elif args[0] in ["-t", "--stat"]:
        pysed.textStat()


def checkArguments(args):
    """Execute arguments
    """
    if len(args) == 1 and args[0] in ["-h", "--help"]:
        helps()
    elif len(args) == 1 and args[0] in ["-v", "--version"]:
        version()
    elif len(args) == 0:
        usage()
        sys.exit("{0}: {1}".format(__prog__, messageError(100, Err="")))
    elif args and args[0] not in ["-r", "--replace", "-f", "--findall",
                                  "-s", "--search", "-m", "--match",
                                  "-l", "--lines", "-g", "--highlight",
                                  "-t", "--stat"]:
        usage()
        sys.exit("{0}: {1}".format(__prog__, messageError(300, Err=args[0])))


def main():
    # import argparse
    # parser = argparse.ArgumentParser(description='pysed')
    # parser.add_argument('-w', '--write', type=str, help='writes to file')
    # parser.add_argument('search', nargs='+')
    # parser.add_argument('replace', nargs='+')
    # ap = parser.parse_args()

    args = sys.argv
    args.pop(0)
    data = ""
    isWrite = False

    checkArguments(args)
    if len(args) > 6:
        usage()
        sys.exit("{0}: {1}".format(__prog__, messageError(200, Err="")))

    if args[-1] in ['-w', '--write']:
        isWrite = True
        del args[-1]
    elif len(args) == 6 and args[-1] not in ['-w', '--write']:
        usage()
        sys.exit("{0}: {1}".format(__prog__, messageError(300, Err=args[-1])))

    filename = "{0}.log".format(__prog__)
    not_piping = sys.stdin.isatty()
    if not_piping:
        fileInput = filename = args[len(args) - 1]
        try:
            f = open(fileInput)
            data = f.read()
        except IOError:
            usage()
            sys.exit("{0}: {1}".format(
                __prog__, messageError(400, Err=args[len(args) - 1])))
    else:
        args.append("last")
        try:
            data = sys.stdin.read()
        except KeyboardInterrupt:
            print("")
            sys.exit(0)

    executeArguments(args, data, filename, isWrite)

if __name__ == "__main__":
    main()
