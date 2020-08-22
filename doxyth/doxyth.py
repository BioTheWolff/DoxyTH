class DoxyTH:

    def __init__(self):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("lang", help="The language to translate the doc to")
        parser.add_argument("filename", help="The file to replace the docs into")
        args = parser.parse_args()

        self.__flow(args)

    def __flow(self, args):
        from .utils.postprocess import postprocess_dispatcher

        self.config = self.__fetch_docs()
        self.docs = self.config['docs'][args.lang]
        self.lines = self.__fetch_file_lines(args.filename)

        lines = self.__modify_lines()

        if self.config['postprocess']:
            postprocess_dispatcher(self.config['postprocess'], args.filename, lines)
        else:
            for line in lines:
                print(line.rstrip())

    @staticmethod
    def __fetch_docs():
        import json
        from doxyth.gendoc import generated_data_file_name

        with open(generated_data_file_name, encoding='utf-8') as f:
            buf = f.read()
        return json.loads(buf)

    @staticmethod
    def __fetch_file_lines(path):
        with open(path, encoding='utf-8') as f:
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
                dls, dle = el['lines']

                modified_doc = [el['offset'] + line for line in self.docs[el['id']]]
                modified_doc.insert(0, el['offset'] + '"""')
                modified_doc.append(el['offset'] + '"""')

                final[dls:dle+1] = modified_doc

        return final


if __name__ == '__main__':
    DoxyTH()
