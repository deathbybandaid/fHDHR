import functools
import schedule
import time

from fHDHR.tools import humanized_time


class Scheduler():
    """
    fHDHR Scheduling events system.
    """

    def __init__(self, settings, logger, db):
        self.config = settings
        self.logger = logger
        self.db = db

        self.schedule = schedule

    # This decorator can be applied to any job function
    def job_wrapper(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            job_name = func.__name__
            start_timestamp = time.time()

            self.logger.debug('Running job "%s"' % job_name)

            result = func(*args, **kwargs)

            total_time = humanized_time(time.time() - start_timestamp)
            self.logger.debug('Job "%s" completed in %d seconds' % (job_name, total_time))

            return result

        return wrapper

    def run(self):
        """
        Run all scheduled tasks.
        """

        while True:
            self.schedule.run_pending()
            time.sleep(1)

    def __getattr__(self, name):
        """
        Quick and dirty shortcuts. Will only get called for undefined attributes.
        """

        if hasattr(self.schedule, name):
            return eval("self.schedule.%s" % name)
