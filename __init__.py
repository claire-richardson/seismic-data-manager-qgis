from .main import SP1Importer

def classFactory(iface):
    return SP1Importer(iface)