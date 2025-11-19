"""
Bootstrap Loader for Halloween Lightning & Thunder Effect

Minimal boot script that verifies main.py exists and executes it.
Keeps boot process lightweight for fast startup.

This file runs automatically when Pico 2 powers on or resets.

DEBUGGING MODE:
Set AUTO_START = False to disable automatic main.py execution.
This allows you to connect to REPL and manually run/test code.
When ready for production, set AUTO_START = True.
"""

import os
import sys

# ============================================================================
# DEBUGGING CONFIGURATION
# ============================================================================
# Set to False during development to prevent auto-start boot loops
# Set to True for production deployment (autonomous operation)
AUTO_START = False  # ⚠️ Change to True when deploying to Halloween display


def fileExists(filename):
    """
    Check if a file exists in the root directory.
    
    Args:
        filename: Name of file to check (e.g., "main.py")
    
    Returns:
        True if file exists, False otherwise
    """
    try:
        # List all files in root directory
        files = [f for f in os.listdir()]
        return filename in files
    except Exception as e:
        print(f"Error checking for {filename}:", e)
        return False


def main():
    """
    Main bootstrap function.
    
    Verifies main.py exists, then executes it in the global namespace.
    Any errors during main.py execution will be displayed and halt boot.
    
    Respects AUTO_START flag - if False, prints instructions and stops.
    """
    print("🎃 Halloween Lightning & Thunder Effect - Boot")
    
    if not AUTO_START:
        print("=" * 50)
        print("⚠️  AUTO_START = False (Debugging Mode)")
        print("=" * 50)
        print()
        print("Boot paused. REPL is ready for manual testing.")
        print()
        print("To run main application:")
        print("  >>> import main")
        print()
        print("To test individual modules:")
        print("  >>> from lights import testLightning")
        print("  >>> testLightning(16, 300)")
        print()
        print("To enable auto-start:")
        print("  Edit boot.py and set AUTO_START = True")
        print("=" * 50)
        return  # Stop here, don't execute main.py
    
    # AUTO_START is True - proceed with normal boot
    print("AUTO_START = True (Production Mode)")
    print()
    
    # Verify main.py exists before attempting to execute
    if fileExists("main.py"):
        try:
            print("Executing main.py...")
            # Execute main.py in global namespace
            # This allows main.py to access all modules and state
            with open('main.py') as f:
                exec(f.read(), globals())
        except Exception as e:
            print("❌ Error executing main.py:", e)
            sys.exit(1)
    else:
        print("❌ main.py not found. Please upload main.py to the Pico.")
        print("   Use: devops/deploy.sh or mpremote cp src/main.py :main.py")
        sys.exit(1)


# Execute bootstrap
# This runs automatically when boot.py loads
main()
