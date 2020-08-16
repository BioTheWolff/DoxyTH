import json


class DoxyTH:

    def __init__(self):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("lang", help="The language to translate the doc to")
        parser.add_argument("file", help="The file to replace the docs into")
        args = parser.parse_args()

        self.__flow(args)

    def __flow(self, args):
        self.docs = self.__fetch_docs(args.lang)
        self.lines = self.__fetch_file_lines(args.file)

        lines = self.__modify_lines()

    def __fetch_docs(self, lang):
        with open(".dtht") as f:
            buf = f.read()
        docs = json.loads(buf)
        return docs[lang]

    def __fetch_file_lines(self, path):
        with open(path) as f:
            buf = f.readlines()
        return buf


if __name__ == '__main__':
    DoxyTH()
