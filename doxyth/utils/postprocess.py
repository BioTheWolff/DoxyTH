available_postprocesses = ['doxypypy']


class DoxypypyPostProcess:
    """
    ### &doc_id postprocess:DoxypypyPostProcess

    The class that serves as a bridge between DoxyTH and Doxypypy
    """

    def __init__(self):
        """
        ### &doc_id postprocess:DoxypypyPostprocess_init

        Tries to import doxypypy, and raises an exception if the module is not installed

        Raises:
            ModuleNotFoundError: if the module is not installed/found
        """

        try:
            import doxypypy
        except ModuleNotFoundError:
            raise Exception("Doxypypy is not installed on this machine. Unable to postprocess data.")

    def __call__(self, filename, lines):
        """
        ### &doc_id postprocess:DoxypypyPostProcess_call

        The main bridge between DoxyTH and Doxypypy. Re-creates the doxypypy variables and gives it to the AstWalker

        Args:
            filename: The file_name name
            lines: The file_name lines
        """

        from doxypypy.doxypypy import AstWalker
        from os import sep
        from optparse import Values
        from .langs import ascii_encode

        # Replace all the lines by a normal \n at the end
        try:
            lines = [f"{line.rstrip()}\n" for line in lines]
        except UnicodeEncodeError:
            lines = [f"{ascii_encode(line).rstrip()}\n" for line in lines]

        # Define options
        options = {'autobrief': True, 'autocode': True, 'topLevelNamespace': None, 'tablength': 4, 'debug': None}

        # All the code below is extracted from doxypypy (with a few edits to fit in with doxyth)

        full_path_namespace = filename.replace(sep, '.')[:-3]
        # Use any provided top-level namespace argument to trim off excess.
        real_namespace = full_path_namespace
        if options['topLevelNamespace']:
            namespace_start = full_path_namespace.find(options['topLevelNamespace'])
            if namespace_start >= 0:
                real_namespace = full_path_namespace[namespace_start:]
        options['fullPathNamespace'] = real_namespace

        ast_walker = AstWalker(lines, Values(defaults=options), filename)
        ast_walker.parseLines()
        # Output the modified source.
        print(ast_walker.getLines())


def postprocess_dispatcher(postprocess: str, filename, lines):
    """
    ### &doc_id postprocess:dispatcher

    Dispatches the file_name name and lines to the right class, depending on the postprocess string given

    Args:
        postprocess: The string of the postprocess, taken directly from the command line argument
        filename: The file_name name
        lines: The file_name lines
    """

    if postprocess not in available_postprocesses:
        raise Exception(f"Postprocess {postprocess} not recognised. Available postprocesses: "
                        f"{' / '.join(available_postprocesses)}")

    if postprocess == 'doxypypy':
        DoxypypyPostProcess()(filename, lines)
