import sys
import os

# Get the directory where the executable is located.
exe_dir = os.path.dirname(sys.executable)

# Add the _internal directory to the system path.
# This ensures that DLLs located there are found.
sys.path.append(os.path.join(exe_dir, '_internal'))
