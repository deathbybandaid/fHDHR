import pathlib

from pip._internal import main as pipmain
from pip._internal.utils.misc import get_installed_distributions


class Dependencies():

    def __init__(self, script_dir):
        self.script_dir = script_dir
        self.core_req = pathlib.Path(script_dir).joinpath('requirements.txt')

        self.pipinstalled = sorted(["%s" % (i.key) for i in get_installed_distributions()])
        print(self.pipinstalled)
