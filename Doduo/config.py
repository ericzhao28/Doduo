"""
Doduo/Doduo.config

Doduo configuration settings.
"""

import os


# File name of the default config file.
# TODO: Change this to point to your config!
CONFIG_FILE = "beer.yml"

# File name of the word embedding file.
EMB_MODEL_FILE = "numberbatch-en-17.06.txt.gz"
# The default cosine distance to permit.
SLACK_DEFAULT = 0.1

# Root directory.
if os.path.exists("/.dockerenv"):
    ROOT_DIR = "/Doduo/"
else:
    ROOT_DIR = (
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/"
    )
