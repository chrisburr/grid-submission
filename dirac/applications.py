import os
import shutil
import tempfile

from six import string_types

from .dirac import GridFile


EXECUTABLE_SCRIPT = (
    '#!/usr/bin/env bash\n'
    'set -e\n'
    'source /cvmfs/lhcb.cern.ch/lib/LbLogin.sh\n'
    'tar -czf boole_sandbox.tar.gz *\n'
    'lb-run {app_name} {version} gaudirun.py {options}\n'
)


class Job(object):
    """Class to wrap around the Dirac Job object to provide a pythonic API."""

    def __init__(self, name='UnnamedJob'):
        self._name = name
        self._executable = []
        self._input_sandbox = []
        self._input_data = []
        self._output_data = []
        self._output_storage_element = None
        self._output_lfn_suffix = ''

    def _as_dirac_job(self):
        from DIRAC.Interfaces.API.Job import Job

        dirac_job = Job()
        dirac_job.setName(self._name)

        if self._input_sandbox != []:
            dirac_job.setInputSandbox(self._input_sandbox)

        if self._input_data != []:
            dirac_job.setInputData(self._input_data)

        # TODO Check this doesn't already exist
        dirac_job.setOutputData(
            self._output_data,
            outputSE=self._output_storage_element,
            outputPath=self._output_lfn_suffix
        )

        for executable in self._executable:
            dirac_job.setExecutable(executable)

        return dirac_job

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def executable(self):
        return self._executable

    @executable.setter
    def executable(self, script):
        if isinstance(script, string_types):
            script = [script]
        self._executable = script

    @property
    def input_sandbox(self):
        return self._input_sandbox

    @input_sandbox.setter
    def input_sandbox(self, filenames):
        if isinstance(filenames, string_types):
            filenames = [filenames]
        self._input_sandbox = filenames

    @property
    def input_data(self):
        return self._input_data

    @input_data.setter
    def input_data(self, lfns):
        self._input_data = lfns

    @property
    def output_data(self):
        return self._output_data

    @output_data.setter
    def output_data(self, paths):
        if isinstance(paths, string_types):
            paths = [paths]
        self._output_data = paths

    @property
    def output_storage_element(self):
        return self._output_storage_element

    @output_storage_element.setter
    def output_storage_element(self, storage_element):
        self._output_storage_element = storage_element

    @property
    def output_lfn_suffix(self):
        return self._output_lfn_suffix

    @output_lfn_suffix.setter
    def output_lfn_suffix(self, suffix):
        self._output_lfn_suffix = suffix


class GaudiJob(Job):
    _app_name = 'Gaudi'

    def __init__(self, version=None):
        self._version = version or ''
        self._options_files = []

        super(GaudiJob, self).__init__()

    def _as_dirac_job(self):
        tmp_dir = tempfile.mkdtemp(prefix='tmp_grid-submission_')

        # TODO Ensure the user doesn't try to add a folder called '_options'
        options_dir = os.path.join(tmp_dir, '_options')
        os.makedirs(options_dir)
        staged_options = []
        for fn in self._options:
            shutil.copy(fn, options_dir)
            staged_options.append(os.path.join('_options', os.path.basename(fn)))

        # TODO Make the job fail if this script fails
        executable_filename = os.path.join(tmp_dir, 'job_script.sh')
        with open(executable_filename, 'wt') as f:
            f.write(EXECUTABLE_SCRIPT.format(
                app_name=self._app_name,
                version=self._version,
                options=' '.join(staged_options)
            ))
        self._executable = [executable_filename]
        self.input_sandbox.append(options_dir)

        dirac_job = super(GaudiJob, self)._as_dirac_job()

        return dirac_job

    @property
    def executable(self):
        raise AttributeError(
            "An executable cannot be specified for a Gaudi based job, perhaps "
            "you mean to use the 'options' property?"
        )

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, paths):
        self._options = paths

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        # TODO Add validation?
        self._version = version


class GaussJob(GaudiJob):
    _app_name = 'Gauss'


class BooleJob(GaudiJob):
    _app_name = 'Boole'


class MooreJob(GaudiJob):
    _app_name = 'Moore'


class BrunelJob(GaudiJob):
    _app_name = 'Brunel'


class DaVinciJob(GaudiJob):
    _app_name = 'DaVinci'
