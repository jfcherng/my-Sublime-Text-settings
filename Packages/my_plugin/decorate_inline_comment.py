import sublime
import sublime_plugin
import re

COMMENT_SCOPE = "comment"

# fmt: off
CMT_CONFIGS = [
    {
        'modifier': '//',
        'fill': '/',
        'fill_with_padding_spaces': False,
        're_whitespaces': None,
    },
    {
        'modifier': '::',
        'fill': '-',
        'fill_with_padding_spaces': True,
        're_whitespaces': None,
    },
    {
        'modifier': '#',
        'fill': '-',
        'fill_with_padding_spaces': True,
        're_whitespaces': None,
    },
    {
        'modifier': ';',
        'fill': '-',
        'fill_with_padding_spaces': True,
        're_whitespaces': None,
    },
]
# fmt: on

for cmt_config in CMT_CONFIGS:
    cmt_config["re_whitespaces"] = re.compile(
        r"^(?P<leading_ws>\s*)(?={})".format(cmt_config["modifier"])
    )


class decorateInlineCommentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        v = self.view

        for sel in v.sel():
            # sel.b is the visual cursor point
            sel = self._get_full_comment_region(v, sel.b)

            if not sel:
                continue

            line_regions = v.lines(sel)

            for line_region in line_regions:
                for cmt_config in CMT_CONFIGS:
                    matches = cmt_config["re_whitespaces"].match(v.substr(line_region))
                    if matches is not None:
                        break

            if not matches:
                print("Unsupported comment: {!r}".format(v.substr(sel)))
                continue

            leading_ws = matches.group("leading_ws")
            max_length = max(map(lambda l: len(l), line_regions))
            line_length = max_length - len(leading_ws + cmt_config["modifier"])

            # "expand selection to scope" may not select the trailing \n
            # in some syntaxes and we try to compensate it here
            if v.substr(sublime.Region(sel.end() - 1, sel.end())) == "\n":
                eols = ("", "\n")
            else:
                eols = ("\n", "")

            if cmt_config["fill_with_padding_spaces"]:
                dummy_content = " " + cmt_config["fill"] * (line_length - 1) + " "
            else:
                dummy_content = cmt_config["fill"] * (line_length + 1)

            # insert ending line
            v.insert(
                edit,
                sel.end(),
                (
                    eols[0]
                    + leading_ws
                    + cmt_config["modifier"]
                    + dummy_content
                    + cmt_config["modifier"]
                    + eols[1]
                ),
            )

            for line_region in reversed(line_regions):
                line = v.substr(line_region)

                # 1 for at least 1 extra trailing whitespace
                padding_r = 1 + (max_length - line_region.size())

                prefix = leading_ws + cmt_config["modifier"]
                suffix = (" " * padding_r) + cmt_config["modifier"]
                cmt_content = line[len(leading_ws + cmt_config["modifier"]) :]

                v.replace(edit, line_region, prefix + cmt_content + suffix)

            # insert begin line
            v.insert(
                edit,
                sel.begin(),
                (
                    leading_ws
                    + cmt_config["modifier"]
                    + dummy_content
                    + cmt_config["modifier"]
                    + "\n"
                ),
            )

    def _get_full_comment_region(self, view: sublime.View, pt: int) -> sublime.Region:
        """
        @brief Get the full comment region with neighbor lines.

        @param view The view
        @param pt   The point

        @return The full comment region.
        """

        # hmm... we are not in comment at all
        if not view.match_selector(pt, COMMENT_SCOPE):
            return sublime.Region(pt)

        row, col = view.rowcol(pt)
        row_begin = row_end = row
        row_max = view.rowcol(view.size())[0]

        # previous lines are comments too?
        while 0 < row_begin < row_max:
            test_row = row_begin - 1
            test_col = len(view.line(view.text_point(test_row, 0)))

            if view.match_selector(view.text_point(test_row, test_col), COMMENT_SCOPE):
                row_begin = test_row
            else:
                break

        # next lines are comments too?
        while 0 < row_end < row_max:
            test_row = row_end + 1
            test_col = len(view.line(view.text_point(test_row, 0)))

            if view.match_selector(view.text_point(test_row, test_col), COMMENT_SCOPE):
                row_end = test_row
            else:
                break

        # fmt: off
        return view.full_line(
            sublime.Region(
                view.text_point(row_begin, col),
                view.text_point(row_end, col),
            )
        )
        # fmt: on
