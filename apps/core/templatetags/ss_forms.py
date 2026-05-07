"""Template helpers for rendering forms with Tailwind classes."""
from django import template
from django.forms.widgets import (
    CheckboxInput,
    CheckboxSelectMultiple,
    FileInput,
    RadioSelect,
    Select,
    SelectMultiple,
    Textarea,
    ClearableFileInput,
)

register = template.Library()


_BASE_INPUT = (
    "w-full rounded-lg border border-slate-300 dark:border-slate-600 "
    "bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 "
    "px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-tropical "
    "focus:border-transparent placeholder-slate-400"
)
_CHECKBOX = "h-4 w-4 text-tropical border-slate-300 rounded focus:ring-tropical"
_FILE = (
    "block w-full text-sm text-slate-700 dark:text-slate-200 "
    "file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 "
    "file:text-sm file:font-medium file:bg-tropical file:text-white "
    "hover:file:bg-tropical-dark"
)


@register.filter(name="ss_field")
def ss_field(field):
    """Re-render a bound form field with appropriate Tailwind classes."""
    widget = field.field.widget
    cls = field.css_classes()
    existing = widget.attrs.get("class", "")

    if isinstance(widget, (CheckboxInput,)):
        new_cls = f"{_CHECKBOX} {existing}".strip()
    elif isinstance(widget, (ClearableFileInput, FileInput)):
        new_cls = f"{_FILE} {existing}".strip()
    elif isinstance(widget, (CheckboxSelectMultiple, RadioSelect)):
        new_cls = existing
    elif isinstance(widget, (Select, SelectMultiple)):
        new_cls = f"{_BASE_INPUT} {existing}".strip()
    elif isinstance(widget, Textarea):
        new_cls = f"{_BASE_INPUT} {existing}".strip()
    else:
        new_cls = f"{_BASE_INPUT} {existing}".strip()

    widget.attrs["class"] = new_cls
    return field.as_widget()


@register.filter(name="add_class")
def add_class(field, css):
    """Add additional CSS classes to a bound field's widget."""
    existing = field.field.widget.attrs.get("class", "")
    field.field.widget.attrs["class"] = f"{existing} {css}".strip()
    return field.as_widget()
