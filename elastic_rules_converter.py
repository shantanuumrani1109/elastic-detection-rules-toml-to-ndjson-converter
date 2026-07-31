#!/usr/bin/env python3
"""
elastic_rules_converter.py
---------------------------
Standalone, parameterized command-line tool that converts Elastic detection-rules
TOML files into Kibana-importable NDJSON — either as one combined file per category,
or as one .ndjson per individual rule.

It is a thin wrapper around Elastic's own, officially documented CLI command
(`detection_rules export-rules-from-repo`) — it does not re-implement rule parsing
or validation itself, so results always match what Elastic's tooling produces.

REQUIREMENTS (on the machine actually running the export):
    - A local clone of https://github.com/elastic/detection-rules  (default: ./detection-rules)
    - Poetry installed, with `poetry install` already run inside that clone
      (see the notebook / README for the one-time setup, or use the prebuilt .exe
      described in the README, which bundles this environment via CI)

USAGE EXAMPLES
    # One combined NDJSON for every Windows rule
    python elastic_rules_converter.py --category windows --mode single

    # One NDJSON per rule, for the Linux category, zipped when done
    python elastic_rules_converter.py --category linux --mode individual --zip

    # Every rule, every platform, combined into one file
    python elastic_rules_converter.py --category rules --mode single --output all_rules.ndjson --zip
"""

import argparse
import os
import shutil
import subprocess
import sys


def find_toml_files(base_dir):
    """Yield the full path of every .toml file under base_dir."""
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".toml"):
                yield os.path.join(root, file)


def run_cli(repo_dir, args):
    """Run `poetry run python -m detection_rules ...` inside repo_dir."""
    cmd = ["poetry", "run", "python", "-m", "detection_rules"] + args
    return subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)


def export_single(repo_dir, rules_subdir, output_file):
    """Export an entire category directory into one combined .ndjson file."""
    output_file = os.path.abspath(output_file)
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

    print(f"Exporting all rules under '{rules_subdir}' -> {output_file}")
    result = run_cli(repo_dir, ["export-rules-from-repo", "-d", rules_subdir, "-o", output_file])

    if result.returncode != 0:
        print("Export failed:")
        print(result.stderr)
        sys.exit(1)

    print(f"Export succeeded -> {output_file}")
    return output_file


def export_individual(repo_dir, rules_subdir, output_dir):
    """Export every .toml rule in a category directory as its own .ndjson file."""
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    rules_full_dir = os.path.join(repo_dir, rules_subdir)
    success, failed = 0, 0

    for rule_path in find_toml_files(rules_full_dir):
        rel_rule_path = os.path.relpath(rule_path, repo_dir)
        output_name = os.path.basename(rule_path).replace(".toml", ".ndjson")
        output_path = os.path.join(output_dir, output_name)

        print(f"Exporting {os.path.basename(rule_path)}...")
        result = run_cli(repo_dir, ["export-rules-from-repo", "-f", rel_rule_path, "-o", output_path])

        if result.returncode == 0:
            success += 1
        else:
            failed += 1
            print(f"  Failed: {rel_rule_path}")
            print(f"  {result.stderr.strip()}")

    print()
    print("=" * 60)
    print(f"Exported : {success}")
    print(f"Failed   : {failed}")
    print("=" * 60)
    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="Convert Elastic detection-rules TOML files into Kibana-importable NDJSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--repo", default="detection-rules",
        help="Path to the cloned elastic/detection-rules repository (default: ./detection-rules)",
    )
    parser.add_argument(
        "--category", default="windows",
        help="Rule category/subfolder under rules/ to export: windows, linux, macos, network, cloud, etc. "
             "Use 'rules' to target every platform at once.",
    )
    parser.add_argument(
        "--mode", choices=["single", "individual"], default="individual",
        help="'single' = one combined .ndjson for the whole category. "
             "'individual' = one .ndjson per rule (default).",
    )
    parser.add_argument(
        "--output", default=None,
        help="Output file (mode=single) or output directory (mode=individual). "
             "Defaults to '<category>_rules.ndjson' or '<category>_NDJSON/'.",
    )
    parser.add_argument(
        "--zip", action="store_true",
        help="Also zip the result when finished.",
    )
    args = parser.parse_args()

    rules_subdir = "rules" if args.category == "rules" else os.path.join("rules", args.category)
    rules_full_dir = os.path.join(args.repo, rules_subdir)

    if not os.path.isdir(rules_full_dir):
        print(f"Could not find '{rules_full_dir}'. Check --repo and --category.")
        sys.exit(1)

    if args.mode == "single":
        output_file = args.output or f"{args.category}_rules.ndjson"
        result_path = export_single(args.repo, rules_subdir, output_file)
        if args.zip:
            base = os.path.splitext(result_path)[0]
            zip_path = shutil.make_archive(base, "zip", os.path.dirname(result_path), os.path.basename(result_path))
            print(f"Zipped -> {zip_path}")
    else:
        output_dir = args.output or f"{args.category}_NDJSON"
        result_dir = export_individual(args.repo, rules_subdir, output_dir)
        if args.zip:
            zip_path = shutil.make_archive(result_dir, "zip", result_dir)
            print(f"Zipped -> {zip_path}")


if __name__ == "__main__":
    main()
