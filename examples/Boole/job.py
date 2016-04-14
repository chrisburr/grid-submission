j = BooleJob()
j.name = 'Test submission script'
# j.input_sandbox = ['job.py']
j.options = ['options.py']
# j.input_data = ['/lhcb/MC/Upgrade/XDST/00033327/0000/00033327_00000011_1.xdst']
# j.set_output_data('target8.tar.gz', storage_element='CERN-USER', lfn_suffix='testing/grid-submission')
j.set_output_data('target8.tar.gz', storage_element='CERN-USER')
submit(j)
