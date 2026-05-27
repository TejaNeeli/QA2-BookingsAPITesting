class fleetAuthorizationV2:
    def QA2_autho_apple(self):
        return {
            "Content-Type": "application/json",
            "Authorization": "Basic YXBwbGU6dGVzdGFwaUAx"
        }
    def Integ_autho_cdhinterna(self):
        return {
            "Content-Type": "application/json",
            "Authorization": "Basic Q0RISW50ZXJuYWw6dGVzdGFwaUAx"
        }
    def ZimInteg1_autho_integ1fleet1(self):
        return {
            "Content-Type": "application/json",
            "Authorization": "Basic emltcmN3aTFmMTpKa0s5eEZaMngz"
        }
    def ZimInteg2_autho_integ2fleet1(self):
        return {
            "Content-Type": "application/json",
            "Authorization": "Basic emltcmN3aTJmMTpId014VndyNg=="
        }
    def MATSONInteg_autho_matsonfleet(self):
        return {
            "Content-Type": "application/xml",
            "Authorization": "Basic bWF0c29uYmtnYXBpOjNBdDUwbmJrZ0BQMQ=="
        }
    def Prod_autho_vcfleet(self):
        return {
            "Content-Type": "application/json",
            "Authorization": "Basic dmVzc2VsY29ubmVjdDp0ZXN0YXBpQDE="
        }