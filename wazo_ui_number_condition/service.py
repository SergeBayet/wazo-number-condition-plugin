# Copyright 2026 Serge Bayet
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
import tempfile
import threading
import uuid
from pathlib import Path


class NumberConditionService:
    _storage_directory = Path("/var/lib/wazo-ui/number-condition")
    _storage_path = _storage_directory / "rules.json"
    _legacy_storage_path = _storage_directory / "rule.json"

    def __init__(self):
        self._lock = threading.Lock()

    def list(self, **_kwargs):
        with self._lock:
            rules = self._read_rules()
        return {"items": rules, "total": len(rules)}

    def get(self, rule_id):
        with self._lock:
            return self._find_rule(self._read_rules(), rule_id).copy()

    def create(self, rule):
        with self._lock:
            rules = self._read_rules()
            rule["id"] = str(uuid.uuid4())
            rules.append(rule)
            self._write_rules(rules)
        return rule

    def update(self, rule):
        with self._lock:
            rules = self._read_rules()
            existing_rule = self._find_rule(rules, rule["id"])
            existing_rule.clear()
            existing_rule.update(rule)
            self._write_rules(rules)
        return rule

    def delete(self, rule_id):
        with self._lock:
            rules = self._read_rules()
            rule = self._find_rule(rules, rule_id)
            rules.remove(rule)
            self._write_rules(rules)

    def _read_rules(self):
        if self._storage_path.exists():
            with self._storage_path.open(encoding="utf-8") as storage_file:
                routers = json.load(storage_file)
            migrated_routers = [self._migrate_router(router) for router in routers]
            if migrated_routers != routers:
                self._write_rules(migrated_routers)
            return migrated_routers

        if self._legacy_storage_path.exists():
            with self._legacy_storage_path.open(encoding="utf-8") as storage_file:
                legacy_rule = json.load(storage_file)
            legacy_rule["id"] = str(uuid.uuid4())
            routers = [self._migrate_router(legacy_rule)]
            self._write_rules(routers)
            return routers

        return []

    def _write_rules(self, rules):
        self._storage_directory.mkdir(mode=0o750, parents=True, exist_ok=True)
        file_descriptor, temporary_path = tempfile.mkstemp(
            dir=self._storage_directory,
            prefix=".rules-",
            suffix=".json",
            text=True,
        )
        try:
            with os.fdopen(file_descriptor, "w", encoding="utf-8") as storage_file:
                json.dump(rules, storage_file, ensure_ascii=False, indent=2)
                storage_file.write("\n")
            os.chmod(temporary_path, 0o640)
            os.replace(temporary_path, self._storage_path)
        finally:
            if os.path.exists(temporary_path):
                os.unlink(temporary_path)

    def _find_rule(self, rules, rule_id):
        for rule in rules:
            if rule["id"] == rule_id:
                return rule
        raise KeyError(rule_id)

    def _migrate_router(self, router):
        if "rules" in router:
            return router

        return {
            "id": router["id"],
            "name": router["name"],
            "enabled": router.get("enabled", True),
            "rules": [
                {
                    "regex": router["regex"],
                    "destination": router["destination"],
                }
            ],
            "fallback_destination": {"type": "hangup", "cause": "normal"},
        }
