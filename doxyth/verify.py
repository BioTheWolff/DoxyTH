import argparse
import re
import os
from os.path import isfile, join, isdir, abspath
from .utils.langs import is_valid_lang_dir, ascii_encode

## @package verify
#
# This package contains the functions that allow the user to check the format and contents of a directory or file.
# If executed to verify a file, prints the number of doc_ids found and linked to a documentation.
# If executed to verify a language directory, prints the file names and the number of doc_ids found and linked to a
# documentation inside this file.
# If executed to verify the full translations directory, it will instead print the number of doc_ids found for each
# language, allowing you to check that all the languages have to same amount of doc_ids.


def main():
    """
    ### &doc_id verify:main

    The main function of the verify file, executes when you run the file.

    It allows to check that the full/language directory, or a specific file, follows the right format.

    Argparse usage:
        usage: verify.py [-h] {directory,dir,d,languagedirectory,langdir,ld,file,f} documentation
    Subparsers:
        directory (dir, d): refer to the full translations directory
        languagedirectory (langdir, ld): refer to a language directory
        file (f): refer to a lone translations file
    """

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser", help="Sub-modules")

    dir_parser = subparsers.add_parser("directory", help="Verify the documentation format of the whole translations "
                                                         "directory",
                                       aliases=["dir", "d"])
    dir_parser.add_argument("documentation", help="The language directory to verify")
    dir_parser = subparsers.add_parser("languagedirectory", help="Verify the documentation format of a "
                                                                 "language directory",
                                       aliases=["langdir", "ld"])
    dir_parser.add_argument("documentation", help="The language directory to verify")

    file_parser = subparsers.add_parser("file", help="Verify the documentation format of a file",
                                        aliases=["f"])
    file_parser.add_argument("documentation", help="The file to verify")

    args = parser.parse_args()

    if args.subparser in ['directory', 'dir', 'd']:
        verify_full_directory(args.documentation)
    elif args.subparser in ["languagedirectory", "langdir", "ld"]:
        verify_lang_directory(args.documentation)
    elif args.subparser in ["file", "f"]:
        verify_file(args.documentation)


def verify_file(path, lone_file=True, no_print=False):
    """
    ### &doc_id verify:verify_file

    Reads a documentation file, and parses it.

    Args:
        path: The path to the file
        lone_file: Whether it is a lone file or part of a directory sweep
        no_print: Whether we should forbid this function to print results (used for the full directory sweep)
    """

    offset = ''
    print_file_name = False

    with open(path) as f:
        lines = f.readlines()

    final = {}
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
                print(f"ID {buffer_name} found multiple times in the same file.")
                exit()
            final[buffer_name] = buffer
            buffer_name, buffer = None, []
        else:
            buffer.append(stripped_line + '\n')

    if not no_print:
        if not lone_file:
            offset = '  '
            print_file_name = True

        if print_file_name:
            print(path.split('/')[-1])
        if buffer or buffer_name:
            print(f"{offset}Warning: Unexpected EOF while reading file.")
        else:
            print(f"{offset}File read correctly. Found {len(final)} entries.")

    return list(final.keys())


def verify_lang_directory(path, no_print=False):
    """
    ### &doc_id verify:lang_directory

    Verifies a language directory, file per file.

    Args:
        path: The path to the language directory
        no_print: Whether we should forbid this function to print. Simply passed to verify_file, does not affect this
        function directly.
    """

    final = []
    for file in [f for f in os.listdir(path) if isfile(join(path, f))]:
        if file.endswith(".dthdoc"):
            res = verify_file(f"{path}/{file}", False, no_print)

            for new in res:
                if new in final:
                    print(f"ID {new} found multiple times for the same language.")
                    exit()

            final.extend(res)
    return final


def verify_full_directory(path):
    """
    ### &doc_id verify:verify_full_directory

    Verifies the full translations directory.

    Args:
        path: The path to the translations directory
    """

    langs = {}
    for directory in [d for d in os.listdir(path) if isdir(join(path, d))]:
        res = is_valid_lang_dir(directory)
        if res:
            langs[directory] = verify_lang_directory(abspath(directory), True)

    for lang in langs:
        print(f"{lang.upper()}: Found {len(langs[lang])} entries.")

    first_key = list(langs.keys())[0]

    if not all(len(langs[first_key]) == len(langs[key]) for key in langs):
        print("Warning: All the languages do not have the same number of entries. Is this normal?")


if __name__ == '__main__':
    main()
