import os

from maya import standalone

dir, _ = os.path.split(__file__)
maya_settings_dir = os.path.normpath(os.path.join(dir, "maya_settings"))
os.environ["MAYA_APP_DIR"] = maya_settings_dir
os.environ["MAYA_ENV_DIR"] = maya_settings_dir

standalone.initialize()
