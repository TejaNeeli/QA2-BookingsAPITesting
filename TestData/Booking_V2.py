class V2Booking:
    def booking_v2(self, reefers, booked_temperature, action, shipper="Shipper Entity", temperature_qualifier="Celsius"):
        """
        Build V2 booking JSON using provided reefers, temperature, and action.
        reefers: list of reeferIds like ["FBWS0000001", ...]
        booked_temperature: str or number from user input
        action: "associate" or "dissociate"
        shipper: optional shipper name
        temperature_qualifier: e.g., "Celsius"
        """
        if str(action).lower() not in {"associate", "dissociate"}:
            raise ValueError("Invalid action: must be 'associate' or 'dissociate'")
        reefer_items = []
        for r in reefers:
            rid = str(r).strip()
            if not rid:
                raise ValueError("Invalid reeferId: cannot be empty")
            # Build a single-level object per reefer (no nested list)
            reefer_items.append({
                "action": str(action).lower(),
                "reeferId": rid,
                "cargoCare": "DEFAULT",
                "accessCodes": {"accessCode": [""]},
                "bookedTemperature": float(booked_temperature),
                "bookedTemperatureQualifier": temperature_qualifier,
                # Optional defaults retained; adjust as needed
                "bookedTemperatureMin": "-30.0",
                "bookedTemperatureMax": "30.0",
                "humidity": "65",
                "commodity": "apples",
                "STCC": "01232",
                "HS": "0803",
                "gensetId": "WXYZ9876543",
                "ventSetting": "35",
                "HVFlag": "false",
                "serviceLevel": "premium",
                "CAFlag": "true",
                "O2Setpoint": "15.0",
                "O2SetpointMin": "13.0",
                "O2SetpointMax": "17.0",
                "CO2Setpoint": "15.0",
                "CO2SetpointMin": "13.0",
                "CO2SetpointMax": "17.0",
                "CTFlag": "true",
                "CTDays": "14",
                "USDAMaxTemperature": "3.0",
                "postCTTemperature": "8.0",
                "postCTTemperatureDeviation": "5.0",
                "postCTVentSetting": "15 CFM"
            })
        return {
            "booking": {
                "reefers": {"reefer": reefer_items},
                "shipper": shipper,
                # Keep other fields as defaults; can be parameterized if needed
                "shipperCode": "SHIPPER1",
                "consignee": "Consignee Entity",
                "customer": "Customer Entity",
                "agent": "Agent Entity",
                "vessel": "VSLABC",
                "voyage": "12E",
                "POR": "USORL",
                "POL": "SL_Server",
                "POD": "Australia",
                "DEL": "PRCBJ",
                "vesselETD": "2022-02-15T08:00:00",
                "vesselETA": "2022-02-18T14:00:00",
                "BLNumber": "SHPUABC10022172",
                "contractParty": "Contract Entity",
                "consolidation": "Consolidation Party",
                "forwarder": "Forwarder",
                "notify": "Notify"
            }
        }

    def QA2BookingV2_multiplereefers(self):
        return {
            "booking": {
                "reefers": {
                    "reefer": [
                        {
                            "action": "associate",
                            "reeferId": "FBWS0000001",
                            "cargoCare": "CCLR-2",
                            "accessCodes": {
                                "accessCode": [
                                    ""
                                ]
                            },
                            "bookedTemperature": "10.7",
                            "bookedTemperatureQualifier": "Celsius",
                            "bookedTemperatureMin": "9.0",
                            "bookedTemperatureMax": "20.0",
                            "humidity": "65",
                            "commodity": "apples",
                            "STCC": "01232",
                            "HS": "0803",
                            "gensetId": "WXYZ9876543",
                            "ventSetting": "35",
                            "HVFlag": "false",
                            "serviceLevel": "premium",
                            "CAFlag": "true",
                            "O2Setpoint": "15.0",
                            "O2SetpointMin": "13.0",
                            "O2SetpointMax": "17.0",
                            "CO2Setpoint": "15.0",
                            "CO2SetpointMin": "13.0",
                            "CO2SetpointMax": "17.0",
                            "CTFlag": "true",
                            "CTDays": "14",
                            "USDAMaxTemperature": "3.0",
                            "postCTTemperature": "8.0",
                            "postCTTemperatureDeviation": "5.0",
                            "postCTVentSetting": "15 CFM"
                        },
                        {
                            "action": "associate",
                            "reeferId": "FBWS0000003",
                            "cargoCare": "CCLR-2",
                            "accessCodes": {
                                "accessCode": [
                                    ""
                                ]
                            },
                            "bookedTemperature": "10.7",
                            "bookedTemperatureQualifier": "Celsius",
                            "bookedTemperatureMin": "9.0",
                            "bookedTemperatureMax": "20.0",
                            "humidity": "65",
                            "commodity": "apples",
                            "STCC": "01232",
                            "HS": "0803",
                            "gensetId": "WXYZ9876543",
                            "ventSetting": "35",
                            "HVFlag": "false",
                            "serviceLevel": "premium",
                            "CAFlag": "true",
                            "O2Setpoint": "15.0",
                            "O2SetpointMin": "13.0",
                            "O2SetpointMax": "17.0",
                            "CO2Setpoint": "15.0",
                            "CO2SetpointMin": "13.0",
                            "CO2SetpointMax": "17.0",
                            "CTFlag": "true",
                            "CTDays": "14",
                            "USDAMaxTemperature": "3.0",
                            "postCTTemperature": "8.0",
                            "postCTTemperatureDeviation": "5.0",
                            "postCTVentSetting": "15 CFM"
                        }
                    ]
                },
                "shipper": "Shipper Entity",
                "shipperCode": "SHIPPER1",
                "consignee": "Consignee Entity",
                "customer": "Customer Entity",
                "agent": "Agent Entity",
                "vessel": "VSLABC",
                "voyage": "12E",
                "POR": "USORL",
                "POL": "SL_Server",
                "POD": "Australia",
                "DEL": "PRCBJ",
                "vesselETD": "2022-02-15T08:00:00",
                "vesselETA": "2022-02-18T14:00:00",
                "BLNumber": "SHPUABC10022172",
                "contractParty": "Contract Entity",
                "consolidation": "Consolidation Party",
                "forwarder": "Forwarder",
                "notify": "Notify"
            }
        }

    def QA2BookingV2_Unassignsinglereefer(self):
        return {
            "booking": {
                "reefers": {
                    "reefer": [
                        {
                            "action": "dissociate",
                            "reeferId": "FBWS0000001",
                            "cargoCare": "CCLR-2",
                            "accessCodes": {
                                "accessCode": [
                                    ""
                                ]
                            },
                            "bookedTemperature": "10.7",
                            "bookedTemperatureQualifier": "Celsius",
                            "bookedTemperatureMin": "9.0",
                            "bookedTemperatureMax": "20.0",
                            "humidity": "65",
                            "commodity": "apples",
                            "STCC": "01232",
                            "HS": "0803",
                            "gensetId": "WXYZ9876543",
                            "ventSetting": "35",
                            "HVFlag": "false",
                            "serviceLevel": "premium",
                            "CAFlag": "true",
                            "O2Setpoint": "15.0",
                            "O2SetpointMin": "13.0",
                            "O2SetpointMax": "17.0",
                            "CO2Setpoint": "15.0",
                            "CO2SetpointMin": "13.0",
                            "CO2SetpointMax": "17.0",
                            "CTFlag": "true",
                            "CTDays": "14",
                            "USDAMaxTemperature": "3.0",
                            "postCTTemperature": "8.0",
                            "postCTTemperatureDeviation": "5.0",
                            "postCTVentSetting": "15 CFM"
                        },
                        {
                            "action": "associate",
                            "reeferId": "FBWS0000003",
                            "cargoCare": "CCLR-2",
                            "accessCodes": {
                                "accessCode": [
                                    ""
                                ]
                            },
                            "bookedTemperature": "10.7",
                            "bookedTemperatureQualifier": "Celsius",
                            "bookedTemperatureMin": "9.0",
                            "bookedTemperatureMax": "20.0",
                            "humidity": "65",
                            "commodity": "apples",
                            "STCC": "01232",
                            "HS": "0803",
                            "gensetId": "WXYZ9876543",
                            "ventSetting": "35",
                            "HVFlag": "false",
                            "serviceLevel": "premium",
                            "CAFlag": "true",
                            "O2Setpoint": "15.0",
                            "O2SetpointMin": "13.0",
                            "O2SetpointMax": "17.0",
                            "CO2Setpoint": "15.0",
                            "CO2SetpointMin": "13.0",
                            "CO2SetpointMax": "17.0",
                            "CTFlag": "true",
                            "CTDays": "14",
                            "USDAMaxTemperature": "3.0",
                            "postCTTemperature": "8.0",
                            "postCTTemperatureDeviation": "5.0",
                            "postCTVentSetting": "15 CFM"
                        }
                    ]
                },
                "shipper": "Shipper Entity",
                "shipperCode": "SHIPPER1",
                "consignee": "Consignee Entity",
                "customer": "Customer Entity",
                "agent": "Agent Entity",
                "vessel": "VSLABC",
                "voyage": "12E",
                "POR": "USORL",
                "POL": "SL_Server",
                "POD": "Australia",
                "DEL": "PRCBJ",
                "vesselETD": "2022-02-15T08:00:00",
                "vesselETA": "2022-02-18T14:00:00",
                "BLNumber": "SHPUABC10022172",
                "contractParty": "Contract Entity",
                "consolidation": "Consolidation Party",
                "forwarder": "Forwarder",
                "notify": "Notify"
            }
        }
