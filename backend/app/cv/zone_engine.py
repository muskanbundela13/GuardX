import cv2
import numpy as np


class ZoneEngine:
    def __init__(self, zones):
        self.zones = zones

    def get_zone(self, bounding_box):
        x1, y1, x2, y2 = bounding_box

        center_x = int((x1 + x2) / 2)
        bottom_y = int(y2)

        point = (center_x, bottom_y)

        for zone_name, polygon in self.zones.items():
            polygon_points = np.array(polygon, dtype=np.int32)

            inside = cv2.pointPolygonTest(
                polygon_points,
                point,
                False
            )

            if inside >= 0:
                return zone_name

        return None