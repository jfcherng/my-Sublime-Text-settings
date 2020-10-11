# usage: { "keys": ["alt+q"], "command": "private_copy_paste", "args": { "is_cut": false } },

import enum
import sublime
import sublime_plugin

PLUGIN_NAME = "Private Copy Paste"


class Mode(enum.IntEnum):
    COPY = enum.auto()
    PASTE = enum.auto()


PRIVATE_CLIPBOARD = ""
CURRENT_MODE = Mode.COPY


def status_msg(msg: str) -> None:
    sublime.status_message("[{}] {}".format(PLUGIN_NAME, msg))


class PrivateCopyPasteCommand(sublime_plugin.TextCommand):
    """ A command to do "copy" and "paste" without polluting the clipboard. """

    def run(self, edit: sublime.Edit, is_cut: bool = False) -> None:
        if CURRENT_MODE == Mode.COPY:
            self._do_copy(edit, self.view, is_cut)
        elif CURRENT_MODE == Mode.PASTE:
            self._do_paste(edit, self.view)
        else:
            raise RuntimeError

    def _do_copy(self, edit: sublime.Edit, view: sublime.View, is_cut: bool) -> None:
        global PRIVATE_CLIPBOARD, CURRENT_MODE

        sel = view.sel()

        if len(sel) != 1:
            status_msg("Copy mode only supports single selection")
            return

        region = sel[0]

        if len(region) == 0:
            status_msg("Copy mode doesn't work for empty region")
            return

        PRIVATE_CLIPBOARD = view.substr(region)
        CURRENT_MODE = Mode.PASTE

        if is_cut:
            view.replace(edit, region, "")

    def _do_paste(self, edit: sublime.Edit, view: sublime.View) -> None:
        global PRIVATE_CLIPBOARD, CURRENT_MODE

        sel = view.sel()

        for r in reversed(sel):
            view.replace(edit, r, PRIVATE_CLIPBOARD)

        PRIVATE_CLIPBOARD = ""
        CURRENT_MODE = Mode.COPY
