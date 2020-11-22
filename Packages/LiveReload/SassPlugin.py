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

sys.path.append(os.path.join(sublime.packages_path(), 'LiveReload'))
LiveReload = __import__('LiveReload')
sys.path.remove(os.path.join(sublime.packages_path(), 'LiveReload'))


class SassThread(threading.Thread):
    # init class
    def __init__(self, dirname, on_compile, filename):
        # filename
        self.filename = filename

        # dirname
        try:
            self.dirname = self.getLocalOverride.get('dirname') or dirname.replace('\\', '/')
        except Exception as e:
            self.dirname = dirname.replace('\\', '/')

        # default config
        self.config = read_sublime_settings(os.path.join(sublime.packages_path(),'LiveReload','SassPlugin.sublime-settings')) or {}

        # check for local config
        localConfigFile = os.path.join(self.dirname, "sass_config.json");
        if os.path.isfile(localConfigFile):
            localConfig = read_sublime_settings(localConfigFile)
            self.config.update(localConfig)

        try:
            self.command = self.getLocalOverride.get('command') or 'sass --update --stop-on-error --no-cache --sourcemap=none'
        except Exception as e:
            self.command = 'sass --update --stop-on-error --no-cache --sourcemap=none'

        self.stdout = None
        self.stderr = None
        self.on_compile = on_compile
        threading.Thread.__init__(self)

    # get settings from user settings with prefix lrsass
    def getLocalOverride(self):
        try:
            view_settings = sublime.active_window().active_view().settings()
            view_settings = view_settings.get('lrsass')
            if view_settings:
                return view_settings
            else:
                return {}
        except Exception:
            return {}

    def run(self):

        source = os.path.join(self.dirname, self.filename)
        destinationDir = self.dirname if self.config['destination_dir'] is None else self.config['destination_dir']
        destination = os.path.abspath(os.path.join(self.dirname, destinationDir, re.sub("\.(sass|scss)", '.css', self.filename)))

        cmd = self.command + ' "' + source + '":"' + destination + '"'

        print("[LiveReload Sass] source : " + source)
        print("[LiveReload Sass] destination : " + destination)
        print("[LiveReload Sass] Cmd : " + cmd)

        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        compiled = p.stdout.read()

        # Find the file to refresh from the console output
        if compiled:
            print("[LiveReload Sass] reloading : " + compiled.decode("utf-8"));
            matches = re.findall('\S+\.css', compiled.decode("utf-8"))
            if len(matches) > 0:
                for match in matches:
                    self.on_compile(match)


class SassPreprocessor(LiveReload.Plugin, sublime_plugin.EventListener):
    title = 'Sass Preprocessor'
    description = 'Compile and refresh page, when file is compiled'
    file_types = '.scss,.sass'
    this_session_only = True
    file_name = ''

    def on_post_save(self, view):
        self.original_filename = os.path.basename(view.file_name())
        if self.should_run(self.original_filename):
            dirname = os.path.dirname(view.file_name())
            SassThread(dirname, self.on_compile, self.original_filename).start()

    def on_compile(self, file_to_refresh):
        settings = {
            'path': file_to_refresh,
            'apply_js_live': False,
            'apply_css_live': True,
            'apply_images_live': True,
            }
        self.sendCommand('refresh', settings, self.original_filename)
