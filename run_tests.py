#!/usr/bin/env python3
"""
Test runner script for Mockachu
Provides various testing options and reporting
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", coverage=True, verbose=True, parallel=False):
    """Run tests with specified options"""

    cmd = ["python", "-m", "pytest"]

    # Test selection
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "generators":
        cmd.extend(["-m", "generator"])
    elif test_type == "api":
        cmd.extend(["-m", "api"])
    elif test_type == "ui":
        cmd.extend(["-m", "ui"])
    elif test_type != "all":
        cmd.extend([f"tests/test_{test_type}.py"])

    # Coverage
    if coverage:
        cmd.extend([
            "--cov=mockachu",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])

    # Verbosity
    if verbose:
        cmd.append("-v")

    # Parallel execution
    if parallel:
        cmd.extend(["-n", "auto"])

    # Add tests directory
    cmd.append("tests/")

    print(f"Running command: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=Path(__file__).parent)


def main():
    parser = argparse.ArgumentParser(
        description="Run Mockachu tests")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "generators", "api", "ui",
                 "person_generator", "it_generator", "calendar_generator", "string_generator"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )

    args = parser.parse_args()

    result = run_tests(
        test_type=args.type,
        coverage=not args.no_coverage,
        verbose=not args.quiet,
        parallel=args.parallel
    )

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
