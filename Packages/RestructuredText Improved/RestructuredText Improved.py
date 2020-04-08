# disable default "RestructuredText" package

import sublime_plugin, sublime, json, os, re

IS_ST3 = 3000 <= int(sublime.version()) <= 4000
IS_ST4 = 4000 <= int(sublime.version())

#
# sublime bug?: erases all user settings on restart!
#
#settings = sublime.load_settings(u'Preferences.sublime-settings')
#ignored_packages = settings.get(u'ignored_packages', [])
#  if 'RestructuredText' not in ignored_packages:
#   ignored_packages.append(u'RestructuredText')
#   settings.set('ignored_packages', ignored_packages)
#   sublime.save_settings(u'Preferences.sublime-settings')

SECTION_CHAR_RE = re.compile(r'''(?m)^([=\-`:.'"~^_*+\#])\1*$''')

# def get_header_context(view, cursor_pos):
#     r'''returns tuple (section_char, start_pos, end_pos, headline)'''

# class RstCompleteHeadlineUnderline(sublime_plugin.TextCommand):

#     def run(self):
#         if

# class RstEventListener(sublime_plugin.EventListener):

#     def on_query_context(self, view, key, operator=None, operand=None, match_all=False):
#         for sel in view.sel():
#             if sel.begin() != sel.end(): return

#             row, col = view.rowcol(sel.begin())

#             if row-1 > 0 and not view.line(view.text_point(row-2, 0)).strip():
#                 view.line(view.text_point(row-1, 0)).

#             if row-1 == 0:

#             if row-2 < 0
#             start_of_line = view.text_point(row, 0)


def plugin_unloaded():
    pass

def plugin_loaded():

    user_preferences_file = os.path.join(sublime.packages_path(),
        'User', 'Preferences.sublime-settings')

    import sys, re

    sys.stderr.write("user_preferences_file: %s\n" % user_preferences_file)

    user_preferences = {}
    if os.path.exists(user_preferences_file):
        with open(user_preferences_file, 'r', encoding='UTF-8') as f:
            s = f.read()

        s = re.sub(r'(^|(?<=\n))\s*//.*', '', s)
        sys.stderr.write("s: %s\n" % s)
        user_preferences = sublime.decode_value(s)

    if 'ignored_packages' not in user_preferences:
        user_preferences['ignored_packages'] = [ 'Vintage' ]

    changed = False
    if 'RestructuredText' not in user_preferences['ignored_packages']:
        changed = True
        user_preferences['ignored_packages'].append('RestructuredText')

    if changed:
        with open(user_preferences_file, 'rb') as f:
            backup = '.0.bak'
            i = 0
            while os.path.exists(user_preferences_file+backup):
                i += 1
                backup = '.%s.bak' % i

            with open(user_preferences_file+backup, 'wb') as b:
                b.write(f.read())

        with open(user_preferences_file, 'w') as f:
            if IS_ST4:
                f.write(sublime.encode_value(user_preferences, pretty=True))
            else:
                json.dump(user_preferences, f, indent=4)
