class ZoneEventDetector:
    def __init__(self):
        self.previous_zones = {}

    def update(self, track_id, current_zone):
        previous_zone = self.previous_zones.get(track_id)

        event = None

        if previous_zone != current_zone:

            if current_zone is not None:
                event = {
                    "type": "ZONE_ENTRY",
                    "track_id": track_id,
                    "zone": current_zone
                }

            elif previous_zone is not None:
                event = {
                    "type": "ZONE_EXIT",
                    "track_id": track_id,
                    "zone": previous_zone
                }

        self.previous_zones[track_id] = current_zone

        return event