import math
import pygame


from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image


def download_texture(image_path: str):
    image = Image.open(image_path)
    image_bytes = image.tobytes()
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.size[0], image.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, image_bytes)
    return texture_id


class Star:
    """Класс, описывающий звезду"""
    def __init__(self, radius, texture, light_color):
        """
        Создание объекта "Звезда"
        :param radius: радиус звезды
        :param texture: текстура звезды
        :param light_color: цвет собственного освещения
        """
        self._radius = radius
        self._texture = texture
        self._light_color = light_color

    def draw(self):
        """
        Метод, отрисовывающий звезду
        :return: None
        """
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, self._light_color)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self._texture)
        sun1 = gluNewQuadric()
        gluQuadricTexture(sun1, True)
        gluSphere(sun1, self._radius, 30, 30)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()


class System:
    """Класс, описывающий систему планет"""
    def __init__(self):
        """
        Создание объекта "Система планет"
        """
        self._planets = []
        self._star = None

    def add_main_star(self, star: Star):
        """
        Метод добавления звезды
        :param star: Звезда
        :return:None
        """
        self._star = star

    def add_planet(self, planet):
        """
        Метод добавления планеты
        :param planet: Планета
        :return: None
        """
        self._planets.append(planet)

    def move_system(self):
        """
        Метод передвижения всей системы, планет, спутников
        :return: None
        """
        for planet in self._planets:
            planet.draw()  # Отрисовываем каждую планету
        self._star.draw()


class Planet:
    def __init__(self, a, e, planet_radius, period, current_angle, texture, perihelion, orbit_angle):
        """
        Создание объекта "Планета"
        :param a: Большая полуось в млн. км
        :param e: Эксцентриситет орбиты
        :param planet_radius: радиус планеты
        :param period: Период вращения вокруг Солнца в днях
        :param current_angle: Текущий угол, на котором находится планета
        :param texture: Текстура планеты
        :param perihelion: Перигелий планеты
        :param orbit_angle: Угол наклона орбиты планеты
        """
        self._a = a
        self._b = a * math.sqrt(1 - e * e)  # Высчитываем малую полуось
        self._radius = planet_radius
        self._angle_velocity = 360 / period
        self._current_angle = current_angle
        self._around_self = 0
        self._texture = texture
        self._displacement = self._a - perihelion
        self._orbit_angle = orbit_angle
        self._sputniks = []  # Массива спутников
        self._rings = []  # Массив колец планеты

    def _move(self, x, y, z):
        glPushMatrix()
        glRotatef(self._orbit_angle, 0, 0, 1)  # Поворачиваем систему на угол орбиты
        glTranslatef(x - self._displacement, y, z)  # Перемещаем планету
        for sputnik in self._sputniks:
            sputnik.draw()  # Рисуем спутники
        for ring in self._rings:
            ring.draw()  # Рисуем кольца
        glRotatef(90, 1, 0, 0)
        glRotatef(self._around_self, 0, 0, 1)  # Поворачиваем планету вокруг своей оси
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0, 0, 0))
        if self._around_self == 360:
            self._around_self = -1
        self._around_self += 1  # Увеличиваем угол поворота вокруг себя
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self._texture)  # Устанавливаем текстуру
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, True)
        gluSphere(quadric, self._radius, 20, 20)  # Рисуем сферу
        # for sputnik in self._sputniks:
        #    sputnik.draw()
        """glBegin(GL_QUAD_STRIP)
        step = 5
        for ph in range(0, 180, step):
            # glBegin(GL_QUAD_STRIP)
            for th in range(0, 361, step * 2):
                # glColor3f(0, 1, 0)
                glTexCoord2f(th / 360, ph / 180)
                glVertex3fv(make_vertices(th, ph, self._radius))
                # glColor3f(0, 0, 1)
                glTexCoord2f(th / 360, (ph + step) / 180)
                glVertex3fv(make_vertices(th, ph + step, self._radius))
            # glEnd()
        glEnd()"""
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

    def draw(self):
        if self._angle_velocity + self._current_angle > 360:
            self._current_angle = (self._angle_velocity + self._current_angle) - 360
        else:
            self._current_angle += self._angle_velocity
        # Координаты планеты
        z = self._b * math.cos(math.radians(self._current_angle))
        x = self._a * math.sin(math.radians(self._current_angle))
        y = 0
        # y = math.cos(math.radians(45))
        self._draw_orbit(x, y, z)  # Рисуем орбиту
        self._move(x, y, z)  # Перемещаем планету

    def _draw_orbit(self, x, y, z):
        glPushMatrix()
        # glTranslatef(x, y, z)
        glRotatef(self._orbit_angle, 0, 0, 1)  # Поворачиваем орбиту на угол
        glBegin(GL_LINE_STRIP)
        for i in range(361):
            glColor3f(1, 1, 1)
            glVertex3f(self._a * math.sin(math.radians(i)) - self._displacement, y,
                       self._b * math.cos(math.radians(i)))  # Рисуем точки для линии
        glEnd()
        glPopMatrix()

    def add_sputnik(self, sputnik):
        self._sputniks.append(sputnik)

    def add_ring(self, ring):
        self._rings.append(ring)


class Ring:
    """Класс, описывающий кольцо планеты"""
    def __init__(self, y, radius, texture, angle, width):
        """
        Создание объекта "Кольцо планеты"
        :param y: Координата по y
        :param radius: Расстояние удаления от планеты
        :param texture: Текстура кольца
        :param angle: Угол поворота орбиты
        :param width: Ширина кольца
        """
        self._radius = radius
        self._y = y
        self._texture = texture
        self._angle = angle
        self._width = width

    def draw(self):
        glPushMatrix()
        glRotatef(self._angle, 0, 0, 1)  # Поворачиваем орбиту на заданный угол
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self._texture)  # Включаем текстуру
        glBegin(GL_QUAD_STRIP)
        for i in range(361):
            x = math.sin(math.radians(i))
            z = math.cos(math.radians(i))
            glNormal(x, self._y, z)
            glTexCoord2f(i / 360, (z * self._radius + 1) / 2)
            glVertex3f(x * self._radius, self._y, z * self._radius)
            glTexCoord2f(i / 360, (z * (self._radius + self._width) + 1) / 2)
            glVertex3f(x * (self._radius + self._width), self._y, z * (self._radius + self._width))
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()


pygame.init()
display = (1400, 800)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
gluPerspective(45, (display[0]/display[1]), 0.1, 1000)  # Устанавливаем перспективу
glTranslatef(0, -5, -30.5)  # Смещаем оси координат на заданные значения

glEnable(GL_DEPTH_TEST)
textures = []
camera_x = 0
camera_y = -5
camera_z = -30.5

ring_texture = download_texture("images/ring.jpg")  # Текстура кольца Сатурна
saturn_ring = Ring(0, 1, ring_texture, 26.7, 0.5)  # Кольцо Сатурна
sun = download_texture("images/sun.jpg")
earth_texture = download_texture("images/earth.jpg")  # Текстура Земли
mercury_texture = download_texture("images/mercury.jpg")  # Текстура Меркурия
venus_texture = download_texture("images/venus.jpg")  # Текстура Венеры
jupiter_texture = download_texture("images/jupiter.jpg")  # Текстура Юпитера
mars_texture = download_texture("images/mars.jpg")  # Текстура Марса
saturn_texture = download_texture("images/saturn.jpg")  # Текстура Сатурна
uranus_texture = download_texture("images/uranus.jpg")  # Текстура Урана
neptun_texture = download_texture("images/neptun2.jpg")  # Текстура Нептуна
moon_texture = download_texture("images/moon.jpg")  # Текстура Луны

glEnable(GL_LIGHTING)  # Включаем расчет освещения
glEnable(GL_COLOR_MATERIAL)  # Включаем материалы

solar_system = System()
# Параметры: a, e, radius / 2, period, угол, текстура, перигелий, угол наклона орбиты
mercury = Planet(5.7, 0.2056, 0.12, 88, 0, mercury_texture, 4.6, 7.01)  # Меркурий
venus = Planet(10.8, 0.0068, 0.30, 225, 0, venus_texture, 10.7, 3.39)  # Венера
earth = Planet(14.9, 0.0167, 0.315, 365, 0, earth_texture, 14.7, 0)  # Земля
mars = Planet(22.7, 0.0933, 0.165, 686, 0, mars_texture, 20.6, 1.85)  # Марс
jupiter = Planet(77.8, 0.0487, 0.69, 4322, 0, jupiter_texture, 70.4, 1.31)  # Юпитер
saturn = Planet(142.9, 0.0557, 0.60, 10759, 0, saturn_texture, 135.3, 2.49)  # Сатурн
uranus = Planet(287.6, 0.0444, 0.5, 30685, 0, uranus_texture, 274.8, 0.77)  # Уран
neptun = Planet(450.3, 0.0112, 0.48, 60190, 0, neptun_texture, 445.2, 1.77)  # Нептун
moon = Planet(0.384, 0.0549, 0.0637, 27, 0, moon_texture, 0.363, 5.145)  # Луна
earth.add_sputnik(moon)  # Добавляем Луну к Земле
saturn.add_ring(saturn_ring)  # Добавляем кольцо к сатурну
planets = [mercury, venus, earth, mars, jupiter, saturn, uranus, neptun]
for planet in planets:
    solar_system.add_planet(planet)
sun2 = Star(4, sun, (1, 1, 1))
solar_system.add_main_star(sun2)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.K_w:
            camera_y += 0.5
            # glPushMatrix()
            glTranslatef(camera_x, camera_y, camera_z)
            # glPopMatrix()
    keys = pygame.key.get_pressed()
    """
    W - поднять камеру
    S - опустить камеру
    A - сдвинуть камеру влево
    D - сдвинуть камеру вправо
    R - сдвинуть камеру вперед
    F - сдвинуть камеру на себя
    """
    if keys[pygame.K_w]:
        glTranslatef(0, -0.2, 0)
    elif keys[pygame.K_s]:
        glTranslatef(0, 0.2, 0)
        # glTranslatef(0, camera_y, 0)
    elif keys[pygame.K_d]:
        glTranslatef(-0.2, 0, 0)
    elif keys[pygame.K_a]:
        glTranslatef(0.2, 0, 0)
    elif keys[pygame.K_r]:
        glTranslatef(0, 0, 0.4)
    elif keys[pygame.K_f]:
        glTranslatef(0, 0, -0.4)
    # glTranslatef(camera_x, camera_y, camera_z)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Очистка экрана
    light1_diffuse = [1, 1, 1]  # Цвет рассеянного излучения источника света
    light1_position = [0.0, 0.0, 0.0, 1]  # Положение источника света
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light1_diffuse)
    glLightfv(GL_LIGHT0, GL_POSITION, light1_position)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.0)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.2)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.4)
    solar_system.move_system()  # Приводим в движение планеты Солнечной системы
    pygame.display.flip()  # Обновление экрана
    pygame.time.wait(30)  # Небольшая задержка
