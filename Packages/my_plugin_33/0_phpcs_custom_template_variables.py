import importlib
import os
import sublime

template_variables = {
    "home": os.path.expanduser("~"),
    "st_cache_path": sublime.cache_path(),
    "st_executable_path": sublime.executable_path(),
    "st_installed_packages_path": sublime.installed_packages_path(),
    "st_packages_path": sublime.packages_path(),
}

templated_keys = {
    "php_cs_fixer_executable_path",
    "phpcbf_executable_path",
    "phpcs_executable_path",
    "phpcs_php_path",
    "phpcs_php_prefix_path",
    "phpmd_executable_path",
    "scheck_executable_path",
}

try:
    Pref = importlib.import_module("Phpcs.phpcs").Pref  # type: ignore

    load_original = Pref.load

    def load_modified(self, *args, **kwargs) -> None:
        ret = load_original(self, *args, **kwargs)

        variables = sublime.active_window().extract_variables()
        variables.update(template_variables)

        for key in templated_keys:
            expanded = sublime.expand_variables(self.settings.get(key), variables)
            self.settings.set(key, expanded)

        return ret

    Pref.load = load_modified
except Exception as e:
    print(__file__, e)
