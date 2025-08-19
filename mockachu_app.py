#!/usr/bin/env python3
"""
macOS specific app launcher that sets proper app name
"""

import os
import sys
from pathlib import Path

def set_macos_app_name():
    """Set the proper app name for macOS"""
    if sys.platform == "darwin":
        # Set the process name to help macOS identify the app correctly
        try:
            import ctypes
            import ctypes.util
            
            # Load libc and set the process name
            libc = ctypes.CDLL(ctypes.util.find_library('c'))
            if libc:
                # Set process name (shown in Activity Monitor)
                libc.prctl.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
                libc.prctl(15, b'Mockachu', 0, 0, 0)  # PR_SET_NAME = 15
        except:
            pass
            
        # Set environment variable that some tools use
        os.environ['RESOURCE_NAME'] = 'Mockachu'

if __name__ == "__main__":
    set_macos_app_name()
    from mockachu.app import main
    main()
