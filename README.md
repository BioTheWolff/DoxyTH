# DoxyTH
DoxyTH stands for Doxygen inline-documentation Translation Helper. This small package aims to provide a 
quick way to generate Doxygen docs in HTML (LaTeX will come later) in different languages easily.

*Nota Bene:* Below, "a/the Doxyfile" refers to the Doxygen configuration file, however it might be named. However,
`Doxyfile` (in code) refers to the exact name of the file.

## Setup
### Installation
You first have to install the package.
You can install it automatically via pip
```commandline
pip install doxyth
```

You can also install it by cloning the Github repository (deprecated)

### Setting up the translations folder
In your project directory, create a directory that will contain all the translations.
You can name it however you want, even though a meaningful name like `translations` is still better.

Inside, you have to create a directory with the [ISO 639-1 2-letters code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) 
for the desired language. Directories having more or less than 2 charaters will be ignored by DoxyTH, but unrecognised
2-characters directories will generate warnings.

This is an example layout (and the one I use for the DoxyTH package documentation!)
```ignorelang
<path>\DOXYTH\TRANSLATIONS
|--- en/
|       doxyth.dthdoc
|       gendoc.dthdoc
|
|--- fr/
        gendoc.dthdoc
```
(I simplified the tree for more readability)

In each language directory, you will need to create one (or more) `.dthdoc` files. All files having
another extension will be ignored.

#### Layout of a .dthdoc file
Each file follows the current format:
```ignorelang
&doc_id <ID>
"""
<DOCUMENTATION>
"""
```

`ID` is the ID you will put in your code, and `DOCUMENTATION` (everything between the two `"""`) is what will replace
the doclines where this ID is found.

**WARNING**: Be aware that the line breaks are important. The `"""` must be ALONE on their line.

DoxyTH will remove any empty lines between the start of the doclines and the start of your comment 
(same as between the end of your comment and the end of the doclines) to avoid problems when passing the file lines to a 
postprocess.

#### Layout of the language selection file
You can create two files that will alter the output of the language selection html file.

* One is called `_TEMPLATE.html` and must contain the main template.
* The other is called `_SNIPPET.html` and must contain the language snippet that will be used for each language.

##### _TEMPLATE.html 
This file contains the full template of the html file.
Create it however you want, using variables to put things dynamically in the template.

**Mandatory variables**:
* `$langs`: The group of snippets created and filled with variables.

**Optional variables**:
* `$doxythversion`: The current version of DoxyTH
* `$projectname`: The name of the project (`PROJECT_NAME` in the Doxyfile)
* `$projectnumber`: The version of the project (`PROJECT_NUMBER` in the Doxyfile)
* `$projectbrief`: The brief description of the project (`PROJECT_BRIEF` in the Doxyfile)

Example:
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="generator" content="DoxyTH $doxythversion">
<title>$projectname: Language selection</title>
<style>...</style>
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
```

##### _SNIPPET.html
This file contains the snippet that will be used for each language.

**Mandatory variables**:
* `$lang`: The language code

Example:
```html
<a href="./$lang/index.html"><div class="lang">$lang</div></a>
```

### In-code documentation
In your code, you can then start to write the `doc_id`s.
If you wish to replace doclines by a translations, put a `doc_id` following this layout:
```python
"""
### &doc_id <PREFIX>:<ID>
"""
```
(For advanced users, the regex pattern is `r"\s*###\s*&doc_id\s*"`)

**WARNING**: Don't forget the prefix! The prefix is the name of the documentation file
the `doc_id` was found in.

Example: If you have a file named `mydocs.dthdoc` which contains a `my_doc_id` ID inside,
The full `doc_id` you need to include in your code is `mydocs:my_doc_id`.

See below under Usage how to deactivate file prefixes, if you wish to do so.

## Running the program
### Usage
This is the usage provided by argparse itself:
```ignorelang
usage: __main__.py [-h] [--verify] [-V] [--noverbose] [-F] [-D DOXYFILE] [-O OUTPUT]
                   [-P POSTPROCESS] [--listpostprocesses] [--debug | --mute]
                   [--nocleanup] [--skipgen]
                   translation_dir
```

#### Positional arguments
- `translation_dir`: The translations folder explained above.

#### Optional arguments
- `-h`: prints this usage message
- `--verify`: verifies the layout of the translations folder and all files inside, instead of actually generating the 
documentation
- `-V` (or `--version`): prints the version then exits.
- `--noverbose`: no output will be printed in the console.
- `-F` (or `--nofileprefix`): Deactivates the file prefixes when registering `doc_id`s.
- `-D` (or `--doxyfile`): Path to a custom Doxyfile. If this option is not provided, DoxyTH will look for a file 
named `Doxyfile` by default. Passing this option is necessary only when your Doxygen configuration file is 
NOT named `Doxyfile`
- `-O` (or `--output`): Path to the output directory. If not given, defaults to `docs/`.
- `-P` (or `--postprocess`): Passes the file lines to a postprocess instead of printing them back to Doxygen.
- `--listpostprocesses`: Lists all the available postprocesses, then exits.
- [`--debug` | `--mute`]: `debug` prints everything, including non-error from the Doxygen output, whereas `mute` totally
mutes Doxygen, including the warnings and errors (and also those of DoxyTH itself). Both are NOT recommended unless
you perfectly know what you are doing.
- `--nocleanup`: Leaves the temporary files upon finishing generating the documentation. You shouldn't be using this
option unless you know why you use it.
- `--skipgen`: Debug option. Skips the Doxygen docs generation. DO NOT use unless you know how to.


### Generating documentation

If you want to generate the documentation from the different translations files, simply run the gendoc package

```commandline
python -m doxyth.gendoc
```
or
```commandline
python -m doxyth
```

using the usage above.

### Output

The result will be in the output directory you gave, and if you gave none, in `docs/`.

The output directory will contain a subdirectory with the language code of said language, and inside will be a full
Doxygen generation. Doxygen's output language will be set to said language, if a translation exists.

You will also find a index.html in the output directory. This file is created by DoxyTH, following a template html file.
If you wish to customise it, see 


### Verifying the translations

If you wish to verify the translations files/directories, you can do so by running the verify package

```commandline
python -m doxyth.verify
```

Its usage is as follows:
```ignorelang
usage: verify.py [-h]
                 {directory,dir,d,languagedirectory,langdir,ld,file,f} documentation

positional arguments:
  {directory,dir,d,languagedirectory,langdir,ld,file,f}
                        Sub-modules
    directory (dir, d)  Verify the documentation format of the whole
                        translations directory
    languagedirectory   Verify the documentation format of a language
        (langdir, ld)   directory
    file (f)            Verify the documentation format of a file

                        Positional arguments
    documentation       The path of either the directory or the file
```

If you choose to verify the whole directory, it will ouput the number of translations per language and print a warning
if the number of translations of at least one language is different from the others.

If you choose to verify either a language directory or a file, it will print the number of doc_ids found in this file,
or any errors if some are found.