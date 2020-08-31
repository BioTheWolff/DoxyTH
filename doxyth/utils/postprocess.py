available_postprocesses = ['doxypypy']


class DoxypypyPostProcess:

    def __init__(self):
        try:
            import doxypypy
        except ModuleNotFoundError:
            raise Exception("Doxypypy is not installed on this machine. Unable to postprocess data.")

    def __call__(self, filename, lines):
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
    if postprocess not in available_postprocesses:
        raise Exception(f"Postprocess {postprocess} not recognised. Available postprocesses: "
                        f"{' / '.join(available_postprocesses)}")

    if postprocess == 'doxypypy':
        DoxypypyPostProcess()(filename, lines)
