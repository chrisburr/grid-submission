import os

# Gauss config
EVENT_TYPE = '30000000'
ENABLE_SPILLOVER = False
EVENTS_PER_JOB = 500
N_JOBS = 200

# Boole config
DIGI_TYPE = 'Minimal'  # 'Extended'


# Alignment config


# General config
DDDB_TAG = "dddb-20150729"
CONDDB_TAG = "sim-20150716-vc-md100"
OUTPUT_DIR = os.path.expanduser(
    "/pc2013-data5/cburr/Logbook/2016-03-29_Generate_upgrade_velo_alignment_mc/output"
)
DDDB_XML_PATH = None
DETECTORS = ['VP', 'UT', 'FT', 'Magnet']
OUTPUT_SUFFIX = 'VP_{EVENT_TYPE}_spillover={ENABLE_SPILLOVER}'
