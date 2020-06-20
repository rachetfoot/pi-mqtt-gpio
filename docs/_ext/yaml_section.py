import os

import yaml
from docutils import io, nodes, statemachine, utils
from docutils.parsers.rst import Directive, directives
from docutils.utils.error_reporting import ErrorString, SafeString
from sphinx.directives.code import CodeBlock


class YamlSection(Directive):
    required_arguments = 1
    has_content = False
    option_spec = dict(
        section=directives.unchanged_required,
        indent=directives.nonnegative_int,
        display_top_node=directives.flag,
    )

    def run(self):
        if not self.state.document.settings.file_insertion_enabled:
            raise self.warning(
                f'"{self.name}" directive disabled because file_insertion_enabled is disabled.'
            )
        indent = self.options.get("indent", 2)
        source = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1
        )
        source_dir = os.path.dirname(os.path.abspath(source))
        path = directives.path(self.arguments[0])
        path = os.path.normpath(os.path.join(source_dir, path))
        path = utils.relative_path(None, path)
        path = nodes.reprunicode(path)
        encoding = self.options.get(
            "encoding", self.state.document.settings.input_encoding
        )
        e_handler = self.state.document.settings.input_encoding_error_handler
        try:
            self.state.document.settings.record_dependencies.add(path)
            yaml_file = io.FileInput(
                source_path=path, encoding=encoding, error_handler=e_handler
            )
        except UnicodeEncodeError as error:
            raise self.severe(
                'Problems with "%s" directive path:\n'
                'Cannot encode input file path "%s" '
                "(wrong locale?)." % (self.name, SafeString(path))
            )
        except IOError as error:
            raise self.severe(
                'Problems with "%s" directive path:\n%s.'
                % (self.name, ErrorString(error))
            )
        try:
            data = yaml.safe_load(yaml_file.read())
        except FileNotFoundError:
            raise self.error(f"No file found at {self.options['path']}.")
        except yaml.parser.ParserError:
            raise self.error("The file was not in YAML format.")
        keys = self.options["section"].split(".")
        last_key = None
        try:
            for key in keys:
                data = data[key]
                last_key = key
        except KeyError:
            raise self.error(
                f"Unable to find section '{self.options['section']}' in the YAML file.'"
            )
        if "display_top_node" in self.options and last_key is not None:
            data = {last_key: data}

        include_lines = statemachine.string2lines(
            yaml.dump(data, indent=indent), indent, convert_whitespace=True
        )
        self.options['source'] = path
        codeblock = CodeBlock(
            self.name,
            ["yaml"],
            self.options,
            include_lines,
            self.lineno,
            self.content_offset,
            self.block_text,
            self.state,
            self.state_machine,
        )
        return codeblock.run()


def setup(app):
    app.add_directive("yamlsection", YamlSection)

    return dict(version="0.1", parallel_read_safe=True, parallel_write_safe=True)
