import sublime
import sublime_plugin


class AsyncCommandCommand(sublime_plugin.WindowCommand):
    """ Run a given command asynchronously. """

    def run(self, name: str, args: dict = {}) -> None:
        sublime.set_timeout_async(lambda: self.window.run_command(name, args), 0)
