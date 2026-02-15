import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from API_Requests.QA2_V1BookingsAPIRequests import BookingsAPIRequestsV1_QA2

class TestQA2BookingAPIV1:
    @pytest.mark.order(1)
    def test_assign_booking(self):
        BookingsAPIRequestsV1_QA2().assign_booking()

    @pytest.mark.order(2)
    def test_get_booking(self):
        BookingsAPIRequestsV1_QA2().get_booking()

    @pytest.mark.order(3)
    def test_update_booking(self):
        BookingsAPIRequestsV1_QA2().update_booking()

    @pytest.mark.order(4)
    def test_get_bookingupdate(self):
        BookingsAPIRequestsV1_QA2().get_bookingupdate()

    @pytest.mark.order(5)
    def test_assign_new_booking(self):
        BookingsAPIRequestsV1_QA2().assign_new_booking()

    @pytest.mark.order(6)
    def test_get_new_booking(self):
        BookingsAPIRequestsV1_QA2().get_new_booking()

    @pytest.mark.order(7)
    def test_unassign_booking(self):
        BookingsAPIRequestsV1_QA2().unassign_booking()

    @pytest.mark.order(8)
    def test_get_unassign_booking(self):
        BookingsAPIRequestsV1_QA2().get_unassign_booking()

    @pytest.mark.order(9)
    def test_assign_new_bkg_put(self):
        BookingsAPIRequestsV1_QA2().assign_new_bkg_put()

    @pytest.mark.order(10)
    def test_delete_booking(self):
        BookingsAPIRequestsV1_QA2().delete_booking()
