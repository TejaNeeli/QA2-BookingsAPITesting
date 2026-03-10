import inspect
import logging


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelname
        if level == 'INFO':
            record.levelname = '\033[93mINFO\033[0m'  # yellow
        elif level in ['ERROR', 'WARNING']:
            record.levelname = '\033[91m' + level + '\033[0m'  # red
        return super().format(record)


class BookingAPIURLV2:
    def QA2BookingAPIV2URL(self, booking_number: str):
        """
        Build the booking API URL using a user-provided booking number.
        Example booking_number: "BKG_V1@001"
        """
        booking_number = str(booking_number).strip()

        base = "https://awsqa2.tms-orbcomm.com:44344/rcweb/v2/BookingMgmt/Bookings"
        return f"{base}/{booking_number}"

    def INTEGBookingAPIV2URL(self, booking_number: str):
        """
        Build the booking API URL using a user-provided booking number.
        Example booking_number: "BKG_V1@001"
        """
        booking_number = str(booking_number).strip()

        base = "https://integ.tms-orbcomm.com:44344/rcweb/v2/BookingMgmt/Bookings"
        return f"{base}/{booking_number}"

    def ZIMINTEG1BookingAPIV2URL(self, booking_number: str):
        """
        Build the booking API URL using a user-provided booking number.
        Example booking_number: "BKG_V1@001"
        """
        booking_number = str(booking_number).strip()

        base = "https://integ-zim1.tms-orbcomm.com:44344/rcweb/v2/BookingMgmt/Bookings"
        return f"{base}/{booking_number}"

    def ZIMINTEG2BookingAPIV2URL(self, booking_number: str):
        """
        Build the booking API URL using a user-provided booking number.
        Example booking_number: "BKG_V1@001"
        """
        booking_number = str(booking_number).strip()

        base = "https://integ-zim2.tms-orbcomm.com:44344/rcweb/v2/BookingMgmt/Bookings"
        return f"{base}/{booking_number}"

    def PRODBookingAPIV2URL(self, booking_number: str):
        """
        Build the booking API URL using a user-provided booking number.
        Example booking_number: "BKG_V1@001"
        """
        booking_number = str(booking_number).strip()

        base = "https://wamc.wamcentral.net:44344/rcweb/v2/BookingMgmt/Bookings"
        return f"{base}/{booking_number}"

    def LOCALBookingAPIV2URL(self, LOCAL_URL, booking_number: str):
        """
        Build the booking API URL using a user-provided booking number.
        Example booking_number: "BKG_V1@001"
        """
        booking_number = str(booking_number).strip()

        base = f"{LOCAL_URL}/rcweb/v2/BookingMgmt/Bookings"
        return f"{base}/{booking_number}"

    def getlogger(self):
        logger = logging.getLogger(inspect.stack()[1][3])  # Use the calling method name as the logger name
        if not logger.hasHandlers():  # Avoid adding duplicate handlers
            handler = logging.FileHandler('logfile.log', mode='a', encoding='utf-8')
            formatter = ColoredFormatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
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
