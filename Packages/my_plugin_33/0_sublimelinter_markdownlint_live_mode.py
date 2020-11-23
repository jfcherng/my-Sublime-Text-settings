import importlib

try:
    linter = importlib.import_module("SublimeLinter-contrib-markdownlint.linter").MarkdownLint  # type: ignore

    linter.cmd = ("markdownlint", "${args}", "${temp_file}")
    linter.tempfile_suffix = "md"
except Exception as e:
    print(__file__, e)
