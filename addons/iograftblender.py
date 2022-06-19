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

import atexit
import os
import queue
import subprocess
import sys

import bpy
import iograft

bl_info = {
    "name": "iograft Operators",
    "description": "Operators for using iograft interactively in Blender.",
    "author": "Fabrica Software, LLC",
    "version": (1, 0),
    "blender": (2, 92, 0),
    "location": "3D View > Tool",
    "support": "COMMUNITY",
    "doc_url": "https://github.com/iograft/iograft-blender",
    "category": "Development"
}

IOGRAFT_BLENDER_CORE_NAME = "blender"


@atexit.register
def _ensureUninitialized():
    """
    Ensure that iograft has been cleaned up and doesn't prevent Blender
    from exiting.
    """
    if iograft.IsInitialized():
        iograft.Uninitialize()


class IograftPanel(bpy.types.Panel):
    """
    Creates a panel for controlling an iograft session in Blender.
    """
    bl_label = "iograft"
    bl_idname = "VIEW3D_PT_iograft_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("iograft.start")

        row = layout.row()
        row.operator("iograft.stop")

        row = layout.row()
        row.operator("iograft.launch_ui")


class BlenderMainThreadCore(iograft.MainThreadCore):
    """
    TODO: This class is temporary pending a change in the iograft.py module
    that allows the "ProcessReadyNodes" function to not set a "timeout" for
    retrieving nodes. The base implementation waits 1 second for new nodes
    to be added to the queue for processing. This is a problem in Blender
    because we call this function from a modal operator that needs to
    execute as quickly as possible.
    """
    def __init__(self):
        super(BlenderMainThreadCore, self).__init__()

    def _GetAndExecuteQueuedNode(self):
        """
        This is the one function we are overriding to prevent the "wait"
        for queued nodes to arrive. If no nodes exist in the queue, exit
        immediately.
        """
        try:
            node_creator, data_block, result_event = \
                                            self.work_queue.get(False)
        except queue.Empty:
            return False

        try:
            iograft._ExecuteNode(node_creator, data_block)
        except Exception:
            result_event.setException(sys.exc_info())

        result_event.set()
        self.work_queue.task_done()
        return True


def _ProcessQueuedNodes():
    """
    This function is called on a timer when iograft is started within
    Blender to process any nodes that are ready to be executed.
    """
    # Get the core object for the Blender instance.
    try:
        core = iograft.GetCore(IOGRAFT_BLENDER_CORE_NAME,
                               create_if_needed=False)
    except KeyError:
        # iograft must not be initialized, stop the timer.
        return None

    # Process any ready nodes and reset the timer.
    core.ProcessReadyNodes()
    return 0.1


class StartIograftOperator(bpy.types.Operator):
    """
    Start the iograft API inside of Blender and create a Core object for
    working inside Blender. This also starts a persistent timer to listen
    for nodes to be executed from iograft.
    """
    bl_idname = "iograft.start"
    bl_label = "Start iograft"
    bl_description = "Start the iograft API and create a 'blender' Core object"

    def execute(self, context):
        if not iograft.IsInitialized():
            iograft.Initialize()

        # Ensure that there is a "blender" Core object created and setup to
        # handle requests.
        try:
            core = iograft.GetCore(IOGRAFT_BLENDER_CORE_NAME,
                                   create_if_needed=False)
        except KeyError:
            core = BlenderMainThreadCore()
            iograft.RegisterCore(IOGRAFT_BLENDER_CORE_NAME, core)

        # Ensure that the Core's request handler is active.
        core.StartRequestHandler()

        # Start a timer to process nodes as they become queued.
        if not bpy.app.timers.is_registered(_ProcessQueuedNodes):
            bpy.app.timers.register(_ProcessQueuedNodes,
                                    first_interval=0.1,
                                    persistent=True)

        # Get the core address that clients (such as a UI) can connect to.
        core_address = core.GetClientAddress()
        message = "iograft Core: '{}' running at: {}".format(
                            IOGRAFT_BLENDER_CORE_NAME,
                            core_address)
        print(message)
        self.report({"INFO"}, message)
        return {"FINISHED"}


class StopIograftOperator(bpy.types.Operator):
    """
    Operator to shutdown a running iograft Core session within Blender.
    """
    bl_idname = "iograft.stop"
    bl_label = "Stop iograft"
    bl_description = "Stop the iograft API and remove the 'blender' Core object"

    def execute(self, context):
        # Stop the _ProcessQueuedNodes timer if it is running.
        if bpy.app.timers.is_registered(_ProcessQueuedNodes):
            bpy.app.timers.unregister(_ProcessQueuedNodes)

        # Stop iograft if it is currently initialized.
        if not iograft.IsInitialized():
            self.report({"WARNING"},
                        "The iograft API is not currently initialized.")
            return {"CANCELLED"}

        # Otherwise, clear out the "blender" Core object and uninitialize
        # iograft.
        try:
            iograft.UnregisterCore(IOGRAFT_BLENDER_CORE_NAME)
        except KeyError:
            pass

        iograft.Uninitialize()
        self.report({"INFO"}, "The iograft API has been uninitialized.")
        return {"FINISHED"}


class LaunchIograftUIOperator(bpy.types.Operator):
    """
    Operator to launch an iograft UI subprocess for an active Core in Blender.
    """
    bl_idname = "iograft.launch_ui"
    bl_label = "Launch iograft UI"
    bl_description = "Launch the iograft UI and connect to the 'blender' Core"

    def execute(self, context):
        # Check that iograft has been initialized.
        if not iograft.IsInitialized():
            self.report({"WARNING"},
                        "The iograft API has not been initialized.")
            return {"CANCELLED"}

        # Get the address of the Core object running in this session.
        try:
            core = iograft.GetCore(IOGRAFT_BLENDER_CORE_NAME,
                                   create_if_needed=False)
            core_address = core.GetClientAddress()
        except KeyError:
            self.report({"ERROR"},
                        "No iograft Core: '{}' is currently running.".format(
                            IOGRAFT_BLENDER_CORE_NAME))
            return {"CANCELLED"}

        # Sanitize the environment for the iograft_ui session; removing the
        # LD_LIBRARY_PATH so we don't conflict with any libraries that Blender
        # may have set, and clearing the IOGRAFT_ENV environment variable
        # since the UI process will no longer be running under the Blender
        # environment.
        subprocess_env = os.environ.copy()
        subprocess_env.pop("LD_LIBRARY_PATH", None)
        subprocess_env.pop("IOGRAFT_ENV", None)

        # Launch the iograft_ui subprocess.
        subprocess.Popen(["iograft_ui", "-c", core_address], env=subprocess_env)
        self.report({"INFO"}, "iograft_ui launched.")
        return {"FINISHED"}


def register():
    bpy.utils.register_class(StartIograftOperator)
    bpy.utils.register_class(StopIograftOperator)
    bpy.utils.register_class(LaunchIograftUIOperator)
    bpy.utils.register_class(IograftPanel)


def unregister():
    bpy.utils.unregister_class(IograftPanel)
    bpy.utils.unregister_class(LaunchIograftUIOperator)
    bpy.utils.unregister_class(StopIograftOperator)
    bpy.utils.unregister_class(StartIograftOperator)


# This allows directly running the script from Blender's text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
