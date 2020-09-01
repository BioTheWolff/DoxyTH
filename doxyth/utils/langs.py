from typing import List

## The valid ISO 639-1 language codes
valid_codes = ['ab', 'aa', 'af', 'ak', 'sq', 'am', 'ar', 'an', 'hy', 'as', 'av', 'ae', 'ay', 'az', 'bm', 'ba', 'eu',
               'be', 'bn', 'bh', 'bi', 'bs', 'br', 'bg', 'my', 'ca', 'ch', 'ce', 'ny', 'zh', 'cv', 'kw', 'co', 'cr',
               'hr', 'cs', 'da', 'dv', 'nl', 'dz', 'en', 'eo', 'et', 'ee', 'fo', 'fj', 'fi', 'fr', 'ff', 'gl', 'ka',
               'de', 'el', 'gn', 'gu', 'ht', 'ha', 'he', 'hz', 'hi', 'ho', 'hu', 'ia', 'id', 'ie', 'ga', 'ig', 'ik',
               'io', 'is', 'it', 'iu', 'ja', 'jv', 'kl', 'kn', 'kr', 'ks', 'kk', 'km', 'ki', 'rw', 'ky', 'kv', 'kg',
               'ko', 'ku', 'kj', 'la', 'lb', 'lg', 'li', 'ln', 'lo', 'lt', 'lu', 'lv', 'gv', 'mk', 'mg', 'ms', 'ml',
               'mt', 'mi', 'mr', 'mh', 'mn', 'na', 'nv', 'nd', 'ne', 'ng', 'nb', 'nn', 'no', 'ii', 'nr', 'oc', 'oj',
               'cu', 'om', 'or', 'os', 'pa', 'pi', 'fa', 'pl', 'ps', 'pt', 'qu', 'rm', 'rn', 'ro', 'ru', 'sa', 'sc',
               'sd', 'se', 'sm', 'sg', 'sr', 'gd', 'sn', 'si', 'sk', 'sl', 'so', 'st', 'es', 'su', 'sw', 'ss', 'sv',
               'ta', 'te', 'tg', 'th', 'ti', 'bo', 'tk', 'tl', 'tn', 'to', 'tr', 'ts', 'tt', 'tw', 'ty', 'ug', 'uk',
               'ur', 'uz', 've', 'vi', 'vo', 'wa', 'cy', 'wo', 'fy', 'xh', 'yi', 'yo', 'za', 'zu']

## The available doxygen languages in codes, and the linked doxygen languages
doxygen_languages = {
    "af": "Afrikaans",
    "ar": "Arabic",
    "hy": "Armenian",
    # "": "Brazilian", Ignored because of the lack of a language code for Brazilian
    "ca": "Catalan",
    "zh": "Chinese",
    "zh-alt": "Chinese-Traditional",
    "hr": "Croatian",
    "cs": "Czech",
    "da": "Danish",
    "nl": "Dutch",
    "en": "English",
    "eo": "Esperanto",
    # "": "Farsi", Ignored because fa refers to "Persian" macrolanguage, and also to "Farsi". Persian has the priority
    "fi": "Finnish",
    "fr": "French",
    "de": "German",
    "el": "Greek",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ja-alt": "Japanese-en",
    "ko": "Korean",
    "ko-alt": "Korean-en",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "mk": "Macedonian",
    "no": "Norwegian",
    "fa": "Persian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sr": "Serbian",
    "sr-alt": "Serbian-Cyrillic",
    "sk": "Slovak",
    "sl": "Slovene",
    "es": "Spanish",
    "sv": "Swedish",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "vi": "Vietnamese"
}

## UTF-8 chars to HTML chars
html_chars_convert_dict = {'¡': '&iexcl;',
                           '¢': '&cent;',
                           '£': '&pound;',
                           '¤': '&curren;',
                           '¥': '&yen;',
                           '¦': '&brvbar;',
                           '§': '&sect;',
                           '¨': '&uml;',
                           '©': '&copy;',
                           'ª': '&ordf;',
                           '«': '&laquo;',
                           '¬': '&not;',
                           '\xad': '&shy;',
                           '®': '&reg;',
                           '¯': '&macr;',
                           '°': '&deg;',
                           '±': '&plusmn;',
                           '²': '&sup2;',
                           '³': '&sup3;',
                           '´': '&acute;',
                           'µ': '&micro;',
                           '¶': '&para;',
                           '·': '&middot;',
                           '¸': '&cedil;',
                           '¹': '&sup1;',
                           'º': '&ordm;',
                           '»': '&raquo;',
                           '¼': '&frac14;',
                           '½': '&frac12;',
                           '¾': '&frac34;',
                           '¿': '&iquest;',
                           'À': '&Agrave;',
                           'Á': '&Aacute;',
                           'Â': '&Acirc;',
                           'Ã': '&Atilde;',
                           'Ä': '&Auml;',
                           'Å': '&Aring;',
                           'Æ': '&AElig;',
                           'Ç': '&Ccedil;',
                           'È': '&Egrave;',
                           'É': '&Eacute;',
                           'Ê': '&Ecirc;',
                           'Ë': '&Euml;',
                           'Ì': '&Igrave;',
                           'Í': '&Iacute;',
                           'Î': '&Icirc;',
                           'Ï': '&Iuml;',
                           'Ð': '&ETH;',
                           'Ñ': '&Ntilde;',
                           'Ò': '&Ograve;',
                           'Ó': '&Oacute;',
                           'Ô': '&Ocirc;',
                           'Õ': '&Otilde;',
                           'Ö': '&Ouml;',
                           '×': '&times;',
                           'Ø': '&Oslash;',
                           'Ù': '&Ugrave;',
                           'Ú': '&Uacute;',
                           'Û': '&Ucirc;',
                           'Ü': '&Uuml;',
                           'Ý': '&Yacute;',
                           'Þ': '&THORN;',
                           'ß': '&szlig;',
                           'à': '&agrave;',
                           'á': '&aacute;',
                           'â': '&acirc;',
                           'ã': '&atilde;,',
                           'ä': '&auml;',
                           'å': '&aring;',
                           'æ': '&aelig;',
                           'ç': '&ccedil;',
                           'è': '&egrave;',
                           'é': '&eacute;',
                           'ê': '&ecirc;',
                           'ë': '&euml;',
                           'ì': '&igrave;',
                           'í': '&iacute;',
                           'î': '&icirc;',
                           'ï': '&iuml;',
                           'ð': '&eth;',
                           'ñ': '&ntilde;',
                           'ò': '&ograve;',
                           'ó': '&oacute;',
                           'ô': '&ocirc;',
                           'õ': '&otilde;',
                           'ö': '&ouml;',
                           '÷': '&divide;',
                           'ø': '&oslash;',
                           'ù': '&ugrave;',
                           'ú': '&uacute;',
                           'û': '&ucirc;',
                           'ü': '&uuml;',
                           'ý': '&yacute;',
                           'þ': '&thorn;',
                           'ÿ': '&yuml;'}


def is_valid_lang_dir(name):
    """
    Whether the directory name is a valid language code

    Args:
        name: The directory name

    Returns:
        bool
    """

    return name in valid_codes and len(name) == 2


def ascii_encode(string: str):
    """
    Encodes the string in ascii in ignore mode

    Args:
        string: The string

    Returns:
        The string in ascii
    """

    return str(string.encode('ascii', 'ignore'))[2:-1]


def convert_lines_to_html_chars(lines: List[str]):
    final = lines
    for char in html_chars_convert_dict:
        if any(char in line for line in lines):
            for n, line in enumerate(final):
                final[n] = line.replace(char, html_chars_convert_dict[char])
    return final
