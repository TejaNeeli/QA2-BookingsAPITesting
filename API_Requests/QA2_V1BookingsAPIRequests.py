# python
from typing import List, Optional
import requests
import random
import string

from TestData.QA2Booking_V1 import QA2V1Booking
from TestData.QA2fleetapidata_V1 import QA2fleetAPIV1
from Utilities.BaseClass_QA2V1Bkgs import QA2BookingAPIURLV1


class BookingsAPIRequestsV1_QA2:
    """
    Fixed class:
    - Requires user inputs for booking numbers and XML payloads.
    - Creates URLs using `QA2BookingAPIURLV1.QA2BookingAPIV1URL(booking_number)`.
    - Builds XML using `QA2V1Booking.booking_v1(reefers, booked_temperature, shipper)`.
    """

    def __init__(
        self,
        booking_number1: str,
        reefers_initial: List[str],
        booked_temperature_initial: float,
        booking_number2: str,
        booking_number3: str,
        shipper: str = "ShipperEntity",
    ):
        api = QA2BookingAPIURLV1()
        # Generate random alphanumeric booking numbers if not provided
        if booking_number2 is None:
            booking_number2 = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        if booking_number3 is None:
            booking_number3 = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        self.QA2Bkg1_V1URL = api.QA2BookingAPIV1URL(booking_number1)
        self.QA2Bkg2_V1URL = api.QA2BookingAPIV1URL(booking_number2)
        self.QA2Bkg3_V1URL = api.QA2BookingAPIV1URL(booking_number3)

        self.header_apple = QA2fleetAPIV1().autho_apple()
        self.logger = api.getlogger()

        builder = QA2V1Booking()
        random_temp = random.randint(-30, 30)
        # Extract reeferIds from reefers_initial
        reefers_ids = reefers_initial or []
        # Build request bodies from user inputs
        self.initial_request = builder.booking_v1(
            reefers=reefers_ids,
            booked_temperature=booked_temperature_initial,
            action="associate",
            shipper=shipper,
        )
        self.update_request = builder.booking_v1(
            reefers=reefers_ids,
            booked_temperature=random_temp,
            action="associate",
            shipper=shipper,
        )
        self.unassign_request = builder.booking_v1(
            reefers=reefers_ids,
            booked_temperature=random_temp,
            action="dissociate",
            shipper=shipper,
        )

    def assign_booking(self):
        try:
            response_1 = requests.post(
                self.QA2Bkg1_V1URL, data=self.initial_request, headers=self.header_apple, verify=False, timeout=10
            )
            if response_1.status_code == 200:
                self.logger.info("Booking created API request is Successful!")
            else:
                self.logger.error({"Error - status_code": response_1.status_code, "Error - text": response_1.text})
                self.logger.warning("Booking created API request is Failed!")
                assert False, "Booking creation failed: status_code={}, text={}".format(
                    response_1.status_code, response_1.text
                )
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Booking created API request is Failed!")

    def get_booking(self):
        try:
            response_2 = requests.get(self.QA2Bkg1_V1URL, headers=self.header_apple, verify=False, timeout=10)
            if response_2.status_code == 200:
                self.logger.info("Get Booking API request is Successful!")
                self.logger.info(response_2.json())
            else:
                self.logger.error({"Error - status_code": response_2.status_code, "Error - text": response_2.text})
                self.logger.warning("Booking created API request is Failed!")
                assert False, "Get Booking failed: status_code={}, text={}".format(response_2.status_code, response_2.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Get Booking API request is Failed!")

    def update_booking(self):
        try:
            response_3 = requests.post(
                self.QA2Bkg1_V1URL, data=self.update_request, headers=self.header_apple, verify=False, timeout=10
            )
            if response_3.status_code == 200:
                self.logger.info("Booking Updated API request is Successful!")
            else:
                self.logger.error({"Error - status_code": response_3.status_code, "Error - text": response_3.text})
                self.logger.warning("Booking created API request is Failed!")
                assert False, "Update Booking failed: status_code={}, text={}".format(
                    response_3.status_code, response_3.text
                )
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Booking Updated API request is Failed!")

    def get_bookingupdate(self):
        try:
            response_4 = requests.get(self.QA2Bkg1_V1URL, headers=self.header_apple, verify=False, timeout=10)
            if response_4.status_code == 200:
                self.logger.info("Get Booking API request after Booking update is Successful!")
                self.logger.info(response_4.json())
            else:
                self.logger.error({"Error - status_code": response_4.status_code, "Error - text": response_4.text})
                self.logger.warning("Booking created API request is Failed!")
                assert False, "Get Booking update failed: status_code={}, text={}".format(
                    response_4.status_code, response_4.text
                )
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Get Booking API request after Booking update is Failed!")

    def assign_new_booking(self):
        try:
            response_5 = requests.put(
                self.QA2Bkg2_V1URL, data=self.update_request, headers=self.header_apple, verify=False, timeout=10
            )
            if response_5.status_code == 200:
                self.logger.info("Assign New Booking API request is Successful!")
            else:
                self.logger.error({"Error - status_code": response_5.status_code, "Error - text": response_5.text})
                self.logger.warning("Assign New Booking API request is Failed!")
                assert False, "Assign New Booking failed: status_code={}, text={}".format(
                    response_5.status_code, response_5.text
                )
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Assign New Booking API request is Failed!")

    def get_new_booking(self):
        try:
            response_6 = requests.get(self.QA2Bkg2_V1URL, headers=self.header_apple, verify=False, timeout=10)
            if response_6.status_code == 200:
                self.logger.info("Get New Booking API request is Successful!")
                self.logger.info(response_6.json())
            else:
                self.logger.error({"Error - status_code": response_6.status_code, "Error - text": response_6.text})
                self.logger.warning("Get New Booking API request is Failed!")
                assert False, "Get New Booking failed: status_code={}, text={}".format(
                    response_6.status_code, response_6.text
                )
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Get New Booking API request is Failed!")

    def unassign_booking(self):
        try:
            response_7 = requests.post(
                self.QA2Bkg2_V1URL, data=self.unassign_request, headers=self.header_apple, verify=False, timeout=10
            )
            if response_7.status_code == 200:
                self.logger.info("Unassign Booking API request is Successful!")
            else:
                self.logger.error({"Error - status_code": response_7.status_code, "Error - text": response_7.text})
                self.logger.warning("Unassign Booking API request is Failed!")
                assert False, "Booking Unassign failed: status_code={}, text={}".format(
                    response_7.status_code, response_7.text
                )
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Unassign Booking API request is Failed!")

    # def get_unassign_booking(self):
    #     try:
    #         response_8 = requests.get(self.QA2Bkg2_V1URL, headers=self.header_apple, verify=False, timeout=10)
    #         if response_8.status_code == 200:
    #             self.logger.info("Get New Booking API request is Successful!")
    #             self.logger.info(response_8.json())
    #         else:
    #             self.logger.error({"Error - status_code": response_8.status_code, "Error - text": response_8.text})
    #             self.logger.warning("Get New Booking API request is Failed!")
    #             assert False, "Get New Booking failed: status_code={}, text={}".format(
    #                 response_8.status_code, response_8.text
    #             )
    #     except requests.exceptions.RequestException as e:
    #         self.logger.exception(f"API request failed: {e}")
    #         assert False, self.logger.warning("Get New Booking API request is Failed!")

    def assign_new_bkg_put(self):
        try:
            response_9 = requests.put(
                self.QA2Bkg3_V1URL, data=self.update_request, headers=self.header_apple, verify=False, timeout=10
            )
            if response_9.status_code == 200:
                self.logger.info("Assign New Booking Put API request is Successful!")
            else:
                self.logger.error({"Error - status_code": response_9.status_code, "Error - text": response_9.text})
                self.logger.warning("Assign New Booking Put API request is Failed!")
                assert False, "Assign New Booking failed: status_code={}, text={}".format(
                    response_9.status_code, response_9.text
                )
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Assign New Booking Put API request is Failed!")

    def delete_booking(self):
        try:
            response_10 = requests.delete(
                self.QA2Bkg3_V1URL, data=self.update_request, headers=self.header_apple, verify=False, timeout=10
            )
            if response_10.status_code == 200:
                self.logger.info("Delete Booking API request is Successful!")
            else:
                self.logger.error({"Error - status_code": response_10.status_code, "Error - text": response_10.text})
                self.logger.warning("Delete Booking API request is Failed!")
                assert False, "Booking Delete failed: status_code={}, text={}".format(
                    response_10.status_code, response_10.text
                )
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Delete Booking API request is Failed!")