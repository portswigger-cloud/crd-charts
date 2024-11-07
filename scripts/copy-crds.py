#!/usr/bin/env python3
import argparse
import glob
import shutil


def main(chart: str, download_path: str, nested_chart: bool):
    chart_name = chart.split("/", maxsplit=1)[-1]

    chart_kebab = chart.replace("/", "-")

    crds_chart_name = f"{chart_kebab}-crds"

    chart_templates_path = f"./charts/{crds_chart_name}/templates"

    staged_chart_dir = f"{download_path}/{chart_name}"
    if nested_chart:
        for path in glob.glob(f"{staged_chart_dir}/charts/*/crds", recursive=True):
            shutil.copytree(path, chart_templates_path)
    else:
        for path in glob.glob(f"{staged_chart_dir}/**/crds", recursive=True):
            shutil.copytree(path, chart_templates_path)


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

    parser.add_argument(
        "--download-path",
        type=str,
        help="Path that the Helm chart has been downloaded to",
    )

    parser.add_argument(
        "--nested-chart",
        type=bool,
        help="Set to true if CRDs are stored in nested helm chart",
        default=False
    )

    args = parser.parse_args()
    main(chart=args.chart, download_path=args.download_path, nested_chart=args.nested_chart)
