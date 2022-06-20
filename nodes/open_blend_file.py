# Copyright 2022 Fabrica Software, LLC

import iograft
import iobasictypes

import bpy


class OpenFileBlender(iograft.Node):
    """
    Open an exiting Blend file.
    """
    filename = iograft.InputDefinition("filename", iobasictypes.Path())
    out_filename = iograft.OutputDefinition("filename", iobasictypes.Path())

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("open_file_blender")
        node.AddInput(cls.filename)
        node.AddOutput(cls.out_filename)
        return node

    @staticmethod
    def Create():
        return OpenFileBlender()

    def Process(self, data):
        filename = iograft.GetInput(self.filename, data)

        # Open the file.
        bpy.ops.wm.open_mainfile(filepath=filename)

        out_filename = bpy.data.filepath
        iograft.SetOutput(self.out_filename, data, out_filename)


def LoadPlugin(plugin):
    node = OpenFileBlender.GetDefinition()
    plugin.RegisterNode(node, OpenFileBlender.Create)
