import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from API_Requests.QA2_V1BookingsAPIRequests import BookingsAPIRequestsV1_QA2

# User-specifiable values from environment variables
BKG_NUM = os.environ.get('BKG_NUM', 'TEJABKGSAPIV1')
REEFER_ID = os.environ.get('REEFER_ID', 'FBWS0000001').split(',')
BKG_TEMP = float(os.environ.get('BKG_TEMP', '-10'))
# Generate booking_number2 by changing the last character in BKG_NUM to 'X'
booking_number2 = BKG_NUM[:-1] + 'X'
# Generate booking_number3 by changing the last character in booking_number2 to 'Y'
booking_number3 = booking_number2[:-1] + 'Y'


class TestQA2BookingAPIV1:

    @pytest.mark.order(1)
    def test_assign_booking(self):
        BookingsAPIRequestsV1_QA2(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).assign_booking()

    @pytest.mark.order(2)
    def test_get_booking(self):
        BookingsAPIRequestsV1_QA2(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).get_booking()

    @pytest.mark.order(3)
    def test_update_booking(self):
        BookingsAPIRequestsV1_QA2(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).update_booking()

    @pytest.mark.order(4)
    def test_get_bookingupdate(self):
        BookingsAPIRequestsV1_QA2(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).get_bookingupdate()

    @pytest.mark.order(5)
    def test_assign_new_booking(self):
        BookingsAPIRequestsV1_QA2(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).assign_new_booking()

    @pytest.mark.order(6)
    def test_get_new_booking(self):
        BookingsAPIRequestsV1_QA2(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).get_new_booking()

    @pytest.mark.order(7)
    def test_unassign_booking(self):
        BookingsAPIRequestsV1_QA2(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).unassign_booking()

    # @pytest.mark.order(8)
    # def test_get_unassign_booking(self):
    #     BookingsAPIRequestsV1_QA2(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).get_unassign_booking()

    @pytest.mark.order(8)
    def test_assign_new_bkg_put(self):
        BookingsAPIRequestsV1_QA2(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).assign_new_bkg_put()

    @pytest.mark.order(9)
    def test_delete_booking(self):
        BookingsAPIRequestsV1_QA2(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).delete_booking()
