# python
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


class BookingAPIURLV1:
    def QA2BookingAPIV1URL(self, booking_number: str):
        """
        Build the booking API URL using a user-provided booking number.
        Example booking_number: "BKG_V1@001"
        """
        booking_number = str(booking_number).strip()

        base = "https://awsqa2.tms-orbcomm.com:44344/rcweb/v1/BookingMgmt/Bookings"
        return f"{base}/{booking_number}"

    def INTEGBookingAPIV1URL(self, booking_number: str):
        """
        Build the booking API URL using a user-provided booking number.
        Example booking_number: "BKG_V1@001"
        """
        booking_number = str(booking_number).strip()

        base = "https://integ.tms-orbcomm.com:44344/rcweb/v1/BookingMgmt/Bookings"
        return f"{base}/{booking_number}"

    def ZIMINTEG1BookingAPIV1URL(self, booking_number: str):
        """
        Build the booking API URL using a user-provided booking number.
        Example booking_number: "BKG_V1@001"
        """
        booking_number = str(booking_number).strip()

        base = "integ-zim1.tms-orbcomm.com:44344/rcweb/v1/BookingMgmt/Bookings"
        return f"{base}/{booking_number}"

    def ZIMINTEG2BookingAPIV1URL(self, booking_number: str):
        """
        Build the booking API URL using a user-provided booking number.
        Example booking_number: "BKG_V1@001"
        """
        booking_number = str(booking_number).strip()

        base = "integ-zim2.tms-orbcomm.com:44344/rcweb/v1/BookingMgmt/Bookings"
        return f"{base}/{booking_number}"

    def PRODBookingAPIV1URL(self, booking_number: str):
        """
        Build the booking API URL using a user-provided booking number.
        Example booking_number: "BKG_V1@001"
        """
        booking_number = str(booking_number).strip()

        base = "https://wamc.wamcentral.net:44344/rcweb/v1/BookingMgmt/Bookings"
        return f"{base}/{booking_number}"

    def getlogger(self):
        logger = logging.getLogger(inspect.stack()[1][3])
        if not logger.hasHandlers():
            handler = logging.FileHandler('logfile.log', mode='a', encoding='utf-8')
            formatter = ColoredFormatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        logger.setLevel(logging.INFO)
        for handler in logger.handlers:
            handler.flush = lambda: None
        return logger