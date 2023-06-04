"""Provide a FreeMind converter class for mindmap import. 

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/mm2yw7
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pywriter.pywriter_globals import *
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.yw.yw7_file import Yw7File
from pywriter.yw.data_files import DataFiles
from mm2yw7lib.mm_file import MmFile
from pywriter.model.novel import Novel


class MmConverter(YwCnvUi):
    """A converter class for FreeMind mindmap import.

    Public methods:
        run(sourcePath, **kwargs) -- Create source and target objects and run conversion.
    """

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath -- str: the source file path.
        
        Required keyword arguments: 
            (none)
        """
        self.newFile = None

        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'{ERROR}File "{os.path.normpath(sourcePath)}" not found.')
            return

        fileName, fileExtension = os.path.splitext(sourcePath)

        if fileExtension == MmFile.EXTENSION:
            source = MmFile(sourcePath, **kwargs)
            target = Yw7File(f'{fileName}{Yw7File.EXTENSION}', **kwargs)
            self.ui.set_info_what(
                _('Create a yWriter project file from {0}\nNew project: "{1}"').format(source.DESCRIPTION, norm_path(target.filePath)))
            try:
                self.check(source, target)
                source.novel = Novel()
                source.read()
                target.novel = source.novel
                target.write()
            except Exception as ex:
                message = f'!{str(ex)}'
                self.newFile = None
            else:
                message = f'{_("File written")}: "{norm_path(target.filePath)}".'
                self.newFile = target.filePath
            finally:
                self.ui.set_info_how(message)
            return

            if os.path.isfile(f'{fileName}{Yw7File.EXTENSION}'):
                target = DataFiles(f'{fileName}{DataFiles.EXTENSION}', **kwargs)
                self.import_to_yw(sourceFile, target)
            else:
                target = Yw7File(f'{fileName}{Yw7File.EXTENSION}', **kwargs)
                self.create_yw7(sourceFile, target)
        else:
            self.ui.set_info_how(f'{ERROR}File type of "{os.path.normpath(sourcePath)}" not supported.')
