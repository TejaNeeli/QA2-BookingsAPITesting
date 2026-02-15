class QA2V2Booking:
    def QA2BookingV2initial(self):
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
                            "bookedTemperature": "10.0",
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

    def QA2BookingV2Update(self):
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

    def QA2BookingV2Unassign(self):
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
