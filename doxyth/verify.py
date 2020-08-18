import argparse
import re
import os
from os.path import isfile, join, isdir, abspath
from .utils import is_valid_lang_dir


def main():
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
    offset = ''
    print_file_name = False

    with open(path) as f:
        lines = f.readlines()

    final = {}
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
            final[buffer_name] = buffer
            buffer_name, buffer = None, []
        else:
            buffer.append(line.strip() + '\n')

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
    final = []
    for file in [f for f in os.listdir(path) if isfile(join(path, f))]:
        if file.endswith(".dthdoc"):
            res = verify_file(f"{path}/{file}", False, no_print)
            final.extend(res)
    return final


def verify_full_directory(path):
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
