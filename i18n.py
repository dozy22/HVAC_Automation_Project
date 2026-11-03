"""Bilingual (English / Arabic) presentation layer for the HVAC studio.

The engineering code and the widget values stay in canonical English.  This
module translates only what the visitor sees: labels, captions, Markdown,
tables, chart annotations and selectable option labels.  Keeping the canonical
values intact means calculations, test fixtures and saved preferences behave
exactly the same in both languages.
"""

from __future__ import annotations

import html
import re
from typing import Any, Callable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from locales.ar import OPTION_LABELS, PATTERNS, TRANSLATIONS

LANG_EN = "en"
LANG_AR = "ar"
DEFAULT_LANGUAGE = LANG_AR
LANGUAGE_KEY = "language"
THEME_KEY = "dark_mode"

LANGUAGE_LABELS = {"ar": "العربية", "en": "English"}

# Keys are whitespace-normalised so that Markdown indentation and HTML line
# breaks do not hide a valid translation.  Selectable option values (for
# example "Wet bulb" or "Relative humidity") are also valid prose labels, so
# they seed the dictionary before the full page dictionary overrides them.
_DICT: dict[str, str] = {}
for _source, _target in OPTION_LABELS.items():
    _DICT[" ".join(_source.split())] = _target
for _source, _target in TRANSLATIONS.items():
    _DICT[" ".join(_source.split())] = _target

_OPTIONS: dict[str, str] = dict(OPTION_LABELS)
_PATTERN_LIST: list[tuple[re.Pattern[str], str]] = []
for _pattern, _replacement in PATTERNS:
    try:
        _PATTERN_LIST.append((re.compile(_pattern), _replacement))
    except re.error as _exc:  # pragma: no cover - configuration guard
        raise ValueError(f"Invalid Arabic translation pattern: {_pattern!r}") from _exc


def language() -> str:
    """Current UI language, with Arabic as the default presentation language."""
    value = st.session_state.get(LANGUAGE_KEY, DEFAULT_LANGUAGE)
    return value if value in (LANG_EN, LANG_AR) else DEFAULT_LANGUAGE


def is_arabic() -> bool:
    return language() == LANG_AR


def dark_mode() -> bool:
    return bool(st.session_state.get(THEME_KEY, False))


def _normalise(text: str) -> str:
    return " ".join(text.split())


def _preserve_whitespace(original: str, translated: str) -> str:
    lead = original[: len(original) - len(original.lstrip())]
    trail = original[len(original.rstrip()) :]
    return f"{lead}{translated}{trail}"


def _translate_unit(text: str) -> str | None:
    """Translate one exact string or one of the numeric sentence templates."""
    key = _normalise(text)
    if not key:
        return None
    hit = _DICT.get(key)
    if hit is not None:
        return hit
    # Decorative separators are often left in the preceding text node, for
    # example `<span>Last result</span> · BPF 0.95 · ...`.
    core = re.sub(r"^[·•]\s*", "", key)
    if core != key:
        hit = _DICT.get(core)
        if hit is not None:
            return key[: len(key) - len(core)] + hit
    for pattern, replacement in _PATTERN_LIST:
        match = pattern.fullmatch(core)
        if match:
            try:
                rendered = match.expand(replacement)
            except (re.error, IndexError):  # pragma: no cover - config guard
                return None
            return key[: len(key) - len(core)] + rendered
    return None


def translate_text(text: Any) -> Any:
    """Translate visible prose while leaving unknown technical strings intact."""
    if not isinstance(text, str) or not text.strip() or not is_arabic():
        return text

    direct = _translate_unit(text)
    if direct is not None:
        return _preserve_whitespace(text, direct)

    changed = False
    output: list[str] = []

    # First split at blank lines so each Markdown paragraph can be matched.
    paragraphs = re.split(r"(\n\s*\n)", text)
    for paragraph in paragraphs:
        if not paragraph or re.fullmatch(r"\n\s*\n", paragraph):
            output.append(paragraph)
            continue

        hit = _translate_unit(paragraph)
        if hit is not None:
            output.append(_preserve_whitespace(paragraph, hit))
            changed = True
            continue

        stripped = paragraph.strip()
        sentences = re.split(r"(?<=[.!?؟])\s+", stripped)
        if len(sentences) > 1:
            translated_sentences: list[str] = []
            sentence_changed = False
            for sentence in sentences:
                sentence_hit = _translate_unit(sentence)
                if sentence_hit is not None:
                    translated_sentences.append(sentence_hit)
                    sentence_changed = True
                else:
                    translated_sentences.append(sentence)
            if sentence_changed:
                output.append(_preserve_whitespace(paragraph, " ".join(translated_sentences)))
                changed = True
                continue

        # Markdown bullet lists and method notes benefit from line matching.
        lines = paragraph.split("\n")
        if len(lines) > 1:
            translated_lines: list[str] = []
            line_changed = False
            for line in lines:
                line_hit = _translate_unit(line)
                if line_hit is not None:
                    translated_lines.append(_preserve_whitespace(line, line_hit))
                    line_changed = True
                else:
                    translated_lines.append(line)
            if line_changed:
                output.append("\n".join(translated_lines))
                changed = True
                continue

        output.append(paragraph)

    return "".join(output) if changed else text


def translate_markup(markup: Any) -> Any:
    """Translate text nodes inside a small HTML fragment, leaving tags alone."""
    if not isinstance(markup, str) or not markup.strip() or not is_arabic():
        return markup

    if "<" not in markup:
        return translate_text(markup)

    parts = re.split(r"(<[^>]*>)", markup)
    output: list[str] = []
    for part in parts:
        if part.startswith("<"):
            output.append(part)
            continue
        if not part.strip():
            output.append(part)
            continue
        decoded = html.unescape(part)
        translated = translate_text(decoded)
        if translated != decoded:
            output.append(_preserve_whitespace(part, translated))
        else:
            output.append(part)
    return "".join(output)


def option_label(value: Any) -> str:
    """Display label for a canonical selectable value."""
    if isinstance(value, str):
        if not is_arabic():
            return value
        return _OPTIONS.get(value) or translate_text(value)
    return str(value)


def page_label(page: str, *, arabic: bool | None = None) -> str:
    """Localise a navigation page.

    ``arabic`` is captured when the radio is built.  Streamlit's ``format_func``
    can also run outside a script run (for example while the testing harness
    serialises widget state), where session state is unavailable and the
    default language would otherwise leak into the rendered options.
    """
    if arabic is None:
        arabic = is_arabic()
    if not arabic:
        return page
    return _OPTIONS.get(page) or translate_text(page)


def table_value(value: Any) -> Any:
    """Translate a cell while keeping numbers, units and identifiers intact."""
    if not isinstance(value, str):
        return value
    if not is_arabic():
        return value
    key = value.strip()
    if key in _OPTIONS:
        return _OPTIONS[key]
    return translate_text(value)


def localise_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a display/export copy with Arabic headers and categorical cells."""
    if not is_arabic():
        return frame
    copy = frame.copy()
    copy.columns = [translate_text(str(column)) for column in copy.columns]
    for column in copy.columns:
        copy[column] = copy[column].map(table_value)
    if copy.index.name:
        copy.index.name = translate_text(str(copy.index.name))
    return copy


def _localise_chart_units(text: str) -> str:
    """Convert plotting units without touching placeholders or identifiers."""
    replacements = (
        ("degC", "°C"),
        ("m3/h", "م³/ساعة"),
        ("m2", "م²"),
        ("m3", "م³"),
    )
    for source, target in replacements:
        text = text.replace(source, target)
    return text


def _chart_text(text: str) -> str:
    translated = translate_text(text)
    if isinstance(translated, str) and translated != text:
        return translated
    if not is_arabic():
        return text

    # Legend names are composed at runtime in the chart builders.
    match = re.fullmatch(r"(Room|Outdoor) (sensible|latent)", text)
    if match:
        scope = _OPTIONS.get(match.group(1), match.group(1))
        kind = _OPTIONS.get(match.group(2), match.group(2))
        return f"{scope} {kind}"
    if text == "END":
        return "النهاية"
    if text.endswith(" sweep"):
        return f"مسار {translate_text(text[:-6])}"
    # Axis labels such as `50% RH` and `24 degC WB` are composed at runtime.
    match = re.fullmatch(r"(\d+(?:\.\d+)?)% RH", text)
    if match:
        return f"{match.group(1)}% رطوبة نسبية"
    match = re.fullmatch(r"(\d+(?:\.\d+)?) degC WB", text)
    if match:
        return f"{match.group(1)} °C رطبة"

    # Hover strings mix fixed labels with live placeholders.  Translate their
    # label segments and convert units while leaving %{...} tokens untouched.
    if "<br" in text or "<extra>" in text:
        pieces = re.split(r"(<br\s*/?>|<extra>.*?</extra>)", text)
        rendered: list[str] = []
        for piece in pieces:
            if not piece or piece.startswith("<"):
                rendered.append(piece)
                continue
            hit = _translate_unit(piece)
            if hit is not None:
                rendered.append(hit)
                continue
            local = _localise_chart_units(piece)
            local = re.sub(r"^State ", "الحالة ", local)
            local = re.sub(r"^Hour ", "الساعة ", local)
            local = re.sub(r"^Room ", "الغرفة ", local)
            local = re.sub(r"^Outdoor ", "الخارج ", local)
            local = re.sub(r"^Supply ", "الإمداد ", local)
            local = re.sub(r"^Valve ", "الصمام ", local)
            local = re.sub(r"^Sensible ", "محسوس ", local)
            local = re.sub(r"^Latent ", "كامن ", local)
            local = local.replace("Discharge T", "حرارة الطرد")
            local = local.replace(" outdoor", " خارجي")
            rendered.append(local)
        return "".join(rendered)
    return text


def localise_figure(figure: go.Figure) -> go.Figure:
    """Translate figure titles, legends, annotations and hover strings."""
    if not is_arabic():
        return figure

    local = go.Figure(figure)
    for trace in local.data:
        for attribute in ("name", "hovertemplate"):
            value = getattr(trace, attribute, None)
            if isinstance(value, str):
                try:
                    setattr(trace, attribute, _chart_text(value))
                except (ValueError, TypeError):
                    pass
        text = getattr(trace, "text", None)
        if isinstance(text, str):
            try:
                trace.text = _chart_text(text)
            except (ValueError, TypeError):
                pass
        elif isinstance(text, (list, tuple)):
            try:
                trace.text = [_chart_text(item) if isinstance(item, str) else item for item in text]
            except (ValueError, TypeError):
                pass

        # Categorical axes (for example the load-component breakdown) keep their
        # labels in the trace data rather than in axis.ticktext.
        for attribute in ("x", "y", "labels"):
            values = getattr(trace, attribute, None)
            if isinstance(values, (pd.Series, pd.Index)):
                values = values.tolist()
            elif hasattr(values, "tolist") and not isinstance(values, (str, bytes)):
                # Plotly normalises pandas columns to NumPy arrays internally.
                values = values.tolist()
            if isinstance(values, (list, tuple)) and any(
                isinstance(item, str) for item in values
            ):
                try:
                    setattr(
                        trace,
                        attribute,
                        [
                            _chart_text(item) if isinstance(item, str) else item
                            for item in values
                        ],
                    )
                except (ValueError, TypeError):
                    pass

        # Colour-bar captions live on the marker object, not on the axes.
        marker = getattr(trace, "marker", None)
        colorbar = getattr(marker, "colorbar", None) if marker is not None else None
        if colorbar is not None and getattr(colorbar.title, "text", None):
            try:
                colorbar.title.text = _chart_text(str(colorbar.title.text))
            except (ValueError, TypeError):
                pass

    layout = local.layout
    if getattr(layout.title, "text", None):
        layout.title.text = _chart_text(str(layout.title.text))
    if getattr(layout.legend.title, "text", None):
        layout.legend.title.text = _chart_text(str(layout.legend.title.text))
    for axis_name in ("xaxis", "yaxis", "xaxis2", "yaxis2", "xaxis3", "yaxis3"):
        axis = getattr(layout, axis_name, None)
        if axis is None:
            continue
        if getattr(axis.title, "text", None):
            axis.title.text = _chart_text(str(axis.title.text))
        ticktext = getattr(axis, "ticktext", None)
        if isinstance(ticktext, (list, tuple)):
            axis.ticktext = [
                _chart_text(item) if isinstance(item, str) else item for item in ticktext
            ]
        categoryarray = getattr(axis, "categoryarray", None)
        if isinstance(categoryarray, (list, tuple)) and any(
            isinstance(item, str) for item in categoryarray
        ):
            axis.categoryarray = [
                _chart_text(item) if isinstance(item, str) else item
                for item in categoryarray
            ]
    for annotation in getattr(layout, "annotations", ()) or ():
        if getattr(annotation, "text", None):
            annotation.text = _chart_text(str(annotation.text))
    return local


def translate_template(template: str, **values: Any) -> str:
    """Translate an f-string template and interpolate values afterwards."""
    return translate_text(template).format(**values)


class _LocalisedStreamlit:
    """Tiny proxy used by the page modules for direct Streamlit calls."""

    _TEXT_FUNCTIONS = {
        "caption",
        "error",
        "header",
        "info",
        "markdown",
        "subheader",
        "success",
        "text",
        "title",
        "warning",
        "write",
    }
    _LABEL_FUNCTIONS = {
        "checkbox",
        "color_picker",
        "download_button",
        "expander",
        "link_button",
        "multiselect",
        "number_input",
        "radio",
        "selectbox",
        "select_slider",
        "slider",
        "text_area",
        "text_input",
        "toggle",
    }

    def __getattr__(self, name: str) -> Any:
        attribute = getattr(st, name)
        if not callable(attribute):
            return attribute
        if name == "markdown":
            return self._markdown(attribute)
        if name in self._TEXT_FUNCTIONS:
            return self._text(attribute)
        if name in self._LABEL_FUNCTIONS:
            return self._labelled(attribute, name)
        if name == "tabs":
            return self._tabs(attribute)
        if name == "button":
            return self._button(attribute)
        if name == "metric":
            return self._metric(attribute)
        if name == "dataframe":
            return self._dataframe(attribute)
        return attribute

    @staticmethod
    def _translate_help(kwargs: dict[str, Any]) -> None:
        if isinstance(kwargs.get("help"), str):
            kwargs["help"] = translate_text(kwargs["help"])

    def _markdown(self, function: Callable) -> Callable:
        def wrapper(body: Any = "", *args: Any, **kwargs: Any):
            self._translate_help(kwargs)
            return function(translate_markup(body), *args, **kwargs)

        return wrapper

    def _text(self, function: Callable) -> Callable:
        def wrapper(body: Any = "", *args: Any, **kwargs: Any):
            self._translate_help(kwargs)
            if isinstance(body, str):
                body = translate_text(body)
            return function(body, *args, **kwargs)

        return wrapper

    def _labelled(self, function: Callable, name: str) -> Callable:
        def wrapper(label: Any, *args: Any, **kwargs: Any):
            if isinstance(label, str):
                label = translate_text(label)
            self._translate_help(kwargs)
            if is_arabic() and name in {
                "radio",
                "multiselect",
                "selectbox",
                "select_slider",
            }:
                previous = kwargs.get("format_func")
                if previous is None:
                    kwargs["format_func"] = option_label
                else:
                    def combined(value: Any, _previous: Callable = previous) -> str:
                        rendered = _previous(value)
                        return translate_text(rendered) if isinstance(rendered, str) else str(rendered)

                    kwargs["format_func"] = combined
            return function(label, *args, **kwargs)

        return wrapper

    def _button(self, function: Callable) -> Callable:
        def wrapper(label: Any, *args: Any, **kwargs: Any):
            if isinstance(label, str):
                label = translate_text(label)
            self._translate_help(kwargs)
            return function(label, *args, **kwargs)

        return wrapper

    def _tabs(self, function: Callable) -> Callable:
        def wrapper(labels: Any, *args: Any, **kwargs: Any):
            if isinstance(labels, (list, tuple)):
                labels = [translate_text(label) if isinstance(label, str) else label for label in labels]
            return function(labels, *args, **kwargs)

        return wrapper

    def _metric(self, function: Callable) -> Callable:
        def wrapper(label: Any, value: Any, *args: Any, **kwargs: Any):
            if isinstance(label, str):
                label = translate_text(label)
            self._translate_help(kwargs)
            return function(label, value, *args, **kwargs)

        return wrapper

    def _dataframe(self, function: Callable) -> Callable:
        def wrapper(data: Any, *args: Any, **kwargs: Any):
            if is_arabic() and isinstance(data, pd.DataFrame):
                data = localise_frame(data)
            return function(data, *args, **kwargs)

        return wrapper


st_ar = _LocalisedStreamlit()
