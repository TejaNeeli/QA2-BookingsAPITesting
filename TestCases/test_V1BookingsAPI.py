import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from API_Requests.V1BookingsAPIRequests import BookingsAPIRequestsV1

# Environment-aware defaults for V1 tests (with optional UI override)
_ENV = os.environ.get('TEST_ENV', 'QA2').upper()
if _ENV == 'INTEG':
    REEFER_ID = ['CCHD0000001', 'CCHD0000002']
    BKG_NUM = 'INTEGBKGSAPIV1'
    BKG_TEMP = -10.0
elif _ENV == 'ZIMINTEG1':
    REEFER_ID = ['ZMOU8914435']
    BKG_NUM = 'ZIMINTEG1BKGSAPIV1'
    BKG_TEMP = -10.0
elif _ENV == 'ZIMINTEG2':
    REEFER_ID = ['ZCLU9910407']
    BKG_NUM = 'ZIMINTEG2BKGSAPIV1'
    BKG_TEMP = -10.0
elif _ENV == 'PROD':
    REEFER_ID = ['AWSA0000002', 'AWSA0000003']
    BKG_NUM = 'PRODBKGSAPIV1'
    BKG_TEMP = -10.0
else:
    REEFER_ID = ['FBWS0000001', 'FBWS0000002']
    BKG_NUM = 'QA2BKGSAPIV1'
    BKG_TEMP = -10.0

# Optional UI override for REEFER_ID (comma-separated)
_user_reefer_ids = os.environ.get('REEFER_ID')
if _user_reefer_ids:
    REEFER_ID = [x.strip() for x in _user_reefer_ids.split(',') if x.strip()]

# Optional UI override for BKG_NUM
_user_bkg_num = os.environ.get('BKG_NUM')
if _user_bkg_num:
    BKG_NUM = _user_bkg_num.strip()

# Optional UI override for BKG_TEMP
_user_bkg_temp = os.environ.get('BKG_TEMP')
if _user_bkg_temp:
    try:
        BKG_TEMP = float(_user_bkg_temp)
    except ValueError:
        pass  # keep default if parse fails

# Generate booking_number2 by changing the last character in BKG_NUM to 'X'
booking_number2 = BKG_NUM[:-1] + 'X'
# Generate booking_number3 by changing the last character in booking_number2 to 'Y'
booking_number3 = booking_number2[:-1] + 'Y'


class TestBookingAPIV1:

    @pytest.mark.order(1)
    def test_assign_booking(self):
        BookingsAPIRequestsV1(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).assign_booking()

    @pytest.mark.order(2)
    def test_get_booking(self):
        BookingsAPIRequestsV1(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).get_booking()

    @pytest.mark.order(3)
    def test_update_booking(self):
        BookingsAPIRequestsV1(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).update_booking()

    @pytest.mark.order(4)
    def test_get_bookingupdate(self):
        BookingsAPIRequestsV1(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).get_bookingupdate()

    @pytest.mark.order(5)
    def test_assign_new_booking(self):
        BookingsAPIRequestsV1(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).assign_new_booking()

    @pytest.mark.order(6)
    def test_get_new_booking(self):
        BookingsAPIRequestsV1(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).get_new_booking()

    @pytest.mark.order(7)
    def test_unassign_booking(self):
        BookingsAPIRequestsV1(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).unassign_booking()

    @pytest.mark.order(8)
    def test_assign_new_bkg_put(self):
        BookingsAPIRequestsV1(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).assign_new_bkg_put()

    @pytest.mark.order(9)
    def test_delete_booking(self):
        BookingsAPIRequestsV1(BKG_NUM, REEFER_ID, BKG_TEMP, booking_number2, booking_number3).delete_booking()
