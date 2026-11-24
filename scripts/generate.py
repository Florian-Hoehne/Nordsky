#!/usr/bin/env python3
"""Generates all Nordsky theme files from the single palette below.

    python3 scripts/generate.py

Outputs, per theme in THEMES
    jetbrains/src/main/resources/themes/<Stem>.xml          editor colour scheme
    jetbrains/src/main/resources/themes/<Stem>.theme.json   IDE UI theme
    vscode/themes/<slug>-color-theme.json                   VS Code theme
    docs/preview-<slug>.html                                palette + syntax preview

The installable packages are built with the official toolchains afterwards, see README.md.
"""
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------- palette
P = {
    # surfaces, darkest to lightest
    "bg0": "#01142A",  # tool windows, side bars, status bar
    "bg1": "#011C33",  # editor
    "bg2": "#06294A",  # caret row, hover
    "bg3": "#0B3A66",  # pressed, inactive selection
    "sel": "#124D85",  # selection
    "border": "#0A2E4F",
    # text
    "fg": "#DCE7F2",
    "muted": "#7F9BB8",
    "faint": "#3F5F80",
    "linenum": "#2F6FB5",
    # syntax
    "blue": "#4DA3FF",  # keywords
    "sky": "#9CCBFF",  # fields, attribute names
    "orange": "#F5A742",  # keys, constants, escapes
    "green": "#7EDC8A",  # strings
    "mint": "#B5EBC0",  # unquoted string-like values
    "teal": "#4FD6BE",  # types, links
    "aqua": "#9FE8D5",  # markup tags
    "yellow": "#FFD98A",  # function declarations
    "coral": "#FF7B8A",  # numbers
    "lavender": "#B3A5F5",  # annotations, metadata
    "comment": "#5E86AE",
    "doc": "#5FA595",
    "red": "#F0616D",
    "rose": "#F5A3AA",
    "grey": "#71869B",
    # signals
    "error": "#FF5C6C",
    "warning": "#F5A742",
    "accent": "#1668C7",  # default buttons, selected tabs
    "white": "#FFFFFF",
    # tinted backgrounds
    "addBg": "#0E3A2E",
    "delBg": "#4A1B2A",
    "modBg": "#0F3560",
    "conflictBg": "#4A3414",
    "searchBg": "#5A4410",
    "usageBg": "#103E5C",
    "writeBg": "#3D2A55",
}


# Syntax roles point at palette colours, so a theme can assign them differently.
ROLES = {
    "kw": "blue", "str": "green", "plain": "mint", "key": "orange", "const": "orange",
    "esc": "orange", "num": "coral", "type": "teal", "tag": "aqua", "fn": "yellow",
    "field": "sky", "meta": "lavender", "op": "sky", "link": "teal",
}

# Second theme: the look of the terminal the palette was taken from. Red strings, green
# numbers, grey annotations, plain white constants and near-white comments.
CONSOLE = {
    **P,
    "bg0": "#021221", "bg1": "#03182B", "bg2": "#0A2238", "bg3": "#0F3152", "sel": "#12406E",
    "border": "#0B2740", "fg": "#E8EEF4", "muted": "#7C90A5", "faint": "#3D5268",
    "linenum": "#3D5F85", "blue": "#4A96EA", "sky": "#6DB5F7", "teal": "#3EC9A7",
    "green": "#56D06C", "comment": "#A9B8C7", "doc": "#58B878",
}
CONSOLE_ROLES = {
    "kw": "blue", "str": "red", "plain": "rose", "key": "sky", "const": "fg", "esc": "orange",
    "num": "green", "type": "teal", "tag": "teal", "fn": "sky", "field": "fg", "meta": "grey",
    "op": "fg", "link": "green",
}


def resolve(palette, roles):
    return {**palette, **{role: palette[color] for role, color in roles.items()}}


# theme name -> (file stem, palette with roles resolved)
THEMES = {
    "Nordsky": ("Nordsky", resolve(P, ROLES)),
    "Nordsky Console": ("NordskyConsole", resolve(CONSOLE, CONSOLE_ROLES)),
}


def hx(name):
    """Palette name (or literal hex) -> 'RRGGBB' as JetBrains schemes want it."""
    return P.get(name, name).lstrip("#").upper()


def luminance(color):
    rgb = [int(color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = sorted((luminance(P[a]), luminance(P[b])), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# Every text colour must stay readable on the editor background (WCAG AA).
for _theme, (_stem, P) in THEMES.items():
    for _name in ("fg", "muted", "comment", "doc", "error", *ROLES):
        assert contrast(_name, "bg1") >= 4.5, (_theme, _name, round(contrast(_name, "bg1"), 2))

# --------------------------------------------------------------------------- JetBrains editor scheme
EDITOR_COLORS = {
    "CARET_COLOR": "fg",
    "CARET_ROW_COLOR": "bg2",
    "SELECTION_BACKGROUND": "sel",
    "GUTTER_BACKGROUND": "bg1",
    "LINE_NUMBERS_COLOR": "linenum",
    "LINE_NUMBER_ON_CARET_ROW_COLOR": "sky",
    "INDENT_GUIDE": "border",
    "SELECTED_INDENT_GUIDE": "linenum",
    "VISUAL_INDENT_GUIDE": "border",
    "RIGHT_MARGIN_COLOR": "border",
    "SOFT_WRAP_SIGN_COLOR": "faint",
    "WHITESPACES": "faint",
    "TEARLINE_COLOR": "border",
    "SELECTED_TEARLINE_COLOR": "linenum",
    "METHOD_SEPARATORS_COLOR": "border",
    "FOLDED_TEXT_BORDER_COLOR": "border",
    "ADDED_LINES_COLOR": "green",
    "MODIFIED_LINES_COLOR": "blue",
    "DELETED_LINES_COLOR": "coral",
    "WHITESPACES_MODIFIED_LINES_COLOR": "faint",
    "IGNORED_ADDED_LINES_BORDER_COLOR": "green",
    "IGNORED_MODIFIED_LINES_BORDER_COLOR": "blue",
    "IGNORED_DELETED_LINES_BORDER_COLOR": "coral",
    "DOCUMENTATION_COLOR": "bg0",
    "INFORMATION_HINT": "bg0",
    "QUESTION_HINT": "modBg",
    "ERROR_HINT": "delBg",
    "NOTIFICATION_BACKGROUND": "bg2",
    "CONSOLE_BACKGROUND_KEY": "bg0",
    "LOOKUP_COLOR": "bg0",
    "READONLY_BACKGROUND": "bg1",
    "READONLY_FRAGMENT_BACKGROUND": "bg2",
    "FILESTATUS_ADDED": "green",
    "FILESTATUS_MODIFIED": "blue",
    "FILESTATUS_DELETED": "muted",
    "FILESTATUS_UNKNOWN": "coral",
    "FILESTATUS_IDEA_FILESTATUS_IGNORED": "faint",
    "FILESTATUS_NOT_CHANGED_IMMEDIATE": "sky",
    "FILESTATUS_NOT_CHANGED_RECURSIVE": "sky",
    "FILESTATUS_MERGED": "lavender",
    "FILESTATUS_IDEA_FILESTATUS_MERGED_WITH_CONFLICTS": "error",
    "FILESTATUS_addedOutside": "green",
    "FILESTATUS_modifiedOutside": "blue",
    "ScrollBar.Mac.thumbColor": "2F6FB566",
    "ScrollBar.Mac.hoverThumbColor": "2F6FB5AA",
    "VCS_ANNOTATIONS_COLOR_1": "06294A",
    "VCS_ANNOTATIONS_COLOR_2": "08335B",
    "VCS_ANNOTATIONS_COLOR_3": "0B3D6C",
    "VCS_ANNOTATIONS_COLOR_4": "0E477D",
    "VCS_ANNOTATIONS_COLOR_5": "11518E",
}

# name -> "fg=<color> bg=<color> fx=<type>:<color> stripe=<color> b i"
# fx types: line, wave, strike, dotted, box.  "" clears an inherited attribute.
ATTRS = {
    # --- language defaults: every language plugin inherits from these
    "TEXT": "fg=fg bg=bg1",
    "DEFAULT_IDENTIFIER": "fg=fg",
    "DEFAULT_KEYWORD": "fg=kw",
    "DEFAULT_STRING": "fg=str",
    "DEFAULT_VALID_STRING_ESCAPE": "fg=esc",
    "DEFAULT_INVALID_STRING_ESCAPE": "fg=error fx=wave:error",
    "DEFAULT_NUMBER": "fg=num",
    "DEFAULT_LINE_COMMENT": "fg=comment i",
    "DEFAULT_BLOCK_COMMENT": "fg=comment i",
    "DEFAULT_DOC_COMMENT": "fg=doc i",
    "DEFAULT_DOC_COMMENT_TAG": "fg=type b",
    "DEFAULT_DOC_COMMENT_TAG_VALUE": "fg=field",
    "DEFAULT_DOC_MARKUP": "fg=tag",
    "DEFAULT_CLASS_NAME": "fg=type",
    "DEFAULT_CLASS_REFERENCE": "fg=type",
    "DEFAULT_INTERFACE_NAME": "fg=type i",
    "DEFAULT_FUNCTION_DECLARATION": "fg=fn",
    "DEFAULT_FUNCTION_CALL": "fg=fg",
    "DEFAULT_STATIC_METHOD": "fg=fg i",
    "DEFAULT_INSTANCE_FIELD": "fg=field",
    "DEFAULT_STATIC_FIELD": "fg=field i",
    "DEFAULT_CONSTANT": "fg=const",
    "DEFAULT_GLOBAL_VARIABLE": "fg=field i",
    "DEFAULT_LOCAL_VARIABLE": "fg=fg",
    "DEFAULT_PARAMETER": "fg=fg",
    "DEFAULT_REASSIGNED_LOCAL_VARIABLE": "fg=fg fx=dotted:muted",
    "DEFAULT_REASSIGNED_PARAMETER": "fg=fg fx=dotted:muted",
    "DEFAULT_METADATA": "fg=meta",
    "DEFAULT_LABEL": "fg=meta",
    "DEFAULT_PREDEFINED_SYMBOL": "fg=const",
    "DEFAULT_OPERATION_SIGN": "fg=op",
    "DEFAULT_BRACES": "fg=fg",
    "DEFAULT_BRACKETS": "fg=fg",
    "DEFAULT_PARENTHS": "fg=fg",
    "DEFAULT_DOT": "fg=fg",
    "DEFAULT_COMMA": "fg=muted",
    "DEFAULT_SEMICOLON": "fg=muted",
    "DEFAULT_TAG": "fg=tag",
    "DEFAULT_ATTRIBUTE": "fg=field",
    "DEFAULT_ENTITY": "fg=key",
    "DEFAULT_TEMPLATE_LANGUAGE_COLOR": "bg=bg0",
    "DEFAULT_HIGHLIGHTED_REFERENCE": "fg=type",
    # --- editor chrome
    "HYPERLINK_ATTRIBUTES": "fg=link fx=line:link",
    "FOLLOWED_HYPERLINK_ATTRIBUTES": "fg=lavender fx=line:lavender",
    "CTRL_CLICKABLE": "fg=link fx=line:link",
    "SEARCH_RESULT_ATTRIBUTES": "bg=searchBg stripe=orange",
    "WRITE_SEARCH_RESULT_ATTRIBUTES": "bg=writeBg stripe=lavender",
    "TEXT_SEARCH_RESULT_ATTRIBUTES": "bg=searchBg stripe=orange",
    "IDENTIFIER_UNDER_CARET_ATTRIBUTES": "bg=usageBg stripe=teal",
    "WRITE_IDENTIFIER_UNDER_CARET_ATTRIBUTES": "bg=writeBg stripe=lavender",
    "MATCHED_BRACE_ATTRIBUTES": "fg=yellow bg=bg3 b",
    "UNMATCHED_BRACE_ATTRIBUTES": "fg=error bg=delBg b",
    "FOLDED_TEXT_ATTRIBUTES": "fg=muted bg=bg2",
    "DELETED_TEXT_ATTRIBUTES": "fg=muted fx=strike:muted",
    "INLINE_PARAMETER_HINT": "fg=muted bg=bg2",
    "INLINE_PARAMETER_HINT_HIGHLIGHTED": "fg=fg bg=bg3",
    "INLINE_PARAMETER_HINT_CURRENT": "fg=sky bg=bg3",
    "INLAY_DEFAULT": "fg=muted bg=bg2",
    "INLAY_TEXT_WITHOUT_BACKGROUND": "fg=muted",
    "CODE_LENS_BORDER_COLOR": "fg=faint",
    "LIVE_TEMPLATE_ATTRIBUTES": "fx=box:blue",
    "TEMPLATE_VARIABLE_ATTRIBUTES": "fg=lavender",
    "BREADCRUMBS_DEFAULT": "fg=muted",
    "BREADCRUMBS_HOVERED": "fg=fg bg=bg2",
    "BREADCRUMBS_CURRENT": "fg=fg bg=bg3",
    "BREADCRUMBS_INACTIVE": "fg=faint",
    "BREAKPOINT_ATTRIBUTES": "bg=delBg stripe=coral",
    "EXECUTIONPOINT_ATTRIBUTES": "fg=white bg=accent stripe=blue",
    "NOT_TOP_FRAME_ATTRIBUTES": "bg=modBg",
    "BOOKMARKS_ATTRIBUTES": "stripe=yellow",
    # --- inspections
    "ERRORS_ATTRIBUTES": "fx=wave:error stripe=error",
    "WARNING_ATTRIBUTES": "fx=wave:warning stripe=warning",
    "INFO_ATTRIBUTES": "fx=wave:muted stripe=muted",
    "WRONG_REFERENCES_ATTRIBUTES": "fg=error",
    "BAD_CHARACTER": "fg=error fx=wave:error",
    "NOT_USED_ELEMENT_ATTRIBUTES": "fg=faint",
    "DEPRECATED_ATTRIBUTES": "fx=strike:muted",
    "MARKED_FOR_REMOVAL_ATTRIBUTES": "fx=strike:error",
    "TYPO": "fx=wave:doc",
    "TEXT_STYLE_ERROR": "fx=wave:doc",
    "TODO_DEFAULT_ATTRIBUTES": "fg=yellow b i stripe=yellow",
    "DUPLICATE_FROM_SERVER": "bg=bg2",
    "RUNTIME_ERROR": "fx=wave:error stripe=error",
    # --- diff
    "DIFF_INSERTED": "bg=addBg stripe=green",
    "DIFF_DELETED": "bg=delBg stripe=coral",
    "DIFF_MODIFIED": "bg=modBg stripe=blue",
    "DIFF_CONFLICT": "bg=conflictBg stripe=orange",
    # --- console and ANSI colours
    "CONSOLE_NORMAL_OUTPUT": "fg=fg",
    "CONSOLE_ERROR_OUTPUT": "fg=coral",
    "CONSOLE_USER_INPUT": "fg=green i",
    "CONSOLE_SYSTEM_OUTPUT": "fg=muted",
    "CONSOLE_BLACK_OUTPUT": "fg=bg3",
    "CONSOLE_RED_OUTPUT": "fg=coral",
    "CONSOLE_GREEN_OUTPUT": "fg=green",
    "CONSOLE_YELLOW_OUTPUT": "fg=orange",
    "CONSOLE_BLUE_OUTPUT": "fg=blue",
    "CONSOLE_MAGENTA_OUTPUT": "fg=lavender",
    "CONSOLE_CYAN_OUTPUT": "fg=teal",
    "CONSOLE_GRAY_OUTPUT": "fg=fg",
    "CONSOLE_DARKGRAY_OUTPUT": "fg=muted",
    "CONSOLE_RED_BRIGHT_OUTPUT": "fg=FF9CA8",
    "CONSOLE_GREEN_BRIGHT_OUTPUT": "fg=mint",
    "CONSOLE_YELLOW_BRIGHT_OUTPUT": "fg=yellow",
    "CONSOLE_BLUE_BRIGHT_OUTPUT": "fg=sky",
    "CONSOLE_MAGENTA_BRIGHT_OUTPUT": "fg=CFC6FA",
    "CONSOLE_CYAN_BRIGHT_OUTPUT": "fg=aqua",
    "CONSOLE_WHITE_OUTPUT": "fg=white",
    "LOG_ERROR_OUTPUT": "fg=coral",
    "LOG_WARNING_OUTPUT": "fg=orange",
    "LOG_INFO_OUTPUT": "fg=fg",
    "LOG_DEBUG_OUTPUT": "fg=muted",
    "LOG_VERBOSE_OUTPUT": "fg=faint",
    # --- Java / Kotlin
    "ANNOTATION_NAME_ATTRIBUTES": "fg=meta",
    "ANNOTATION_ATTRIBUTE_NAME_ATTRIBUTES": "fg=field",
    "STATIC_FINAL_FIELD_ATTRIBUTES": "fg=const",
    "TYPE_PARAMETER_NAME_ATTRIBUTES": "fg=tag",
    "ABSTRACT_CLASS_NAME_ATTRIBUTES": "fg=type i",
    "ENUM_NAME_ATTRIBUTES": "fg=type",
    "CONSTRUCTOR_CALL_ATTRIBUTES": "fg=type",
    "IMPLICIT_ANONYMOUS_CLASS_PARAMETER_ATTRIBUTES": "fg=field fx=line:sky",
    "KOTLIN_NAMED_ARGUMENT": "fg=field",
    "KOTLIN_LABEL": "fg=meta",
    "KOTLIN_MUTABLE_VARIABLE": "fg=fg fx=dotted:muted",
    # --- XML / HTML
    "XML_TAG": "fg=muted",
    "XML_TAG_NAME": "fg=tag",
    "XML_ATTRIBUTE_NAME": "fg=field",
    "XML_ATTRIBUTE_VALUE": "fg=str",
    "XML_NS_PREFIX": "fg=meta",
    "XML_PROLOGUE": "fg=muted",
    "XML_ENTITY_REFERENCE": "fg=key",
    "XML_TAG_DATA": "fg=fg",
    "HTML_TAG": "fg=muted",
    "HTML_TAG_NAME": "fg=tag",
    "HTML_ATTRIBUTE_NAME": "fg=field",
    "HTML_ATTRIBUTE_VALUE": "fg=str",
    "HTML_ENTITY_REFERENCE": "fg=key",
    # --- YAML / JSON / properties: keys orange, values never plain white
    "YAML_SCALAR_KEY": "fg=key b",
    "YAML_SCALAR_VALUE": "fg=plain",
    "YAML_SCALAR_STRING": "fg=str",
    "YAML_SCALAR_DSTRING": "fg=str",
    "YAML_SCALAR_LIST": "fg=plain",
    "YAML_TEXT": "fg=plain",
    "YAML_ANCHOR": "fg=meta",
    "YAML_SIGN": "fg=field",
    "JSON.PROPERTY_KEY": "fg=key",
    "JSON.KEYWORD": "fg=kw",
    "PROPERTIES.KEY": "fg=key",
    "PROPERTIES.VALUE": "fg=str",
    "PROPERTIES.KEY_VALUE_SEPARATOR": "fg=field",
    # --- shell
    "BASH.SHEBANG": "fg=comment i",
    "BASH.VAR_USE": "fg=field",
    "BASH.VAR_DEF": "fg=field",
    "BASH.HERE_DOC": "fg=str",
    "BASH.HERE_DOC_START": "fg=key",
    "BASH.HERE_DOC_END": "fg=key",
    "BASH.EXTERNAL_COMMAND": "fg=fn",
    "BASH.INTERNAL_COMMAND": "fg=kw",
    "BASH.FUNCTION_DECLARATION": "fg=fn",
    "BASH.BACKQUOTE": "fg=key",
    "BASH.REDIRECTION": "fg=field",
    # --- Markdown
    "MARKDOWN_HEADER_LEVEL_1": "fg=kw b",
    "MARKDOWN_HEADER_LEVEL_2": "fg=kw b",
    "MARKDOWN_HEADER_LEVEL_3": "fg=field b",
    "MARKDOWN_HEADER_LEVEL_4": "fg=field b",
    "MARKDOWN_HEADER_LEVEL_5": "fg=field",
    "MARKDOWN_HEADER_LEVEL_6": "fg=field",
    "MARKDOWN_BOLD": "fg=key b",
    "MARKDOWN_ITALIC": "fg=fn i",
    "MARKDOWN_CODE_SPAN": "fg=str",
    "MARKDOWN_CODE_FENCE": "fg=str",
    "MARKDOWN_CODE_BLOCK": "fg=str",
    "MARKDOWN_BLOCK_QUOTE": "fg=comment i",
    "MARKDOWN_LINK_TEXT": "fg=type",
    "MARKDOWN_LINK_DESTINATION": "fg=muted fx=line:muted",
    "MARKDOWN_LIST_ITEM": "fg=key",
    # --- SQL and regular expressions
    "SQL_KEYWORD": "fg=kw",
    "SQL_STRING": "fg=str",
    "SQL_TABLE": "fg=type",
    "SQL_COLUMN": "fg=field",
    "SQL_PROCEDURE": "fg=fn",
    "REGEXP.META": "fg=key",
    "REGEXP.CHAR_CLASS": "fg=type",
    "REGEXP.QUANTIFIER": "fg=num",
    "REGEXP.ESC_CHARACTER": "fg=key",
    "INJECTED_LANGUAGE_FRAGMENT": "bg=021F38",
}

FX = {"line": 1, "wave": 2, "strike": 3, "dotted": 5, "box": 0}


def attr_xml(name, spec):
    opts = []
    font = 0
    for token in spec.split():
        if token == "b":
            font |= 1
        elif token == "i":
            font |= 2
        else:
            key, value = token.split("=")
            if key == "fg":
                opts.append(("FOREGROUND", hx(value)))
            elif key == "bg":
                opts.append(("BACKGROUND", hx(value)))
            elif key == "stripe":
                opts.append(("ERROR_STRIPE_COLOR", hx(value)))
            elif key == "fx":
                kind, color = value.split(":")
                opts.append(("EFFECT_COLOR", hx(color)))
                opts.append(("EFFECT_TYPE", str(FX[kind])))
    if font:
        opts.append(("FONT_TYPE", str(font)))
    body = "".join(f'\n        <option name="{k}" value="{v}"/>' for k, v in opts)
    return f'    <option name="{escape(name)}">\n      <value>{body}\n      </value>\n    </option>'


def editor_scheme(name):
    colors = "\n".join(f'    <option name="{k}" value="{hx(v)}"/>' for k, v in EDITOR_COLORS.items())
    attrs = "\n".join(attr_xml(k, v) for k, v in ATTRS.items())
    return (f'<scheme name="{name}" version="142" parent_scheme="Darcula">\n'
            f'  <colors>\n{colors}\n  </colors>\n  <attributes>\n{attrs}\n  </attributes>\n</scheme>\n')


# --------------------------------------------------------------------------- JetBrains UI theme
def ui_theme(name, stem):
    return {
        "name": name,
        "dark": True,
        "author": "Nordsky",
        "parentTheme": "ExperimentalDark",
        "editorScheme": f"/themes/{stem}.xml",
        "colors": {k: v for k, v in P.items()},
        "ui": {
            "*": {
                "background": "bg0",
                "foreground": "fg",
                "infoForeground": "muted",
                "disabledForeground": "faint",
                "inactiveForeground": "muted",
                "inactiveBackground": "bg0",
                "selectionBackground": "sel",
                "selectionForeground": "white",
                "selectionInactiveBackground": "bg3",
                "selectionBackgroundInactive": "bg3",
                "lightSelectionBackground": "bg2",
                "lightSelectionForeground": "fg",
                "lightSelectionInactiveBackground": "bg2",
                "hoverBackground": "bg2",
                "borderColor": "border",
                "disabledBorderColor": "border",
                "separatorColor": "border",
                "focusColor": "blue",
                "focusedBorderColor": "blue",
                "acceleratorForeground": "muted",
                "acceleratorSelectionForeground": "sky",
                "modifiedItemForeground": "blue",
                "errorForeground": "error",
            },
            "ActionButton": {
                "hoverBackground": "bg2", "hoverBorderColor": "bg2",
                "pressedBackground": "bg3", "pressedBorderColor": "bg3",
            },
            "Button": {
                "startBackground": "bg2", "endBackground": "bg2",
                "startBorderColor": "bg3", "endBorderColor": "bg3",
                "focusedBorderColor": "blue", "shadowColor": "#00000000",
                "default": {
                    "foreground": "white",
                    "startBackground": "accent", "endBackground": "accent",
                    "startBorderColor": "accent", "endBorderColor": "accent",
                    "focusedBorderColor": "sky", "focusColor": "blue",
                    "shadowColor": "#00000000",
                },
            },
            "ComboBox": {
                "background": "bg1", "nonEditableBackground": "bg1",
                "ArrowButton": {"background": "bg1", "nonEditableBackground": "bg1",
                                "iconColor": "sky", "disabledIconColor": "faint"},
            },
            "CompletionPopup": {
                "matchForeground": "orange",
                "selectionBackground": "sel", "selectionInactiveBackground": "bg3",
            },
            "Component": {
                "borderColor": "bg3", "focusColor": "blue", "focusedBorderColor": "blue",
                "disabledBorderColor": "border", "iconColor": "muted", "hoverIconColor": "fg",
                "errorFocusColor": "error", "inactiveErrorFocusColor": "delBg",
                "warningFocusColor": "warning", "inactiveWarningFocusColor": "conflictBg",
            },
            "Counter": {"background": "accent", "foreground": "white"},
            "DefaultTabs": {
                "background": "bg0", "borderColor": "border", "hoverBackground": "bg2",
                "underlineColor": "blue", "inactiveUnderlineColor": "linenum",
                "underlinedTabBackground": "bg1", "underlinedTabForeground": "white",
            },
            "DragAndDrop": {"areaBackground": "bg3", "areaBorderColor": "blue", "areaForeground": "fg"},
            "Editor": {"background": "bg0", "foreground": "muted", "shortcutForeground": "blue"},
            "EditorPane": {"background": "bg1", "inactiveBackground": "bg1"},
            "EditorTabs": {
                "background": "bg0", "borderColor": "border", "hoverBackground": "bg2",
                "inactiveColoredFileBackground": "#00000000",
                "underlineColor": "blue", "inactiveUnderlineColor": "linenum",
                "underlinedTabBackground": "bg1", "underlinedTabForeground": "white",
                "underlineHeight": 3,
            },
            "FileColor": {
                "Yellow": "#3A2F12", "Green": "#0E3327", "Blue": "#0B2F55",
                "Violet": "#2A2550", "Orange": "#3D2A12", "Rose": "#3F1B2A",
            },
            "Link": {
                "activeForeground": "teal", "hoverForeground": "aqua",
                "pressedForeground": "aqua", "visitedForeground": "lavender",
                "secondaryForeground": "muted",
            },
            "List": {"background": "bg0", "hoverBackground": "bg2"},
            "MainToolbar": {
                "background": "bg0", "inactiveBackground": "bg0",
                "Dropdown": {"background": "bg0", "hoverBackground": "bg2", "pressedBackground": "bg3"},
                "Icon": {"hoverBackground": "bg2", "pressedBackground": "bg3"},
            },
            "Menu": {"background": "bg0", "borderColor": "border", "separatorColor": "border",
                     "selectionBackground": "sel"},
            "MenuBar": {"borderColor": "border"},
            "NavBar": {"borderColor": "border"},
            "Notification": {
                "background": "bg2", "borderColor": "bg3", "foreground": "fg",
                "errorBackground": "delBg", "errorBorderColor": "error", "errorForeground": "fg",
                "ToolWindow": {
                    "informativeBackground": "addBg", "informativeBorderColor": "doc",
                    "informativeForeground": "fg",
                    "warningBackground": "conflictBg", "warningBorderColor": "warning",
                    "warningForeground": "fg",
                    "errorBackground": "delBg", "errorBorderColor": "error", "errorForeground": "fg",
                },
            },
            "Panel": {"background": "bg0"},
            "Plugins": {
                "background": "bg0", "tagBackground": "bg3", "tagForeground": "sky",
                "lightSelectionBackground": "bg2", "hoverBackground": "bg2",
                "SearchField": {"background": "bg1", "borderColor": "border"},
                "SectionHeader": {"background": "bg1", "foreground": "muted"},
                "Button": {
                    "installForeground": "sky", "installBorderColor": "blue",
                    "installFillForeground": "white", "installFillBackground": "accent",
                    "updateForeground": "white", "updateBackground": "accent",
                    "updateBorderColor": "accent",
                },
            },
            "Popup": {
                "paintBorder": True, "borderColor": "bg3", "inactiveBorderColor": "border",
                "separatorColor": "border",
                "Header": {"activeBackground": "bg2", "inactiveBackground": "bg1"},
                "Toolbar": {"background": "bg0", "borderColor": "border"},
                "Advertiser": {"background": "bg1", "borderColor": "border", "foreground": "muted"},
            },
            "PopupMenu": {"background": "bg0", "translucentBackground": "bg0"},
            "ProgressBar": {
                "trackColor": "bg3", "progressColor": "blue",
                "indeterminateStartColor": "accent", "indeterminateEndColor": "sky",
                "passedColor": "green", "passedEndColor": "mint",
                "failedColor": "error", "failedEndColor": "coral",
            },
            "ScrollBar": {
                "trackColor": "#00000000", "thumbColor": "#2F6FB555", "thumbBorderColor": "#00000000",
                "hoverTrackColor": "#00000000", "hoverThumbColor": "#2F6FB5AA",
                "hoverThumbBorderColor": "#00000000",
                "Transparent": {
                    "trackColor": "#00000000", "thumbColor": "#2F6FB555",
                    "thumbBorderColor": "#00000000", "hoverTrackColor": "#00000000",
                    "hoverThumbColor": "#2F6FB5AA", "hoverThumbBorderColor": "#00000000",
                },
                "Mac": {
                    "trackColor": "#00000000", "thumbColor": "#2F6FB555",
                    "thumbBorderColor": "#00000000", "hoverTrackColor": "#00000000",
                    "hoverThumbColor": "#2F6FB5AA", "hoverThumbBorderColor": "#00000000",
                    "Transparent": {
                        "trackColor": "#00000000", "thumbColor": "#2F6FB555",
                        "thumbBorderColor": "#00000000", "hoverTrackColor": "#00000000",
                        "hoverThumbColor": "#2F6FB5AA", "hoverThumbBorderColor": "#00000000",
                    },
                },
            },
            "SearchEverywhere": {
                "Header": {"background": "bg1"},
                "Tab": {"selectedBackground": "accent", "selectedForeground": "white"},
                "SearchField": {"background": "bg0", "borderColor": "border"},
                "Advertiser": {"background": "bg1", "foreground": "muted"},
            },
            "SearchMatch": {"startBackground": "orange", "endBackground": "orange"},
            "Separator": {"separatorColor": "border"},
            "SidePanel": {"background": "bg0"},
            "SpeedSearch": {"background": "bg2", "borderColor": "bg3", "foreground": "fg",
                            "errorForeground": "error"},
            "StatusBar": {
                "background": "bg0", "borderColor": "border", "hoverBackground": "bg2",
                "Widget": {"hoverBackground": "bg2", "pressedBackground": "bg3"},
                "Breadcrumbs": {"hoverBackground": "bg2", "selectionBackground": "bg3",
                                "selectionInactiveBackground": "bg2"},
            },
            "TabbedPane": {
                "background": "bg0", "contentAreaColor": "border", "underlineColor": "blue",
                "disabledUnderlineColor": "faint", "hoverColor": "bg2", "focusColor": "bg3",
            },
            "Table": {"background": "bg0", "stripeColor": "bg1", "gridColor": "border",
                      "hoverBackground": "bg2"},
            "TableHeader": {"background": "bg1", "separatorColor": "border", "bottomSeparatorColor": "border"},
            "TextArea": {"background": "bg1"},
            "TextField": {"background": "bg1"},
            "TextPane": {"background": "bg1"},
            "FormattedTextField": {"background": "bg1"},
            "PasswordField": {"background": "bg1"},
            "TitlePane": {"background": "bg0", "inactiveBackground": "bg0",
                          "Button": {"hoverBackground": "bg2"}},
            "ToggleButton": {
                "onBackground": "accent", "onForeground": "white",
                "offBackground": "bg2", "offForeground": "muted",
                "buttonColor": "fg", "borderColor": "bg3",
            },
            "ToolBar": {"background": "bg0"},
            "ToolTip": {
                "background": "bg2", "foreground": "fg", "borderColor": "bg3",
                "infoForeground": "muted", "shortcutForeground": "sky",
                "Actions": {"background": "bg1", "infoForeground": "muted"},
            },
            "ToolWindow": {
                "background": "bg0",
                "Header": {"background": "bg0", "inactiveBackground": "bg0", "borderColor": "border"},
                "HeaderTab": {
                    "selectedBackground": "bg2", "selectedInactiveBackground": "bg2",
                    "hoverBackground": "bg2", "hoverInactiveBackground": "bg2",
                    "underlineColor": "blue", "inactiveUnderlineColor": "linenum",
                },
                "Button": {"hoverBackground": "bg2", "selectedBackground": "accent",
                           "selectedForeground": "white"},
            },
            "Tree": {"background": "bg0", "hoverBackground": "bg2",
                     "selectionBackground": "sel", "selectionInactiveBackground": "bg3",
                     "modifiedItemForeground": "blue"},
            "ValidationTooltip": {
                "errorBackground": "delBg", "errorBorderColor": "error",
                "warningBackground": "conflictBg", "warningBorderColor": "warning",
            },
            "VersionControl": {
                "Log": {"Commit": {"currentBranchBackground": "bg1", "hoveredBackground": "bg2",
                                   "unmatchedForeground": "faint"}},
                "FileHistory": {"Commit": {"selectedBranchBackground": "bg1"}},
                "RefLabel": {"foreground": "fg", "backgroundBase": "sky"},
                "GitLog": {"headIconColor": "yellow", "localBranchIconColor": "green",
                           "remoteBranchIconColor": "lavender", "tagIconColor": "orange",
                           "otherIconColor": "muted"},
            },
            "WelcomeScreen": {
                "background": "bg1", "borderColor": "border", "separatorColor": "border",
                "SidePanel": {"background": "bg0"},
                "Details": {"background": "bg1"},
                "Projects": {
                    "background": "bg1", "selectionBackground": "sel",
                    "selectionInactiveBackground": "bg3",
                    "actions": {"background": "bg2", "selectionBackground": "accent"},
                },
            },
        },
        "icons": {
            "ColorPalette": {
                "Checkbox.Background.Default.Dark": P["bg1"],
                "Checkbox.Border.Default.Dark": P["linenum"],
                "Checkbox.Background.Selected.Dark": P["accent"],
                "Checkbox.Border.Selected.Dark": P["accent"],
                "Checkbox.Foreground.Selected.Dark": P["white"],
                "Checkbox.Background.Disabled.Dark": P["bg0"],
                "Checkbox.Border.Disabled.Dark": P["bg3"],
                "Checkbox.Foreground.Disabled.Dark": P["faint"],
                "Checkbox.Focus.Wide.Dark": P["blue"],
                "Checkbox.Focus.Thin.Default.Dark": P["blue"],
                "Checkbox.Focus.Thin.Selected.Dark": P["sky"],
            }
        },
    }


# --------------------------------------------------------------------------- VS Code
def vscode_theme(name):
    def tok(name, scopes, color, style=None):
        settings = {"foreground": P[color]}
        if style is not None:
            settings["fontStyle"] = style
        return {"name": name, "scope": scopes, "settings": settings}

    a = lambda color, alpha: P[color] + alpha  # noqa: E731
    return {
        "name": name,
        "type": "dark",
        "semanticHighlighting": True,
        "colors": {
            "foreground": P["fg"], "descriptionForeground": P["muted"], "disabledForeground": P["faint"],
            "focusBorder": P["blue"], "errorForeground": P["error"],
            "selection.background": P["sel"], "icon.foreground": P["muted"],
            "editor.background": P["bg1"], "editor.foreground": P["fg"],
            "editor.lineHighlightBackground": P["bg2"], "editor.selectionBackground": P["sel"],
            "editor.inactiveSelectionBackground": P["bg3"],
            "editor.selectionHighlightBackground": a("sel", "88"),
            "editor.wordHighlightBackground": P["usageBg"],
            "editor.wordHighlightStrongBackground": P["writeBg"],
            "editor.findMatchBackground": a("orange", "66"),
            "editor.findMatchHighlightBackground": P["searchBg"],
            "editorCursor.foreground": P["fg"], "editorWhitespace.foreground": P["faint"],
            "editorLineNumber.foreground": P["linenum"], "editorLineNumber.activeForeground": P["sky"],
            "editorIndentGuide.background1": P["border"], "editorIndentGuide.activeBackground1": P["linenum"],
            "editorBracketMatch.background": P["bg3"], "editorBracketMatch.border": P["blue"],
            "editorError.foreground": P["error"], "editorWarning.foreground": P["warning"],
            "editorInfo.foreground": P["blue"], "editorLink.activeForeground": P["teal"],
            "editorGutter.addedBackground": P["green"], "editorGutter.modifiedBackground": P["blue"],
            "editorGutter.deletedBackground": P["coral"],
            "editorWidget.background": P["bg0"], "editorWidget.border": P["bg3"],
            "editorSuggestWidget.selectedBackground": P["sel"],
            "editorSuggestWidget.highlightForeground": P["orange"],
            "editorHoverWidget.background": P["bg0"], "editorHoverWidget.border": P["bg3"],
            "editorGroup.border": P["border"], "editorGroupHeader.tabsBackground": P["bg0"],
            "editorInlayHint.foreground": P["muted"], "editorInlayHint.background": P["bg2"],
            "diffEditor.insertedTextBackground": a("green", "22"),
            "diffEditor.removedTextBackground": a("coral", "22"),
            "tab.activeBackground": P["bg1"], "tab.activeForeground": P["white"],
            "tab.inactiveBackground": P["bg0"], "tab.inactiveForeground": P["muted"],
            "tab.activeBorderTop": P["blue"], "tab.border": P["border"], "tab.hoverBackground": P["bg2"],
            "activityBar.background": P["bg0"], "activityBar.foreground": P["fg"],
            "activityBar.inactiveForeground": P["faint"], "activityBar.border": P["border"],
            "activityBar.activeBorder": P["blue"], "activityBarBadge.background": P["accent"],
            "activityBarBadge.foreground": P["white"],
            "sideBar.background": P["bg0"], "sideBar.foreground": P["fg"], "sideBar.border": P["border"],
            "sideBarSectionHeader.background": P["bg0"], "sideBarSectionHeader.border": P["border"],
            "sideBarTitle.foreground": P["muted"],
            "list.activeSelectionBackground": P["sel"], "list.activeSelectionForeground": P["white"],
            "list.inactiveSelectionBackground": P["bg3"], "list.hoverBackground": P["bg2"],
            "list.focusOutline": P["blue"], "list.highlightForeground": P["orange"],
            "list.errorForeground": P["error"], "list.warningForeground": P["warning"],
            "statusBar.background": P["bg0"], "statusBar.foreground": P["muted"],
            "statusBar.border": P["border"], "statusBar.debuggingBackground": P["orange"],
            "statusBar.debuggingForeground": P["bg0"], "statusBar.noFolderBackground": P["bg0"],
            "statusBarItem.hoverBackground": P["bg2"], "statusBarItem.remoteBackground": P["accent"],
            "statusBarItem.remoteForeground": P["white"],
            "titleBar.activeBackground": P["bg0"], "titleBar.activeForeground": P["fg"],
            "titleBar.inactiveBackground": P["bg0"], "titleBar.inactiveForeground": P["muted"],
            "titleBar.border": P["border"],
            "panel.background": P["bg0"], "panel.border": P["border"],
            "panelTitle.activeBorder": P["blue"], "panelTitle.activeForeground": P["white"],
            "panelTitle.inactiveForeground": P["muted"],
            "button.background": P["accent"], "button.foreground": P["white"],
            "button.hoverBackground": "#1E7AE0", "button.secondaryBackground": P["bg3"],
            "button.secondaryForeground": P["fg"],
            "input.background": P["bg1"], "input.foreground": P["fg"], "input.border": P["bg3"],
            "input.placeholderForeground": P["faint"],
            "inputOption.activeBackground": P["sel"], "inputOption.activeBorder": P["blue"],
            "dropdown.background": P["bg0"], "dropdown.border": P["bg3"],
            "badge.background": P["accent"], "badge.foreground": P["white"],
            "progressBar.background": P["blue"],
            "scrollbarSlider.background": a("linenum", "55"),
            "scrollbarSlider.hoverBackground": a("linenum", "AA"),
            "scrollbarSlider.activeBackground": a("linenum", "CC"),
            "menu.background": P["bg0"], "menu.foreground": P["fg"],
            "menu.selectionBackground": P["sel"], "menu.selectionForeground": P["white"],
            "menu.separatorBackground": P["border"], "menu.border": P["border"],
            "notifications.background": P["bg2"], "notifications.border": P["bg3"],
            "quickInput.background": P["bg0"], "quickInputList.focusBackground": P["sel"],
            "pickerGroup.foreground": P["blue"], "pickerGroup.border": P["border"],
            "peekView.border": P["blue"], "peekViewEditor.background": P["bg0"],
            "peekViewResult.background": P["bg0"], "peekViewTitle.background": P["bg2"],
            "textLink.foreground": P["teal"], "textLink.activeForeground": P["aqua"],
            "textCodeBlock.background": P["bg2"], "textBlockQuote.background": P["bg2"],
            "textBlockQuote.border": P["bg3"],
            "gitDecoration.addedResourceForeground": P["green"],
            "gitDecoration.modifiedResourceForeground": P["blue"],
            "gitDecoration.deletedResourceForeground": P["muted"],
            "gitDecoration.untrackedResourceForeground": P["coral"],
            "gitDecoration.ignoredResourceForeground": P["faint"],
            "gitDecoration.conflictingResourceForeground": P["error"],
            "terminal.background": P["bg0"], "terminal.foreground": P["fg"],
            "terminalCursor.foreground": P["fg"], "terminal.selectionBackground": P["sel"],
            "terminal.ansiBlack": P["bg3"], "terminal.ansiRed": P["coral"],
            "terminal.ansiGreen": P["green"], "terminal.ansiYellow": P["orange"],
            "terminal.ansiBlue": P["blue"], "terminal.ansiMagenta": P["lavender"],
            "terminal.ansiCyan": P["teal"], "terminal.ansiWhite": P["fg"],
            "terminal.ansiBrightBlack": P["muted"], "terminal.ansiBrightRed": "#FF9CA8",
            "terminal.ansiBrightGreen": P["mint"], "terminal.ansiBrightYellow": P["yellow"],
            "terminal.ansiBrightBlue": P["sky"], "terminal.ansiBrightMagenta": "#CFC6FA",
            "terminal.ansiBrightCyan": P["aqua"], "terminal.ansiBrightWhite": P["white"],
        },
        "tokenColors": [
            tok("Comments", ["comment", "punctuation.definition.comment"], "comment", "italic"),
            tok("Doc comments", ["comment.block.documentation", "comment.block.javadoc",
                                 "string.quoted.docstring"], "doc", "italic"),
            tok("Doc tags", ["keyword.other.documentation", "storage.type.class.jsdoc",
                             "entity.name.tag.javadoc"], "type", "bold"),
            tok("Keywords", ["keyword", "storage", "storage.type", "storage.modifier",
                             "keyword.control", "variable.language", "constant.language"], "kw", ""),
            tok("Operators", ["keyword.operator", "punctuation.accessor"], "op", ""),
            tok("Strings", ["string", "string.quoted", "markup.inline.raw", "markup.fenced_code",
                            "markup.raw"], "str"),
            tok("Unquoted values", ["string.unquoted", "string.unquoted.plain.out.yaml",
                                    "string.unquoted.plain.in.yaml"], "plain"),
            tok("Escapes and regex", ["constant.character.escape", "string.regexp",
                                      "constant.other.placeholder", "constant.character.entity"], "esc"),
            tok("Numbers", ["constant.numeric"], "num"),
            tok("Constants", ["constant.other", "variable.other.constant",
                              "variable.other.enummember", "support.constant"], "const"),
            tok("Types", ["entity.name.type", "entity.name.class", "entity.other.inherited-class",
                          "support.type", "support.class", "storage.type.java",
                          "storage.type.object.array.java", "entity.name.namespace"], "type", ""),
            tok("Type parameters", ["storage.type.generic", "entity.name.type.parameter"], "tag"),
            tok("Function declarations", ["entity.name.function", "meta.function entity.name.function",
                                          "support.function"], "fn"),
            tok("Variables", ["variable", "variable.parameter", "meta.function-call",
                              "entity.name.function.member.call"], "fg"),
            tok("Fields", ["variable.other.property", "variable.other.member",
                           "variable.other.object.property", "meta.attribute"], "field"),
            tok("Annotations", ["storage.type.annotation", "meta.annotation punctuation.definition.annotation",
                                "meta.decorator", "entity.name.function.decorator",
                                "punctuation.decorator", "entity.name.label"], "meta"),
            tok("Markup tags", ["entity.name.tag", "meta.tag.sgml"], "tag"),
            tok("Markup tag punctuation", ["punctuation.definition.tag"], "muted"),
            tok("Attribute names", ["entity.other.attribute-name"], "field"),
            tok("Keys", ["entity.name.tag.yaml", "support.type.property-name",
                         "support.type.property-name.json", "keyword.other.definition.ini",
                         "meta.property-name", "support.type.property-name.toml"], "key", "bold"),
            tok("Punctuation", ["punctuation.separator", "punctuation.terminator"], "muted"),
            tok("Headings", ["markup.heading", "entity.name.section"], "kw", "bold"),
            tok("Bold", ["markup.bold"], "key", "bold"),
            tok("Italic", ["markup.italic"], "fn", "italic"),
            tok("Quotes", ["markup.quote"], "comment", "italic"),
            tok("Links", ["markup.underline.link", "string.other.link"], "link", "underline"),
            tok("Lists", ["punctuation.definition.list.begin", "beginning.punctuation.definition.list"],
                "key"),
            tok("Inserted", ["markup.inserted"], "str"),
            tok("Deleted", ["markup.deleted"], "num"),
            tok("Changed", ["markup.changed"], "kw"),
            tok("Invalid", ["invalid"], "error"),
        ],
        "semanticTokenColors": {
            "class": P["type"], "interface": {"foreground": P["type"], "italic": True},
            "enum": P["type"], "struct": P["type"], "type": P["type"], "typeParameter": P["tag"],
            "namespace": P["fg"], "function.declaration": P["fn"], "method.declaration": P["fn"],
            "property": P["field"], "enumMember": P["const"], "variable.readonly": P["const"],
            "property.readonly": P["const"], "property.static.readonly": P["const"],
            "annotation": P["meta"], "decorator": P["meta"], "macro": P["meta"],
            "parameter": P["fg"], "variable": P["fg"],
        },
    }


# --------------------------------------------------------------------------- preview
SAMPLES = {
    "TxResourceRequestInterceptor.java": """\
[doc]/**
 * Collects inline resources from a POSTed request. [doct]@see[/] [field]TxResourceValidationSupport[/]
 */[/]
[meta]@Interceptor[/]
[kw]public class[/] [type]TxResourceRequestInterceptor[/]
{
    [kw]private static final[/] [type]Logger[/] [const]LOGGER[/] [op]=[/] [type]LoggerFactory[/].[em]getLogger[/]([type]Interceptor[/].[kw]class[/])[muted];[/]
    [kw]private static final int[/] [const]HOOK_ORDER[/] [op]=[/] [num]-99[/][muted];[/]
    [kw]private final[/] [type]FhirContext[/] [field]fhirContext[/][muted];[/]

    [comment]// a failing remote service must not turn that into an error[/]
    [meta]@Nullable[/]
    [kw]private static[/] [type]LookupCodeResult[/] [fn]lookUp[/]([kw]final[/] [type]Coding[/] coding)
    {
        [const]LOGGER[/].warn([str]"Display of {}#{} not checked[/][esc]\\n[/][str]"[/][muted],[/] coding.getCode())[muted];[/]
        [kw]return null[/][muted];[/]
    }
}""",
    "dependabot.yml": """\
[comment]# Weekly, grouped minor/patch updates[/]
[key]version[/][op]:[/] [num]2[/]
[key]updates[/][op]:[/]
  [op]-[/] [key]package-ecosystem[/][op]:[/] [str]"maven"[/]
    [key]directory[/][op]:[/] [str]"/"[/]
    [key]schedule[/][op]:[/]
      [key]interval[/][op]:[/] [plain]weekly[/]
    [key]open-pull-requests-limit[/][op]:[/] [num]1[/]
    [key]commit-message[/][op]:[/]
      [key]prefix[/][op]:[/] [str]"build"[/]""",
    "DATA-STORE.run.xml": """\
[muted]<[/][tag]configuration[/] [field]name[/][muted]=[/][str]"DATA-STORE"[/] [field]type[/][muted]=[/][str]"docker-deploy"[/][muted]>[/]
  [muted]<[/][tag]option[/] [field]name[/][muted]=[/][str]"imageTag"[/] [field]value[/][muted]=[/][str]"postgres:18"[/] [muted]/>[/]
  [muted]<[/][tag]option[/] [field]name[/][muted]=[/][str]"hostPort"[/] [field]value[/][muted]=[/][str]"5491"[/] [muted]/>[/]
[muted]</[/][tag]configuration[/][muted]>[/]""",
    ".bashrc": """\
[comment]# some more ls aliases[/]
[kw]alias[/] [field]ll[/][op]=[/][str]'ls -alF'[/]
[kw]if[/] [ -f [plain]~/.bash_aliases[/] ][muted];[/] [kw]then[/]
    [kw].[/] [plain]~/.bash_aliases[/]
[kw]fi[/]
[kw]export[/] [field]PATH[/][op]=[/][str]"[/][field]$PATH[/][str]:[/][esc]$([/][fn]go[/] env GOPATH[esc])[/][str]/bin"[/]""",
}

SWATCHES = [
    ("kw", "Keywords"), ("str", "Strings"), ("plain", "Plain values"), ("key", "Keys"),
    ("num", "Numbers"), ("type", "Types"), ("tag", "Tags"), ("fn", "Functions"),
    ("field", "Fields, attributes"), ("meta", "Annotations"), ("comment", "Comments"), ("doc", "Docs"),
]


def preview_html(name):
    def render(text):
        text = escape(text)
        text = re.sub(r"\[/\]", "</span>", text)
        return re.sub(r"\[([a-z]+)\]", r'<span class="\1">', text)

    panes = "".join(
        f'<section><header>{escape(name)}</header><pre>{render(code)}</pre></section>'
        for name, code in SAMPLES.items())
    swatches = "".join(
        f'<li><i style="background:{P[c]}"></i><b>{label}</b><code>{P[c]}</code></li>'
        for c, label in SWATCHES)
    css_vars = "".join(f"--{k}:{v};" for k, v in P.items())
    classes = "".join(f".{k}{{color:var(--{k})}}" for k in P)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{name}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{{{css_vars}}}
*{{box-sizing:border-box}}
body{{margin:0;padding:28px;background:var(--bg0);color:var(--fg);
  font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}}
h1{{margin:0 0 4px;font-size:22px;letter-spacing:.02em}}
p{{margin:0 0 20px;color:var(--muted)}}
ul{{list-style:none;margin:0 0 24px;padding:0;display:grid;gap:8px;
  grid-template-columns:repeat(auto-fill,minmax(170px,1fr))}}
li{{display:grid;grid-template-columns:28px 1fr;column-gap:10px;align-items:center;
  padding:8px 10px;background:var(--bg1);border:1px solid var(--border);border-radius:6px}}
li i{{grid-row:span 2;width:28px;height:28px;border-radius:5px}}
li b{{font-weight:600;font-size:13px}}
li code{{color:var(--muted);font-size:12px}}
main{{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr))}}
section{{background:var(--bg1);border:1px solid var(--border);border-radius:8px;overflow:hidden}}
section:first-child{{grid-row:span 3}}
header{{padding:7px 14px;background:var(--bg0);border-bottom:1px solid var(--border);
  box-shadow:inset 0 3px 0 var(--blue);color:var(--white);font-size:13px}}
pre{{margin:0;padding:14px 16px;overflow-x:auto;
  font:13px/1.6 "JetBrains Mono","Fira Code",ui-monospace,Menlo,Consolas,monospace}}
{classes}
.comment,.doc{{font-style:italic}}.doct{{color:var(--type);font-weight:700}}
.key{{font-weight:700}}.em{{font-style:italic}}
</style></head><body>
<h1>{name}</h1><p>Deep-navy theme for JetBrains IDEs and VS Code</p>
<ul>{swatches}</ul><main>{panes}</main>
</body></html>
"""


# --------------------------------------------------------------------------- write
def write(path, text):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    for theme, (stem, P) in THEMES.items():
        slug = theme.lower().replace(" ", "-")
        write(f"jetbrains/src/main/resources/themes/{stem}.xml", editor_scheme(theme))
        write(f"jetbrains/src/main/resources/themes/{stem}.theme.json",
              json.dumps(ui_theme(theme, stem), indent=2) + "\n")
        write(f"vscode/themes/{slug}-color-theme.json", json.dumps(vscode_theme(theme), indent=2) + "\n")
        write(f"docs/preview-{slug}.html", preview_html(theme))
