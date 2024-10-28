#!/opt/bin/lv_micropython
import os
import sys

def fileExists(filename):
    print("Loading", filename, "...")
    try:
        # Check if main.py exists in the root directory
        files = [f for f in os.listdir()]
        found = filename in files
        
        return found
    except Exception as e:
        print("Error checking for main.py:", e)
        return False

def main():
    # Perform any necessary initialization here
    print("Booting ...")

    # Check if main.py exists
    if fileExists("main.py"):
        try:
            # Execute main.py
            with open('main.py') as f:
                exec(f.read(), globals())
        except Exception as e:
            print("Error executing main.py:", e)
            sys.exit(1)
    else:
        print("main.py not found. Please upload main.py to the root directory.")
        sys.exit(1)

# Run the main function
main()