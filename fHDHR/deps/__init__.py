import sys
import pathlib

try:
    __import__('pip')
except ImportError:
    print("pip appears to not be installed")
    sys.exit(1)

import pkg_resources

from pip._internal import main as pipmain
from pip._internal.utils.misc import get_installed_distributions


class Dependencies():

    def __init__(self, script_dir):
        self.script_dir = script_dir
        self.core_req = pathlib.Path(script_dir).joinpath('requirements.txt')

        print("Checking and Installing Core Dependencies.")
        corereqs = self.get_requirements(self.core_req)
        self.check_requirements(corereqs)

    @property
    def pipinstalled(self):
        installed_packages = pkg_resources.working_set
        return sorted(["%s" % i.key for i in installed_packages])

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

    def check_requirements(self, reqs):
        installed = self.pipinstalled
        not_installed = [x for x in reqs if x not in installed]
        for pipdep in not_installed:
            print("%s missing. Attempting installation" % pipdep)
            pipmain(['install', pipdep])
