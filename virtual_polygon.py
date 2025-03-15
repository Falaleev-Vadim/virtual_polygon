import time
from vpython import *
import math
import asyncio

scene = canvas(title="Моделирование полета снаряда", width=1200, height=600, background=color.gray(0.9))
scene.range = 5000

shot_data = []
g = 9.80665
air_density = 1.225


def calculate_trajectory(v0, angle_deg, c_d, mass, caliber_mm):
    """Расчет траектории снаряда с учетом аэродинамического сопротивления"""
    try:
        angle = math.radians(angle_deg)
        caliber = caliber_mm / 1000
        radius = caliber / 2
        area = math.pi * radius ** 2

        dt = 0.01
        x, y = 0.0, 0.0
        vx = v0 * math.cos(angle)
        vy = v0 * math.sin(angle)

        trajectory = []
        time = 0.0

        while y >= 0:
            v = math.hypot(vx, vy)
            f_drag = 0.5 * c_d * air_density * area * v ** 2
            a_drag = f_drag / mass

            ax = -a_drag * (vx / v)
            ay = -g - a_drag * (vy / v)

            vx += ax * dt
            vy += ay * dt
            x += vx * dt
            y += vy * dt
            time += dt

            trajectory.append((x, y))

            if y < 0:
                break

        return trajectory, time

    except Exception as e:
        print(f"Ошибка расчета траектории: {e}")
        return [], 0

def create_animation(trajectory, target_distance):
    """Создание анимации полета снаряда"""
    ground = box(pos=vector(target_distance * 1000 / 2, -50, 0),
                 size=vector(target_distance * 1000, 10, 100),
                 color=color.green)

    target = cylinder(pos=vector(target_distance * 1000, 0, 0),
                      axis=vector(0, 50, 0),
                      radius=30,
                      color=color.red)

    projectile = sphere(pos=vector(0, 0, 0),
                        radius=15,
                        color=color.blue,
                        make_trail=True,
                        trail_color=color.white,
                        trail_radius=5)

    scene.camera.follow(projectile)

    start_time = time.time()
    for (x, y) in trajectory:
        projectile.pos = vector(x, y, 0)
        rate(200)

    flight_time = time.time() - start_time
    return flight_time

def input_with_validation(prompt, min_val=0.0, max_val=None, numeric_type=float):
    """Ввод данных с проверкой корректности"""
    while True:
        try:
            value = numeric_type(input(prompt))
            if value < min_val:
                print(f"Значение должно быть больше {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"Значение должно быть меньше {max_val}")
                continue
            return value
        except ValueError:
            print("Введите корректное числовое значение")

async def main():
    print("Введите параметры выстрела:")
    v0 = input_with_validation("Начальная скорость (м/с, 100-2000): ", 100, 2000)
    angle = input_with_validation("Угол выстрела (градусы, 0-90): ", 0, 90)
    c_d = input_with_validation("Коэффициент сопротивления (0.1-2.0): ", 0.1, 2.0)
    mass = input_with_validation("Масса снаряда (кг, 0.1-1000): ", 0.1, 1000)
    caliber = input_with_validation("Калибр (мм, 1-500): ", 1, 500)
    distance = input_with_validation("Дистанция до цели (км, 0.1-50): ", 0.1, 50)

    trajectory, calc_time = calculate_trajectory(v0, angle, c_d, mass, caliber)

    if not trajectory:
        print("Не удалось рассчитать траекторию")
        return

    flight_time = create_animation(trajectory, distance)

    shot_data.append({
        'скорость': v0,
        'угол': angle,
        'c_d': c_d,
        'масса': mass,
        'калибр': caliber,
        'дистанция': distance,
        'траектория': trajectory,
        'расчетное время': calc_time,
        'время анимации': flight_time
    })

    max_height = max(y for (x, y) in trajectory)
    max_distance = trajectory[-1][0] if trajectory else 0
    print("\nРезультаты:")
    print(f"Максимальная высота: {max_height:.1f} м")
    print(f"Дальность полета: {max_distance:.1f} м")
    print(f"Расчетное время: {calc_time:.2f} с")
    print(f"Время анимации: {flight_time:.2f} с")

if __name__ == "__main__":
    asyncio.run(main())
    input("Нажмите Enter для выхода...")