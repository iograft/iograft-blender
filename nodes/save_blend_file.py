# Copyright 2022 Fabrica Software, LLC

import iograft
import iobasictypes

import bpy


class SaveFileBlender(iograft.Node):
    """
    Save the current Blend file.
    """
    filename = iograft.InputDefinition("filename", iobasictypes.Path())
    out_filename = iograft.OutputDefinition("filename", iobasictypes.Path())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("save_file_blender")
        node.AddInput(cls.filename)
        node.AddOutput(cls.out_filename)
        return node

    @staticmethod
    def Create():
        return SaveFileBlender()

    def Process(self, data):
        filename = iograft.GetInput(self.filename, data)

        # Save the file.
        bpy.ops.wm.save_mainfile(filepath=filename)
        out_filename = bpy.data.filepath
        iograft.SetOutput(self.out_filename, data, out_filename)


def LoadPlugin(plugin):
    node = SaveFileBlender.GetDefinition()
    plugin.RegisterNode(node, SaveFileBlender.Create)
