"""
Modified from https://github.com/ahuff44/sublime-better-tab-cycling

Keybinding example:

// go to the previous tab view
{ "keys": ["ctrl+super+j"], "command": "step_tab_cycle", "args": { "steps": -1 } },
// go to the next tab view
{ "keys": ["ctrl+super+l"], "command": "step_tab_cycle", "args": { "steps": 1 } },
"""

import sublime
import sublime_plugin


class StepTabCycleCommand(sublime_plugin.WindowCommand):
    """
    Switch to the next tab in the active pane.
    Like sublime's builtin next_view, but stays within the active pane
    """

    def run(self, steps: int) -> None:
        window = self.window
        view = window.active_view()

        if not view:
            return

        group_index, view_index = window.get_view_index(view)
        views = window.views_in_group(group_index)
        window.focus_view(views[(view_index + steps) % len(views)])
