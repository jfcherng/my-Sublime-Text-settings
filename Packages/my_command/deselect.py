# Sublime Deselect plugin
#
# based on a forum post by C0D312:
# https://www.sublimetext.com/forum/viewtopic.php?f=2&t=4716#p21219

import sublime
import sublime_plugin


class DeselectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sel = self.view.sel()

        if len(sel) <= 0:
            return

        end = sel[0].b
        r = sublime.Region(end, end)

        sel.clear()
        sel.add(r)
