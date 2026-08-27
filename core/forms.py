from django import forms


class StyledFormMixin:
    """Applies ProjectFlow widget classes and removes the default label colon.

    Include this mixin on every form so fields render with the design
    system's .form-input / .form-select / .form-textarea / .form-checkbox-list
    classes even when a widget is left unstyled, and so labels render without
    Django's default ':' suffix.
    """

    # Ordered so subclasses are matched before their base classes.
    widget_classes = (
        (forms.CheckboxSelectMultiple, 'form-checkbox-list'),
        (forms.SelectMultiple, 'form-select'),
        (forms.Select, 'form-select'),
        (forms.Textarea, 'form-textarea'),
        (forms.EmailInput, 'form-input'),
        (forms.PasswordInput, 'form-input'),
        (forms.DateInput, 'form-input'),
        (forms.DateTimeInput, 'form-input'),
        (forms.TimeInput, 'form-input'),
        (forms.NumberInput, 'form-input'),
        (forms.URLInput, 'form-input'),
        (forms.TextInput, 'form-input'),
        (forms.ClearableFileInput, 'form-file-input'),
        (forms.FileInput, 'form-file-input'),
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            self._apply_widget_class(field.widget)

    def _apply_widget_class(self, widget):
        for klass, css_class in self.widget_classes:
            if isinstance(widget, klass):
                existing = widget.attrs.get('class', '')
                if css_class not in existing.split():
                    widget.attrs['class'] = f"{existing} {css_class}".strip()
                break
