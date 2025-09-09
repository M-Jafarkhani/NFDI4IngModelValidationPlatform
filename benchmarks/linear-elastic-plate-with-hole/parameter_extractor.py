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
        targets = {"kratosmultiphysics-all", "fenics-dolfinx"}
        envs = self._list_conda_envs()
        results = {}

        for _, env_path in envs.items():
            try:
                pkgs = self._get_packages(env_path)
            except Exception as e:
                # skip environments that cannot be read
                continue

            found = targets.intersection(pkgs.keys())
            for pkg in found:
                results[pkg] = pkgs[pkg]

        return results

    def _get_type(self, val):
        if isinstance(val, float):
            return "schema:Float"
        elif isinstance(val, int):
            return "schema:Integer"
        elif isinstance(val, str):
            return "schema:Text"
        return None
    
    def _list_conda_envs(self):
        """Return a dict {env_name: env_path} of all conda environments."""
        result = subprocess.run(
            ["conda", "env", "list", "--json"],
            capture_output=True, text=True, check=True
        )
        envs_info = json.loads(result.stdout)
        return {path.split("/")[-1]: path for path in envs_info["envs"]}

    def _get_packages(self,env_path):
        """Return dict {package: version} for given env path."""
        result = subprocess.run(
            ["conda", "list", "--prefix", env_path, "--json"],
            capture_output=True, text=True, check=True
        )
        return {pkg["name"]: pkg["version"] for pkg in json.loads(result.stdout)}