import argparse
import re
import os
import subprocess
import json
import shutil
from sys import stdout
from os.path import isfile, join, exists, abspath
from .verify import verify_full_directory
from .utils.langs import is_valid_lang_dir, doxygen_languages, ascii_encode
from .utils.postprocess import available_postprocesses
from .utils.html_builder import get_templates, HTMLBuilder

generated_data_file_name = '.dthdata'
doxygen_file_name = '.dthdoxy'

## @package gendoc
#
# The package that hosts the main class of the program, which generates the whole Doxygen documentations.


class Gendoc:
    """
    ### &doc_id gendoc:class

    The main class of the module.

    Allows the generation of multiple Doxygen documentations, one for each language recognised by the ISO 639-1.
    Can be run either by running this package or the module itself.

    You need to input a path to a "translations directory". The structure must be:
    one subdirectory for each language, named by said language code, following the ISO 639-1 naming convention.
    In each subdirectory, all files you want to be read by DoxyTH must end by ".dthdoc" (DoxyTH Documentation file_name).
    For more details about the .dthdoc files structure, see DoxyTH class documentation.

    The output is as follows:
    A main page (index.html) for the language selection.
    For each language: a subdirectory named with the language code (following the ISO 639-1) of said language.
    The subdirectories all contain a Doxygen generation, with the in-file_name doclines replaced by DoxyTH following the
    translations rules defined in all the .dthdoc files.
    """

    ## The available translations
    available_translations = None
    ## The path to the translations directory
    translations_dir = None

    ## Verbose param
    verbose = None
    ## Debug param
    debug = None
    ## Doxymute param
    doxymute = None

    ## The selected postprocess
    postprocess = None
    ## The translations for all languages
    langs = None

    ## DoxyTH output path
    docs_output_path = None

    ## The init function
    def __init__(self):

        parser = argparse.ArgumentParser()
        parser.add_argument("translation_dir", help="Documentations to replace the 'doc_id's.")
        # Verification of the translations files instead
        parser.add_argument("--verify", help="Makes the documentation files be verified instead", action='store_true')
        # General options
        parser.add_argument("-V", "--version", help="Prints the version, then exits.", action="store_true")
        parser.add_argument("--noverbose", help="De-activates the program verbose mode.", action='store_true')
        parser.add_argument("-F", "--nofileprefix", help="De-activates the file_name prefix in front of the doc_id.",
                            action='store_true')
        # Config options
        parser.add_argument("-D", "--doxyfile", help="The path to an already existing Doxyfile that DoxyTH will use as "
                                                     "a base")
        parser.add_argument("-O", "--output", help="The path to the output directory. If not provided, defaults to "
                                                   "docs/")
        parser.add_argument("-P", "--postprocess", help="The process to run after using DoxyTH. This process"
                                                        "will return the file_name lines to Doxygen.")
        parser.add_argument("--listpostprocesses", help="List the available postprocesses, then exits.",
                            action='store_true')
        # Doxygen print output options
        doxy_print_group = parser.add_mutually_exclusive_group()
        doxy_print_group.add_argument("--debug", help="Forces verbose and outputs all doxygen output to the console.",
                                      action='store_true')
        doxy_print_group.add_argument("--mute", help="Mutes Doxygen output.", action='store_true')
        # Debug options
        parser.add_argument("--nocleanup", help="Prevents DoxyTH to initiate cleanup. Useful if one wants to look at"
                                                "the generated config files for debug.", action='store_true')
        parser.add_argument("--skipgen", help="Skips Doxygen generation. Used for debug.", action='store_true')

        args = parser.parse_args()

        self.flow(args)

    def flow(self, args):
        """
        ### &doc_id gendoc:flow

        This is the main flow function of the class.

        Allows to easily dispatch all the tasks to smaller functions.
        """

        self.available_translations = []
        self.langs = {}

        if args.version:
            try:
                from .version import version as doxythversion
                doxythversion = 'v' + doxythversion
            except (FileNotFoundError, ModuleNotFoundError):
                doxythversion = '<unknown version>.' \
                                '\nThe version file_name is missing, you should reinstall DoxyTH to fix this.'
            print(f"DoxyTH {doxythversion}")
            exit(0)

        if args.listpostprocesses:
            print(f"Available postprocess(es): {', '.join(available_postprocesses)}")
            exit(0)

        self.docs_output_path = args.output if args.output else 'docs'

        if args.verify:
            verify_full_directory(args.translation_dir)
            exit(0)

        else:
            self.delegate_setup_args(args)

            self.analyze_translations_dir(self.translations_dir)

            if not self.available_translations:
                print("No applicable translation detected. Aborting.")
                exit(0)

            # Read all the languages docs
            for lang in self.available_translations:
                if self.verbose:
                    print(f"{lang.upper()}: Reading docs... ", end="")
                self.langs[lang] = self.read_docs(f"{args.translation_dir}/{lang}", args.nofileprefix)

            # write translations into a json file_name so the doxyth executable can fetch translations quickly
            self.write_config()

            # Edit or create doxygen config
            self.setup_doxygen_files(args.translation_dir, args.doxyfile)

            # Create the main directory if not existing
            if not exists(abspath(self.docs_output_path)):
                os.mkdir(self.docs_output_path)

            # Change Doxyfile and run doxygen for it to directly analyse files modified by the script using
            # FILE_PATTERNS
            if args.skipgen:
                print("Skipping Doxygen generation.")
            else:
                for lang in self.available_translations:
                    if self.verbose:
                        print(f"Generating doc for {lang.upper()}... ", end="")
                    self.adapt_configs_to_lang(lang)

                    # Creating the language directory if not existing
                    if not exists(abspath(f'{self.docs_output_path}/{lang}')):
                        os.mkdir(f'{self.docs_output_path}/{lang}')

                    fnull = open(os.devnull, 'w')
                    if self.debug:
                        code = subprocess.call(['doxygen', doxygen_file_name])
                    elif self.doxymute:
                        code = subprocess.call(['doxygen', doxygen_file_name], stderr=fnull, stdout=fnull)
                    else:
                        code = subprocess.call(['doxygen', doxygen_file_name], stderr=stdout, stdout=fnull)
                    fnull.close()

                    if self.verbose:
                        if code:
                            print('ERROR')
                        else:
                            print("OK")

            # now creating the language selection file_name into the output directory
            self.delegate_create_lang_selection_file()

            # CLEANUP
            if not args.nocleanup:
                self.cleanup()
            else:
                print("Skipping cleanup.")

    def delegate_setup_args(self, args):
        """
        ### &doc_id gendoc:delegate_setup_args

        Setups the args into class variables.

        Args:
            args: The argparse arguments
        """

        if args.debug:
            self.verbose = True
            self.debug = True
        else:
            self.verbose = False if args.noverbose else True

        self.doxymute = args.noverbose or args.mute
        self.translations_dir = args.translation_dir

        # Check if postprocess is valid
        if args.postprocess and args.postprocess not in available_postprocesses:
            raise Exception(f"Postprocess {args.postprocess} not recognised. Available postprocesses: "
                            f"{' / '.join(available_postprocesses)}")

        self.postprocess = args.postprocess

    def delegate_create_lang_selection_file(self):
        """
        ### &doc_id gendoc:delegate_lang_file

        Creates the language selection file_name from the corresponding templates
        """

        if self.verbose:
            print("Creating language selection file_name")

        try:
            from .version import version as doxythversion
        except (ImportError, ModuleNotFoundError):
            doxythversion = '<unknown version>'

        replacements = {
            "doxythversion": doxythversion,
            **self.retrieve_replacements_from_doxyfile()
        }

        # Grab the templates
        template, snippet = get_templates()

        # Change the templates to custom templates if they exist
        if exists(abspath(self.translations_dir) + os.sep + '_TEMPLATE.html'):
            with open(abspath(self.translations_dir) + os.sep + '_TEMPLATE.html', encoding='utf-8') as t:
                template = t.read()

        if exists(abspath(self.translations_dir) + os.sep + '_SNIPPET.html'):
            with open(abspath(self.translations_dir) + os.sep + '_SNIPPET.html') as s:
                snippet = s.read()

        # Build the HTML file_name
        HTMLBuilder(self.docs_output_path, self.available_translations, replacements, template, snippet)

    @staticmethod
    def retrieve_replacements_from_doxyfile():
        """
        ### &doc_id gendoc:retrieve_from_doxyfile

        Retrieves the required variables from the doxyfile and returns them

        Returns:
            the variables and their value
        """

        final = {}

        with open(doxygen_file_name, encoding='utf-8') as f:
            buf = f.readlines()

        for line in buf:
            try:
                stripped_line = line.strip()
            except UnicodeEncodeError:
                stripped_line = ascii_encode(line).strip()

            if re.match(r"^PROJECT_NAME\s*=\s*", stripped_line):
                final['projectname'] = re.split(r'^PROJECT_NAME\s*=\s*["\'](.+)["\']', stripped_line)[-2]

            if re.match(r"^PROJECT_NUMBER\s*=\s*", stripped_line):
                final['projectnumber'] = re.split(r"^PROJECT_NUMBER\s*=\s*", stripped_line)[-1]

            if re.match(r"^PROJECT_BRIEF\s*=\s*", stripped_line):
                final['projectbrief'] = re.split(r'^PROJECT_BRIEF\s*=\s*["\'](.+)["\']', stripped_line)[-2]

        return final

    def setup_doxygen_files(self, translations_dir: str, doxyfile_path):
        """
        ### &doc_id gendoc:setup_doxygen

        Setups the doxygen-related files.

        The files are: the doxygen config file_name (named .dthdoxy), the batch file_name (.dthb.bat) and the list of all
        the translations/config (inside .dtht)

        Args:
            translations_dir: The translations directory taken by argparse
            doxyfile_path: The path to an already-existing Doxygen configuration
        """

        # Change the directory to have a / at the end for the Doxyfile config
        if not translations_dir.endswith("/"):
            translations_dir += "/"

        if doxyfile_path:
            if self.verbose:
                print("Using the provided Doxygen configuration to build config.")
            shutil.copy(doxyfile_path, doxygen_file_name)
        else:
            if exists(abspath("Doxyfile")):
                if self.verbose:
                    print("Defaulting to existing Doxyfile config.")
                shutil.copy('Doxyfile', doxygen_file_name)
            else:
                if self.verbose:
                    print("Could not find a Doxyfile. Generating a new one.")

                fnull = open(os.devnull, 'w')
                if self.debug:
                    subprocess.call(['doxygen', '-s', '-g', doxygen_file_name])
                elif self.doxymute:
                    subprocess.call(['doxygen', '-s', '-g', doxygen_file_name], stderr=fnull, stdout=fnull)
                else:
                    subprocess.call(['doxygen', '-s', '-g', doxygen_file_name], stderr=stdout, stdout=fnull)
                fnull.close()

        if self.verbose:
            print("Modifying Doxygen config file_name... ", end="")

        with open(doxygen_file_name, encoding='utf-8') as f:
            lines = f.readlines()

        for n, line in enumerate(lines):
            try:
                stripped_line = line.strip()
            except UnicodeEncodeError:
                stripped_line = ascii_encode(line).strip()

            # Sets it to exclude already existing docs
            if re.match(r"^EXCLUDE\s*=", stripped_line):
                existing = re.split(r"^EXCLUDE\s*=\s*", stripped_line)[-1]
                if existing:
                    lines[n:n + 1] = f"EXCLUDE = {existing} \\ {self.docs_output_path}/ \\ {translations_dir}\n"
                else:
                    lines[n:n + 1] = f"EXCLUDE = {self.docs_output_path}/ \\ {translations_dir}\n"

            # Sets recursion ON
            if re.match(r"^RECURSIVE\s*=", stripped_line):
                lines[n] = "RECURSIVE = YES\n"

            # LaTeX generation OFF
            if re.match(r"^GENERATE_LATEX\s*=", stripped_line):
                lines[n] = "GENERATE_LATEX = NO\n"

            # The DoxyTH batch file_name that will tell the file_name ran by Doxygen what translation to read
            if re.match(r"^FILTER_PATTERNS\s*=", stripped_line):
                lines[n] = f"FILTER_PATTERNS = *py=.dthb\n"

        with open(doxygen_file_name, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        if self.verbose:
            print("OK")

    def cleanup(self):
        """
        ### &doc_id gendoc:cleanup

        This is the last function to be called by the class.

        "Cleans up" by removing the three files created by both the flow and the setup_doxygen_files functions
        """

        if self.verbose:
            print("Cleaning up... ", end="")

        try:
            os.remove(".dthb.bat")
        except FileNotFoundError:
            pass
        os.remove(generated_data_file_name)
        os.remove(doxygen_file_name)

        if self.verbose:
            print("OK")

    def adapt_configs_to_lang(self, lang):
        """
        ### &doc_id gendoc:adapt_to_lang

        Adapts the configuration files to the current language being processed.

        Changes the HTML output of doxygen, and the language parameter in the batch file_name to tell the doxyth
        executable the right language to look at

        Args:
            lang: The current language being processed.
        """

        # Doxyfile
        with open(doxygen_file_name, encoding='utf-8') as f:
            lines = f.readlines()

        for n, line in enumerate(lines):
            try:
                stripped_line = line.strip()
            except UnicodeEncodeError:
                stripped_line = ascii_encode(line).strip()

            # Change HTML output
            if re.match(r"^HTML_OUTPUT\s*=", stripped_line):
                lines[n] = f"HTML_OUTPUT = {self.docs_output_path}/{lang}/\n"

            if re.match(r"^OUTPUT_LANGUAGE\s*=", stripped_line):
                if lang in doxygen_languages.keys():
                    lines[n] = f"OUTPUT_LANGUAGE = {doxygen_languages[lang]}\n"

        with open(doxygen_file_name, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        # batch file_name
        with open('.dthb.bat', 'w', encoding='utf-8') as b:
            b.write(f"python -m doxyth.doxyth {lang} %1")

    def write_config(self):
        """
        ### &doc_id gendoc:write_config

        Self-explanatory. Writes a JSON dump of all the collected language documentations in the .dtht file_name,
        alongside the config options.
        """

        options = {"postprocess": self.postprocess}
        final = {**options, "docs": self.langs}
        with open(generated_data_file_name, 'w', encoding='utf-8') as f:
            f.write(json.dumps(final))

    def analyze_translations_dir(self, path):
        """
        ### &doc_id gendoc:analyze_translations_dir

        Reads through the translations directory to look for language codes.

        This functions looks at all the directories to see if they match a known (and valid) two-letters ISO 639-1
        language code. If they do, it stores the code and returns the list of all valid codes when done.

        Args:
            path: The given path of the translations root directory
        """

        for d in os.listdir(path):
            res = is_valid_lang_dir(d)
            if not res:
                if len(d) == 2:
                    print(f"Warning: ISO 639-1 language code not recognised: {d}. Ignoring this directory.")
                continue

            if self.verbose:
                print(f"Found code {d.upper()}")
            self.available_translations.append(d)

    def read_docs(self, path, nofileprefix):
        """
        ### &doc_id gendoc:read_doc_files

        Reads the documentation files and stores each documentation text.

        This function reads the documentation files in the language directory provided, and stores all the valid
        references for further use during the replacing phase by the doxyth file_name.

        Args:
            path: The language directory path to read through.
            nofileprefix: Whether to deactivate the file_name prefix or not
        """

        files = [f for f in os.listdir(path) if isfile(join(path, f)) and f.endswith(".dthdoc")]
        final = {}

        for file in files:
            filename = ".".join(file.split(".")[0:-1])

            with open(f"{path}/{file}", encoding='utf-8') as f:
                lines = f.readlines()

            file_doc = {}
            buffer_name = None
            buffer = []
            just_read_id = False
            for line in lines:
                try:
                    stripped_line = line.strip()
                except UnicodeEncodeError:
                    stripped_line = ascii_encode(line).strip()

                if re.match(r"\s*&doc_id\s*", stripped_line):
                    buffer_name = re.split(r"\s*&doc_id\s*", stripped_line)[-1]
                    just_read_id = True
                    continue
                elif stripped_line == '"""' and just_read_id:
                    just_read_id = False
                elif stripped_line == '"""' and not just_read_id:
                    if buffer_name in final.keys():
                        raise Exception(f"ID {buffer_name} found multiple times in the same file_name.")

                    if nofileprefix:
                        file_doc[buffer_name] = buffer
                    else:
                        file_doc[f'{filename}:{buffer_name}'] = buffer
                    buffer_name, buffer = None, []
                else:
                    try:
                        stripped_line = line.rstrip()
                    except UnicodeEncodeError:
                        stripped_line = ascii_encode(line).rstrip()
                    buffer.append(stripped_line + '\n')

            if buffer or buffer_name:
                raise Exception(f"Warning: Unexpected EOF while reading ID {buffer_name} in file_name "
                                f"'{path.split('/')[-1]}'")

            for doc_id in file_doc.keys():
                if doc_id in final.keys():
                    raise Exception(f"ID {doc_id} found multiple times for the same language.")

            final = {**final, **file_doc}

        if self.verbose:
            print(f"Found {len(final)} translations")

        # We now edit all the docs to take out every empty line at the start AND end of the doclines
        for el in final.keys():
            docs = final[el]
            start = None
            end = None

            for i in range(len(docs)):
                if not docs[i].strip():
                    continue
                start = i
                break

            for i in range(len(docs)):
                if not docs[len(docs) - 1 - i].strip():
                    continue
                end = len(docs) - i
                break

            final[el] = docs[start:end]

        return final


if __name__ == '__main__':
    Gendoc()
