"""Helper file for mm2yw7 test.

Create config file.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/mm2yw7
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import sys
import os
from pywriter.config.configuration import Configuration
from mm2yw7_ import SETTINGS
from mm2yw7_ import OPTIONS
from mm2yw7_ import APPNAME


def run(iniFile):
    iniDir = os.path.dirname(iniFile)
    if not os.path.isdir(iniDir):
        os.makedirs(iniDir)
    configuration = Configuration(SETTINGS, OPTIONS)
    configuration.write(iniFile)
    print(f'{iniFile} written.')


if __name__ == '__main__':
    try:
        iniFile = sys.argv[1]
    except:
        iniFile = f'./{APPNAME}.ini'
    run(iniFile)
