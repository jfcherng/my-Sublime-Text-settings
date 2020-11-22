#!/usr/bin/python
# -*- coding: utf-8 -*-

from .server.Settings import read_sublime_settings
import os
import threading
import subprocess
import sys
import sublime
import sublime_plugin
import shlex
import re
import json

# fix for import order

sys.path.append(os.path.join(sublime.packages_path(), "LiveReload"))
LiveReload = __import__("LiveReload")
sys.path.remove(os.path.join(sublime.packages_path(), "LiveReload"))


class CompassThread(threading.Thread):
    def getLocalOverride(self):
        """
        You can override defaults in sublime-project file

        Discussion: https://github.com/dz0ny/LiveReload-sublimetext2/issues/43

        Example:

            "settings": {
              "lrcompass": {
                "dirname": "/path/to/directory/which/contains/config.rb",
                "command": "compass compile -e production --force"
              }
            }
        """
        try:
            view_settings = sublime.active_window().active_view().settings()
            view_settings = view_settings.get("lrcompass")
            if view_settings:
                return view_settings
            else:
                return {}
        except Exception:
            return {}

    def __init__(self, dirname, on_compile):
        ##TODO: Proper handler for this
        try:
            self.dirname = self.getLocalOverride.get("dirname") or dirname.replace("\\", "/")
        except Exception as e:
            self.dirname = dirname.replace("\\", "/")

        try:
            self.command = self.getLocalOverride.get("command") or "compass compile"
        except Exception as e:
            self.command = "compass compile"

        self.stdout = None
        self.stderr = None
        self.on_compile = on_compile
        threading.Thread.__init__(self)

    #  Check if a config.rb file exists in the current directory
    #  If no config.rb is found then check the parent and stop when root directory is reached
    def check_for_compass_config(self):
        if os.path.isfile(os.path.join(self.dirname, "config.rb")):
            return True
        dirname = os.path.abspath(os.path.join(self.dirname, os.pardir)).replace("\\", "/")
        if self.dirname == dirname:
            return False
        else:
            self.dirname = dirname
            return self.check_for_compass_config()

    # Generate config.rb file
    def generate_conf_rb(self, dirname):
        config_rb = """http_path = "/"
        css_dir = "."
        sass_dir = "."
        images_dir = "img"
        javascripts_dir = "javascripts"
        output_style = :nested
        relative_assets=true
        line_comments = false
        """
        with open(os.path.join(dirname, "config.rb"), "w") as f:
            f.write(config_rb)
        self.dirname = dirname
        return

    def run(self):
        dirname = self.dirname
        if not self.check_for_compass_config():
            if read_sublime_settings(
                os.path.join(
                    sublime.packages_path(),
                    "LiveReload",
                    "CompassPlugin.sublime-settings",
                )
            )["create_configrb"]:
                self.generate_conf_rb(dirname)
            else:
                sublime.error_message(
                    "Could not find Compass config.rb. Please check your sublime-project file and adjust settings accordingly!"
                )
                return
        # cmd = shlex.split(self.command)
        # cmd.append(self.dirname)
        # Mac doesn't compile array
        cmd = self.command + ' "' + self.dirname + '"'
        p = subprocess.Popen(
            cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        compiled = p.stdout.read()

        # Find the file to refresh from the console output
        if compiled:
            print("Compass : " + compiled.decode("utf-8"))
            matches = re.findall("\S+\.css", compiled.decode("utf-8"))
            if len(matches) > 0:
                for match in matches:
                    self.on_compile(match)


class CompassPreprocessor(LiveReload.Plugin, sublime_plugin.EventListener):

    title = "Compass Preprocessor"
    description = "Compile and refresh page, when file is compiled"
    file_types = ".scss,.sass"
    this_session_only = True
    file_name = ""

    def on_post_save(self, view):
        self.original_filename = os.path.basename(view.file_name())
        if self.should_run(self.original_filename):
            dirname = os.path.dirname(view.file_name())
            CompassThread(dirname, self.on_compile).start()

    def on_compile(self, file_to_refresh):
        settings = {
            "path": file_to_refresh,
            "apply_js_live": False,
            "apply_css_live": True,
            "apply_images_live": True,
        }
        self.sendCommand("refresh", settings, self.original_filename)
