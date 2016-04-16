"""A nicer wrapper around an instance of the dirac API"""
import os

from DIRAC.Interfaces.API.Dirac import Dirac
from LHCbDIRAC.Interfaces.API.DiracLHCb import DiracLHCb

from LHCbDIRAC.Core.Utilities import File
# The guid calculated using File.makeGuid might be incorrect if ROOT is not
# available so import ROOT now instead
# TODO Handle this possibility in a more graceful fashion
import ROOT  # NOQA


class DiracException(Exception):
    """Exception in a call to the DIRAC API."""


class GridFile(object):
    def __init__(self, lfn):
        self._lfn = lfn
        self._loaded = False

    def download(self, destination=None):
        self._load_attributes()
        resp = _dirac.getFile(self._lfn, destination or os.getcwd())
        self._check_response(resp)

    def upload(self, path, storage_element, guid=None):
        if guid is None:
            guid = File.makeGuid(path)[path]
        resp = _dirac.addFile(self._lfn, path, storage_element, fileGuid=guid)
        self._check_response(resp)

    def remove(self):
        self._load_attributes()
        resp = _dirac.removeFile(self._lfn)
        self._check_response(resp)
        # Reset this objects proerties
        self._loaded = False

    def replicate(self, destination, source=''):
        self._load_attributes()
        resp = _dirac.replicate(
            self._lfn,
            destinationSE=destination,
            sourceSE=source
        )
        self._check_response(resp)

    @property
    def lfn(self):
        return self._lfn

    @property
    def exists(self):
        try:
            self._load_attributes()
        except DiracException:
            return False
        else:
            return True

    @property
    def replicas(self):
        self._load_attributes()
        return self._replicas

    @property
    def guid(self):
        self._load_attributes()
        return self._guid

    def _load_attributes(self, force=False):
        # Only load once unless force is set
        if not force and self._loaded:
            return

        # TODO Consider using getAllReplicas
        resp = _dirac.getReplicas(self._lfn)
        self._check_response(resp)
        self._replicas = resp['Value']['Successful'][self._lfn]

        resp = _dirac.getLfnMetadata(self._lfn)
        self._check_response(resp)
        self._guid = resp['Value']['Successful'][self._lfn]['GUID']

        self._loaded = True

    def _check_response(self, response):
        if not response['OK']:
            raise DiracException(response['Message'])
        if self._lfn not in response['Value']['Successful']:
            raise DiracException(response['Value']['Failed'][self._lfn])


def get_job_output(job_id, output_folder):
    """Download output sandbox for the given job.

    This functions wraps `getOutputSandbox` and it downloads
    the output sandbox in output_folder/job_id.

    Arguments:
        job_id (int): Job ID to download the output sandbox from.
        output_folder (str): Folder to download the sandbox to.
            If it doesn't exist, it is created.

    Returns:
        str: Output folder.

    Raises:
        DiracException: If the call to the API fails.

    """
    output_folder = os.path.abspath(output_folder)
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)
    response = DiracLHCb().getOutputSandbox(job_id, outputDir=output_folder, noJobDir=False)
    if not response['OK']:
        raise DiracException(response['Message'])
    return os.path.join(output_folder, str(job_id))

_dirac = Dirac()
submit = _dirac.submit
status = _dirac.status

__all__ = [
    submit,
    status,
    get_job_output,
    DiracException
]
