import io
import os
import sublime

from AutoFileName import autofilename, getimageinfo

from .filesize import naturalsize


def prepare_completion(self, view: sublime.View, this_dir: str, directory: str) -> sublime.CompletionItem:
    path = os.path.join(this_dir, directory)

    annotation = ""
    annotation_head = ""
    annotation_head_kind = sublime.KIND_ID_AMBIGUOUS
    details_head = ""
    details_parts = []

    if os.path.isdir(path):
        annotation = "Dir"
        annotation_head = "📁"
        annotation_head_kind = sublime.KIND_ID_MARKUP
        details_head = "Directory"
    elif os.path.isfile(path):
        annotation = "File"
        annotation_head = "📄"
        annotation_head_kind = sublime.KIND_ID_MARKUP
        details_head = "File"
        details_parts.append("Size: " + naturalsize(os.stat(path).st_size))

    if path.endswith((".gif", ".jpeg", ".jpg", ".png")):
        details_head = "Image"

        with io.open(path, "rb") as f:
            read_data = f.read() if path.endswith((".jpeg", ".jpg")) else f.read(24)

        try:
            w, h = getimageinfo.getImageInfo(read_data)
            details_parts.append("Height: " + str(h))
            details_parts.append("Width: " + str(w))
        except Exception:
            pass

    return sublime.CompletionItem(
        trigger=directory.replace(".", "·"),
        annotation=annotation,
        completion=autofilename.apply_post_replacements(view, directory),
        kind=(annotation_head_kind, annotation_head, details_head),
        details=", ".join(details_parts),
    )


if int(sublime.version()) > 4073:
    autofilename.FileNameComplete.prepare_completion = prepare_completion  # type: ignore
