from dirac.applications import Job, BooleJob
from dirac import submit, GridFile

# Cleanup as required
f = GridFile('/lhcb/user/c/cburr/grid-submission/test_suite/simple_sandbox.tar.gz')
if f.exists:
    f.remove()
f = GridFile('/lhcb/user/c/cburr/grid-submission/test_suite/boole_sandbox.tar.gz')
if f.exists:
    f.remove()


# Submit a simple job
j = Job()
j.executable = 'simple/script.sh'
j.name = 'grid-submission testing simple'
j.output_data = 'simple_sandbox.tar.gz'
j.output_storage_element = 'CERN-USER'
j.output_lfn_suffix = 'grid-submission/test_suite'
submit(j)

# Submit and example Boole job
boole_input = GridFile('/lhcb/user/c/cburr/grid-submission/boole_test.sim')
if not boole_input.exists:
    boole_input.upload('/afs/cern.ch/work/c/cburr/Gauss_30000000/Gauss/Gauss__VP_30000000_spillover=False_0.sim', 'CERN-USER')
j = BooleJob()
j.name = 'Test submission script'
j.options = ['Boole/options.py']
j.input_data = '/lhcb/user/c/cburr/grid-submission/boole_test.sim'
j.output_data = 'boole_sandbox.tar.gz'
j.output_storage_element = 'CERN-USER'
j.output_lfn_suffix = 'grid-submission/test_suite'
submit(j)
