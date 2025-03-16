import tkinter as tk
import numpy as np
import math

WIDTH, HEIGHT = 800, 600
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2

def to_canvas_coords(x, y):
    return CENTER_X + x, CENTER_Y - y

def multiply_matrix(matrix, point):
    return matrix @ point

def create_rotation_matrix(angle_deg):
    rad = math.radians(angle_deg)
    return np.array([
        [math.cos(rad), -math.sin(rad), 0],
        [math.sin(rad),  math.cos(rad), 0],
        [0, 0, 1]
    ])

def create_translation_matrix(dx, dy):
    return np.array([
        [1, 0, dx],
        [0, 1, dy],
        [0, 0, 1]
    ])

class Gear:
    def __init__(self, canvas, center_x, center_y, radius, teeth, color, initial_angle=0):
        self.canvas = canvas
        self.center = np.array([center_x, center_y])
        self.radius = radius
        self.teeth = teeth
        self.color = color
        self.angle = initial_angle  # Начальный угол для зубцового смещения
        self.items = []

        self.base_points = self.create_gear_shape()

    def create_gear_shape(self):
        points = []
        tooth_angle = 360 / self.teeth
        for i in range(self.teeth):
            angle_base = i * tooth_angle
            angle_tip = angle_base + tooth_angle / 2

            r_inner = self.radius * 0.85  # Основание зубца
            r_outer = self.radius * 1.15  # Вершина зубца

            # Левая точка основания зубца
            angle_l = math.radians(angle_base)
            x1 = r_inner * math.cos(angle_l)
            y1 = r_inner * math.sin(angle_l)

            # Вершина (острый кончик зубца)
            angle_t = math.radians(angle_tip)
            x2 = r_outer * math.cos(angle_t)
            y2 = r_outer * math.sin(angle_t)

            # Правая точка основания следующего зубца
            angle_r = math.radians(angle_base + tooth_angle)
            x3 = r_inner * math.cos(angle_r)
            y3 = r_inner * math.sin(angle_r)

            # Добавляем 3 точки треугольника-зубца
            points.append(np.array([x1, y1, 1]))
            points.append(np.array([x2, y2, 1]))
            points.append(np.array([x3, y3, 1]))
        return points

    def rotate(self, angle_delta):
        self.angle += angle_delta
        self.draw()

    def draw(self):
        for item in self.items:
            self.canvas.delete(item)
        self.items.clear()

        rot_matrix = create_rotation_matrix(self.angle)
        trans_matrix = create_translation_matrix(self.center[0], self.center[1])
        transform = trans_matrix @ rot_matrix

        coords = []
        for pt in self.base_points:
            transformed = multiply_matrix(transform, pt)
            x, y = to_canvas_coords(transformed[0], transformed[1])
            coords.extend([x, y])

        gear = self.canvas.create_polygon(coords, fill=self.color, outline='black', width=2)
        self.items.append(gear)

class GearSystem:
    def __init__(self, canvas):
        self.canvas = canvas

        # Радиусы шестерен и зубья
        r1 = 60
        r2 = 60
        r3 = 60
        t1 = 12
        t2 = 12
        t3 = 12

        # Центры по осям — чтобы касались друг друга
        x1 = - (r1 + r2)
        x2 = 0
        x3 = r2 + r3

        # Начальные углы соседних шестерен — смещение зубьев в пазы
        self.gear1 = Gear(canvas, x1, 0, r1, t1, 'lightblue', initial_angle=180 / t1)
        self.gear2 = Gear(canvas, x2, 0, r2, t2, 'lightgreen', initial_angle=0)
        self.gear3 = Gear(canvas, x3, 0, r3, t3, 'lightpink', initial_angle=180 / t3)  # сдвиг на половину зуба

        self.gears = [self.gear1, self.gear2, self.gear3]

        # Передаточные числа: противооборотные
        self.ratio = [-self.gear2.radius / self.gear1.radius,
                      1,
                     -self.gear2.radius / self.gear3.radius]

        self.animate()

    def animate(self):
        base_angle = 2
        for i, gear in enumerate(self.gears):
            gear.rotate(self.ratio[i] * base_angle)
        self.canvas.after(50, self.animate)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Механизм: шестерни с острыми зубцами")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='white')
        self.canvas.pack()
        self.draw_axes()
        self.system = GearSystem(self.canvas)

    def draw_axes(self):
        self.canvas.create_line(0, CENTER_Y, WIDTH, CENTER_Y, fill='gray')
        self.canvas.create_line(CENTER_X, 0, CENTER_X, HEIGHT, fill='gray')

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
