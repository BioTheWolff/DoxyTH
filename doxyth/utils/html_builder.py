from os import sep

## @package html_builder
#
# Contains the classes that build the language selection html file


class HTMLBuilder:
    """
    ### &doc_id html_builder:HTMLBuilder

    Builds the HTML file from the layout and the language snippet given.
    """

    def __init__(self, output_dir, langs_list: list, replacements: dict, template: str, lang_snippet_template: str):
        """
        ### &doc_id html_builder:HTMLBuilder_init

        Initialises and runs the whole class.

        Args:
            output_dir: The output directory where the index.html should be located
            langs_list: The list of languages processed by doxyTH
            replacements: The dictionary containing the replacements to some variables in the layout or snippet
            template: The string of the HTML layout template file
            lang_snippet_template: The string of the language snippet template
        """
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
        """
        ### &doc_id html_builder:build_languages_list

        Builds the $langs replacement from the snippet template, for each language.
        """

        for lang in self.langs_list:
            self.langs += self.snippet_template.replace("$lang", lang.upper())
        self.replacements['langs'] = self.langs

    def __replace_in_template(self):
        """
        ### &doc_id html_builder:replace_in_template

        Replaces the variables ($<variable name>) by their replacement in the dict
        """

        for key in self.replacements:
            if f'${key}' in self.template:
                self.template = self.template.replace(f'${key}', self.replacements[key])

    def __write_template_to_output(self):
        """
        ### &doc_id html_builder:write_template_to_output

        Writes the modified template file to the output directory under the name index.html
        """

        with open(self.output + '/index.html', 'w', encoding='utf-8') as f:
            f.write(self.template)


class PrepareTemplates:
    """
    ### &doc_id html_builder:PrepareTemplates

    Small class that retrieves the templates from the resources/ folder of the module
    """

    def __init__(self, gendoc_path: str):
        """
        ### &doc_id html_builder:PrepareTemplates_init

        Prepares the path of the resources folder

        Args:
            gendoc_path: The path of the gendoc file (this class should only be run by gendoc or verify for accurate
            location of the resources folder)
        """

        self.path = sep.join(gendoc_path.split(sep)[0:-1])
        self.path += f'{sep}resources{sep}'

    def __call__(self):
        """
        ### &doc_id html_builder:PrepareTemplates_call

        Opens and reads the templates, and returns the strings.
        """

        with open(f'{self.path}{sep}template.html') as t:
            buf = t.read()
        template = buf

        with open(f'{self.path}{sep}lang_snippet.html') as s:
            buf = s.read()
        snippet = buf

        return template, snippet
