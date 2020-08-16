import argparse
import re
import os
from .verify import verify_directory
import shutil
import errno
from os.path import isfile, join, isdir, abspath


def copy(src, dest):
    if isdir(dest):
        shutil.rmtree(dest)
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy2(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)


class DoxyTH:
    valid_codes = ['ab', 'aa', 'af', 'ak', 'sq', 'am', 'ar', 'an', 'hy', 'as', 'av', 'ae', 'ay', 'az', 'bm', 'ba', 'eu',
                   'be', 'bn', 'bh', 'bi', 'bs', 'br', 'bg', 'my', 'ca', 'ch', 'ce', 'ny', 'zh', 'cv', 'kw', 'co', 'cr',
                   'hr', 'cs', 'da', 'dv', 'nl', 'dz', 'en', 'eo', 'et', 'ee', 'fo', 'fj', 'fi', 'fr', 'ff', 'gl', 'ka',
                   'de', 'el', 'gn', 'gu', 'ht', 'ha', 'he', 'hz', 'hi', 'ho', 'hu', 'ia', 'id', 'ie', 'ga', 'ig', 'ik',
                   'io', 'is', 'it', 'iu', 'ja', 'jv', 'kl', 'kn', 'kr', 'ks', 'kk', 'km', 'ki', 'rw', 'ky', 'kv', 'kg',
                   'ko', 'ku', 'kj', 'la', 'lb', 'lg', 'li', 'ln', 'lo', 'lt', 'lu', 'lv', 'gv', 'mk', 'mg', 'ms', 'ml',
                   'mt', 'mi', 'mr', 'mh', 'mn', 'na', 'nv', 'nd', 'ne', 'ng', 'nb', 'nn', 'no', 'ii', 'nr', 'oc', 'oj',
                   'cu', 'om', 'or', 'os', 'pa', 'pi', 'fa', 'pl', 'ps', 'pt', 'qu', 'rm', 'rn', 'ro', 'ru', 'sa', 'sc',
                   'sd', 'se', 'sm', 'sg', 'sr', 'gd', 'sn', 'si', 'sk', 'sl', 'so', 'st', 'es', 'su', 'sw', 'ss', 'sv',
                   'ta', 'te', 'tg', 'th', 'ti', 'bo', 'tk', 'tl', 'tn', 'to', 'tr', 'ts', 'tt', 'tw', 'ty', 'ug', 'uk',
                   'ur', 'uz', 've', 'vi', 'vo', 'wa', 'cy', 'wo', 'fy', 'xh', 'yi', 'yo', 'za', 'zu']
    available_translations = None
    verbose = None
    langs = None

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("translation_dir", help="Documentations to replace the 'doc_id's.")
        parser.add_argument("working_dir", help="The directory where the documentation will be placed")
        parser.add_argument("--verify", help="Makes the documentation files be verified instead", action='store_true')
        parser.add_argument("-V", "--verbose", help="Activates the program verbose mode. Only available when not "
                                                    "verifying the files", action='store_true')

        args = parser.parse_args()

        self.__flow(args)

    def __flow(self, args):
        self.available_translations = []
        self.langs = {}

        if args.verify:
            self.__analyze_translations_dir(args.translation_dir)
            for lang in self.available_translations:
                verify_directory(f"{args.translation_dir}/{lang}")
        else:
            self.verbose = args.verbose
            self.__analyze_translations_dir(args.translation_dir)

            if not self.available_translations:
                print("No applicable translation detected. Aborting.")
                exit(0)

            # Read all the languages docs
            for lang in self.available_translations:
                if self.verbose:
                    print(f"{lang.upper()}: Reading docs")
                self.langs[lang] = self.__read_docs(f"{args.translation_dir}/{lang}")

            # Backup files in a directory (".dthstems")
            copy(args.working_dir, ".dthstems")

            # Replace all files' 'doc_id's with corresponding documentations
            for lang in self.available_translations:
                if self.verbose:
                    print(f"{lang.upper()}: Reading and replacing documentation IDs")
                test = self.__read_working_dir(args.working_dir)
                print(test)

    def __analyze_translations_dir(self, path):
        for d in os.listdir(path):
            if len(d) != 2:
                continue
            if d not in self.valid_codes:
                print(f"Warning: ISO 639-1 language code not recognised: {d}. Ignoring this directory.")
                continue

            if self.verbose:
                print(f"Found language code {d}")
            self.available_translations.append(d)

    def __read_docs(self, path):
        files = [f for f in os.listdir(path) if isfile(join(path, f)) and f.endswith(".dthdoc")]
        final = {}

        for file in files:
            with open(f"{path}/{file}") as f:
                lines = f.readlines()

            file_doc = {}
            buffer_name = None
            buffer = []
            just_read_id = False
            for line in lines:
                if re.match(r"\s*@doc_id\s*", line.strip()):
                    buffer_name = re.split(r"\s*@doc_id\s*", line.strip())[-1]
                    just_read_id = True
                    continue
                elif line.strip() == '"""' and just_read_id:
                    just_read_id = False
                elif line.strip() == '"""' and not just_read_id:
                    if self.verbose:
                        print(f"Linked ID {buffer_name}.")
                    file_doc[buffer_name] = buffer
                    buffer_name, buffer = None, []
                else:
                    buffer.append(line.strip() + '\n')

            if buffer or buffer_name:
                raise Exception(f"Warning: Unexpected EOF while reading ID {buffer_name} in file "
                                f"'{path.split('/')[-1]}'")

            final = {**final, **file_doc}

        return final

    def __read_working_dir(self, directory):
        final = {}

        for e in os.listdir(directory):
            p = f"{directory}/{e}"
            if isfile(p):
                final[p] = self.__read_file_from_path(p)
            elif isdir(p):
                res = self.__read_working_dir(p)
                final = {**final, **res} if res else final

        return final

    @staticmethod
    def __read_file_from_path(path):
        with open(path) as f:
            lines = f.readlines()

        final = {}
        in_doc = False
        doclines = [None, None]

        offset = None
        doc_id = None

        for n, line in enumerate(lines):
            if line.strip() == '"""':
                if not in_doc:
                    # We just entered in a doc, set the starting line number and the offset
                    doclines[0] = n
                    offset = re.split(r'(\s*)"""', line)[1]
                if in_doc:
                    # We are exiting a doc, set the ending line and register the thing to replace
                    doclines[1] = n
                    final[tuple(doclines)] = {"id": doc_id, "offset": offset}
                    # Reset values to what they were initially
                    offset = None
                    doc_id = None
                    doclines = [None, None]

                in_doc = False if in_doc else True

            if in_doc:
                if re.match(r"\s*###\s*@doc_id\s*", line):
                    # Found, we now split by regex and register the doc id
                    doc_id = re.split(r"\s*###\s*@doc_id\s*", line.rstrip())[-1]

        if in_doc:
            raise Exception(f"Unexpected EOF while reading {path}")

        return final

    @staticmethod
    def __write_file(path, content):
        with open(path, mode="w") as f:
            for line in content:
                f.write(line)


if __name__ == '__main__':
    DoxyTH()