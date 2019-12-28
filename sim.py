import pygame
import cubes
import geometry
import math
import collections

SubFace = collections.namedtuple('SubFace', ['face', 'o', 'p'])
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700

SIDE = 200
SCREEN_DIST = SIDE / math.sqrt(2) + 1
EYE_DIST = SCREEN_DIST + 2 * SIDE  # the bigger it is, the closer to no perspective, best around SCREEN_DIST + SIDE
DOT_SIZE = 5

BLACK = 0, 0, 0
WHITE = 255, 255, 255
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
YELLOW = 255, 255, 0
MAGENTA = 255, 0, 255
CYAN = 0, 255, 255
ORANGE = 255, 122, 0
BACKGROUND_COLOR = ORANGE

IS_ORTHOGONAL = False
MIN_DISTANCE = -50
CHANGE_DIST = 50

COLORING = True
SHADING = True

DIVISOR = 10
LIGHT_VECTOR = geometry.Vector(0, 0, 1)


def get_face_points(face):
    corners = []
    for corner in face.corners:
        corners += [(corner.x, corner.y)]
    return corners


class Simulation3D:
    def __init__(self):
        self._running = True
        self._cube = cubes.Cube(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 0, SIDE, SCREEN_DIST, EYE_DIST)
        self._clock = pygame.time.Clock()
        self._angle = 0
        self._this_rel = (0, 0)
        self._since_last_rel = (0, 0)
        self._screen_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self._trans_surface = None

    def run(self):
        pygame.init()

        self._this_rel = pygame.mouse.get_rel()
        self._resize_surface()
        self._running = True

        while self._running:
            # self._clock.tick(1000000)
            self._handle_events()
            self._handle_mouse_clicks()

            self._handle_keys()
            self._redraw()
        pygame.quit()

    def _resize_surface(self) -> None:
        pygame.display.set_mode(self._screen_size, pygame.RESIZABLE)
        self._cube.change_center(geometry.Vector(self._screen_size[0] / 2, self._screen_size[1] / 2, 0))

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._end_simulation()

            elif event.type == pygame.VIDEORESIZE:
                self._screen_size = event.size
                self._resize_surface()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self._cube.rotate((self._cube.length / math.sqrt(2), 0), True, False, False)
                elif event.key == pygame.K_d:
                    self._cube.rotate((-self._cube.length / math.sqrt(2), 0), True, False, False)
                elif event.key == pygame.K_w:
                    self._cube.rotate((0, -self._cube.length / math.sqrt(2)), False, True, False)
                elif event.key == pygame.K_s:
                    self._cube.rotate((0, self._cube.length / math.sqrt(2)), False, True, False)

    def _handle_keys(self):
        circle_magnitude = self._cube.length / math.sqrt(math.pow(50, 2))

        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self._cube.rotate((self._cube.length / 50, 0), True, False, False)

        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self._cube.rotate((-self._cube.length / 50, 0), True, False, False)

        if pygame.key.get_pressed()[pygame.K_UP]:
            self._cube.rotate((0, -self._cube.length / 50), False, True, False)

        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self._cube.rotate((0, self._cube.length / 50), False, True, False)

        if pygame.key.get_pressed()[pygame.K_l]:
            self._cube.rotate((-circle_magnitude, -circle_magnitude), False, False, True)

        if pygame.key.get_pressed()[pygame.K_j]:
            self._cube.rotate((circle_magnitude, circle_magnitude), False, False, True)

        if pygame.key.get_pressed()[pygame.K_n] and self._cube.center_to_screen_dist >= MIN_DISTANCE + CHANGE_DIST:
            # zoom in
            self._cube.add_distance(-CHANGE_DIST)

        if pygame.key.get_pressed()[pygame.K_m]:
            # zoom out
            self._cube.add_distance(CHANGE_DIST)

        self._handle_events()

    def _handle_mouse_clicks(self):
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            mx, my = mouse_pos[0], mouse_pos[1]
            x, y = self._cube.get_x(), self._cube.get_y()
            max_length = self._cube.length / math.sqrt(2)

            # move from where mouse was 1/7s ago to where it is now
            pygame.mouse.get_rel()
            self._clock.tick(7)
            self._handle_events()
            self._this_rel = pygame.mouse.get_rel()
            self._this_rel = -self._this_rel[0], self._this_rel[1]

            if x - max_length < mx < x + max_length and y - max_length < my < y + max_length:
                self._cube.rotate(self._this_rel, True, True, False)
            else:
                self._cube.rotate(self._this_rel, False, False, True, mouse_pos)

            self._handle_events()

    def _redraw(self):
        surface = pygame.display.get_surface()
        surface.fill(BACKGROUND_COLOR)
        self._trans_surface = pygame.Surface(self._screen_size, pygame.SRCALPHA)

        self._draw_cube(COLORING, SHADING)

        surface.blit(self._trans_surface, (0, 0))
        pygame.display.flip()

    def _draw_cube(self, coloring, shading):
        surface = pygame.display.get_surface()

        if IS_ORTHOGONAL:
            faces = self._cube.orthogonal_faces
        else:
            faces = self._cube.perspective_faces

        if coloring:
            for key in faces:
                if key == 'CBAD':
                    pygame.draw.polygon(surface, RED, get_face_points(faces[key]))
                    pygame.draw.lines(surface, BLACK, True, get_face_points(faces[key]))
                elif key == 'CDEF':
                    pygame.draw.polygon(surface, GREEN, get_face_points(faces[key]))
                    pygame.draw.lines(surface, BLACK, True, get_face_points(faces[key]))
                elif key == 'GFEH':
                    pygame.draw.polygon(surface, BLUE, get_face_points(faces[key]))
                    pygame.draw.lines(surface, BLACK, True, get_face_points(faces[key]))
                elif key == 'GHAB':
                    pygame.draw.polygon(surface, YELLOW, get_face_points(faces[key]))
                    pygame.draw.lines(surface, BLACK, True, get_face_points(faces[key]))
                elif key == 'HEDA':
                    pygame.draw.polygon(surface, MAGENTA, get_face_points(faces[key]))
                    pygame.draw.lines(surface, BLACK, True, get_face_points(faces[key]))
                elif key == 'BCFG':
                    pygame.draw.polygon(surface, CYAN, get_face_points(faces[key]))
                    pygame.draw.lines(surface, BLACK, True, get_face_points(faces[key]))

        if shading:
            self._draw_shading(DIVISOR)

    def _draw_shading(self, divisor: int):
        faces = self._cube.orthogonal_faces
        all_sub_faces = {}
        keys = list(faces.keys())
        center = geometry.Vector(self._cube.get_x(), self._cube.get_y(), self._cube.get_z())

        for key_idx, key in enumerate(keys):
            face = faces[key]
            first_corner = face.corners[0]

            sub_face_displacements = []
            for corner_idx, corner in enumerate(face.corners):
                delta = corner.minus(first_corner)

                xy = math.sqrt(math.pow(delta.x, 2) + math.pow(delta.y, 2))
                xz = math.sqrt(math.pow(delta.x, 2) + math.pow(delta.z, 2))

                point = geometry.Vector(xy / divisor * math.cos(math.atan2(delta.y, delta.x)),
                                        xy / divisor * math.sin(math.atan2(delta.y, delta.x)),
                                        xz / divisor * math.sin(math.atan2(delta.z, delta.x)))

                sub_face_displacements += [point]

            d1 = sub_face_displacements[0]
            d2 = sub_face_displacements[1]
            d3 = sub_face_displacements[2]
            d4 = sub_face_displacements[3]

            curr_sub_faces = []
            for i in range(divisor):
                start = first_corner.minus(center).plus(d4.times(i))
                for j in range(divisor):
                    o_point1 = start.plus(d1).plus(center)
                    o_point2 = start.plus(d2).plus(center)
                    o_point3 = start.plus(d3).plus(center)
                    o_point4 = start.plus(d4).plus(center)

                    o_points = [o_point1, o_point2, o_point3, o_point4]
                    o_sub_face = geometry.Face(o_points, cubes.face_center(o_points))

                    p_point1 = self._cube.orthogonal_to_perspective(o_point1)
                    p_point2 = self._cube.orthogonal_to_perspective(o_point2)
                    p_point3 = self._cube.orthogonal_to_perspective(o_point3)
                    p_point4 = self._cube.orthogonal_to_perspective(o_point4)
                    p_sub_face = cubes.PerspectiveFace([p_point1, p_point2, p_point3, p_point4])

                    curr_sub_faces += [SubFace(face, o_sub_face, p_sub_face)]
                    start = start.plus(d2)

            all_sub_faces.update({key: curr_sub_faces})  # give all_sub_faces same keys as orthogonal_faces

        surface = pygame.display.get_surface()
        for curr_sub_faces in all_sub_faces.values():
            for sub_face in curr_sub_faces:
                center_to_sub_face = cubes.face_center(sub_face.o.corners).minus(center)
                alpha = center_to_sub_face.angle_between_vectors(LIGHT_VECTOR) * 255 / math.pi

                if IS_ORTHOGONAL:
                    if sub_face.o.normal_vector.z > 0:
                        pygame.draw.polygon(self._trans_surface, (0, 0, 0, alpha), get_face_points(sub_face.o))
                else:
                    eye_vector = geometry.Vector(center.x, center.y, center.z + self._cube.center_to_eye_dist)
                    face_center = cubes.face_center(sub_face.face.corners)
                    eye_to_face = face_center.minus(eye_vector)

                    if sub_face.face.normal_vector.angle_between_vectors(eye_to_face) >= math.pi / 2:
                        pygame.draw.polygon(self._trans_surface, (0, 0, 0, alpha), get_face_points(sub_face.p))

    def _end_simulation(self):
        self._running = False


if __name__ == '__main__':
    Simulation3D().run()
