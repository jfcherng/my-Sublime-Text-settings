import re
import sublime
import sublime_plugin

from typing import Any, AnyStr, Dict, Iterable, List, Match, Optional, Tuple, Union


# test case
"""
[test][]

[id1]: https://google.com "Google"
[id2]: https://yahoo.com 'Yahoo'
[id5]: <https://example.com> (Example)
[id8]: <> ()
[id9]: <https://en.wikipedia.org/wiki/Hobbit#Lifestyle> "Hobbit lifestyles"
"""


def truncate(s: str, max_length: int, ellipsis: str = "…") -> str:
    """
    @brief Truncate str to no more than max_length chars.

    @param s          The input string
    @param max_length The max length of the output string
    @param ellipsis   The ellipsis when the truncation happens

    @return The truncated string.
    """

    return s if len(s) <= max_length else s[: max_length - 1] + ellipsis


def strip_pairs(
    s: str, pairs: Iterable[Union[List[str], Tuple[str]]], only_first: bool = True
) -> str:
    """
    @brief Strip pairs from the string.

    @param s          The input string
    @param pairs      Pairs to be stripped
    @param only_first Only strip the first found pair

    @return The string after stripping.
    """

    for pair in pairs:
        len_0, len_1 = len(pair[0]), len(pair[1])

        if len(s) >= len_0 + len_1 and s[:len_0] == pair[0] and s[-len_1] == pair[1]:
            s = s[len_0:-len_1]

            if only_first:
                return s

    return s


class MarkdownReferenceCompletions(sublime_plugin.EventListener):
    """
    @brief Provide completions that match just after typing an opening square bracket.
    """

    # fmt: off
    # @see https://www.markdownguide.org/basic-syntax/#reference-style-links
    re_ref_links = re.compile(
        r"(?:^[ \t]*((?:[\-*]|\d+\.)[ \t]+)?)"
        r"\[(?P<ref_id>[^\]]+)\]:"
        r"(?:[ \t]+(?P<link><[^>]*>|[^\s]*))"
        r"(?:[ \t]+(?P<title>.*))?",
        re.MULTILINE,
    )
    # fmt: on

    re_linkable = re.compile(r"^(https?|ftps?)://", re.IGNORECASE)

    working_scope = (
        "text.html.markdown meta.link.reference"
        "    (constant.other.reference.link.markdown | punctuation.definition.constant.end.markdown)"
    )

    def on_post_text_command(
        self, view: sublime.View, command_name: str, args: Dict[str, Any]
    ) -> None:
        cursor = view.sel()[0].b

        if command_name in ("move", "drag_select", "left_delete", "right_delete", "delete_word"):
            return

        # auto invoke auto_complete
        if view.match_selector(cursor, self.working_scope):
            view.run_command("auto_complete")

    def on_query_completions(
        self, view: sublime.View, prefix: str, locations: List[int]
    ) -> Optional[sublime.CompletionList]:
        cursor = locations[0]

        if not view.match_selector(cursor, self.working_scope):
            return None

        # make sure we're inside the reference name portion
        pt = cursor - len(prefix)
        if view.substr(sublime.Region(pt - 2, pt)) != "][":
            return None

        return sublime.CompletionList(
            [
                self._generate_completion_item(m)
                for m in self.re_ref_links.finditer(view.substr(sublime.Region(0, len(view))))
            ],
            sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS,
        )

    def _generate_completion_item(self, m: Match[AnyStr]) -> sublime.CompletionItem:
        """
        @brief Generate the CompletionItem for the matched reference link.

        @param m The regex Match object

        @return The CompletionItem object.
        """

        # ------------- #
        # prepare title #
        # ------------- #

        title = (m.group("title") or "").strip()
        title = strip_pairs(title, [("'", "'"), ('"', '"'), ("(", ")")])

        if not title:
            title = "No title"

        # ------------ #
        # prepare link #
        # ------------ #

        link = (m.group("link") or "").strip()
        link = strip_pairs(link, [("<", ">")])

        if not link:
            link = "No link"

        # --------------- #
        # prepare details #
        # --------------- #

        details = link

        # make the link clickable if it's a URL
        if self.re_linkable.match(link):
            attr_href = sublime.command_url("open_url", {"url": link})
            details = f'<a href="{attr_href}">OPEN</a> {link}'

        return sublime.CompletionItem(
            annotation=truncate(title, 30),
            completion=m.group("ref_id"),
            completion_format=sublime.COMPLETION_FORMAT_TEXT,
            details=details,
            kind=(sublime.KIND_ID_MARKUP, "m", "Ref"),
            trigger=m.group("ref_id"),
        )
