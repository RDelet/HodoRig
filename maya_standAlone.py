import os

from maya import standalone

# Set maya settings directory
dir, _ = os.path.split(__file__)
maya_settings_dir = os.path.normpath(os.path.join(dir, "batch_settings"))
os.environ["MAYA_APP_DIR"] = maya_settings_dir
os.environ["MAYA_ENV_DIR"] = maya_settings_dir
"""
if "MAYA_APP_DIR" in os.environ:
    del os.environ["MAYA_APP_DIR"]
"""

standalone.initialize()
