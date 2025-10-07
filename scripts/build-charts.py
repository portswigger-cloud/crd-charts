#!/usr/bin/env python
# this script pulls the referenced helm charts in helmfile.yaml and creates
# crd charts
import glob
import os
import shutil
import sys
import subprocess
from typing import NamedTuple, Iterable, Any
from yaml import safe_load, safe_dump


class Release(NamedTuple):
    name: str
    chart: str
    version: str
    oci: bool
    url: str
    nested_charts: bool


def run(args: list[str]):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"invocation failed: {' '.join(args)}")
        for line in result.stdout.splitlines():
            print(f"stdout: {line}")
        for line in result.stderr.splitlines():
            print(f"stderr: {line}")
    else:
        print(f"successfully ran {' '.join(args)}")


def is_nested_chart(release: dict[str, Any]) -> bool:
    for hook in release.get("hooks", []):
        for args in hook.get("args", []):
            if "--nested-chart" in args:
                return True
    return False

class HelmFile(object):
    def __init__(self, path: str):
        with open(path, "r") as f:
            data = safe_load(f)
        self.reps = {x["name"]: (x["url"], x.get("oci") == True) for x in data["repositories"]}

        def release(r: dict[str, Any]) -> Release:
            repo, chart = r["chart"].split("/")
            url, oci = self.reps[repo]
            url = url.rstrip("/")
            return Release(
                name=r["name"],
                chart=r["chart"],
                version=r["version"],
                oci=oci,
                url=url,
                nested_charts=is_nested_chart(r)
            )

        self.releases = tuple(release(r) for r in data["releases"])

    def releases(self) -> Iterable[Release]:
        return iter(self.releases)


def pull_and_extract(release: Release) -> str:
    repo, chart = release.chart.split("/")
    d = f"./work/{repo}-{chart}"
    args = ["helm", "pull", "--version", release.version, "--untar", "--untardir", d]
    if release.oci:
        run(args + [f"oci://{release.url}/{chart}"])
    else:
        run(args + ["--repo", release.url, chart])
    return d

def create_chart_yaml(name: str, version: str, path: str):
    chart_yaml = {
        "apiVersion": "v2",
        "name": name,
        "type": "application",
        "version": version,
        "appVersion": "0.0.0",
    }

    os.makedirs(path, 0o755, exist_ok=True)
    with open(f"{path}/Chart.yaml", "w") as chart_yaml_file:
        safe_dump(chart_yaml, chart_yaml_file)

def filter_direct_descendents(paths: Iterable[str]) -> Iterable[str]:
    """Filter out paths that are prefixes of other paths in the input."""
    sorted_paths = sorted(paths)
    result = []
    for path in sorted_paths:
        # Check if any previously seen path is a prefix of the current path
        if not any(path.startswith(seen) for seen in result):
            result.append(path)
    return result


def find_and_copy_files(staging_dir: str, output_dir: str, nested_charts: bool):
    if nested_charts:
        for path in glob.glob(f"{staging_dir}/charts/*/crds", recursive=True):
            shutil.copytree(path, output_dir)
    else:
        for path in glob.glob(f"{staging_dir}/**/crds", recursive=True):
            shutil.copytree(path, output_dir, dirs_exist_ok=True)


def create_crd_chart(release: Release, staging_dir: str, output_dir: str, nested_charts: bool):
    print(f"creating a crd_chart for {release}")
    repo, chart = release.chart.split("/")
    crd_chart_name = f"{repo}-{chart}-crds"
    create_chart_yaml(name=crd_chart_name, version=release.version, path=f"{output_dir}/{crd_chart_name}")
    find_and_copy_files(staging_dir, f"{output_dir}/{crd_chart_name}/templates", nested_charts)


def main():
    helmfile = HelmFile(sys.argv[1])
    for release in HelmFile.releases(helmfile):
        staging_dir = pull_and_extract(release)
        repo, chart = release.chart.split("/")
        #staging_dir = f"./work/{repo}-{chart}/{chart}"
        create_crd_chart(release, staging_dir, "./charts2", release.nested_charts)


if __name__ == "__main__":
    main()
