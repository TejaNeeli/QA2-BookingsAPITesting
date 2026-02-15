import inspect
import logging


class QA2BookingAPIURLV1:
    def QA2BookingAPIV1URL_1(self):
        return "https://awsqa2.tms-orbcomm.com:44344/rcweb/v1/BookingMgmt/Bookings/BKG_V1@001"

    def QA2BookingAPIV1URL_2(self):
        return "https://awsqa2.tms-orbcomm.com:44344/rcweb/v1/BookingMgmt/Bookings/BKG_V1@002"

    def QA2BookingAPIV1URL_3(self):
        return "https://awsqa2.tms-orbcomm.com:44344/rcweb/v1/BookingMgmt/Bookings/BKG_V1@003"

    def getlogger(self):
        logger = logging.getLogger(inspect.stack()[1][3])  # Use the calling method name as the logger name
        if not logger.hasHandlers():  # Avoid adding duplicate handlers
            handler = logging.FileHandler('logfile.log', mode='a', encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            # Add a StreamHandler to ensure logs are also written to stdout
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        logger.setLevel(logging.INFO)

        # Ensure logs are flushed immediately
        for handler in logger.handlers:
            handler.flush = lambda: None

        return logger
