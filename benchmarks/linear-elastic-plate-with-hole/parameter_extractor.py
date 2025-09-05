import json
import os
from snakemake_report_plugin_metadata4ing.interfaces import (
    ParameterExtractorInterface,
)
import yaml
import re

class ParameterExtractor(ParameterExtractorInterface):
    def extract_params(self, rule_name: str, file_path: str) -> dict:
        results = {}
        file_name = os.path.basename(file_path)
        if (
            file_name.startswith("parameters_")
            and file_name.endswith(".json")
            and (rule_name.startswith("postprocess_") or rule_name.startswith("run_"))
        ):
            results.setdefault(rule_name, {}).setdefault("has parameter", [])
            with open(file_path) as f:
                data = json.load(f)
            for key, val in data.items():
                if isinstance(val, dict):
                    results[rule_name]["has parameter"].append({key: {
                        "value": val["value"],
                        "unit": f"units:{val["unit"] }" if "unit" in val else None,
                        "json-path": f"/{key}/value",
                        "data-type": self._get_type(val["value"]),
                    }})
                else:
                    results[rule_name]["has parameter"].append({key: {
                        "value": val,
                        "unit": None,
                        "json-path": f"/{key}",
                        "data-type": self._get_type(val),
                    }})
        elif (
            file_name.startswith("solution_")
            and file_name.endswith(".json")
            and (rule_name.startswith("postprocess_") or rule_name.startswith("run_"))
        ):
            results.setdefault(rule_name, {}).setdefault("investigates", [])
            with open(file_path) as f:
                data = json.load(f)
            for key, val in data.items():
                if key == "max_von_mises_stress_nodes":
                    results[rule_name]["investigates"].append({key: {
                        "value": val,
                        "unit": None,
                        "json-path": f"/{key}",
                        "data-type": "schema:Float",
                    }})
        return results

    def extract_tools(self, rule_name: str, env_file_content: str,) -> dict:
        results = {}
        parsed = yaml.safe_load(env_file_content)
        dependencies = parsed.get("dependencies", [])
        targets = {"fenics-dolfinx", "KratosMultiphysics-all"}
    
        for dep in dependencies:
            if isinstance(dep, str):
                match = re.match(r'^([a-zA-Z0-9_\-]+)([=<>!].*)?$', dep)
                if match:
                    name, version = match.groups()
                    if name in targets:
                        results[name] = version if version else None
            elif isinstance(dep, dict):
                for _, pkgs in dep.items():
                    for pkg in pkgs:
                        match = re.match(r'^([a-zA-Z0-9_\-]+)([=<>!].*)?$', pkg)
                        if match:
                            name, version = match.groups()
                            if name in targets:
                                results[name] = version if version else None
    
        return results

    def _get_type(self, val):
        if isinstance(val, float):
            return "schema:Float"
        elif isinstance(val, int):
            return "schema:Integer"
        elif isinstance(val, str):
            return "schema:Text"
        return None
