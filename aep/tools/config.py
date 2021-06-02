#!/usr/bin/env python3
""" Handle worker config"""

import argparse
import os
import sys
from pathlib import Path
from typing import Text, Tuple, Dict, List

import caep
from pkg_resources import resource_string

import aep.tools.libs.data

CONFIG_ID = "aep"
CONFIG_NAME = "config"


def parseargs() -> argparse.Namespace:
    """ Parse arguments """

    parser = argparse.ArgumentParser(
        "aep config",
        epilog="""
    show - Print default config

    user - Copy default config to {0}/{1}

    system - Copy default config to /etc/{1}

""".format(
            caep.get_config_dir(CONFIG_ID), CONFIG_NAME
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("action", nargs=1, choices=["show", "user", "system"])

    return parser.parse_args()


def default_config() -> Text:
    "Get content of default config "
    return resource_string("aep.tools", "etc/{}".format(CONFIG_NAME)).decode(
        "utf-8"
    )


def save_config(filename: Text) -> None:
    """ Save config to specified filename """
    if os.path.isfile(filename):
        sys.stderr.write(f"Config already exists: {filename}\n")
        sys.exit(1)

    try:
        with open(filename, "w") as f:
            f.write(default_config())
    except PermissionError as err:
        sys.stderr.write("{}\n".format(err))
        sys.exit(2)

    print(f"Config copied to {filename}")


def split_arg(argument, delimiter=","):
    """ Split argument with delimiter and return list """
    if not argument:
        return []

    return [arg.strip() for arg in argument.split(delimiter) if arg]


def common_args(description: Text) -> argparse.ArgumentParser:
    """ Parse default arguments """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "--config-dir",
        default=caep.get_config_dir("aep"),
        help="Default config dir with configurations for scio and plugins",
    )

    parser.add_argument(
        "--data-dir", type=Path, default=".", help="Root directory of data files"
    )
    parser.add_argument(
        "--promise-descriptions",
        type=Path,
        default="promise_descriptions.csv",
        help="Promise description file (CSV)",
    )
    parser.add_argument(
        "--conditions", type=Path, default="conditions.csv", help="Conditions (CSV)"
    )
    parser.add_argument(
        "--technique-promises",
        type=Path,
        default="technique_promises.json",
        help="Path for techniques.json. "
        "Supports data relative to root data directory and absolute path",
    )

    return parser


def handle_args(parser: argparse.ArgumentParser, tool: Text) -> argparse.Namespace:
    args = caep.config.handle_args(parser, "aep", "config", tool)

    if not args.technique_promises:
        sys.stderr.write("--technique-promises must be specified\n")
        sys.exit(1)

    return args


def fatal(message: Text, exit_code: int = 1) -> None:
    """ Print message to stderr and exit with status code """
    sys.stderr.write(message.strip() + "\n")
    sys.exit(exit_code)


def file_exists_or_die(filename, message):
    """
    Expand filename and check if it exsists.
    Return expanded filename on success, otherwise it exits
    """
    filename = filename.expanduser().resolve()
    if not filename.is_file():
        fatal(f"{message}: {filename}\n")

    return filename


def read_technique_promises(args: argparse.Namespace):
    """ Wrapper for data.read_data() that uses parameters from config and verifies whether the file exists """

    # Resolve files relative to args.data_dir and exit if they do not exist
    return aep.tools.libs.data.read_technique_promises(
        tech_promises_file=file_exists_or_die(
            args.data_dir / args.technique_promises,
            "technique-promises file does not exist",
        ),
        promise_descriptions_file=file_exists_or_die(
            args.data_dir / args.promise_descriptions,
            "promise-descripion file does not exist",
        ),
        conditions_file=file_exists_or_die(
            args.data_dir / args.conditions, "promise-descripion file does not exist"
        ),
    )


def read_data(args: argparse.Namespace) -> Tuple[Dict, List[Text]]:
    """ Wrapper for data.read_data() that uses parameters from config and verifies whether the file exists """

    techniques = aep.tools.libs.data.read_tech_bundle(
        file_exists_or_die(
            args.data_dir / args.technique_bundle,
            "technique-bundle does not exist",
        ),
        include_tool_techniques=args.include_tools,
    )

    technique_promises, expand_map, ok = read_technique_promises(args)

    if not ok:
        fatal(f"One or more technique in {args.technique_promises} are missing a required field")

    techniques = aep.tools.libs.data.preprocess_techniques(
        technique_promises,
        expand_map,
        techniques)

    return technique_promises, techniques


def main() -> None:
    "main function"
    args = parseargs()

    if "show" in args.action:
        print(default_config())

    if "user" in args.action:
        config_dir = caep.get_config_dir(CONFIG_ID, create=True)
        save_config(os.path.join(config_dir, CONFIG_NAME))

    if "system" in args.action:
        save_config("/etc/{}".format(CONFIG_NAME))


if __name__ == "__main__":
    main()
