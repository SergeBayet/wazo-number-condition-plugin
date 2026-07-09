# Copyright 2026 Serge Bayet
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import flash
from flask_babel import gettext as _
from flask_babel import lazy_gettext as l_
from flask_classful import route

from wazo_ui.helpers.menu import menu_item
from wazo_ui.helpers.view import BaseIPBXHelperView

from .form import NumberConditionForm


class NumberConditionView(BaseIPBXHelperView):
    form = NumberConditionForm
    resource = "number condition"

    @menu_item(
        ".ipbx.call_management.number_conditions",
        l_("Number Conditions"),
        order=2,
        icon="filter",
        multi_tenant=True,
    )
    def index(self):
        return super().index()

    def post(self):
        form = self.form()
        if not self._validate_form(form):
            return self._index(form)

        self.service.create(form.to_dict())
        flash(_("Number condition has been created."), "success")
        return self._redirect_for("index")

    @route("/put/<id>", methods=["POST"])
    def put(self, id):
        form = self.form()
        if not self._validate_form(form):
            return self._get(id, form)

        rule = form.to_dict()
        rule["id"] = id
        self.service.update(rule)
        flash(_("Number condition has been updated."), "success")
        return self._redirect_for("index")

    def _validate_form(self, form):
        valid = form.csrf_token.validate(form)
        valid = form.name.validate(form) and valid
        valid = form.regex.validate(form) and valid

        destination_form = form.destination.form
        destination_type = destination_form.type.data
        if not destination_type:
            destination_form.type.errors.append(_("A destination is required."))
            valid = False

        if not valid:
            self._flash_form_errors(form)
        return valid

    def _flash_form_errors(self, form):
        for field in (form.csrf_token, form.name, form.regex):
            for error in field.errors:
                flash(f"{field.label.text} - {error}", "error")

        destination_form = form.destination.form
        for error in destination_form.type.errors:
            flash(f"{destination_form.type.label.text} - {error}", "error")
