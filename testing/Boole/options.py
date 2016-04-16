from Configurables import Boole
from Configurables import CondDB
from Configurables import DDDBConf
from Configurables import DigiConf
from Configurables import LHCbApp

import inspect
import os
import sys
sys.path.append(os.path.dirname(inspect.getfile(inspect.currentframe())))  # NOQA
import config

# $APPCONFIGROOT/options/Boole/Upgrade-WithTruth.py
Boole().DataType = "Upgrade"
LHCbApp().EvtMax = 2

# enable spillover
if config.ENABLE_SPILLOVER:
    Boole().UseSpillover = True
    DigiConf().SpilloverPaths = ['PrevPrev', 'Prev', 'Next', 'NextNext']

# $APPCONFIGROOT/Conditions/Upgrade.py
conddb = CondDB()
conddb.Upgrade = True

Boole().DetectorDigi = config.DETECTORS
Boole().DetectorLink = config.DETECTORS + ['Tr']
Boole().DetectorMoni = config.DETECTORS + ['MC']

# $APPCONFIGROOT/options/Boole/Upgrade-NoTruth.py
Boole().DigiType = config.DIGI_TYPE

LHCbApp().DDDBtag = config.DDDB_TAG
LHCbApp().CondDBtag = config.CONDDB_TAG
if config.DDDB_XML_PATH is not None:
    DDDBConf().DbRoot = config.DDDB_XML_PATH

Boole().DatasetName = (
    "Boole_{output_fn}_{digi_type}.digi"
    .format(output_fn=config.OUTPUT_SUFFIX, digi_type=Boole().DigiType)
).format(**config.__dict__)
