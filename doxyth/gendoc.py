import argparse
import re
import os
from .verify import verify_directory
from os.path import isfile, join, exists
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
    docs_output_path = 'docs'

    def __init__(self):
        """
        ### @doc_id gendoc_init
        """

        parser = argparse.ArgumentParser()
        parser.add_argument("translation_dir", help="Documentations to replace the 'doc_id's.")
        parser.add_argument("--verify", help="Makes the documentation files be verified instead", action='store_true')
        parser.add_argument("-V", "--verbose", help="Activates the program verbose mode. Only available when not "
                                                    "verifying the files", action='store_true')

        args = parser.parse_args()

        self.flow(args)

    def flow(self, args):
        """
        ### @doc_id gendoc_flow

        This is the main flow function of the class.

        Allows to easily dispatch all the tasks to smaller functions.
        """

        self.available_translations = []
        self.langs = {}

        if args.verify:
            self.analyze_translations_dir(args.translation_dir)
            for lang in self.available_translations:
                verify_directory(f"{args.translation_dir}/{lang}")
        else:
            self.verbose = args.verbose
            self.analyze_translations_dir(args.translation_dir)

            if not self.available_translations:
                print("No applicable translation detected. Aborting.")
                exit(0)

            # Read all the languages docs
            for lang in self.available_translations:
                if self.verbose:
                    print(f"{lang.upper()}: Reading docs")
                self.langs[lang] = self.read_docs(f"{args.translation_dir}/{lang}")

            # write translations into a json file so the doxyth executable can fetch translations quickly
            self.write_translations_to_file()

            # Edit or create doxygen config
            self.setup_doxygen_files(args.translation_dir)

            # Create the main directory if not existant
            if not exists(os.path.abspath(self.docs_output_path)):
                os.mkdir(self.docs_output_path)

            # Change Doxyfile and run doxygen for it to directly analyse files modified by the script using
            # FILE_PATTERNS
            for lang in self.available_translations:
                if self.verbose:
                    print(f"Generating doc for {lang.upper()}... ", end="")
                self.adapt_configs_to_lang(lang)

                # Creating the language directory if not existant
                if not exists(os.path.abspath(f'{self.docs_output_path}/{lang}')):
                    os.mkdir(f'{self.docs_output_path}/{lang}')

                fnull = open(os.devnull, 'w')
                code = subprocess.call(['doxygen', '.dthdoxy'], stdout=fnull, stderr=subprocess.STDOUT)
                fnull.close()

                if self.verbose:
                    if code:
                        print('ERROR')
                    else:
                        print("OK")

        self.cleanup()

    @staticmethod
    def setup_doxygen_files(translations_dir: str):
        """
        ### @doc_id setup_doxygen

        Setups the doxygen-related files.

        The files are: the doxygen config file (named .dthdoxy), the batch file (.dthb.bat) and the list of all
        the translations (inside .dtht)

        Args:
            translations_dir: The translations directory taken by argparse
        """

        # Change the directory to have a / at the end for the Doxyfile
        if not translations_dir.endswith("/"):
            translations_dir += "/"

        if not os.path.exists('Doxyfile'):
            fnull = open(os.devnull, 'w')
            subprocess.call(['doxygen', '-s', '-g', '.dthdoxy'], stdout=fnull, stderr=subprocess.STDOUT)
            fnull.close()

        with open('.dthdoxy', encoding='utf-8') as f:
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

            # Optimise Doxygen output for Python
            if re.match(r"^OPTIMIZE_OUTPUT_JAVA\s*=", line.strip()):
                lines[n] = f"OPTIMIZE_OUTPUT_JAVA = YES\n"

        with open('.dthdoxy', 'w', encoding='utf-8') as f:
            f.writelines(lines)

    @staticmethod
    def cleanup():
        """
        ### @doc_id gendoc_cleanup

        This is the last function to be called by the class.

        "Cleans up" by removing the three files created by both the flow and the setup_doxygen_files functions
        """

        os.remove(".dthb.bat")
        os.remove(".dtht")
        os.remove(".dthdoxy")

    def adapt_configs_to_lang(self, lang):
        """
        ### @doc_id adapt_to_lang

        Adapts the configuration files to the current language being processed.

        Changes the HTML output of doxygen, and the language parameter in the batch file to tell the doxyth
        executable the right language to look at

        Args:
            lang: The current language being processed.
        """

        # Doxyfile
        with open('.dthdoxy', encoding='utf-8') as f:
            lines = f.readlines()

        for n, line in enumerate(lines):
            # Change HTML output
            if re.match(r"^HTML_OUTPUT\s*=", line.strip()):
                lines[n] = f"HTML_OUTPUT = {self.docs_output_path}/{lang}/\n"

        with open('.dthdoxy', 'w', encoding='utf-8') as f:
            f.writelines(lines)

        # batch file
        with open('.dthb.bat', 'w', encoding='utf-8') as b:
            b.write(f"python -m doxyth.doxyth {lang} %1")

    def write_translations_to_file(self):
        """
        ### @doc_id write_translations

        Self-explanatory. Writes a JSON dump of all the collected language documentations in the .dtht file
        """
        with open(".dtht", 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.langs))

    def analyze_translations_dir(self, path):
        """
        ### @doc_id analyze_translations_dir

        Reads through the translations directory to look for language codes.

        This functions looks at all the directories to see if they match a known (and valid) two-letters ISO 639-1
        language code. If they do, it stores the code and returns the list of all valid codes when done.

        Args:
            path: The given path of the translations root directory
        """

        for d in os.listdir(path):
            if len(d) != 2:
                continue
            if d not in self.valid_codes:
                print(f"Warning: ISO 639-1 language code not recognised: {d}. Ignoring this directory.")
                continue

            if self.verbose:
                print(f"Found language code {d}")
            self.available_translations.append(d)

    def read_docs(self, path):
        """
        ### @doc_id read_doc_files

        Reads the documentation files and stores each documentation text.

        This function reads the documentation files in the language directory provided, and stores all the valid
        references for further use during the replacing phase by the doxyth file.

        Args:
            path: The language directory path to read through.
        """

        files = [f for f in os.listdir(path) if isfile(join(path, f)) and f.endswith(".dthdoc")]
        final = {}

        for file in files:
            with open(f"{path}/{file}", encoding='utf-8') as f:
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
