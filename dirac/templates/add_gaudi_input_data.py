from GaudiConf import IOExtension
from Gaudi.Configuration import FileCatalog

IOExtension().inputFiles([
    '{lfns}'
], clear=True)

FileCatalog().Catalogs = ['xmlcatalog_file:pool_xml_catalog.xml']
