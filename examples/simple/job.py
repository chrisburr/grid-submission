j = Job()
j.executable = 'script.sh'
j.name = 'Test submission script'
j.input_sandbox = ['/afs/cern.ch/user/c/cburr/Downloads/grid-submission/examples/options']
# j.input_data = ['/lhcb/MC/Upgrade/XDST/00033327/0000/00033327_00000011_1.xdst']
j.set_output_data('target3.tar.gz', storage_element='CERN-USER', lfn_suffix='testing/grid-submission')
submit(j)
