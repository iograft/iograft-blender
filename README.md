# iograft for Blender

This repository contains scripts and nodes for running iograft within Blender. It includes a subcore command (`iogblender_subcore`) for executing Blender in "batch" mode from an iograft session, an Add-On for running iograft within an interactive Blender session, and a few example iograft Blender nodes.

## Getting started with a Blender environment

Below are the steps required to setup a new environment in iograft for executing nodes in Blender.

1. Clone this iograft-blender repository.
2. Open the iograft Environment Manager and create a new environment for Blender (i.e. "blender3").
3. Add the "nodes" directory of the iograft-blender repository to the **Plugin Path**.
4. Update the **Subcore Launch Command** to the `iogblender_subcore` command. Note: On Windows this will automatically resolve to the `iogblender_subcore.bat` script.
5. Add the "bin" directory of the iograft-blender repository to the **Path**.
6. Add the directory containing the Blender executable to the **Path**. (i.e. `C:/Program Files/Blender Foundation/Blender 3.2`).
7. Depending on the version of Blender, update the **Python Path** entry for `...\iograft\python39` by switching "python39" to the directory for the correct version of Python (for Blender 3, this is "python310").

<details><summary>Example Nuke environment JSON</summary>
<p>

```json
{
    "plugin_path": [
        "C:\\Program Files\\iograft\\types",
        "C:\\Program Files\\iograft\\nodes",
        "{IOGRAFT_USER_CONFIG_DIR}\\types",
        "{IOGRAFT_USER_CONFIG_DIR}\\nodes",
        "C:\\Users\\dtkno\\Projects\\iograft-public\\iograft-blender\\nodes"
    ],
    "subcore": {
        "launch_command": "iogblender_subcore"
    },
    "path": [
        "C:\\Program Files\\iograft\\bin",
        "C:\\Users\\dtkno\\Projects\\iograft-public\\iograft-blender\\bin"
        "C:\\Program Files\\Blender Foundation\\Blender 3.2",
    ],
    "python_path": [
        "C:\\Program Files\\iograft\\types",
        "C:\\Program Files\\iograft\\python310"
    ],
    "environment_variables": {},
    "appended_environments": [],
    "name": "blender3"
}
```

</p>
</details>

## Using iograft within Blender

To use iograft within an interactive Blender session, we need to ensure that the iograft libraries are accessible to Blender (via the Path/Python Path), and tell iograft what environment we are in. This can be done in a few ways with the easiest options being using a custom startup script, or by launching Blender using `iograft_env`.

### Startup Script

Blender allows for running Python scripts at startup if they are placed in Blender's `.../scripts/startup` directory. See the [Blender Docs](https://docs.blender.org/api/current/info_overview.html#the-default-environment) for the location of this directory on your platform.

Below is an example `iograftSetup.py` script that initializes Blender to use iograft:
```python
# Ensure that the iograft python modules can be found.
import os
import sys
IOGRAFT_PYTHON_PATH = "C:/Program Files/iograft/python310"
if IOGRAFT_PYTHON_PATH not in sys.path:
    sys.path.append(IOGRAFT_PYTHON_PATH)

# Initialize the environment named "blender3"
import iograft
environment_name = "blender3"
try:
    iograft.InitializeEnvironment(environment_name)
except KeyError as e:
    print("Failed to initialize iograft environment: {}: {}".format(
            environment_name, e))


# To avoid Blender warning about missing "register" function.
def register():
    pass
def unregister():
    pass
```

### iograft_env

The second method for launching Blender so iograft can be used is via `iograft_env`. iograft_env first initializes all of the environment variables contained within tje environment JSON and then launches the given command (the Blender executable in the example below).

```bat
iograft_env -e blender3 -c blender
```

## iograft Add-On for Blender

The iograft Add-On for Blender allows iograft to be run from inside an interactive Blender session. The add-on registers three operators for controlling iograft as well as an iograft panel in the `3D View > Tools` menu.

To install the Add-On either install manually from Blender's Preferences > Add-ons panel, or copy the iograftblender.py script from this repository to your Blender addons directory.

The three operators are:
1. **`bpy.ops.iograft.start()`**
Used to initialize a local iograft session within Blender. Starts an iograft Core using Blender's active Python interpreter. Also starts a persistent timer in the background to execute any nodes from iograft that are ready to be processed.

2. **`bpy.ops.iograft.stop()`**
Used to shutdown the iograft session within Blender.

3. **`bpy.ops.iograft.launch_ui()`**
Launch the iograft UI as a subprocess and connect to the iograft Core running inside of Blender.

All other operations for interacting with the Core object should be completed using the iograft Python API.

When the `bpy.ops.iograft.start()` operator is executed, it registers a Core named "blender" that can be retrieved with the Python API as shown below:

```python
import iograft
core = iograft.GetCore("blender")
```

Using the Python API, we have access to useful functionality on the Core such as loading graphs, setting input values on a graph, and processing the graph.
