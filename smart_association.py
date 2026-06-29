import math


class PPEAssociator:

    def __init__(self):
        pass

    def get_center(self, box):

        x1, y1, x2, y2 = box

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        return cx, cy

    def point_inside(self, point, box):

        px, py = point

        x1, y1, x2, y2 = box

        return x1 <= px <= x2 and y1 <= py <= y2

    def distance(self, p1, p2):

        return math.sqrt(
            (p1[0] - p2[0]) ** 2 +
            (p1[1] - p2[1]) ** 2
        )

    def associate(self, tracked_persons, detections):

        results = {}

        # initialize results
        for person in tracked_persons:

            results[person["id"]] = {
                "no_helmet": False,
                "no_vest": False
            }

        # process detections
        for det in detections:

            cls = det["class"]

            ppe_box = det["box"]

            ppe_center = self.get_center(ppe_box)

            best_person = None

            best_distance = 999999

            # compare with persons
            for person in tracked_persons:

                track_id = person["id"]

                person_box = person["box"]

                # check inside person
                if not self.point_inside(
                    ppe_center,
                    person_box
                ):
                    continue

                person_center = self.get_center(
                    person_box
                )

                dist = self.distance(
                    ppe_center,
                    person_center
                )

                if dist < best_distance:

                    best_distance = dist

                    best_person = track_id

            # assign violation
            if best_person is not None:

                results[best_person][cls] = True

        return results