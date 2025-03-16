import tkinter as tk
import numpy as np
import math

# Размеры окна приложения
WIDTH, HEIGHT = 800, 600
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2  # Центр холста

# Перевод координат из математических в координаты холста (где ось Y направлена вниз)
def to_canvas_coords(x, y):
    return CENTER_X + x, CENTER_Y - y

# Умножение матрицы преобразования на вектор-точку
def multiply_matrix(matrix, point):
    return matrix @ point  # Символ @ — это умножение матриц в NumPy

# Создание матрицы поворота на заданный угол (в градусах)
def create_rotation_matrix(angle_deg):
    rad = math.radians(angle_deg)  # Перевод градусов в радианы
    return np.array([
        [math.cos(rad), -math.sin(rad), 0],
        [math.sin(rad),  math.cos(rad), 0],
        [0, 0, 1]  # Однородные координаты (3x3 матрица)
    ])

# Создание матрицы сдвига (трансляции) по x и y
def create_translation_matrix(dx, dy):
    return np.array([
        [1, 0, dx],
        [0, 1, dy],
        [0, 0, 1]
    ])

# Класс, описывающий шестерню
class Gear:
    def __init__(self, canvas, center_x, center_y, radius, teeth, color, initial_angle=0):
        self.canvas = canvas  # Холст для рисования
        self.center = np.array([center_x, center_y])  # Центр шестерни
        self.radius = radius  # Радиус окружности основания зубьев
        self.teeth = teeth  # Количество зубцов
        self.color = color  # Цвет шестерни
        self.angle = initial_angle  # Начальный угол поворота
        self.items = []  # Список графических объектов для удаления при обновлении

        # Создаем координаты зубцов
        self.base_points = self.create_gear_shape()

    # Метод для создания зубцов (треугольной формы)
    def create_gear_shape(self):
        points = []
        tooth_angle = 360 / self.teeth  # Угол между двумя соседними зубьями
        for i in range(self.teeth):
            angle_base = i * tooth_angle  # Угол левой стороны зубца
            angle_tip = angle_base + tooth_angle / 2  # Угол вершины зубца

            # Радиусы для внутренней и внешней части зубца
            r_inner = self.radius * 0.85  # Радиус основания зубца (внутренний)
            r_outer = self.radius * 1.15  # Радиус вершины зубца (внешний)

            # Точка слева у основания зубца
            angle_l = math.radians(angle_base)
            x1 = r_inner * math.cos(angle_l)
            y1 = r_inner * math.sin(angle_l)

            # Вершина зубца
            angle_t = math.radians(angle_tip)
            x2 = r_outer * math.cos(angle_t)
            y2 = r_outer * math.sin(angle_t)

            # Правая точка у основания следующего зубца
            angle_r = math.radians(angle_base + tooth_angle)
            x3 = r_inner * math.cos(angle_r)
            y3 = r_inner * math.sin(angle_r)

            # Добавляем точки одного треугольного зубца
            points.append(np.array([x1, y1, 1]))  # Левая точка
            points.append(np.array([x2, y2, 1]))  # Вершина
            points.append(np.array([x3, y3, 1]))  # Правая точка
        return points

    # Метод для поворота шестерни на определённый угол
    def rotate(self, angle_delta):
        self.angle += angle_delta
        self.draw()  # Перерисовка после поворота

    # Метод отрисовки шестерни
    def draw(self):
        # Удаляем старые графические объекты
        for item in self.items:
            self.canvas.delete(item)
        self.items.clear()

        # Матрица поворота
        rot_matrix = create_rotation_matrix(self.angle)
        # Матрица переноса к центру шестерни
        trans_matrix = create_translation_matrix(self.center[0], self.center[1])
        # Общая матрица трансформации = перенос × поворот
        transform = trans_matrix @ rot_matrix

        # Массив координат для отрисовки многоугольника
        coords = []
        for pt in self.base_points:
            transformed = multiply_matrix(transform, pt)
            x, y = to_canvas_coords(transformed[0], transformed[1])
            coords.extend([x, y])

        # Отрисовка шестерни как одного многоугольника из треугольников
        gear = self.canvas.create_polygon(coords, fill=self.color, outline='black', width=2)
        self.items.append(gear)

# Класс, создающий и анимирующий систему из трёх шестерен
class GearSystem:
    def __init__(self, canvas):
        self.canvas = canvas

        # Радиусы шестерен и количество зубьев
        r1 = 60
        r2 = 60
        r3 = 60
        t1 = 12
        t2 = 12
        t3 = 12

        # Расположение центров — шестерни соприкасаются друг с другом
        x1 = - (r1 + r2)  # Левая шестерня
        x2 = 0            # Центральная шестерня
        x3 = r2 + r3      # Правая шестерня

        # Начальные углы для правильного зацепления зубьев
        self.gear1 = Gear(canvas, x1, 0, r1, t1, 'lightblue', initial_angle=180 / t1)
        self.gear2 = Gear(canvas, x2, 0, r2, t2, 'lightgreen', initial_angle=0)
        self.gear3 = Gear(canvas, x3, 0, r3, t3, 'lightpink', initial_angle=180 / t3)

        self.gears = [self.gear1, self.gear2, self.gear3]

        # Передаточные отношения — отрицательные значения для противоположного направления вращения
        self.ratio = [
            -self.gear2.radius / self.gear1.radius,  # gear1 вращается в противоположную сторону
            1,  # gear2 — основная, вращается напрямую
            -self.gear2.radius / self.gear3.radius  # gear3 тоже противоположна gear2
        ]

        self.animate()  # Запуск анимации

    # Метод для постоянного вращения шестерен
    def animate(self):
        base_angle = 2  # Базовый угол поворота
        for i, gear in enumerate(self.gears):
            gear.rotate(self.ratio[i] * base_angle)
        # Повторить анимацию через 50 миллисекунд
        self.canvas.after(50, self.animate)

# Главный класс приложения
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Механизм: шестерни с острыми зубцами")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='white')
        self.canvas.pack()
        self.draw_axes()  # Отрисовка координатных осей
        self.system = GearSystem(self.canvas)  # Запуск системы шестерен

    # Метод рисует оси координат (для наглядности)
    def draw_axes(self):
        self.canvas.create_line(0, CENTER_Y, WIDTH, CENTER_Y, fill='gray')  # Ось X
        self.canvas.create_line(CENTER_X, 0, CENTER_X, HEIGHT, fill='gray')  # Ось Y

# Точка входа — запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()