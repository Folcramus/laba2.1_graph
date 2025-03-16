import tkinter as tk
import numpy as np
import math

WIDTH, HEIGHT = 800, 600
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2

def to_canvas_coords(x, y):
    return CENTER_X + x, CENTER_Y - y

class Shape:
    def __init__(self, canvas):
        self.canvas = canvas
        self.color = 'blue'
        self.star_color = 'black'
        self.shadow_color = 'gray20'

        # Прямоугольник
        self.original_rect_points = np.array([
            [-91, -55],
            [90, -55],
            [90, 100],
            [-91, 100]
        ])

        # Объемная перевернутая трехконечная звезда
        self.star_center = [0, 0]
        self.star_radius = 100  # кончики касаются граней прямоугольника
        self.star_width = 60  # ширина клина в градусах
        self.original_star_triangles = []

        angles_deg = [90, 210, 330]  # перевернутая звезда

        for angle_deg in angles_deg:
            angle = math.radians(angle_deg)
            angle_left = angle - math.radians(self.star_width)
            angle_right = angle + math.radians(self.star_width)

            tip_x = self.star_radius * math.cos(angle)
            tip_y = self.star_radius * math.sin(angle)

            side1_x = self.star_radius * 0.2 * math.cos(angle_left)
            side1_y = self.star_radius * 0.2 * math.sin(angle_left)

            side2_x = self.star_radius * 0.2 * math.cos(angle_right)
            side2_y = self.star_radius * 0.2 * math.sin(angle_right)

            triangle = [
                [0, 0],  # Центр
                [side1_x, side1_y],  # Левая грань клина
                [tip_x, tip_y],  # Кончик луча
                [side2_x, side2_y]  # Правая грань клина
            ]
            self.original_star_triangles.append(triangle)

        self.rect_points = self.original_rect_points.copy()
        self.star_triangles = [np.array(tri) for tri in self.original_star_triangles]

        self.rect_id = None
        self.star_ids = []
        self.draw()

    def draw(self):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        for sid in self.star_ids:
            self.canvas.delete(sid)
        self.star_ids.clear()

        # Прямоугольник
        coords = []
        for x, y in self.rect_points:
            cx, cy = to_canvas_coords(x, y)
            coords.extend([cx, cy])
        self.rect_id = self.canvas.create_polygon(coords, fill='', outline=self.color, width=2)

        # Звезда
        for tri in self.star_triangles:
            coords = []
            for x, y in tri:
                cx, cy = to_canvas_coords(x, y)
                coords.extend([cx, cy])
            poly = self.canvas.create_polygon(coords, fill=self.shadow_color, outline='black')
            self.star_ids.append(poly)

    def apply_transform(self, matrix):
        # Прямоугольник
        transformed = []
        for x, y in self.rect_points:
            vec = np.array([x, y, 1])
            res = matrix @ vec
            transformed.append([res[0], res[1]])
        self.rect_points = np.array(transformed)

        # Звезда
        new_star = []
        for tri in self.star_triangles:
            new_tri = []
            for x, y in tri:
                vec = np.array([x, y, 1])
                res = matrix @ vec
                new_tri.append([res[0], res[1]])
            new_star.append(np.array(new_tri))
        self.star_triangles = new_star

        self.draw()

    def reset(self):
        self.rect_points = self.original_rect_points.copy()
        self.star_triangles = [tri.copy() for tri in self.original_star_triangles]
        self.draw()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Преобразования фигур")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='white')
        self.canvas.pack(side=tk.LEFT)
        self.create_axes()

        self.shape = Shape(self.canvas)
        self.build_controls()

    def create_axes(self):
        self.canvas.create_line(0, CENTER_Y, WIDTH, CENTER_Y, fill='gray')
        self.canvas.create_line(CENTER_X, 0, CENTER_X, HEIGHT, fill='gray')

    def build_controls(self):
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

if __name__ == "__main__":
    import tkinter.simpledialog
    root = tk.Tk()
    app = App(root)
    root.mainloop()
