class V3Booking:
    def booking_v3(self,drys, reefers, booked_temperature, action, shipper="Shipper Entity", temperature_qualifier="Celsius"):
        """
        Build V3 booking JSON dynamically based on QA2 structure.
        reefers: list of reeferIds like ["FBWS0000001", ...]
        booked_temperature: str or number from user input
        action: "associate" or "dissociate"
        shipper: optional shipper name
        temperature_qualifier: e.g., "Celsius"
        """
        if str(action).lower() not in {"associate", "dissociate"}:
            raise ValueError("Invalid action: must be 'associate' or 'dissociate'")

        asset_items = []
        for d in drys:
            asset_items.append({
                "action": str(action).lower(),
                "assetId": str(d).strip(),
                "cargoCare": "DEFAULT",
                "commodity": "apples",
                "STCC": "01232",
                "HS": "0803",
                "ventSetting": "35",
                "HVFlag": "false",
                "serviceLevel": "premium",
                "accessCodes": {
                    "accessCode": [
                        ""
                    ]
                }
            },)
        for r in reefers:
            rid = str(r).strip()
            if not rid:
                raise ValueError("Invalid assetId: cannot be empty")
            asset_items.append(
                {
                "action": str(action).lower(),
                "assetId": rid,
                "cargoCare": "DEFAULT",
                "commodity": "apples",
                "STCC": "01232",
                "HS": "0803",
                "ventSetting": "35",
                "HVFlag": "false",
                "serviceLevel": "premium",
                "accessCodes": {
                    "accessCode": [
                        ""
                    ]
                },
                "reefer": {
                    "bookedTemperature": str(float(booked_temperature)),
                    "bookedTemperatureQualifier": temperature_qualifier,
                    "bookedTemperatureMin": "-30.0",
                    "bookedTemperatureMax": "30.0",
                    "humidity": "70",
                    "gensetId": "WXYZ9876543",
                    "CA": {
                        "O2Setpoint": "15.0",
                        "O2SetpointMin": "13.0",
                        "O2SetpointMax": "17.0",
                        "CO2Setpoint": "15.0",
                        "CO2SetpointMin": "13.0",
                        "CO2SetpointMax": "17.0"
                    },
                    "CT": {
                        "CTDays": "14",
                        "CTTemperatureUnit": "Celsius",
                        "USDAMaxTemperature": "3.0",
                        "postCTTemperature": "8.0",
                        "postCTTemperatureDeviation": "5.0",
                        "postCTVentSetting": "15 CFM"
                    }
                }
            })

        return {
            "booking": {
                "BLNumber": "SHPUABC10055123",
                "parties": {
                    "shipper": shipper,
                    "shipperCode": "ShipperCode",
                    "consignee": "Consignee",
                    "customer": "Customer",
                    "agent": "Agent",
                    "contractParty": "Contract",
                    "consolidation": "Consolidation",
                    "forwarder": "Forwarder",
                    "notify": "Notify"
                },
                "routing": {
                    "vessel": "VVC",
                    "voyage": "12E",
                    "vesselETD": "2025-02-15T08:00:00",
                    "vesselETA": "2025-02-18T14:00:00",
                    "POR": "USORL",
                    "POL": "USJAX",
                    "POD": "PRSJU",
                    "DEL": "PRCBJ"
                },
                "assets": {
                    "asset": asset_items
                }
            }
        }


    def QA2BookingV3_singlereefer(self, reefers, booked_temperature, action, shipper="Shipper", temperature_qualifier="Celsius"):
        """
        Build V3 booking JSON dynamically based on QA2 structure.
        """
        return {
            "booking": {
                "BLNumber": "SHPUABC10055123",
                "parties": {
                    "shipper": "Shipper",
                    "shipperCode": "ShipperCode",
                    "consignee": "Consignee",
                    "customer": "Customer",
                    "agent": "Agent",
                    "contractParty": "Contract",
                    "consolidation": "Consolidation",
                    "forwarder": "Forwarder",
                    "notify": "Notify"
                },
                "routing": {
                    "vessel": "VVC",
                    "voyage": "12E",
                    "vesselETD": "2025-02-15T08:00:00",
                    "vesselETA": "2025-02-18T14:00:00",
                    "POR": "USORL",
                    "POL": "USJAX",
                    "POD": "PRSJU",
                    "DEL": "PRCBJ"
                },
                "assets": {
                    "asset": [
                        {
                            "action": "associate",
                            "assetId": "ABCN0000007",
                            "cargoCare": "DEFAULT",
                            "commodity": "apples",
                            "STCC": "01235",
                            "HS": "0803",
                            "ventSetting": "35",
                            "HVFlag": "false",
                            "serviceLevel": "premium",
                            "accessCodes": {
                                "accessCode": [
                                    "DryBooking"
                                ]
                            }
                        },
                        {
                            "action": "associate",
                            "assetId": "SPCC0009805",
                            "cargoCare": "DEFAULT",
                            "commodity": "apples",
                            "STCC": "01232",
                            "HS": "0803",
                            "ventSetting": "35",
                            "HVFlag": "false",
                            "serviceLevel": "premium",
                            "accessCodes": {
                                "accessCode": [
                                    "DryBooking"
                                ]
                            },
                            "reefer": {
                                "bookedTemperature": "14.5",
                                "bookedTemperatureQualifier": "Celsius",
                                "bookedTemperatureMin": "12.0",
                                "bookedTemperatureMax": "16.0",
                                "humidity": "70",
                                "gensetId": "WXYZ9876543",
                                "CA": {
                                    "O2Setpoint": "15.0",
                                    "O2SetpointMin": "13.0",
                                    "O2SetpointMax": "17.0",
                                    "CO2Setpoint": "15.0",
                                    "CO2SetpointMin": "13.0",
                                    "CO2SetpointMax": "17.0"
                                },
                                "CT": {
                                    "CTDays": "14",
                                    "CTTemperatureUnit": "Celsius",
                                    "USDAMaxTemperature": "3.0",
                                    "postCTTemperature": "8.0",
                                    "postCTTemperatureDeviation": "5.0",
                                    "postCTVentSetting": "15 CFM"
                                }
                            }
                        }
                    ]
                }
            }
        }

    def QA2BookingV3_multiplereefers(self):
        return {
    "booking": {
        "BLNumber": "SHPUABC10055123",
        "parties": {
            "shipper": "Shipper",
            "shipperCode": "ShipperCode",
            "consignee": "Consignee",
            "customer": "Customer",
            "agent": "Agent",
            "contractParty": "Contract",
            "consolidation": "Consolidation",
            "forwarder": "Forwarder",
            "notify": "Notify"
        },
        "routing": {
            "vessel": "VVC",
            "voyage": "12E",
            "vesselETD": "2022-02-15T08:00:00",
            "vesselETA": "2022-02-18T14:00:00",
            "POR": "USORL",
            "POL": "USJAX",
            "POD": "PRSJU",
            "DEL": "PRCBJ"
        },
        "assets": {
            "asset": [
                {
                    "action": "associate",
                    "assetId": "FBWS0000001",
                    "cargoCare": "DEFAULT",
                    "commodity": "apples",
                    "STCC": "01235",
                    "HS": "0803",
                    "ventSetting": "38",
                    "HVFlag": "false",
                    "serviceLevel": "premium",
                    "accessCodes": {
                        "accessCode": [
                            "DryBooking"
                        ]
                    },
                    "reefer": {
                        "bookedTemperature": "13.5",
                        "bookedTemperatureQualifier": "Celsius",
                        "bookedTemperatureMin": "10.0",
                        "bookedTemperatureMax": "14.0",
                        "humidity": "70",
                        "gensetId": "WXYZ9876543",
                        "CA": {
                            "O2Setpoint": "15.0",
                            "O2SetpointMin": "13.0",
                            "O2SetpointMax": "17.0",
                            "CO2Setpoint": "15.0",
                            "CO2SetpointMin": "13.0",
                            "CO2SetpointMax": "17.0"
                        },
                        "CT": {
                            "CTDays": "14",
                            "USDAMaxTemperature": "3.0",
                            "postCTTemperature": "8.0",
                            "postCTTemperatureDeviation": "5.0",
                            "postCTVentSetting": "15 CFM"
                        }
                    }
                }
            ]
        }
    }
}

    def QA2BookingV3_Unassignsinglereefer(self):
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
