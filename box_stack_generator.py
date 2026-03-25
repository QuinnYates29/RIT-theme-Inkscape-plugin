from enum import Enum

import inkex

# Enum representing box type in stack - allowing for adding future kinds of boxes in a stack
class BoxType(Enum):
    TITLE = 1
    BODY = 2

# Doubly Linked list Node representing a single box in a stack
class LinkedNode:
    def __init__(self, name, box_type : BoxType, prev_node=None, next_node=None):
        self.name = name
        self.type = box_type
        self.next = next_node
        self.prev = prev_node

    def add_next(self, next_node):
        self.next = next_node
        self.next.prev = self

# Linked list representing a stack of boxes of type LinkedNode
class BoxStack:
    def __init__(self, head : LinkedNode):
        self.head = head

#
class BoxStackGenerator(inkex.EffectExtension):
    def generate_stack(self, data):

    def add_arguments(self, pars):
        pars.add_argument("--title", type=str, help="Title of top box")
        pars.add_argument("--height", type=str, help="Height of the box")
        pars.add_argument("--width", type=str, help="Width of the box")
        pars.add_argument("--stack_data", type=str, default="")

    def effect(self):
        layer = self.svg.get_current_layer()




if __name__ == '__main__':
    BoxStackGenerator().run()