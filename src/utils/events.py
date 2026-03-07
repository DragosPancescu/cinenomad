from enum import Enum


class MouseEvent(str, Enum):
    LEFT_CLICK = "<Button-1>"
    MIDDLE_CLICK = "<Button-2>"
    RIGHT_CLICK = "<Button-3>"
    
    LEFT_PRESS = "<ButtonPress-1>"
    MIDDLE_PRESS = "<ButtonPress-2>"
    RIGHT_PRESS = "<ButtonPress-3>"

    LEFT_RELEASE = "<ButtonRelease-1>"
    MIDDLE_RELEASE = "<ButtonRelease-2>"
    RIGHT_RELEASE = "<ButtonRelease-3>"

    DOUBLE_LEFT_CLICK = "<Double-Button-1>"
    DOUBLE_MIDDLE_CLICK = "<Double-Button-2>"
    DOUBLE_RIGHT_CLICK = "<Double-Button-3>"

    MOVE = "<Motion>"

    DRAG_LEFT = "<B1-Motion>"
    DRAG_MIDDLE = "<B2-Motion>"
    DRAG_RIGHT = "<B3-Motion>"

    ENTER = "<Enter>"
    LEAVE = "<Leave>"

    WHEEL = "<MouseWheel>"        # Windows / macOS
    WHEEL_UP = "<Button-4>"       # Linux
    WHEEL_DOWN = "<Button-5>"     # Linux
    
    
class KeyEvent(str, Enum):
    PRESS = "<KeyPress>"
    RELEASE = "<KeyRelease>"

    ENTER = "<Return>"
    ESCAPE = "<Escape>"
    TAB = "<Tab>"
    BACKSPACE = "<BackSpace>"
    DELETE = "<Delete>"
    SPACE = "<space>"

    UP = "<Up>"
    DOWN = "<Down>"
    LEFT = "<Left>"
    RIGHT = "<Right>"


class FocusEvent(str, Enum):
    IN = "<FocusIn>"
    OUT = "<FocusOut>"


class WidgetEvent(str, Enum):
    CONFIGURE = "<Configure>"   # resize / move
    DESTROY = "<Destroy>"
    MAP = "<Map>"
    UNMAP = "<Unmap>"
