# Copyright 2022 Fabrica Software, LLC

import iograft
import iobasictypes

import bpy


class OpenFileBlender(iograft.Node):
    """
    Open an exiting Blend file.
    """
    filepath = iograft.InputDefinition("filepath", iobasictypes.Path())
    out_filepath = iograft.OutputDefinition("filepath", iobasictypes.Path())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("open_blend_file")
        node.AddInput(cls.filepath)
        node.AddOutput(cls.out_filepath)
        return node

    @staticmethod
    def Create():
        return OpenFileBlender()

    def Process(self, data):
        filepath = iograft.GetInput(self.filepath, data)

        # Open the file.
        bpy.ops.wm.open_mainfile(filepath=filepath)

        out_filepath = bpy.data.filepath
        iograft.SetOutput(self.out_filepath, data, out_filepath)


def LoadPlugin(plugin):
    node = OpenFileBlender.GetDefinition()
    plugin.RegisterNode(node, OpenFileBlender.Create)
