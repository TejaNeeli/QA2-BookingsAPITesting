# python
class V1Booking:
    def booking_v1(self, reefers, booked_temperature, action, shipper="ShipperEntity"):
        """
        Build booking XML using provided reefers and temperature.
        reefers: list of reeferIds like ["FBWS0000001", ...]
        booked_temperature: int or str from user input
        action: "associate" or "dissociate"
        shipper: optional shipper name
        """
        if action.lower() not in {"associate", "dissociate"}:
            raise ValueError("Invalid action: must be 'associate' or 'dissociate'")
        items = []
        for r in reefers:
            rid = str(r).strip()
            if not rid:
                raise ValueError("Invalid reeferId: cannot be empty")
            items.append(
                f"""
        <reefers>
            <reefer>
                <action>{action.lower()}</action>
                <reeferId>{rid}</reeferId>
                <cargoCare />
            </reefer>
        </reefers>"""
            )

        return (
            f"""<booking>{''.join(items)}
        <bookedTemperature>{booked_temperature}</bookedTemperature>
        <Shipper>{shipper}</Shipper>
    </booking>"""
        )


