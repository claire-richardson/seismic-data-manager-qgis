from .main import SeismicManager

def classFactory(iface):
    return SeismicManager(iface)