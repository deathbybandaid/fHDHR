import sys
import pathlib

try:
    __import__('pip')
except ImportError:
    print("pip appears to not be installed")
    sys.exit(1)

from pip._internal import main as pipmain
from pip._internal.utils.misc import get_installed_distributions


class Dependencies():

    def __init__(self, script_dir):
        self.script_dir = script_dir
        self.core_req = pathlib.Path(script_dir).joinpath('requirements.txt')

        corereqs = self.get_requirements(self.core_req)
        print(corereqs)

    @property
    def pipinstalled(self):
        return sorted(["%s" % (i.key) for i in get_installed_distributions()])

    def get_requirements(self, req_file):
        pipreqsdeps = []
        piprequires = [line.rstrip('\n') for line in open(req_file)]
        for pypipreq in piprequires:
            if pypipreq not in ['']:
                if "=" in pypipreq:
                    pypipreq = pypipreq.split("=")[0]
                if ">" in pypipreq:
                    pypipreq = pypipreq.split(">")[0]
                if "<" in pypipreq:
                    pypipreq = pypipreq.split("<")[0]
                pipreqsdeps.append(pypipreq)
        return pipreqsdeps
