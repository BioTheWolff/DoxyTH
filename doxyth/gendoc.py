import argparse
import re
import os
from .verify import verify_directory
from os.path import isfile, join, isdir
import subprocess
import json


class Gendoc:
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

            # write translations into a json file so the doxyth executable can fetch translations quickly
            self.__write_translations_to_file()

            # Check or create doxygen config
            self.__setup_doxygen_files(args.translation_dir)

            # Change Doxyfile and run doxygen for it to directly analyse files modified by the script using
            # FILE_PATTERNS
            for lang in self.available_translations:
                if self.verbose:
                    print(f"{lang.upper()}... ")

    @staticmethod
    def __setup_doxygen_files(translations_dir: str):
        # Change the directory to have a / at the end for the Doxyfile
        if not translations_dir.endswith("/"):
            translations_dir += "/"

        if not os.path.exists('Doxyfile'):
            fnull = open(os.devnull, 'w')
            subprocess.call(['doxygen', '-s', '-g', 'Doxyfile'], stdout=fnull, stderr=subprocess.STDOUT)
            fnull.close()

        with open('Doxyfile') as f:
            lines = f.readlines()

        for n, line in enumerate(lines):
            # Sets it to exclude already existing docs
            if re.match(r"^EXCLUDE\s*=", line.strip()):
                lines[n:n+1] = f"EXCLUDE = docs/\n" \
                               f"          {translations_dir}\n"

            # Sets recursion ON
            if re.match(r"^RECURSIVE\s*=", line.strip()):
                lines[n] = "RECURSIVE = YES\n"

            # LaTeX generation OFF
            if re.match(r"^GENERATE_LATEX\s*=", line.strip()):
                lines[n] = "GENERATE_LATEX = NO\n"

            # The DoxyTH batch file that will tell the file ran by Doxygen what translation to read
            if re.match(r"^FILTER_PATTERNS\s*=", line.strip()):
                lines[n] = f"FILTER_PATTERNS = *py=.dthb\n"

        with open('Doxyfile', 'w') as f:
            f.writelines(lines)

    @staticmethod
    def __adapt_configs_to_lang(lang):
        # Doxyfile
        with open('Doxyfile') as f:
            lines = f.readlines()

        for n, line in enumerate(lines):
            # Change HTML output to docs/
            if re.match(r"^HTML_OUTPUT\s*=", line.strip()):
                lines[n] = f"HTML_OUTPUT = docs/{lang}/\n"

        with open('Doxyfile', 'w') as f:
            f.writelines(lines)

        # batch file
        with open('.dthb.bat') as b:
            b.write(f"python -m doxyth.doxyth {lang} %1")

    def __write_translations_to_file(self):
        with open(".dtht", 'w') as f:
            f.write(json.dumps(self.langs))

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
                    buffer.append(line.rstrip() + '\n')

            if buffer or buffer_name:
                raise Exception(f"Warning: Unexpected EOF while reading ID {buffer_name} in file "
                                f"'{path.split('/')[-1]}'")

            final = {**final, **file_doc}

        return final


if __name__ == '__main__':
    Gendoc()
