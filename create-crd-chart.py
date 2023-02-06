#!/usr/bin/env python3
import argparse
import pathlib
import yaml


def create_chart_yaml(name: str, version: str, path: str):
    chart_yaml = {
        "apiVersion": "v2",
        "name": name,
        "type": "application",
        "version": version,
        "appVersion": "0.0.0",
    }

    with open(f"{path}/Chart.yaml", "w") as chart_yaml_file:
        yaml.safe_dump(chart_yaml, chart_yaml_file)


def main(chart: str, version: str):
    chart_kebab = chart.replace("/", "-")

    crds_chart_name = f"{chart_kebab}-crds"

    chart_path = f"./charts/{crds_chart_name}"

    pathlib.Path(chart_path).mkdir(parents=True, exist_ok=True)

    create_chart_yaml(name=crds_chart_name, version=version, path=chart_path)

    print(f"{chart} CRDs skeleton created")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="Creates a helm chart containing crds from other helm charts",
    )

    parser.add_argument(
        "--chart",
        type=str,
        help="Helm chart to fetch crds from (format repo/chart or chart)",
    )
    parser.add_argument("--version", type=str, help="Helm chart version")

    args = parser.parse_args()
    main(chart=args.chart, version=args.version)
