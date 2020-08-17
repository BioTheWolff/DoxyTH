import argparse
import re
import os
from os.path import isfile, join
from .utils import valid_codes

available_translations = []


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser", help="Sub-modules")

    dir_parser = subparsers.add_parser("directory", help="Verify the documentation format of a language directory",
                                       aliases=["dir", "d"])
    dir_parser.add_argument("documentation", help="The language directory to verify")

    file_parser = subparsers.add_parser("file", help="Verify the documentation format of a file",
                                        aliases=["f"])
    file_parser.add_argument("documentation", help="The file to verify")

    args = parser.parse_args()

    if args.subparser in ["directory", "dir", "d"]:
        verify_directory(args.documentation)
    elif args.subparser in ["file", "f"]:
        verify_file(args.documentation)


def verify_file(path, lone_file=True):
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

    if not lone_file:
        offset = '  '
        print_file_name = True

    if print_file_name:
        print(path.split('/')[-1])
    if buffer or buffer_name:
        print(f"{offset}Warning: Unexpected EOF while reading file.")
    else:
        print(f"{offset}Found the following documentation IDs:")
        for name in final.keys():
            print(f"{offset}-  {name}")


def verify_directory(path):
    for file in [f for f in os.listdir(path) if isfile(join(path, f))]:
        if file.endswith(".dthdoc"):
            verify_file(f"{path}/{file}", False)


if __name__ == '__main__':
    main()
