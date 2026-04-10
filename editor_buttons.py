from __future__ import annotations

from collections.abc import Callable

from aqt.editor import Editor

EditorButtonHandler = Callable[[Editor], None]


def register_editor_buttons() -> None:
    """Reserved for future editor-toolbar integration."""
    return None


def make_editor_button(
    buttons: list[str],
    editor: Editor,
    *,
    cmd: str,
    handler: EditorButtonHandler,
    tip: str,
    label: str,
    button_id: str,
    rightside: bool = True,
    toggleable: bool = False,
    icon: str | None = None,
) -> str:
    """Small wrapper around ``editor.addButton`` for reusable toolbar buttons."""
    button = editor.addButton(
        icon=icon,
        cmd=cmd,
        func=lambda current_editor: handler(current_editor),
        tip=tip,
        label=label,
        id=button_id,
        rightside=rightside,
        toggleable=toggleable,
    )
    buttons.append(button)
    return button
