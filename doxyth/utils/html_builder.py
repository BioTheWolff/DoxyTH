from os import sep

## @package html_builder
#
# Contains the classes that build the language selection html file_name


class HTMLBuilder:
    """
    ### &doc_id html_builder:HTMLBuilder

    Builds the HTML file_name from the layout and the language snippet given.
    """

    ## The output directory
    output = None
    ## The replacements dictionary
    replacements = None
    ## The html layout template file_name
    template = None
    ## The list of languages
    langs_list = None
    ## The language snippet template
    snippet_template = None
    ## The string that will contain all the langs
    langs = None

    def __init__(self, output_dir, langs_list: list, replacements: dict, template: str, lang_snippet_template: str):
        """
        ### &doc_id html_builder:HTMLBuilder_init

        Initialises and runs the whole class.

        Args:
            output_dir: The output directory where the index.html should be located
            langs_list: The list of languages processed by doxyTH
            replacements: The dictionary containing the replacements to some variables in the layout or snippet
            template: The string of the HTML layout template file_name
            lang_snippet_template: The string of the language snippet template
        """
        self.output = output_dir
        self.replacements = replacements
        self.template = template
        self.langs_list = langs_list
        self.snippet_template = lang_snippet_template
        self.langs = ''

        self.__flow()

    ## The flow function
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

        Writes the modified template file_name to the output directory under the name index.html
        """

        with open(self.output + '/index.html', 'w', encoding='utf-8') as f:
            f.write(self.template)


class PrepareTemplates:
    """
    ### &doc_id html_builder:PrepareTemplates

    Small class that retrieves the templates from the resources/ folder of the module
    @deprecated This class writes the html files into the resources/ folder and grabs them. Use get_templates.
    """

    ## The path to the resources
    path = None

    def __init__(self, gendoc_path: str):
        """
        ### &doc_id html_builder:PrepareTemplates_init

        Prepares the path of the resources folder

        Args:
            gendoc_path: The path of the gendoc file_name (this class should only be run by gendoc or verify for accurate
            location of the resources folder)
        """

        from os import mkdir
        from os.path import exists

        self.path = sep.join(gendoc_path.split(sep)[0:-1])
        self.path += f'{sep}resources{sep}'

        if not exists(self.path):
            mkdir(self.path)

        if not exists(self.path + sep + 'template.html'):
            GenerateTemplates(self.path)('template')
        if not exists(self.path + sep + 'lang_snippet.html'):
            GenerateTemplates(self.path)('snippet')

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


class GenerateTemplates:
    """
    ### &doc_id html_builder:GenerateTemplates

    The class that generates the templates from the given strings, in the resources folder given.
    """

    ## The html template
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="generator" content="DoxyTH $doxythversion">
    <title>$projectname: Language selection</title>
    <style>
        html { background-color: #171717; color: #858585; font-family: Tahoma, Arial, sans-serif;}
        #projectname { font-size: 2.5rem;}
        #projectnumber { font-size: 1rem;}
        #projectbrief { font-size: 1.2rem; font-style: italic;}
        #lang-container { display: flex; }
        .lang { border: 2px solid #454545; padding: 10px; margin: 10px;}
        a:visited { color: #757575;}
        a:not(visited) {color: rgb(0, 110, 191);}
        a:hover {color: rgb(0, 145, 200);}
    </style>
    </head>
    <body>
    <div id="projectname">
        $projectname
        <span id="projectnumber">$projectnumber</span>
    </div>
    <div id="projectbrief">$projectbrief</div>
    <hr>
    <h2>Language selection</h2>
    
    <div id="lang-container">
        $langs
    </div>
    
    </body>
    </html>
    """

    ## The language snippet
    snippet = """
    <a href="./$lang/index.html"><div class="lang">$lang</div></a>
    """

    ## The path to the resources folder
    path = None

    def __init__(self, resources_path):
        """
        ### &doc_id html_builder:GenerateTemplates_init

        Simply saves the resource path

        Args:
            resources_path: The path to the resource
        """

        self.path = resources_path

    def __call__(self, file_name):
        """
        ### &doc_id html_builder:GenerateTemplates_call

        Writes the templates in the corresponding files

        Args:
            file_name: Either 'template' or 'snippet', to render either of the two.
        """

        if file_name == 'template':
            with open(self.path + sep + 'template.html', 'w', encoding='utf-8') as f:
                formatted = "".join([line.strip() + '\n' for line in self.template.split('\n')])
                f.write(formatted)
        elif file_name == 'snippet':
            with open(self.path + sep + 'lang_snippet.html', 'w', encoding='utf-8') as f:
                formatted = "".join([line.strip() + '\n' for line in self.snippet.split('\n')])
                f.write(formatted)


## Returns the templates
def get_templates():
    return GenerateTemplates.template, GenerateTemplates.snippet
