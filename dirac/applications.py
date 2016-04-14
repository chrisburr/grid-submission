import os
import shutil
import tempfile


EXECUTABLE_SCRIPT = (
    '#!/usr/bin/env bash\n'
    'set -e\n'
    'source /cvmfs/lhcb.cern.ch/lib/LbLogin.sh\n'
    'tar -czf target8.tar.gz *\n'
    'lb-run {app_name} {version} gaudirun.py {options}\n'
)


class Job(object):
    """Class to wrap around the Dirac Job object to provide a pythonic API."""

    def __init__(self, *args, **kwargs):
        from DIRAC.Interfaces.API.Job import Job
        self._dirac_job = Job(*args, **kwargs)
        self._input_sandbox = []

    def _prepare_and_get_job_object(self):
        return self._dirac_job

    def set_output_data(self, paths, storage_element=None, lfn_suffix=''):
        self._dirac_job.setOutputData(paths, outputSE=storage_element, outputPath=lfn_suffix)
        # TODO Check this doesn't already exist
        self._output_data = paths

    @property
    def name(self):
        return self._dirac_job.name

    @name.setter
    def name(self, name):
        self._dirac_job.setName(name)

    @property
    def executable(self):
        return self._executable

    @executable.setter
    def executable(self, path):
        self._executable = path
        # FIXME: These will chain if set multiple times
        self._dirac_job.setExecutable(self._executable)

    @property
    def input_sandbox(self):
        return self._input_sandbox

    @input_sandbox.setter
    def input_sandbox(self, filenames):
        self._dirac_job.setInputSandbox(filenames)
        self._input_sandbox = filenames

    @property
    def input_data(self):
        return self._input_data

    @input_data.setter
    def input_data(self, lfns):
        self._dirac_job.setInputData(lfns)
        self._input_data = lfns

    @property
    def output_data(self):
        return self._output_data

    @output_data.setter
    def output_data(self, paths):
        self.set_output_data(paths)


class GaudiJob(Job):
    _app_name = 'Gaudi'

    def __init__(self, version=None, stdout='std.out', stderr='std.err'):
        self._version = version or ''
        self._options_files = []

        super(GaudiJob, self).__init__(stdout='std.out', stderr='std.err')

    def _prepare_and_get_job_object(self):
        tmp_dir = tempfile.mkdtemp(prefix='tmp_grid-submission')

        # TODO Ensure the user doesn't try to add a folder called '_options'
        options_dir = os.path.join(tmp_dir, '_options')
        os.makedirs(options_dir)
        staged_options = []
        for fn in self._options:
            shutil.copy(fn, options_dir)
            staged_options.append(os.path.join('_options', os.path.basename(fn)))

        executable_filename = os.path.join(tmp_dir, 'job_script.sh')
        with open(executable_filename, 'wt') as f:
            f.write(EXECUTABLE_SCRIPT.format(
                app_name=self._app_name,
                version=self._version,
                options=' '.join(staged_options)
            ))
        self._dirac_job.setExecutable(executable_filename)
        self.input_sandbox.append(options_dir)

        return self._dirac_job

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
