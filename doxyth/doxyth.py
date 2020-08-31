from .utils.langs import ascii_encode

## @package doxyth
#
# Package that contains the DoxyTH class, used by Doxygen as a file pattern processor.
# For more information about the Doxygen file patterns, see the DoxyTH class documentation.


class DoxyTH:
    """
    ### &doc_id doxyth:class

    Class that is made to be called by doxygen as a file pattern processor.

    This file (and class) is automatically called by Doxygen for it to process any file Doxygen encounters that follows
    the rule defined in the FILE_PATTERNS option of the config.
    By default, DoxyTH sets the FILE_PATTERNS value of the Doxygen config to "*py=.dthb", ".dthb" being the batch file
    called by Doxygen when it encounters any file ending by ".py".

    The batch file has "python -m doxyth.doxyth <lang> %1" as content. LANG is automatically changed by the gendoc class
    each time we change language. Doxygen then passes the file path, which is taken by the DoxyTH class as an input.

    The file is methodically read, and every doc_id matching the default regex pattern is registered, and then the whole
    doclines where the doc_id has been found are replaced by the linked documentation for this language.

    The file is then printed line per line for Doxygen to read it back and process it. If a postprocessing has been
    set upon running Gendoc, the file lines are instead sent to the postprocess (doxypy, doxypypy, etc.) which will
    take care of printing the line itself, after doing its job. The lines are sent through a class built for said
    postprocess, that acts as a bridge between what DoxyTH produced and what the postprocess requires.
    """

    ## The current doxyTH config (retrieved from the generated data file)
    config = None
    ## The current language
    lang = None
    ## The file name
    filename = None
    ## The translations for this language
    docs = None
    ## The file lines
    lines = None

    def __init__(self):
        """
        ### &doc_id doxyth:init

        Parses the args
        """

        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("lang", help="The language to translate the doc to")
        parser.add_argument("filename", help="The file to replace the docs into")
        args = parser.parse_args()

        self.__flow(args)

    def __flow(self, args):
        """
        ### &doc_id doxyth:flow

        The flow function

        We fetch the doc lines for this language, and then all the file lines.
        We call the lines modifier function and then either print the lines or send them to the postprocess bridge.

        Args:
            args: The argparse arguments
        """

        from .utils.postprocess import postprocess_dispatcher
        from os import sep

        self.config = self.__fetch_data_file()
        self.lang, self.filename = args.lang, args.filename.split(sep)[-1]
        self.docs = self.config['docs'][args.lang]
        self.lines = self.__fetch_file_lines(args.filename)

        lines = self.__modify_lines()

        if self.config['postprocess']:
            postprocess_dispatcher(self.config['postprocess'], args.filename, lines)
        else:
            for line in lines:
                try:
                    print(line.rstrip())
                except UnicodeEncodeError:
                    print(ascii_encode(line).rstrip())

    @staticmethod
    def __fetch_data_file():
        """
        ### &doc_id doxyth:fetch_data_file

        Simply fetches the generated data file and reads its content.

        Returns:
            The content of the data file
        """

        import json
        from doxyth.gendoc import generated_data_file_name

        with open(generated_data_file_name, encoding='utf-8') as f:
            buf = f.read()
        return json.loads(buf)

    @staticmethod
    def __fetch_file_lines(path):
        """
        ### &doc_id doxyth:fetch_file_lines

        Simply reads the file and returns its lines.

        Args:
            path: The file path

        Returns:
            The file lines
        """

        with open(path, encoding='utf-8') as f:
            buf = f.readlines()
        return buf

    def __modify_lines(self):
        """
        ### &doc_id doxyth:modify_lines

        The main function of this class. Processes the file lines to replace the doc_ids.

        The function reads the file line per line, and only looks for a doc_id in doclines. If multiple IDs are found in
        one doc, only the first is kept as an ID.
        Once the file is entirely read, each doclines containing a doc ID are replaced by the matching doclines
        registered in the translations file(s) of this language.

        Returns:
            The modified file lines
        """

        import re
        from sys import stderr

        final = self.lines.copy()
        to_change = []
        in_doc = False
        doclines = [None, None]

        offset = None
        doc_id = None

        # Find the lines that are to replace
        for n, line in enumerate(final):
            try:
                stripped_line = line.strip()
            except UnicodeEncodeError:
                stripped_line = ascii_encode(line).strip()
            if stripped_line == '"""':
                if not in_doc:
                    # We just entered in a doc, set the starting line number and the offset
                    doclines[0] = n
                    offset = re.split(r'(\s*)"""', line)[1]
                if in_doc:
                    # If no doc_id has been found, we leave the doclines untouched.
                    if doc_id:
                        # We are exiting a doc, set the ending line and register the thing to replace
                        doclines[1] = n
                        to_change.append({"lines": tuple(doclines), "id": doc_id, "offset": offset})
                    # Reset values to what they were initially
                    offset = None
                    doc_id = None
                    doclines = [None, None]

                in_doc = False if in_doc else True

            if in_doc:
                if re.match(r"\s*###\s*&doc_id\s*", line):
                    # Found, we now split by regex and register the doc id
                    try:
                        new = re.split(r"\s*###\s*&doc_id\s*", line.rstrip())[-1]
                    except UnicodeEncodeError:
                        new = re.split(r"\s*###\s*&doc_id\s*", ascii_encode(line).rstrip())[-1]
                    if doc_id:
                        print(f"{self.filename}:{n}: warning: Found multiple IDs in the same doclines:"
                              f" 1st '{doc_id}'; 2nd '{new}'.", file=stderr)
                    else:
                        if new in self.docs:
                            doc_id = new
                        else:
                            print(f"{self.filename}:{n}: warning: ID {new} could not be found in the "
                                  f"doc_IDs.", file=stderr)

        if in_doc:
            raise Exception(f"Unexpected EOF while reading.")

        # Now reverse the list, and replace the doclines
        to_change.reverse()

        for el in to_change:
            if el['id'] in self.docs:
                dls, dle = el['lines']

                modified_doc = [el['offset'] + line for line in self.docs[el['id']]]
                modified_doc.insert(0, el['offset'] + '"""')
                modified_doc.append(el['offset'] + '"""')

                final[dls:dle+1] = modified_doc

        return final


if __name__ == '__main__':
    DoxyTH()
