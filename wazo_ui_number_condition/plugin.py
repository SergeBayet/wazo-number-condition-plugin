# Copyright 2026 Serge Bayet
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_ui.helpers.menu import register_flaskview
from wazo_ui.helpers.plugin import create_blueprint

from .view import NumberConditionView

number_condition = create_blueprint("number_condition", __name__)


class Plugin:
    def load(self, dependencies):
        core = dependencies["flask"]

        NumberConditionView.register(number_condition, route_base="/number_conditions")
        register_flaskview(number_condition, NumberConditionView)

        core.register_blueprint(number_condition)
