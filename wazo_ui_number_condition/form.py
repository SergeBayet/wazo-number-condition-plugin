# Copyright 2026 Serge Bayet
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from flask_babel import lazy_gettext as l_
from wtforms.fields import BooleanField, FieldList, FormField, StringField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

from wazo_ui.helpers.destination import DestinationField
from wazo_ui.helpers.form import BaseForm


def validate_regex(_form, field):
    try:
        re.compile(field.data)
    except re.error as error:
        raise ValidationError(l_("Invalid regular expression: %(error)s", error=error)) from error


class NumberConditionRuleForm(BaseForm):
    regex = StringField(
        l_("Caller number regular expression"),
        validators=[InputRequired(), Length(max=255), validate_regex],
        description=l_("Example: ^\\+32"),
    )
    destination = DestinationField(destination_label=l_("Destination"))


class NumberConditionForm(BaseForm):
    name = StringField(l_("Name"), validators=[InputRequired(), Length(max=128)])
    rules = FieldList(FormField(NumberConditionRuleForm), min_entries=1)
    fallback_destination = DestinationField(
        destination_label=l_("Default destination")
    )
    enabled = BooleanField(l_("Enabled"), default=True)
    submit = SubmitField(l_("Save"))
