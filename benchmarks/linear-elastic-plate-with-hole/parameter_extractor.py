import json
import os
from snakemake_report_plugin_metadata4ing.interfaces import (
    ParameterExtractorInterface,
)
import subprocess

class ParameterExtractor(ParameterExtractorInterface):
    def extract_params(self, rule_name: str, file_path: str) -> dict:
        results = {}
        file_name = os.path.basename(file_path)
        if (
            file_name.startswith("summary")
            and rule_name == "summary"
        ):
            with open(file_path) as f:
                data = json.load(f)
            for experiment in data:
                config = experiment['configuration']
                results.setdefault(config, {})
                results[config].setdefault('has parameter', [])
                results[config].setdefault('investigates', [])
                for key, val in experiment['parameters'].items():
                    if isinstance(val, dict):
                        results[config]["has parameter"].append({key: {
                            "value": val["value"],
                            "unit": self._get_unit(key),
                            "json-path": f"/{key}/value",
                            "data-type": self._get_type(val["value"]),
                        }})
                    else:
                        results[config]["has parameter"].append({key: {
                            "value": val,
                            "unit": None,
                            "json-path": f"/{key}",
                            "data-type": self._get_type(val),
                        }})
                for key, val in experiment['metrics'].items():
                    if isinstance(val, dict):
                        results[config]["investigates"].append({key: {
                            "value": val["value"],
                            "unit": self._get_unit(key),
                            "json-path": f"/{key}/value",
                            "data-type": self._get_type(val["value"]),
                        }})
                    else:
                        results[config]["investigates"].append({key: {
                            "value": val,
                            "unit": None,
                            "json-path": f"/{key}",
                            "data-type": self._get_type(val),
                        }})        
        return results

    def extract_tools(self, rule_name: str, env_file_content: str,) -> dict:
        command = subprocess.run(
            ["conda", "list", "--json"],
            capture_output=True,
            text=True
        )
        print(command.stdout)
        packages = json.loads(command.stdout)
        targets = ["fenics-dolfinx", "KratosMultiphysics-all"]
        results = {}
        for pkg_name in targets:
            pkg = next((p for p in packages if p["name"] == pkg_name), None)
            if pkg:
                results[pkg_name] = pkg["version"]
        return results

    def _get_unit(self, name: str):
        return {
            "young-modulus": "units:PA",
            "load": "units:MegaPA",
            "length": "units:m",
            "radius": "units:m",
            "element-size": "units:m",
        }.get(name)

    def _get_type(self, val):
        if isinstance(val, float):
            return "schema:Float"
        elif isinstance(val, int):
            return "schema:Integer"
        elif isinstance(val, str):
            return "schema:Text"
        return None
