#!/usr/bin/env python3
"""
Side-by-side two-lane road comparison.
Left: Chaos (random driving)
Right: AI (lane-aware spacing + intersection priority)
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle, Circle
import random

COLOR_BG = '#0f1419'
COLOR_ROAD = '#2b3a55'
COLOR_LANE = '#f5d442'
COLOR_TEXT = '#e5e7eb'
COLOR_CAR = '#3b82f6'
COLOR_EMERGENCY = '#f97316'

LANES_X = [-3.2, -0.8, 0.8, 3.2]
LANES_Y = [-3.2, -0.8, 0.8, 3.2]


class Car:
    def __init__(self, car_id, orientation, lane_idx, direction):
        self.car_id = car_id
        self.orientation = orientation
        self.lane_idx = lane_idx
        self.direction = direction
        self.is_emergency = random.random() < 0.15
        self.max_speed = random.uniform(0.045, 0.06) * (1.3 if self.is_emergency else 1.0)
        self.speed = self.max_speed
        self.wait_timer = 0.0

        coord = LANES_X if orientation == 'vertical' else LANES_Y
        fixed = coord[lane_idx]
        start = -5.2 if direction == 1 else 5.2

        if orientation == 'vertical':
            self.x = fixed
            self.y = start
            self.heading = 90 if direction == 1 else 270
        else:
            self.x = start
            self.y = fixed
            self.heading = 0 if direction == 1 else 180

        self.active = True

    def position(self):
        return self.x, self.y

    def move(self, dt=1.0):
        if not self.active:
            return
        if self.wait_timer > 0:
            self.wait_timer -= dt
            return

        delta = self.speed * dt * self.direction
        if self.orientation == 'vertical':
            self.y += delta
            if abs(self.y) > 5.5:
                self.active = False
        else:
            self.x += delta
            if abs(self.x) > 5.5:
                self.active = False


class Simulation:
    def __init__(self, mode='chaos'):
        self.mode = mode
        self.cars = []
        self.frame = 0
        self.spawn_interval = 20
        self.collision_count = 0

    def spawn_car(self):
        orientation = random.choice(['vertical', 'horizontal'])
        lane_idx = random.randint(0, 1) if orientation == 'vertical' else random.randint(2, 3)
        direction = random.choice([1, -1])
        car = Car(f"{self.mode}_{len(self.cars)+1}", orientation, lane_idx, direction)
        self.cars.append(car)

    def near_intersection(self, car):
        if car.orientation == 'vertical':
            return abs(car.y) < 0.6 and abs(car.x) in [LANES_X[1], LANES_X[2]]
        else:
            return abs(car.x) < 0.6 and abs(car.y) in [LANES_Y[1], LANES_Y[2]]

    def conflict(self, car):
        if not self.near_intersection(car):
            return None
        for other in self.cars:
            if other is car or not other.active:
                continue
            if car.orientation == other.orientation:
                continue
            if abs(car.x - other.x) < 0.4 and abs(car.y - other.y) < 0.4:
                return other
        return None

    def follow_gap(self, car, distance=0.6):
        for other in self.cars:
            if other is car or not other.active:
                continue
            if other.orientation != car.orientation:
                continue
            if other.lane_idx != car.lane_idx:
                continue
            if other.direction != car.direction:
                continue

            if car.orientation == 'vertical':
                gap = (other.y - car.y) * car.direction
            else:
                gap = (other.x - car.x) * car.direction

            if 0 < gap < distance:
                return gap
        return None

    def apply_ai(self, car):
        if self.mode != 'ai':
            return

        gap = self.follow_gap(car, distance=0.9)
        if gap is not None:
            car.speed = max(0.015, min(car.max_speed, gap * 0.35))
        else:
            car.speed = min(car.max_speed, car.speed + 0.003)

        other = self.conflict(car)
        if other:
            priority = (car.is_emergency, not other.is_emergency, car.car_id < other.car_id)
            if priority > (other.is_emergency, not car.is_emergency, other.car_id < car.car_id):
                other.wait_timer = 12
            else:
                car.wait_timer = 12

    def update(self):
        self.frame += 1

        if self.frame % self.spawn_interval == 0 and len([c for c in self.cars if c.active]) < 14:
            self.spawn_car()

        for car in self.cars:
            if not car.active:
                continue
            if self.mode == 'ai':
                self.apply_ai(car)
            car.move()

        if self.mode == 'chaos':
            for car in self.cars:
                if not car.active:
                    continue
                other = self.conflict(car)
                if other:
                    car.active = False
                    other.active = False
                    self.collision_count += 1


class RoadDemo:
    def __init__(self):
        self.fig = plt.figure(figsize=(14, 7), facecolor=COLOR_BG)
        self.ax_chaos = self.fig.add_subplot(1, 2, 1)
        self.ax_ai = self.fig.add_subplot(1, 2, 2)
        self.sim_chaos = Simulation('chaos')
        self.sim_ai = Simulation('ai')
        for _ in range(4):
            self.sim_chaos.spawn_car()
            self.sim_ai.spawn_car()

    def draw_scene(self, ax, cars, title, collisions):
        ax.clear()
        ax.set_xlim(-5.5, 5.5)
        ax.set_ylim(-5.5, 5.5)
        ax.set_aspect('equal')
        ax.set_facecolor(COLOR_BG)
        ax.axis('off')

        for center in [-2, 2]:
            ax.add_patch(Rectangle((center - 1.2, -5.5), 2.4, 11, facecolor=COLOR_ROAD))
            ax.add_patch(Rectangle((-5.5, center - 1.2), 11, 2.4, facecolor=COLOR_ROAD))

        for lane in LANES_X:
            ax.plot([lane, lane], [-5.5, 5.5], color=COLOR_LANE, linestyle='--', alpha=0.4)
        for lane in LANES_Y:
            ax.plot([-5.5, 5.5], [lane, lane], color=COLOR_LANE, linestyle='--', alpha=0.4)

        for x in [-2, 2]:
            for y in [-2, 2]:
                ax.add_patch(Circle((x, y), 0.55, facecolor='#fde047', alpha=0.2))

        ax.set_title(title, color=COLOR_TEXT, fontsize=14)

        for car in cars:
            if not car.active:
                continue
            color = COLOR_EMERGENCY if car.is_emergency else COLOR_CAR
            ax.add_patch(Circle(car.position(), 0.22, facecolor=color, edgecolor='white', linewidth=1.2))

        ax.text(
            -5.3,
            5.2,
            f"Collisions: {collisions}",
            color='white',
            fontsize=10,
            bbox=dict(boxstyle='round', facecolor='#00000088', edgecolor='none'),
        )

    def update(self, frame):
        self.sim_chaos.update()
        self.sim_ai.update()
        self.draw_scene(self.ax_chaos, self.sim_chaos.cars, 'Chaos Mode (no AI)', self.sim_chaos.collision_count)
        self.draw_scene(self.ax_ai, self.sim_ai.cars, 'AI Mode (speed + priority)', self.sim_ai.collision_count)

    def run(self):
        print("🎬 Two-lane road demo running!")
        # Draw initial frame
        self.draw_scene(self.ax_chaos, self.sim_chaos.cars, 'Chaos Mode (no AI)', 0)
        self.draw_scene(self.ax_ai, self.sim_ai.cars, 'AI Mode (speed + priority)', 0)
        
        anim = FuncAnimation(self.fig, self.update, interval=120, blit=False)
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    demo = RoadDemo()
    demo.run()

