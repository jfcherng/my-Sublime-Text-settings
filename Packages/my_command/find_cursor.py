"""
Find Cursor.

Licensed under MIT
Copyright (c) 2014 - 2016 Isaac Muse <isaacmuse@gmail.com>

Makes Sublime cursors highly visible for a short duration.

Also, iterate through cursors centering them, or pan through view showing cursors.

Example Keymap:
    //////////////////////////////////
    // Find Cursor: Iterative Find
    //////////////////////////////////
    {
        "keys": ["ctrl+."],
        "command": "find_cursor",
        "args": {"reverse": false, "pan": false}
    },
    {
        "keys": ["ctrl+shift+."],
        "command": "find_cursor",
        "args": {"reverse": true, "pan": false}
    }

    //////////////////////////////////
    // Find Cursor: Panning Find
    //////////////////////////////////
    {
        "keys": ["ctrl+."],
        "command": "find_cursor",
        "args": {"reverse": false, "pan": true}
    },
    {
        "keys": ["ctrl+shift+."],
        "command": "find_cursor",
        "args": {"reverse": true, "pan": true}
    }
"""
import sublime_plugin
import sublime
import time
from collections import namedtuple

PAN_MODE = -2
NULL_INDEX = -1
FORWARD = 1
BACKWARD = -1


class PanCursor(namedtuple('PanCursor', ['cursor', 'distance', 'index'], verbose=False)):
    """Pan cursor object."""

    pass


class FindCursorCommand(sublime_plugin.TextCommand):
    """Find cursor command."""

    def save_item(self, defaults, src, dest):
        """Save the item if setting is available."""

        setting = self.settings.get(dest, None)
        if setting is not None:
            defaults[src] = setting

    def save(self):
        """Save the view's caret settings."""

        self.settings = self.view.settings()
        if self.settings.get("caret_defaults", None) is None:
            defaults = {}
            self.save_item(defaults, "width", "caret_extra_width")
            self.save_item(defaults, "top", "caret_extra_top")
            self.save_item(defaults, "bottom", "caret_extra_bottom")
            self.save_item(defaults, "style", "caret_style")
            self.save_item(defaults, "inverse", "inverse_caret_state")
            self.settings.set("caret_defaults", defaults)

    def restore_item(self, defaults, src, dest):
        """Restore item if setting is available. Erase item if it is not."""

        setting = defaults.get(src, None)
        if setting is not None:
            self.settings.set(dest, setting)
        else:
            self.settings.erase(dest)

    def restore(self, t):
        """Restore the view's caret settings."""

        if self.settings.get("caret_last_change", "") == t:
            defaults = self.settings.get("caret_defaults", None)
            if defaults is not None:
                self.restore_item(defaults, "width", "caret_extra_width")
                self.restore_item(defaults, "top", "caret_extra_top")
                self.restore_item(defaults, "bottom", "caret_extra_bottom")
                self.restore_item(defaults, "style", "caret_style")
                self.restore_item(defaults, "inverse", "inverse_caret_state")
            self.settings.erase("caret_defaults")
            if int(self.settings.get("caret_last_index", NULL_INDEX)) != NULL_INDEX:
                self.settings.erase("caret_last_index")

    def high_visibility(self):
        """Make the caret highly visible."""

        self.time = time.time()
        self.settings.set("caret_extra_width", 10)
        self.settings.set("caret_extra_bottom", 0)
        self.settings.set("caret_extra_top", 0)
        self.settings.set("inverse_caret_state", False)
        self.settings.set("caret_style", "smooth")
        self.settings.set("caret_last_change", str(self.time))

    def focus_cursor(self, cursor, index, pan):
        """
        Set focus on the given cursor if applicable.

        Set the last cursor index in the view settings.
        """

        if not self.skip_focus:
            if pan:
                self.view.show(cursor, True)
            else:
                self.view.show_at_center(cursor)
        self.settings.set("caret_last_index", index)

    def find_cursor(self, direction, pan):
        """Find cursor and adjust view if not the first time."""

        if direction not in [FORWARD, BACKWARD]:
            return

        cursor, index = self.get_cursor(direction, pan)

        if cursor is not None:
            self.focus_cursor(cursor, index, pan)

    def get_cursor(self, direction, pan):
        """Get the cursor."""

        return self.get_pan_cursor(direction) if pan else self.get_iter_cursor(direction)

    def get_pan_cursor(self, direction):
        """
        Get cursor in pan mode.

        On first call, get first cursor in viewable region.
        If no cursor in viewable region or on additional calls,
        grab first cursor outside of viewable region in the desired direction.
        """

        self.skip_focus = int(self.settings.get("caret_last_index", NULL_INDEX)) == NULL_INDEX
        cursor = None
        index = int(self.settings.get("caret_last_index", NULL_INDEX))

        sel = self.view.sel()
        visible_region = self.view.visible_region()

        if index != PAN_MODE:
            for s in sel:
                if visible_region.begin() <= s.b <= visible_region.end():
                    cursor = s
                    index = PAN_MODE

        if cursor is None:
            backwards = direction == BACKWARD
            before = False
            after = False
            for s in (reversed(sel) if backwards else sel):
                if before is False and visible_region.begin() > s.b:
                    before = True
                    cursor = s
                    if direction == BACKWARD:
                        break
                elif after is False and visible_region.end() < s.b:
                    after = True
                    cursor = s
                    if direction == FORWARD:
                        break

            if cursor is not None:
                self.skip_focus = False
                index = PAN_MODE

        return cursor, index

    def get_iter_cursor(self, direction):
        """
        Iterate through cursors.

        On first call get first cursor in viewable region opposite to the desired direction.
        If no cursors is in viewable region or on additional calls,
        iterate to the next cursor in the desired direction.
        """

        self.skip_focus = False
        cursor = None
        index = int(self.settings.get("caret_last_index", NULL_INDEX))

        if index == PAN_MODE:
            index = NULL_INDEX

        sel = self.view.sel()
        visible_region = self.view.visible_region()

        if len(sel):
            if index == NULL_INDEX:
                # Select first selection nearest the center of viewable region.
                # This is done only on first search.
                center_pt = visible_region.begin() + int((visible_region.end() - visible_region.begin()) / 2)
                closest = None
                idx = -1
                for s in sel:
                    idx += 1
                    if visible_region.begin() <= s.b <= visible_region.end():
                        distance = abs(center_pt - s.b)
                        if closest is None or distance < closest.distance:
                            closest = PanCursor(s, distance, idx)
                    elif s.b > visible_region.end():
                        break

                if closest is not None:
                    cursor = closest.cursor
                    index = closest.index

            if cursor is None:
                # Next cursor or offscreen cursor
                # if a visible cusrsor was not found
                index += 1 * direction
                if index < 0:
                    index = len(sel) - 1
                elif index >= len(sel):
                    index = 0
                cursor = sel[index]

        return cursor, index

    def run(self, edit, reverse=False, pan=False):
        """Show the cursor and the carets in a highly visible way, then revert them back to normal."""

        self.settings = sublime.load_settings("find_cursor.sublime-settings")
        timeout = self.settings.get("find_mode_timeout", 3000)
        self.save()
        self.high_visibility()
        self.find_cursor(FORWARD if not reverse else BACKWARD, pan)
        sublime.set_timeout(lambda t=str(self.time): self.restore(t), timeout)


class FindCursorListener(sublime_plugin.EventListener):
    """FindCursor listener."""

    def on_selection_modified_async(self, view):
        """
        Handle on selection modified event.

        If selection was modified, erase the tracked last index.
        """

        view.settings().erase("caret_last_index")
