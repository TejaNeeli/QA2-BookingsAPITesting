import inspect
import logging

class QA2BookingAPIURLV2:
    def QA2BookingAPIV2URL(self, booking_number: str):
        """
        Build the booking API URL using a user-provided booking number.
        Example booking_number: "BKG_V1@001"
        """
        booking_number = str(booking_number).strip()

        base = "https://awsqa2.tms-orbcomm.com:64344/rcweb/v2/BookingMgmt/Bookings"
        return f"{base}/{booking_number}"

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
