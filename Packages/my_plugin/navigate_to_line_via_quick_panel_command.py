import sublime
import sublime_plugin


class NavigateToLineViaQuickPanelCommand(sublime_plugin.WindowCommand):
    def run(self) -> None:
        # if the file gets closed during selection, `view` will become `None`
        view = self.window.active_view()

        orig_sel = [r for r in view.sel()]

        sublime.active_window().show_quick_panel(
            view.substr(sublime.Region(0, view.size())).split("\n"),
            on_select=lambda idx: self._select_entry(idx, view, orig_sel),
            on_highlight=lambda idx: self._highlight_entry(idx, view),
            flags=sublime.KEEP_OPEN_ON_FOCUS_LOST | sublime.MONOSPACE_FONT,
        )

    def _highlight_entry(self, idx: int, view: sublime.View) -> None:
        if not view:
            return

        view.window().focus_view(view)
        view.run_command("goto_line", {"line": idx + 1})
        view_select_regions_only(view, [view_full_line(view, view.text_point(idx, 0), True)])

    def _select_entry(self, idx: int, view: sublime.View, orig_sel: list) -> None:
        if not view:
            return

        if idx == -1:
            view.window().focus_view(view)
            view_select_regions_only(view, orig_sel)

            if orig_sel:
                view.show(orig_sel[-1])  # moving to the last selection makes more sense?


def view_full_line(view: sublime.View, point: int, no_line_ending: bool = False) -> sublime.Region:
    region = view.full_line(point)

    # "region" may be empty if it meets EOF
    if no_line_ending and region and view.substr(region.b - 1) == "\n":
        region.b -= 1

    return region


def view_select_regions_only(view: sublime.View, regions: list) -> None:
    view.sel().clear()
    view.sel().add_all(regions)
