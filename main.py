import tkinter as tk
import numpy as np
import math

# Размеры окна
WIDTH, HEIGHT = 800, 600
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2  # Центр координат в системе Canvas

# Преобразование координат из математических в координаты холста (Canvas)
def to_canvas_coords(x, y):
    return CENTER_X + x, CENTER_Y - y  # Canvas: X вправо, Y вниз

class Shape:
    def __init__(self, canvas):
        self.canvas = canvas
        self.color = 'blue'           # Цвет прямоугольника
        self.star_color = 'black'     # Цвет звезды (не используется, но можно задать)
        self.shadow_color = 'gray20'  # Цвет заливки звезды (делает её объемной)

        # Исходные точки прямоугольника (левая нижняя, правая нижняя, правая верхняя, левая верхняя)
        self.original_rect_points = np.array([
            [-91, -55],
            [90, -55],
            [90, 100],
            [-91, 100]
        ])

        # --- Создание перевернутой объемной трехконечной звезды ---
        self.star_center = [0, 0]          # Центр звезды (в центре прямоугольника)
        self.star_radius = 100             # Длина луча от центра до края
        self.star_width = 60               # Ширина каждого луча в градусах
        self.original_star_triangles = []  # Список треугольников, составляющих звезду

        angles_deg = [90, 210, 330]  # Углы направлений лучей (перевернутая звезда)

        for angle_deg in angles_deg:
            angle = math.radians(angle_deg)                     # Угол в радианах
            angle_left = angle - math.radians(self.star_width) # Левый край луча
            angle_right = angle + math.radians(self.star_width) # Правый край луча

            # Кончик луча (дальний конец)
            tip_x = self.star_radius * math.cos(angle)
            tip_y = self.star_radius * math.sin(angle)

            # Левые и правые боковые грани луча (не такие длинные, чтобы выглядело объемно)
            side1_x = self.star_radius * 0.2 * math.cos(angle_left)
            side1_y = self.star_radius * 0.2 * math.sin(angle_left)

            side2_x = self.star_radius * 0.2 * math.cos(angle_right)
            side2_y = self.star_radius * 0.2 * math.sin(angle_right)

            # Треугольник: центр -> левая грань -> кончик -> правая грань
            triangle = [
                [0, 0],                # Центр
                [side1_x, side1_y],   # Левая грань луча
                [tip_x, tip_y],       # Кончик луча
                [side2_x, side2_y]    # Правая грань луча
            ]
            self.original_star_triangles.append(triangle)

        # Копируем исходные точки в текущие (для трансформаций)
        self.rect_points = self.original_rect_points.copy()
        self.star_triangles = [np.array(tri) for tri in self.original_star_triangles]

        self.rect_id = None    # ID прямоугольника на холсте
        self.star_ids = []     # ID всех частей звезды
        self.draw()            # Отрисовка

    def draw(self):
        # Очистка предыдущих фигур
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        for sid in self.star_ids:
            self.canvas.delete(sid)
        self.star_ids.clear()

        # --- Отрисовка прямоугольника ---
        coords = []
        for x, y in self.rect_points:
            cx, cy = to_canvas_coords(x, y)
            coords.extend([cx, cy])
        self.rect_id = self.canvas.create_polygon(coords, fill='', outline=self.color, width=2)

        # --- Отрисовка звезды (каждый треугольник) ---
        for tri in self.star_triangles:
            coords = []
            for x, y in tri:
                cx, cy = to_canvas_coords(x, y)
                coords.extend([cx, cy])
            poly = self.canvas.create_polygon(coords, fill=self.shadow_color, outline='black')
            self.star_ids.append(poly)

    def apply_transform(self, matrix):
        # --- Преобразование прямоугольника ---
        transformed = []
        for x, y in self.rect_points:
            vec = np.array([x, y, 1])     # Однородные координаты
            res = matrix @ vec            # Умножение на матрицу
            transformed.append([res[0], res[1]])
        self.rect_points = np.array(transformed)

        # --- Преобразование звезды ---
        new_star = []
        for tri in self.star_triangles:
            new_tri = []
            for x, y in tri:
                vec = np.array([x, y, 1])
                res = matrix @ vec
                new_tri.append([res[0], res[1]])
            new_star.append(np.array(new_tri))
        self.star_triangles = new_star

        self.draw()  # Перерисовка

    def reset(self):
        # Сброс всех фигур к исходному состоянию
        self.rect_points = self.original_rect_points.copy()
        self.star_triangles = [tri.copy() for tri in self.original_star_triangles]
        self.draw()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Преобразования фигур")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='white')
        self.canvas.pack(side=tk.LEFT)

        self.create_axes()               # Рисуем оси координат
        self.shape = Shape(self.canvas) # Создаем фигуру
        self.build_controls()           # Панель управления

    def create_axes(self):
        # Отображение осей координат
        self.canvas.create_line(0, CENTER_Y, WIDTH, CENTER_Y, fill='gray')    # X-ось
        self.canvas.create_line(CENTER_X, 0, CENTER_X, HEIGHT, fill='gray')   # Y-ось

    def build_controls(self):
        # Создание кнопок управления
        frame = tk.Frame(self.root)
        frame.pack(side=tk.RIGHT, padx=10, pady=10)

        tk.Button(frame, text="Перенос по X", command=self.translate_x).pack(fill='x')
        tk.Button(frame, text="Перенос по Y", command=self.translate_y).pack(fill='x')
        tk.Button(frame, text="Отражение по OX", command=self.reflect_x).pack(fill='x')
        tk.Button(frame, text="Отражение по OY", command=self.reflect_y).pack(fill='x')
        tk.Button(frame, text="Отражение по Y=X", command=self.reflect_xy).pack(fill='x')
        tk.Button(frame, text="Масштабирование", command=self.scale).pack(fill='x')
        tk.Button(frame, text="Поворот (центр)", command=self.rotate_origin).pack(fill='x')
        tk.Button(frame, text="Поворот (точка)", command=self.rotate_point).pack(fill='x')
        tk.Button(frame, text="Сброс", command=self.shape.reset).pack(fill='x')

    def get_value(self, prompt):
        # Диалоговое окно для ввода чисел
        return tk.simpledialog.askfloat("Ввод", prompt)

    def translate_x(self):
        dx = self.get_value("Введите dx:")
        if dx is not None:
            matrix = np.array([[1, 0, dx], [0, 1, 0], [0, 0, 1]])
            self.shape.apply_transform(matrix)

    def translate_y(self):
        dy = self.get_value("Введите dy:")
        if dy is not None:
            matrix = np.array([[1, 0, 0], [0, 1, dy], [0, 0, 1]])
            self.shape.apply_transform(matrix)

    def reflect_x(self):
        matrix = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]])
        self.shape.apply_transform(matrix)

    def reflect_y(self):
        matrix = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.shape.apply_transform(matrix)

    def reflect_xy(self):
        matrix = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 1]])
        self.shape.apply_transform(matrix)

    def scale(self):
        sx = self.get_value("Масштаб по X:")
        sy = self.get_value("Масштаб по Y:")
        if sx is not None and sy is not None:
            matrix = np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]])
            self.shape.apply_transform(matrix)

    def rotate_origin(self):
        angle = self.get_value("Угол в градусах:")
        if angle is not None:
            rad = math.radians(angle)
            matrix = np.array([
                [math.cos(rad), -math.sin(rad), 0],
                [math.sin(rad),  math.cos(rad), 0],
                [0, 0, 1]
            ])
            self.shape.apply_transform(matrix)

    def rotate_point(self):
        x0 = self.get_value("X центра поворота:")
        y0 = self.get_value("Y центра поворота:")
        angle = self.get_value("Угол в градусах:")
        if x0 is not None and y0 is not None and angle is not None:
            rad = math.radians(angle)
            T1 = np.array([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]])
            R = np.array([
                [math.cos(rad), -math.sin(rad), 0],
                [math.sin(rad),  math.cos(rad), 0],
                [0, 0, 1]
            ])
            T2 = np.array([[1, 0, x0], [0, 1, y0], [0, 0, 1]])
            matrix = T2 @ R @ T1
            self.shape.apply_transform(matrix)

# Запуск приложения
if __name__ == "__main__":
    import tkinter.simpledialog
    root = tk.Tk()
    app = App(root)
    root.mainloop()
