# Copyright 2026 Serge Bayet
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import render_template
from flask_babel import lazy_gettext as l_

from wazo_ui.helpers.classful import LoginRequiredView
from wazo_ui.helpers.menu import menu_item


class NumberConditionView(LoginRequiredView):
    @menu_item(
        ".ipbx.call_management.number_conditions",
        l_("Number Conditions"),
        order=2,
        icon="filter",
        multi_tenant=True,
    )
    def index(self):
        return render_template("number_condition/index.html")
