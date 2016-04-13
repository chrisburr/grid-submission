"""A nicer wrapper around an instance of the dirac API"""
import os

from DIRAC.Interfaces.API.Dirac import Dirac
from LHCbDIRAC.Interfaces.API.DiracLHCb import DiracLHCb


class DiracException(Exception):
    """Exception in a call to the DIRAC API."""


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
    res = DiracLHCb().getOutputSandbox(job_id, outputDir=output_folder, noJobDir=False)
    if not res['OK']:
        raise DiracException(res['Message'])
    return os.path.join(output_folder, str(job_id))


_dirac = Dirac()
submit = _dirac.submit

__all__ = [
    submit,
    get_job_output,
    DiracException
]
