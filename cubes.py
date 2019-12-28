import math
import geometry
import collections

PerspectiveFace = collections.namedtuple('PerspectiveFace', ['corners'])
PI = math.pi
HUGE = 1e7
TINY = 1 / HUGE
EPSILON = .0001  # big enough to avoid trouble, small enough to be accurate
BUFFER = 1 - EPSILON


class NotPairedTupleError(Exception):
    pass


def face_center(points):
    d1 = points[0].minus(points[1]).times(.5)
    d2 = points[2].minus(points[1]).times(.5)
    center = points[1].plus(d1).plus(d2)
    return center


class Cube:
    def __init__(self, x: int or float, y: int or float, z: int or float, length: int or float,
                 center_to_screen_dist: int or float, center_to_eye_dist: int or float) -> None:
        self._x = x
        self._y = y
        self._z = z

        self.length = length
        self.center_to_screen_dist = center_to_screen_dist
        self.center_to_eye_dist = center_to_eye_dist

        self.orthogonal_points = {}
        self.orthogonal_faces = {}

        self.perspective_points = {}
        self.perspective_faces = {}  # will also have normal vectors, but won't use them

        self._create_points()

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_z(self):
        return self._z

    def add_distance(self, dist):
        self.center_to_screen_dist += dist
        self.center_to_eye_dist += dist
        self._update_perspective_points()

    def change_center(self, new_center: geometry.Vector) -> None:
        x = self._x
        y = self._y
        z = self._z

        new_x = new_center.x
        new_y = new_center.y
        new_z = new_center.z

        for key in self.orthogonal_points.keys():
            self.orthogonal_points[key] = geometry.Vector(new_x + self.orthogonal_points[key].x - x,
                                                          new_y + self.orthogonal_points[key].y - y,
                                                          new_z + self.orthogonal_points[key].z - z)

        self._x = new_x
        self._y = new_y
        self._z = new_z

        self._update_perspective_points()

    def rotate(self, xy_coords: (int or float, int or float), rotate_xz: bool,
               rotate_yz: bool, rotate_xy: bool, position=(0, 0)):
        """
        Updates cube to rotate in a given direction. The magnitude of rotation is
        given by some element or both in the paired tuple passed in.
        """

        if len(xy_coords) != 2:
            raise NotPairedTupleError('Not a paired tuple. Must be exactly 2 elements')
        elif type(xy_coords[0]) not in (int, float) or type(xy_coords[1]) not in (int, float):
            raise NotPairedTupleError('Paired tuple must be made up of only ints and/or floats.')

        scale = math.sqrt(2) * PI / (2 * self.length)
        if rotate_xz:
            for point in self.orthogonal_points:
                x = self.orthogonal_points[point].x - self._x
                z = self.orthogonal_points[point].z - self._z

                # x component of xy_coords => only rotating left and right
                delta_angle = xy_coords[0] * scale
                angle = math.atan2(z, x) + delta_angle

                new_x = math.cos(angle) * math.sqrt(x * x + z * z)
                new_z = math.sin(angle) * math.sqrt(x * x + z * z)

                self.orthogonal_points[point] = \
                    geometry.Vector(self._x + new_x, self.orthogonal_points[point].y, self._z + new_z)

        if rotate_yz:
            for point in self.orthogonal_points:
                y = self.orthogonal_points[point].y - self._y
                z = self.orthogonal_points[point].z - self._z

                # y component of xy_coords = only rotating up and down
                delta_angle = xy_coords[1] * scale
                angle = math.atan2(y, z) + delta_angle

                new_y = math.sin(angle) * math.sqrt(y * y + z * z)
                new_z = math.cos(angle) * math.sqrt(y * y + z * z)

                self.orthogonal_points[point] = \
                    geometry.Vector(self.orthogonal_points[point].x, self._y + new_y, self._z + new_z)

        if rotate_xy:
            for point in self.orthogonal_points:
                x = self.orthogonal_points[point].x - self._x
                y = self.orthogonal_points[point].y - self._y

                mouse_angle = math.atan2(position[1] - self._x, position[0] - self._y)
                cos_pos = math.cos(mouse_angle)
                sin_pos = math.sin(mouse_angle)

                delta_angle = (xy_coords[0] * sin_pos + xy_coords[1] * cos_pos) * scale
                angle = math.atan2(y, x) + delta_angle

                new_y = math.sin(angle) * math.sqrt(x * x + y * y)
                new_x = math.cos(angle) * math.sqrt(x * x + y * y)

                self.orthogonal_points[point] = \
                    geometry.Vector(self._x + new_x, self._y + new_y, self.orthogonal_points[point].z)

        self._update_perspective_points()

    def _create_points(self):
        self._create_orthogonal_points()  # have to do first
        self._update_perspective_points()

    def _create_orthogonal_points(self):
        x = self._x
        y = self._y
        z = self._z
        s = self.length
        self.orthogonal_points = {'A': geometry.Vector(x - s / 2, y - s / 2, z + s / 2),  # A
                                  'B': geometry.Vector(x + s / 2, y - s / 2, z + s / 2),  # B
                                  'C': geometry.Vector(x + s / 2, y + s / 2, z + s / 2),  # C
                                  'D': geometry.Vector(x - s / 2, y + s / 2, z + s / 2),  # D
                                  'E': geometry.Vector(x - s / 2, y + s / 2, z - s / 2),  # E
                                  'F': geometry.Vector(x + s / 2, y + s / 2, z - s / 2),  # F
                                  'G': geometry.Vector(x + s / 2, y - s / 2, z - s / 2),  # G
                                  'H': geometry.Vector(x - s / 2, y - s / 2, z - s / 2)}  # H

    def _update_perspective_points(self):
        for i, key in enumerate(self.orthogonal_points):
            orthogonal_point = self.orthogonal_points[key]
            perspective_point = self.orthogonal_to_perspective(orthogonal_point)
            self.perspective_points.update({key: perspective_point})
        self._update_faces()

    def orthogonal_to_perspective(self, point):
        x = point.x - self._x
        y = point.y - self._y
        z = point.z - self._z

        e = self.center_to_eye_dist
        p = self.center_to_screen_dist
        scale = (e - p) / (e - z)

        return geometry.Point2(x * scale + self._x, y * scale + self._y)

    def _update_faces(self):
        face_keys = ['CBAD', 'CDEF', 'GFEH', 'GHAB', 'HEDA', 'BCFG']  # orthogonal_faces keys = perspective_faces keys
        for key in face_keys:
            orthogonal_face = self._face_key_to_orthogonal_face(key)
            self.orthogonal_faces.update({key: orthogonal_face})

            perspective_face = self._face_key_to_perspective_face(key)
            self.perspective_faces.update({key: perspective_face})

        self._sort_faces_keys(face_keys, 0, len(face_keys) - 1)
        self.orthogonal_faces = {key: self.orthogonal_faces[key] for key in face_keys}
        self.perspective_faces = {key: self.perspective_faces[key] for key in face_keys}

    def _face_key_to_orthogonal_face(self, faces_key: str):
        points = []
        for char in faces_key:
            point = self.orthogonal_points[char]
            points += [point]
        center = face_center(points)
        return geometry.Face(points, center)

    def _face_key_to_perspective_face(self, faces_key: str):
        points = []
        for char in faces_key:
            point = self.perspective_points[char]
            points += [point]
        return PerspectiveFace(points)

    def _sort_faces_keys(self, faces_keys: [str], low: int, high: int) -> None:
        """ From https://www.geeksforgeeks.org/python-program-for-quicksort/ """
        if low < high:
            pi = self._partition(faces_keys, low, high)

            self._sort_faces_keys(faces_keys, low, pi - 1)
            self._sort_faces_keys(faces_keys, pi + 1, high)

    def _partition(self, keys: [str], low: int, high: int) -> int:
        """ From https://www.geeksforgeeks.org/python-program-for-quicksort/ """
        i = low - 1
        pivot = self.orthogonal_faces[keys[high]].normal_vector.z

        for j in range(low, high):
            if self.orthogonal_faces[keys[j]].normal_vector.z <= pivot:
                i += 1
                keys[i], keys[j] = keys[j], keys[i]

        keys[i + 1], keys[high] = keys[high], keys[i + 1]
        return i + 1
