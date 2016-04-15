from __future__ import print_function
from __future__ import division

# Use gevent to monkey patch the standard libary
import gevent
import gevent.queue
import gevent.pool
import gevent.subprocess
import gevent.monkey
gevent.monkey.patch_all()  # NOQA

import os

import leveldb

# Magic command to initalise Dirac
# TODO(chrisburr) There must be a better way
from DIRAC.Core.Base import Script
Script.parseCommandLine(ignoreErrors=False)  # NOQA

# Setup the database
WORKDIR = os.getcwd()  # NOQA
db = leveldb.LevelDB(os.path.join(WORKDIR, 'jobs.db'))  # NOQA

from . import applications
from .dirac import GridFile
from .ui import start_ui
from .workers import start_workers, submit


__all__ = [
    GridFile,
    start_ui,
    start_workers,
    submit,
    applications
]
