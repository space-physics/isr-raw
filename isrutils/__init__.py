"""
remember that __future__ imports affect only the file that it resides in, NOT files imported by it!
"""
from six import PY2
if PY2:
    from pathlib2 import Path
else:
    from pathlib import Path
