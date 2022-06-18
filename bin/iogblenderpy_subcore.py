#!/usr/bin/env python3
# Copyright 2022 Fabrica Software, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys

import iograft


class BlenderArgParser(argparse.ArgumentParser):
    """
    Special argument parser for handling receiving args from Blender. When
    executing a Python script in Blender via the "--python" flag, all args
    in sys.argv are available to the Python script (This includes Blender
    specific arguments that we do not want passed to our script.). To control
    which arguments are passed to ONLY the Python script, Blender does not
    try try to parse any arguments after a '--' delimeter in the args list.

    This BlenderArgParser checks for the '--' delimeter in the arg list and if
    found, only attempts to parse the args after that delimeter. If '--' is
    not found in the arg list, the full arg list is parsed. This allows this
    argument parser to be used in both the case where we are executing via
    the Blender executable AND when we are executing with Python directly.
    """
    def _get_argv_after_doubledash(self):
        try:
            # Get the subarray of args AFTER the '--' delimeter.
            delimeter_index = sys.argv.index("--")
            return sys.argv[delimeter_index + 1:]
        except ValueError:
            # No '--' found, return the original argv list.
            return sys.argv

    def parse_args(self):
        return super().parse_args(args=self._get_argv_after_doubledash())


def parse_args():
    parser = BlenderArgParser(
                description="Start an iograft subcore process in Blender")
    parser.add_argument("--core-address", dest="core_address", required=True)
    return parser.parse_args()


def StartSubcore(core_address):
    # Initialize iograft.
    iograft.Initialize()

    # Create the subcore object and listen for nodes to be processed. Use
    # the MainThreadSubcore to ensure that all nodes are executed in the
    # main thread.
    subcore = iograft.MainThreadSubcore(core_address)
    subcore.ListenForWork()

    # Uninitialize iograft.
    iograft.Uninitialize()


if __name__ == "__main__":
    args = parse_args()

    # Start the subcore.
    StartSubcore(args.core_address)
