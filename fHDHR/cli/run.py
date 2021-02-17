import os
import argparse
import time
import pathlib

from fHDHR import fHDHR_VERSION, fHDHR_OBJ
import fHDHR.exceptions
import fHDHR.config
import fHDHR.logger
import fHDHR.plugins
import fHDHR.versions
import fHDHR.scheduler
import fHDHR.web
import fHDHR.origins
from fHDHR.db import fHDHRdb

ERR_CODE = 1
ERR_CODE_NO_RESTART = 2


def build_args_parser(script_dir):
    """Build argument parser for fHDHR"""
    parser = argparse.ArgumentParser(description='fHDHR')
    parser.add_argument('-c', '--config', dest='cfg', type=str, default=pathlib.Path(script_dir).joinpath('config.ini'), required=False, help='configuration file to load.')
    parser.add_argument('--setup', dest='setup', type=str, required=False, nargs='?', const=True, default=False, help='Setup Configuration file.')
    parser.add_argument('--iliketobreakthings', dest='iliketobreakthings', type=str, nargs='?', const=True, required=False, default=False, help='Override Config Settings not meant to be overridden.')
    return parser.parse_args()


def job():
    print("I'm working...")


def run(settings, logger, db, script_dir, fHDHR_web, plugins, versions, web, scheduler):

    fhdhr = fHDHR_OBJ(settings, logger, db, plugins, versions, web, scheduler)
    fhdhrweb = fHDHR_web.fHDHR_HTTP_Server(fhdhr)

    fhdhr.scheduler.every(10).seconds.do(job)

    try:

        # Start Flask Thread
        fhdhrweb.start()

        # Perform some actions now that HTTP Server is running
        fhdhr.api.get("/api/startup_tasks")

        # Start SSDP Thread
        if fhdhr.device.ssdp.multicast_address and "ssdp" in list(fhdhr.threads.keys()):
            fhdhr.device.ssdp.start()

        # Start EPG Thread
        if settings.dict["epg"]["method"] and "epg" in list(fhdhr.threads.keys()):
            fhdhr.device.epg.start()

        for interface_plugin in fhdhr.device.interfaces.keys():
            if hasattr(fhdhr.device.interfaces[interface_plugin], 'run_thread'):
                fhdhr.device.interfaces[interface_plugin].run_thread()

        logger.noob("fHDHR and fHDHR_web should now be running and accessible via the web interface at %s" % fhdhr.api.base)
        if settings.dict["logging"]["level"].upper() == "NOOB":
            logger.noob("Set your [logging]level to INFO if you wish to see more logging output.")

        # wait forever
        restart_code = "restart"
        while fhdhr.threads["flask"].is_alive():
            time.sleep(1)
        if restart_code in ["restart"]:
            logger.noob("fHDHR has been signaled to restart.")
        return restart_code

    except KeyboardInterrupt:
        return ERR_CODE_NO_RESTART

    return ERR_CODE


def start(args, script_dir, fHDHR_web):
    """Get Configuration for fHDHR and start"""

    try:
        settings = fHDHR.config.Config(args, script_dir)
    except fHDHR.exceptions.ConfigurationError as e:
        print(e)
        return ERR_CODE_NO_RESTART

    # Setup Logging
    logger = fHDHR.logger.Logger(settings)
    settings.logger = logger

    logger.noob("Loading fHDHR %s with fHDHR_web %s" % (fHDHR_VERSION, fHDHR_web.fHDHR_web_VERSION))
    logger.info("Importing Core config values from Configuration File: %s" % settings.config_file)

    logger.debug("Logging to File: %s" % os.path.join(settings.internal["paths"]["logs_dir"], '.fHDHR.log'))

    # Continue non-core settings setup
    settings.secondary_setup()

    # Setup Database
    db = fHDHRdb(settings, logger)

    logger.debug("Setting Up shared Web Requests system.")
    web = fHDHR.web.WebReq()

    # Setup Version System
    versions = fHDHR.versions.Versions(settings, fHDHR_web, logger, web)

    # Find Plugins and import their default configs
    plugins = fHDHR.plugins.PluginsHandler(settings, logger, db, versions)

    scheduler = fHDHR.scheduler.Scheduler()

    return run(settings, logger, db, script_dir, fHDHR_web, plugins, versions, web, scheduler)


def config_setup(args, script_dir, fHDHR_web):
    settings = fHDHR.config.Config(args, script_dir, fHDHR_web)
    fHDHR.plugins.PluginsHandler(settings)
    settings.setup_user_config()
    return ERR_CODE


def main(script_dir, fHDHR_web):
    """fHDHR run script entry point"""

    try:
        args = build_args_parser(script_dir)

        if args.setup:
            return config_setup(args, script_dir, fHDHR_web)

        while True:
            returned_code = start(args, script_dir, fHDHR_web)
            if returned_code not in ["restart"]:
                return returned_code
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        return ERR_CODE


if __name__ == '__main__':
    main()
