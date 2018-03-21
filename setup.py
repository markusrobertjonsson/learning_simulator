import os
import sys
from distutils.core import setup
import cx_Freeze
import matplotlib

base = "Console"

executable = [
    cx_Freeze.Executable("lesim.py", base=base)
]

build_exe_options = {"includes": ["matplotlib.backends.backend_tkagg", "ccplot.algorithms",
                                  "ccplot.hdf"],
                     "packages": ["tkinter", "tkinter.filedialog"],
                     "include_files": [(matplotlib.get_data_path(), "mpl-data")],
                     "excludes": ["collections.abc"],
                     }

cx_Freeze.setup(
    name="py",
    options={"build_exe": build_exe_options},
    version="0.0",
    description="standalone",
    executables=executable
)


# import sys
# import os
# from cx_Freeze import setup, Executable
# import matplotlib

# os.environ['TCL_LIBRARY'] = r'C:\Python\Python36-32\tcl\tcl8.6'
# os.environ['TK_LIBRARY'] = r'C:\Python\Python36-32\tcl\tk8.6'

# # Dependencies are automatically detected, but it might need fine tuning.
# build_exe_options = {"includes": ["tkinter"]}

# options = {
#     'build_exe': {

#         # Sometimes a little fine-tuning is needed
#         # exclude all backends except wx
#         'excludes': ['gtk', 'PyQt4', 'PyQt5'],  # , 'Tkinter'],
#         'includes': ['matplotlib']
#     }
# }

# # GUI applications require a different base on Windows (the default is for a
# # console application).
# base = 'Console'
# if sys.platform == "win32":
#     base = "Win32GUI"

# setup(
#     name="simple_Tkinter",
#     version="0.1",
#     description="Sample cx_Freeze Tkinter script",
#     options=options,  # {"build_exe": build_exe_options},
#     executables=[Executable("lesim.py", base=base)])
