# Copyright 2022 Fabrica Software, LLC

import iograft
import iobasictypes

import bpy


class SaveFileBlender(iograft.Node):
    """
    Save the current Blend file.
    """
    filepath = iograft.InputDefinition("filepath", iobasictypes.Path())
    out_filepath = iograft.OutputDefinition("filepath", iobasictypes.Path())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("save_blend_file")
        node.SetMenuPath("Blender")
        node.AddInput(cls.filepath)
        node.AddOutput(cls.out_filepath)
        return node

    @staticmethod
    def Create():
        return SaveFileBlender()

    def Process(self, data):
        filepath = iograft.GetInput(self.filepath, data)

        # Save the file.
        bpy.ops.wm.save_as_mainfile(filepath=filepath)
        out_filepath = bpy.data.filepath
        iograft.SetOutput(self.out_filepath, data, out_filepath)


def LoadPlugin(plugin):
    node = SaveFileBlender.GetDefinition()
    plugin.RegisterNode(node, SaveFileBlender.Create)
