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

    def list_jobs(self):
        jobsdict = []
        joblist = self.jobs
        for job_item in joblist:
            jobsdict.append(job_item.tags.keys()[0])
            print(job_item)
            print(job_item.tags)
        print(jobsdict)

        """
        [Every 4 to 5 hours do threadget(url='/api/channels?method=scan&source=ustvgo') (last run: [never], next run: 2021-10-13 17:40:18), Every 43200 seconds do threadget(url='/api/epg?method=update&source=ustvgo') (last run: [never], next run: 2021-10-14 01:40:18), Every 1800 seconds do threadget(url='/api/ssdp?method=alive') (last run: [never], next run: 2021-10-13 14:10:18), Every 2 to 3 hours do sched_update() (last run: [never], next run: 2021-10-13 15:40:19)]
        """

    def run(self):
        """
        Run all scheduled tasks.
        """

        self.list_jobs()

        while True:
            self.schedule.run_pending()
            time.sleep(1)

    def __getattr__(self, name):
        """
        Quick and dirty shortcuts. Will only get called for undefined attributes.
        """

        if hasattr(self.schedule, name):
            return eval("self.schedule.%s" % name)
