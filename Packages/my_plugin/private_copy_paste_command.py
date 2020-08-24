# usage: { "keys": ["alt+q"], "command": "private_copy_paste" },

import sublime
import sublime_plugin


PLUGIN_NAME = "Private Copy Paste"
MODE_COPY = "copy"
MODE_PASTE = "paste"

PRIVATE_CLIPBOARD = ""
CURRENT_MODE = MODE_COPY


def status_msg(msg: str) -> None:
    sublime.status_message("[{}] {}".format(PLUGIN_NAME, msg))


class PrivateCopyPasteCommand(sublime_plugin.TextCommand):
    """ A command to do "copy" and "paste" without polluting the clipboard. """

    def run(self, edit: sublime.Edit) -> None:
        global PRIVATE_CLIPBOARD, CURRENT_MODE

        v = self.view
        sel = v.sel()

        # copy mode
        if CURRENT_MODE == "copy":
            if len(sel) != 1:
                status_msg("Copy mode only supports single selection")
                return

            if len(sel[0]) == 0:
                status_msg("Copy mode doesn't work for empty region")
                return

            PRIVATE_CLIPBOARD = v.substr(sel[0])
            CURRENT_MODE = MODE_PASTE

            v.replace(edit, sel[0], "")

        # paste mode
        else:
            for r in reversed(sel):
                v.replace(edit, r, PRIVATE_CLIPBOARD)

            PRIVATE_CLIPBOARD = ""
            CURRENT_MODE = MODE_COPY
