import sublime
import sublime_plugin


# { "keys": ["ctrl+shift+l"], "command": "extend_selection_to_previous_line" },
class ExtendSelectionToPreviousLineCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        v = self.view
        sel = v.sel()
        regions = [[r.begin(), r.end()] for r in sel]

        for r in regions:
            line = v.line(sublime.Region(*r))

            row, col = v.rowcol(r[0])
            if col != 0:
                r[0] = v.text_point(row + 1, 0)

            row, col = v.rowcol(r[1])
            if col != 0:
                r[1] = max(r[1], line.end())

        sel.clear()
        sel.add_all([sublime.Region(r[1], r[0]) for r in regions])

        # run select previous line
        v.run_command("move", {"by": "lines", "extend": True, "forward": False})
