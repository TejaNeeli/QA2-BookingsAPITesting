class QA2V1Booking:
    def QA2BookingV1initial(self):
        return """
    <booking>
        <reefers>
            <reefer>
                <action>associate</action>
                <reeferId>FBWS0000001</reeferId>
                <cargoCare />
            </reefer>
        </reefers>
        <reefers>
            <reefer>
                <action>associate</action>
                <reeferId>FBWS0000003</reeferId>
                <cargoCare />
            </reefer>
        </reefers>
        <bookedTemperature>36</bookedTemperature>
        <Shipper>ShipperEntity</Shipper>
    </booking>"""

    def QA2BookingV1Update(self):
        return """
        <booking>
            <reefers>
                <reefer>
                    <action>associate</action>
                    <reeferId>FBWS0000001</reeferId>
                    <cargoCare />
                </reefer>
            </reefers>
            <reefers>
                <reefer>
                    <action>associate</action>
                    <reeferId>FBWS0000003</reeferId>
                    <cargoCare />
                </reefer>
            </reefers>
            <bookedTemperature>39</bookedTemperature>
            <Shipper>ShipperEntity</Shipper>
        </booking>"""

    def QA2BookingV1Unassign(self):
        return """
    <booking>
        <reefers>
            <reefer>
                <action>dissociate</action>
                <reeferId>FBWS0000001</reeferId>
                <cargoCare />
            </reefer>
            <reefer>
                <action>associate</action>
                <reeferId>FBWS0000003</reeferId>
                <cargoCare />
            </reefer>
        </reefers>
        <bookedTemperature>39</bookedTemperature>
        <Shipper>ShipperEntity</Shipper>
    </booking>"""
