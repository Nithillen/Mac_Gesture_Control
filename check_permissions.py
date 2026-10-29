"""
check_permissions.py
Checks and guides the user through macOS Camera & Accessibility permissions.
"""

import ctypes
import os
import subprocess
import sys


def is_accessibility_granted():
    """Checks whether the running application has Accessibility permissions."""
    try:
        app = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices')
        app.AXIsProcessTrusted.restype = ctypes.c_bool
        app.AXIsProcessTrusted.argtypes = []
        return app.AXIsProcessTrusted()
    except Exception as e:
        print(f"Could not verify Accessibility permission: {e}")
        return False


def request_accessibility():
    """Prompts macOS to ask for accessibility permissions."""
    try:
        app = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices')
        cf = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
        
        # Open System Settings directly to Accessibility panel
        subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"], check=False)
        print("\n⚠️  [ACTION REQUIRED] macOS Accessibility Permission Needed:")
        print("   1. A System Settings window has been opened for you.")
        print("   2. Look for your terminal application (e.g., Terminal, iTerm, VS Code, or Antigravity).")
        print("   3. Toggle the switch to ON to allow it to control the mouse cursor.")
        print("   4. Once enabled, restart the script.\n")
    except Exception as e:
        print(f"Error opening system preferences: {e}")


if __name__ == "__main__":
    trusted = is_accessibility_granted()
    if trusted:
        print("✅ macOS Accessibility: GRANTED (Cursor control enabled)")
        sys.exit(0)
    else:
        print("❌ macOS Accessibility: NOT GRANTED")
        request_accessibility()
        sys.exit(1)
