import requests

from TestData.QA2Booking_V2 import QA2V2Booking
from TestData.QA2fleetapidata_V2 import QA2fleetAPIV2
from Utilities.BaseClass_QA2V2Bkgs import QA2BookingAPIURLV2


class BookingsAPIRequestsV2_QA2:
    QA2Bkg1_V2URL = QA2BookingAPIURLV2().QA2BookingAPIV2URL_1()
    QA2Bkg2_V2URL = QA2BookingAPIURLV2().QA2BookingAPIV2URL_2()
    header_apple = QA2fleetAPIV2().autho_apple()
    initial_request = QA2V2Booking().QA2BookingV2initial()
    update_request = QA2V2Booking().QA2BookingV2Update()
    unassign_request = QA2V2Booking().QA2BookingV2Unassign()
    QA2Bkg3_V2URL = QA2BookingAPIURLV2().QA2BookingAPIV2URL_3()
    QA2Bkg4_V2URL = QA2BookingAPIURLV2().QA2BookingAPIV2URL_4()
    QA2Bkg5_V2URL = QA2BookingAPIURLV2().QA2BookingAPIV2URL_5()
    assignbkg_multiplereefersrequest = QA2V2Booking().QA2BookingV2_multiplereefers()
    unassignbkg_singlereefer = QA2V2Booking().QA2BookingV2_Unassignsinglereefer()
    logger = QA2BookingAPIURLV2().getlogger()

    def assign_booking(self):
        try:
            response_1 = requests.post(self.QA2Bkg1_V2URL, json=self.initial_request, headers=self.header_apple,
                                       verify=False, timeout=10)  # Assign Bkg
            if response_1.status_code == 200:
                self.logger.info("Booking created API request is Successful!")
            else:
                self.logger.error({"Error - status_code": response_1.status_code, "Error - text": response_1.text})
                self.logger.warning("Booking created API request is Failed!")
                assert False, "Booking creation failed: status_code={}, text={}".format(response_1.status_code,
                                                                                        response_1.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Booking created API request is Failed!")

    def get_booking(self):
        try:
            response_2 = requests.get(self.QA2Bkg1_V2URL, headers=self.header_apple, verify=False,
                                      timeout=10)  # Get Bkg details
            if response_2.status_code == 200:
                self.logger.info("Get Booking API request is Successful!")
                self.logger.info(response_2.json())
            else:
                self.logger.error({"Error - status_code": response_2.status_code, "Error - text": response_2.text})
                self.logger.warning("Booking created API request is Failed!")
                assert False, "Get Booking failed: status_code={}, text={}".format(response_2.status_code,
                                                                                   response_2.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Get Booking API request is Failed!")

    def update_booking(self):
        try:
            response_3 = requests.post(self.QA2Bkg1_V2URL, json=self.update_request, headers=self.header_apple,
                                       verify=False, timeout=10)  # Update Bkg
            if response_3.status_code == 200:
                self.logger.info("Booking Updated API request is Successful!")
            else:
                self.logger.error({"Error - status_code": response_3.status_code, "Error - text": response_3.text})
                self.logger.warning("Booking created API request is Failed!")
                assert False, "Update Booking failed: status_code={}, text={}".format(response_3.status_code,
                                                                                      response_3.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Booking Updated API request is Failed!")

    def get_bookingupdate(self):
        try:
            response_4 = requests.get(self.QA2Bkg1_V2URL, headers=self.header_apple, verify=False,
                                      timeout=10)  # Get Bkg details after update
            if response_4.status_code == 200:
                self.logger.info("Get Booking API request after Booking update is Successful!")
                self.logger.info(response_4.json())
            else:
                self.logger.error({"Error - status_code": response_4.status_code, "Error - text": response_4.text})
                self.logger.warning("Booking created API request is Failed!")
                assert False, "Get Booking update failed: status_code={}, text={}".format(response_4.status_code,
                                                                                          response_4.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Get Booking API request after Booking update is Failed!")

    def assign_new_booking(self):
        try:
            response_5 = requests.put(self.QA2Bkg2_V2URL, json=self.update_request, headers=self.header_apple,
                                      verify=False, timeout=10)  # Assign new Bkg
            if response_5.status_code == 200:
                self.logger.info("Assign New Booking API request is Successful!")
            else:
                self.logger.error({"Error - status_code": response_5.status_code, "Error - text": response_5.text})
                self.logger.warning("Assign New Booking API request is Failed!")
                assert False, "Assign New Booking failed: status_code={}, text={}".format(response_5.status_code,
                                                                                          response_5.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Assign New Booking API request is Failed!")

    def get_new_booking(self):
        try:
            response_6 = requests.get(self.QA2Bkg2_V2URL, headers=self.header_apple, verify=False,
                                      timeout=10)  # Get new Bkg details
            if response_6.status_code == 200:
                self.logger.info("Get New Booking API request is Successful!")
                self.logger.info(response_6.json())
            else:
                self.logger.error({"Error - status_code": response_6.status_code, "Error - text": response_6.text})
                self.logger.warning("Get New Booking API request is Failed!")
                assert False, "Get New Booking failed: status_code={}, text={}".format(response_6.status_code,
                                                                                       response_6.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Get New Booking API request is Failed!")

    def unassign_booking(self):
        try:
            response_7 = requests.post(self.QA2Bkg2_V2URL, json=self.unassign_request, headers=self.header_apple,
                                       verify=False, timeout=10)  # Unassign Bkg
            if response_7.status_code == 200:
                self.logger.info("Unassign Booking API request is Successful!")
            else:
                self.logger.error({"Error - status_code": response_7.status_code, "Error - text": response_7.text})
                self.logger.warning("Unassign Booking API request is Failed!")
                assert False, "Booking Unassign failed: status_code={}, text={}".format(response_7.status_code,
                                                                                        response_7.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Unassign Booking API request is Failed!")

    def get_unassign_booking(self):
        try:
            response_8 = requests.get(self.QA2Bkg2_V2URL, headers=self.header_apple, verify=False,
                                      timeout=10)  # Get new Bkg details
            if response_8.status_code == 200:
                self.logger.info("Get New Booking API request is Successful!")
                self.logger.info(response_8.json())
            else:
                self.logger.error({"Error - status_code": response_8.status_code, "Error - text": response_8.text})
                self.logger.warning("Get New Booking API request is Failed!")
                assert False, "Get New Booking failed: status_code={}, text={}".format(response_8.status_code,
                                                                                       response_8.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Get New Booking API request is Failed!")

    def assign_new_bkg_put(self):
        try:
            response_9 = requests.put(self.QA2Bkg3_V2URL, json=self.update_request, headers=self.header_apple,
                                      verify=False, timeout=10)  # Assign new Bkg
            if response_9.status_code == 200:
                self.logger.info("Assign New Booking API request is Successful!")
            else:
                self.logger.error({"Error - status_code": response_9.status_code, "Error - text": response_9.text})
                self.logger.warning("Assign New Booking API request is Failed!")
                assert False, "Assign New Booking failed: status_code={}, text={}".format(response_9.status_code,
                                                                                          response_9.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Assign New Booking Put API request is Failed!")

    def delete_booking(self):
        try:
            response_10 = requests.delete(self.QA2Bkg3_V2URL, json=self.update_request, headers=self.header_apple,
                                          verify=False, timeout=10)  # Delete Bkg
            if response_10.status_code == 200:
                self.logger.info("Delete Booking API request is Successful!")
            else:
                self.logger.error({"Error - status_code": response_10.status_code, "Error - text": response_10.text})
                self.logger.warning("Delete Booking API request is Failed!")
                assert False, "Booking Delete failed: status_code={}, text={}".format(response_10.status_code,
                                                                                      response_10.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Delete Booking API request is Failed!")

    def assignbkg_multiplereefers(self):
        try:
            response_10 = requests.post(self.QA2Bkg4_V2URL, json=self.assignbkg_multiplereefersrequest,
                                        headers=self.header_apple, verify=False, timeout=10)  # Delete Bkg
            if response_10.status_code == 200:
                self.logger.info("Booking API request for Multiple reefers is Successful!")
            else:
                self.logger.error({"Error - status_code": response_10.status_code, "Error - text": response_10.text})
                self.logger.warning("Booking API request for Multiple reefers is Failed!")
                assert False, "Booking API request for Multiple reefers failed: status_code={}, text={}".format(
                    response_10.status_code, response_10.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Booking API request for Multiple reefers is Failed!")

    def unassignbkg_single_multiplereefers(self):
        try:
            response_11 = requests.post(self.QA2Bkg4_V2URL, json=self.unassignbkg_singlereefer,
                                        headers=self.header_apple, verify=False, timeout=10)  # Delete Bkg
            if response_11.status_code == 200:
                self.logger.info("Booking API request for Unassign single reefer in multiple reefers is Successful!")
            else:
                self.logger.error({"Error - status_code": response_11.status_code, "Error - text": response_11.text})
                self.logger.warning("Booking API request for Unassign single reefer in multiple reefers is Failed!")
                assert False, "Booking API request for Unassign single reefer in multiple reefers failed: status_code={}, text={}".format(
                    response_11.status_code, response_11.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Booking API request for Unassign single reefer in multiple reefers is Failed!")

    def getbkg_multiplereefers(self):
        try:
            response_11 = requests.get(self.QA2Bkg4_V2URL, json=self.unassignbkg_singlereefer,
                                       headers=self.header_apple, verify=False, timeout=10)  # Delete Bkg
            if response_11.status_code == 200:
                self.logger.info("Get Booking API request for Multiple reefers is Successful!")
                self.logger.info(response_11.json())
            else:
                self.logger.error({"Error - status_code": response_11.status_code, "Error - text": response_11.text})
                self.logger.warning("Get Booking API request for Multiple reefers is Failed!")
                assert False, "Get Booking API request for Multiple reefers failed: status_code={}, text={}".format(
                    response_11.status_code, response_11.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Get Booking API request for Multiple reefers is Failed!")

    def assignnewbkg_multiplereefers(self):
        try:
            response_12 = requests.put(self.QA2Bkg5_V2URL, json=self.assignbkg_multiplereefersrequest,
                                       headers=self.header_apple, verify=False, timeout=10)  # Delete Bkg
            if response_12.status_code == 200:
                self.logger.info("Assign New Booking API request for Multiple reefers is Successful!")
            else:
                self.logger.error({"Error - status_code": response_12.status_code, "Error - text": response_12.text})
                self.logger.warning("Assign New Booking API request for Multiple reefers is Failed!")
                assert False, "Assign New Booking API request for Multiple reefers failed: status_code={}, text={}".format(
                    response_12.status_code, response_12.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Assign New Booking API request for Multiple reefers is Failed!")

    def getnewbkg_multiplereefers(self):
        try:
            response_13 = requests.get(self.QA2Bkg5_V2URL, json=self.assignbkg_multiplereefersrequest,
                                       headers=self.header_apple, verify=False, timeout=10)  # Delete Bkg
            if response_13.status_code == 200:
                self.logger.info("Get Booking API request for Multiple reefers is Successful!")
                self.logger.info(response_13.json())
            else:
                self.logger.error({"Error - status_code": response_13.status_code, "Error - text": response_13.text})
                self.logger.warning("Get Booking API request for Multiple reefers is Failed!")
                assert False, "Get Booking API request for Multiple reefers failed: status_code={}, text={}".format(
                    response_13.status_code, response_13.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.warning("Assign New Booking API request for Multiple reefers is Failed!")

    def deletebkg_multiplereefers(self):
        try:
            response_14 = requests.delete(self.QA2Bkg5_V2URL, json=self.assignbkg_multiplereefersrequest,
                                          headers=self.header_apple, verify=False, timeout=10)  # Delete Bkg
            if response_14.status_code == 200:
                self.logger.info("Delete Booking API request for Multiple reefers is Successful!")
            else:
                self.logger.error({"Error - status_code": response_14.status_code, "Error - text": response_14.text})
                self.logger.warning("Delete Booking API request for Multiple reefers is Failed!")
                assert False, "Delete Booking API request for Multiple reefers failed: status_code={}, text={}".format(
                    response_14.status_code, response_14.text)
        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request failed: {e}")
            assert False, self.logger.info("Delete Booking API request for Multiple reefers is Failed!")