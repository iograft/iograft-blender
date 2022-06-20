# Copyright 2022 Fabrica Software, LLC

import iograft
import iobasictypes

import bpy


class NewFileBlender(iograft.Node):
    """
    Open the default Blend file. If use_empty is True, start with an empty
    Blend file.
    """
    use_empty = iograft.InputDefinition("use_empty", iobasictypes.Bool(),
                                        default_value=False)

    @classmethod
    def GetDefinition(cls):
        node = iograft.NodeDefinition("new_blend_file")
        node.AddInput(cls.use_empty)
        return node

    @staticmethod
    def Create():
        return NewFileBlender()

    def Process(self, data):
        use_empty = iograft.GetInput(self.use_empty, data)

        # Create the new Blend file.
        bpy.ops.wm.read_homefile(use_empty=use_empty)


def LoadPlugin(plugin):
    node = NewFileBlender.GetDefinition()
    plugin.RegisterNode(node, NewFileBlender.Create)
