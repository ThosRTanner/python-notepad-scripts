from Npp import editor, SCINTILLANOTIFICATION

import ctypes

from ctypes import addressof

from ctypes.wintypes import BOOL, HWND, UINT, WPARAM, LPARAM
LRESULT = ctypes.c_ssize_t

SendMessage = ctypes.windll.user32.SendMessageW
SendMessage.restype = LRESULT
SendMessage.argtypes = [HWND, UINT, WPARAM, LPARAM]

from commctrl import (
    STATUSCLASSNAME, SB_GETPARTS, SB_GETTEXT, SB_GETTEXTLENGTH, SB_SETPARTS
)

WNDENUMPROC = ctypes.WINFUNCTYPE(BOOL, HWND, LPARAM)

FindWindow = ctypes.windll.user32.FindWindowW
SendMessage = ctypes.windll.user32.SendMessageW
EnumChildWindows = ctypes.windll.user32.EnumChildWindows
GetClassName = ctypes.windll.user32.GetClassNameW

statusbar_handle = None

# It seems wrong getting the notepad++ window and wandering down it.
# However, not sure how to get the current window from python
def find_status_bar(hwnd, param):
    curr_class = ctypes.create_unicode_buffer(256)
    GetClassName(hwnd, curr_class, 256)
    if curr_class.value == STATUSCLASSNAME:
        global statusbar_handle
        statusbar_handle = hwnd
        return False
    return True

def read_statusbar_section(handle, section):
    retcode = SendMessage(handle, SB_GETTEXTLENGTH, section, 0)
    length = retcode & 0xFFFF
    type = (retcode >> 16) & 0xFFFF
    val = ctypes.create_string_buffer(length + 1)
    ret = SendMessage(handle, SB_GETTEXT, section, addressof(val))
    return val.value

parts = None

def override_status_bar(args):
    global parts
    val = read_statusbar_section(statusbar_handle, 0)
    if not val.startswith(" - ") or val == " - ":
        if parts is not None:
            SendMessage(
                statusbar_handle, SB_SETPARTS, len(parts), addressof(parts)
            )
            parts = None
    else:
        if parts is None:
            # Save the current values
            num_parts = SendMessage(statusbar_handle, SB_GETPARTS, 0, 0)
            parts = (ctypes.c_int * num_parts)()
            res = SendMessage(
                statusbar_handle, SB_GETPARTS, num_parts, addressof(parts)
            )
            # Now set the width of the first part to everything
            nparts = (ctypes.c_int * num_parts)()
            for i in range(0, len(parts) - 1):
                nparts[i] = parts[num_parts - 1] - (num_parts - i)
            SendMessage(
                statusbar_handle, SB_SETPARTS, len(nparts), addressof(nparts)
            )

def main():    
    hwnd = FindWindow(u"Notepad++", None)
    EnumChildWindows(hwnd, WNDENUMPROC(find_status_bar), 0)

    editor.callback(override_status_bar, [SCINTILLANOTIFICATION.UPDATEUI])

if __name__ == "__main__":
    main()
