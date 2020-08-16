class DoxyTH:

    def __init__(self):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("lang", help="The language to translate the doc to")
        parser.add_argument("file", help="The file to replace the docs into")
        args = parser.parse_args()

        self.__flow(args)

    def __flow(self, args):
        # self.docs = self.__fetch_docs(args.lang)
        self.docs = {
            'future_function': [
                 'Template of a future function.\n',
                 'Not implemented yet. Raises NotImplementedError if called.\n',
                 '\n',
                 'Raises:\n',
                 '    Always raises NotImplementedError for now\n'
            ],
            'get_master_router': [
                'Get master route from all the routers\n',
                '\n',
                ':return master: master router instance\n',
                ':raises Exception: when no master or more than one is found\n'
            ]
        }
        self.lines = self.__fetch_file_lines(args.file)

        lines = self.__modify_lines()

        for line in lines:
            print(line.rstrip())

    @staticmethod
    def __fetch_docs(lang):
        import json

        with open(".dtht") as f:
            buf = f.read()
        docs = json.loads(buf)
        return docs[lang]

    @staticmethod
    def __fetch_file_lines(path):
        with open(path) as f:
            buf = f.readlines()
        return buf

    def __modify_lines(self):
        import re

        final = self.lines.copy()
        to_change = []
        in_doc = False
        doclines = [None, None]

        offset = None
        doc_id = None

        # Find the lines that are to replace
        for n, line in enumerate(final):
            if line.strip() == '"""':
                if not in_doc:
                    # We just entered in a doc, set the starting line number and the offset
                    doclines[0] = n
                    offset = re.split(r'(\s*)"""', line)[1]
                if in_doc:
                    # We are exiting a doc, set the ending line and register the thing to replace
                    doclines[1] = n
                    to_change.append({"lines": tuple(doclines), "id": doc_id, "offset": offset})
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
            raise Exception(f"Unexpected EOF while reading.")

        # Now reverse the list, and replace the doclines
        to_change.reverse()

        for el in to_change:
            if el['id'] in self.docs:
                s, e = el['lines']

                modified_doc = [el['offset'] + line for line in self.docs[el['id']]]
                modified_doc.insert(0, el['offset'] + '"""')
                modified_doc.append(el['offset'] + '"""')

                final[s:e+1] = modified_doc

        return final


if __name__ == '__main__':
    DoxyTH()
