from os import sep


class HTMLBuilder:

    def __init__(self, output_dir, langs_list: list, replacements: dict, template: str, lang_snippet_template: str):
        self.output = output_dir
        self.replacements = replacements
        self.template = template
        self.langs_list = langs_list
        self.snippet_template = lang_snippet_template
        self.langs = ''

        self.__flow()

    def __flow(self):
        self.__build_languages_list()
        self.__replace_in_template()
        self.__write_template_to_output()

    def __build_languages_list(self):
        for lang in self.langs_list:
            self.langs += self.snippet_template.replace("$lang", lang.upper())
        self.replacements['langs'] = self.langs

    def __replace_in_template(self):
        for key in self.replacements:
            if f'${key}' in self.template:
                self.template = self.template.replace(f'${key}', self.replacements[key])

    def __write_template_to_output(self):
        with open(self.output + '/index.html', 'w', encoding='utf-8') as f:
            f.write(self.template)


class PrepareTemplates:

    def __init__(self, gendoc_path: str):
        self.path = sep.join(gendoc_path.split(sep)[0:-1])
        self.path += f'{sep}resources{sep}'

    def __call__(self):
        with open(f'{self.path}{sep}template.html') as t:
            buf = t.read()
        template = buf

        with open(f'{self.path}{sep}lang_snippet.html') as s:
            buf = s.read()
        snippet = buf

        return template, snippet
