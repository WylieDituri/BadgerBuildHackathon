"""
Manim Animation: Chaos vs AI Traffic Coordination
A visually impressive demo showing independent vs coordinated traffic management.
"""

from manim import *
import numpy as np
from typing import List, Tuple


class Car(VGroup):
    """A simple car representation."""
    def __init__(self, color=BLUE, label=""):
        super().__init__()
        # Car body
        body = RoundedRectangle(
            width=0.4, height=0.25,
            corner_radius=0.05,
            fill_color=color,
            fill_opacity=1,
            stroke_color=WHITE,
            stroke_width=1
        )
        # Car label
        if label:
            text = Text(label, font_size=12, color=WHITE)
            text.move_to(body.get_center())
            self.add(body, text)
        else:
            self.add(body)
    
    def get_center(self):
        return self[0].get_center()


class TrafficDemo(Scene):
    def construct(self):
        # Title
        title = Text("Traffic Coordination: Chaos vs AI", font_size=48, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(1)
        
        # Create road network
        road_network = self.create_road_network()
        
        # Split screen
        divider = Line(UP * 3.5, DOWN * 3.5, color=GRAY)
        self.play(Create(divider))
        
        # Left side: CHAOS
        chaos_label = Text("CHAOS MODE", font_size=32, color=RED)
        chaos_label.to_corner(UL, buff=0.3).shift(RIGHT * 2.5)
        self.play(Write(chaos_label))
        
        # Right side: AI
        ai_label = Text("AI MODE", font_size=32, color=GREEN)
        ai_label.to_corner(UR, buff=0.3).shift(LEFT * 2.5)
        self.play(Write(ai_label))
        
        self.wait(0.5)
        
        # Create road networks for both sides
        left_roads = self.create_road_network().shift(LEFT * 3.5)
        right_roads = self.create_road_network().shift(RIGHT * 3.5)
        
        self.play(
            Create(left_roads),
            Create(right_roads)
        )
        
        # Run chaos mode
        self.play_chaos_mode(left_roads)
        
        # Run AI mode
        self.play_ai_mode(right_roads)
        
        # Final comparison
        self.wait(1)
        comparison_text = Text(
            "AI Coordination: Zero Collisions",
            font_size=36,
            color=GREEN
        )
        comparison_text.to_edge(DOWN, buff=1)
        self.play(Write(comparison_text))
        self.wait(2)
    
    def create_road_network(self):
        """Create a simple intersection grid with realistic lane markings."""
        roads = VGroup()
        
        # Horizontal roads
        for y in [-1, 0, 1]:
            # Road base
            road = Line(LEFT * 2, RIGHT * 2, color=GRAY, stroke_width=8)
            road.shift(UP * y)
            roads.add(road)
            
            # Solid yellow center line (divider between opposite directions)
            center_line = Line(LEFT * 2, RIGHT * 2, color=YELLOW, stroke_width=2)
            center_line.shift(UP * y)
            roads.add(center_line)
            
            # Dashed white lines for lanes going same direction
            white_line_top = DashedLine(LEFT * 2, RIGHT * 2, color=WHITE, stroke_width=1.5, dash_length=0.15)
            white_line_top.shift(UP * (y + 0.08))
            roads.add(white_line_top)
            
            white_line_bottom = DashedLine(LEFT * 2, RIGHT * 2, color=WHITE, stroke_width=1.5, dash_length=0.15)
            white_line_bottom.shift(UP * (y - 0.08))
            roads.add(white_line_bottom)
        
        # Vertical roads
        for x in [-1, 0, 1]:
            # Road base
            road = Line(UP * 1.5, DOWN * 1.5, color=GRAY, stroke_width=8)
            road.shift(RIGHT * x)
            roads.add(road)
            
            # Solid yellow center line (divider between opposite directions)
            center_line = Line(UP * 1.5, DOWN * 1.5, color=YELLOW, stroke_width=2)
            center_line.shift(RIGHT * x)
            roads.add(center_line)
            
            # Dashed white lines for lanes going same direction
            white_line_left = DashedLine(UP * 1.5, DOWN * 1.5, color=WHITE, stroke_width=1.5, dash_length=0.15)
            white_line_left.shift(RIGHT * (x - 0.08))
            roads.add(white_line_left)
            
            white_line_right = DashedLine(UP * 1.5, DOWN * 1.5, color=WHITE, stroke_width=1.5, dash_length=0.15)
            white_line_right.shift(RIGHT * (x + 0.08))
            roads.add(white_line_right)
        
        # Intersection markers
        intersections = []
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                dot = Dot(point=[x, y, 0], radius=0.08, color=YELLOW)
                intersections.append(dot)
        
        roads.add(*intersections)
        return roads
    
    def play_chaos_mode(self, roads):
        """Show chaos mode with collisions."""
        # Create cars with random paths
        cars = []
        colors = [RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE]
        
        # Car 1: Left to Right
        car1 = Car(color=colors[0], label="1")
        car1.move_to([-2.5, 0, 0])
        cars.append((car1, [-2.5, 0], [2.5, 0], 0))
        
        # Car 2: Top to Bottom (will collide!)
        car2 = Car(color=colors[1], label="2")
        car2.move_to([0, 2.5, 0])
        cars.append((car2, [0, 2.5], [0, -2.5], 0))
        
        # Car 3: Right to Left
        car3 = Car(color=colors[2], label="3")
        car3.move_to([2.5, -1, 0])
        cars.append((car3, [2.5, -1], [-2.5, -1], 0))
        
        # Car 4: Bottom to Top
        car4 = Car(color=colors[3], label="4")
        car4.move_to([-1, -2.5, 0])
        cars.append((car4, [-1, -2.5], [-1, 2.5], 0))
        
        # Add cars to scene
        for car, _, _, _ in cars:
            self.add(car)
        
        # Animate movement
        collision_happened = False
        run_time = 3
        
        # Create animations
        animations = []
        for i, (car, start, end, _) in enumerate(cars):
            # Random speed variation for chaos
            speed = 0.8 + np.random.random() * 0.4
            anim = car.animate(run_time=run_time / speed).move_to(end)
            animations.append(anim)
        
        # Play animations
        self.play(*animations, rate_func=linear)
        
        # Show collision at center
        collision_point = Dot(point=[0, 0, 0], radius=0.15, color=RED)
        collision_text = Text("💥 COLLISION!", font_size=24, color=RED)
        collision_text.move_to([0, 0.5, 0])
        
        self.play(
            FadeIn(collision_point, scale=2),
            Write(collision_text)
        )
        self.wait(0.5)
        
        # Fade out collision
        self.play(
            FadeOut(collision_point),
            FadeOut(collision_text)
        )
        
        # Remove cars
        for car, _, _, _ in cars:
            self.remove(car)
    
    def play_ai_mode(self, roads):
        """Show AI mode with coordinated movement."""
        # Create cars with coordinated paths
        cars = []
        colors = [RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE]
        
        # Car 1: Left to Right (goes first)
        car1 = Car(color=colors[0], label="1")
        car1.move_to([-2.5, 0, 0])
        cars.append((car1, [-2.5, 0], [2.5, 0], 0))
        
        # Car 2: Top to Bottom (waits, then goes)
        car2 = Car(color=colors[1], label="2")
        car2.move_to([0, 2.5, 0])
        cars.append((car2, [0, 2.5], [0, -2.5], 1))  # Delay = 1
        
        # Car 3: Right to Left
        car3 = Car(color=colors[2], label="3")
        car3.move_to([2.5, -1, 0])
        cars.append((car3, [2.5, -1], [-2.5, -1], 0.5))
        
        # Car 4: Bottom to Top
        car4 = Car(color=colors[3], label="4")
        car4.move_to([-1, -2.5, 0])
        cars.append((car4, [-1, -2.5], [-1, 2.5], 1.5))
        
        # Add cars to scene
        for car, _, _, _ in cars:
            self.add(car)
        
        # Show coordination indicator
        ai_indicator = Text("AI: Coordinating...", font_size=20, color=GREEN)
        ai_indicator.move_to([3.5, 2, 0])
        self.play(Write(ai_indicator))
        
        # Animate with coordination (staggered starts)
        run_time = 2.5
        
        # Car 1 goes first
        self.play(
            cars[0][0].animate(run_time=run_time).move_to(cars[0][2]),
            rate_func=linear
        )
        
        # Car 2 waits, then goes
        wait_time = 0.3
        self.wait(wait_time)
        self.play(
            cars[1][0].animate(run_time=run_time).move_to(cars[1][2]),
            rate_func=linear
        )
        
        # Car 3 goes
        self.play(
            cars[2][0].animate(run_time=run_time).move_to(cars[2][2]),
            rate_func=linear
        )
        
        # Car 4 goes last
        self.wait(wait_time)
        self.play(
            cars[3][0].animate(run_time=run_time).move_to(cars[3][2]),
            rate_func=linear
        )
        
        # Show success
        success_text = Text("✓ No Collisions", font_size=24, color=GREEN)
        success_text.move_to([3.5, 0, 0])
        self.play(Write(success_text))
        self.wait(0.5)
        
        # Clean up
        self.play(
            FadeOut(ai_indicator),
            FadeOut(success_text)
        )
        
        # Remove cars
        for car, _, _, _ in cars:
            self.remove(car)


class DetailedComparison(Scene):
    """A more detailed side-by-side comparison."""
    def construct(self):
        # Title
        title = Text("Traffic Coordination Demo", font_size=42, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        
        # Split screen
        divider = DashedLine(UP * 3.5, DOWN * 3.5, color=GRAY, dash_length=0.2)
        self.add(divider)
        
        # Labels
        chaos_label = Text("CHAOS", font_size=36, color=RED, weight=BOLD)
        chaos_label.to_corner(UL, buff=0.5).shift(RIGHT * 2.5)
        
        ai_label = Text("AI COORDINATED", font_size=36, color=GREEN, weight=BOLD)
        ai_label.to_corner(UR, buff=0.5).shift(LEFT * 2.5)
        
        self.play(Write(chaos_label), Write(ai_label))
        
        # Create road networks
        left_roads = self.create_detailed_roads().shift(LEFT * 3.5)
        right_roads = self.create_detailed_roads().shift(RIGHT * 3.5)
        
        self.play(Create(left_roads), Create(right_roads))
        
        # Run both simultaneously
        self.play_both_modes(left_roads, right_roads)
        
        # Final stats
        self.show_stats()
    
    def create_detailed_roads(self):
        """Create a more detailed road network with realistic lane markings."""
        roads = VGroup()
        
        # Horizontal roads with lane markings
        for y_pos in [1, -1]:
            # Road base
            h_road = Line(LEFT * 2.5, RIGHT * 2.5, color=GRAY, stroke_width=10)
            h_road.shift(UP * y_pos)
            roads.add(h_road)
            
            # Solid yellow center line
            center_line = Line(LEFT * 2.5, RIGHT * 2.5, color=YELLOW, stroke_width=2)
            center_line.shift(UP * y_pos)
            roads.add(center_line)
            
            # Dashed white lines for lanes
            white_top = DashedLine(LEFT * 2.5, RIGHT * 2.5, color=WHITE, stroke_width=1.5, dash_length=0.15)
            white_top.shift(UP * (y_pos + 0.1))
            roads.add(white_top)
            
            white_bottom = DashedLine(LEFT * 2.5, RIGHT * 2.5, color=WHITE, stroke_width=1.5, dash_length=0.15)
            white_bottom.shift(UP * (y_pos - 0.1))
            roads.add(white_bottom)
        
        # Vertical roads with lane markings
        for x_pos in [-1, 1]:
            # Road base
            v_road = Line(UP * 2, DOWN * 2, color=GRAY, stroke_width=10)
            v_road.shift(RIGHT * x_pos)
            roads.add(v_road)
            
            # Solid yellow center line
            center_line = Line(UP * 2, DOWN * 2, color=YELLOW, stroke_width=2)
            center_line.shift(RIGHT * x_pos)
            roads.add(center_line)
            
            # Dashed white lines for lanes
            white_left = DashedLine(UP * 2, DOWN * 2, color=WHITE, stroke_width=1.5, dash_length=0.15)
            white_left.shift(RIGHT * (x_pos - 0.1))
            roads.add(white_left)
            
            white_right = DashedLine(UP * 2, DOWN * 2, color=WHITE, stroke_width=1.5, dash_length=0.15)
            white_right.shift(RIGHT * (x_pos + 0.1))
            roads.add(white_right)
        
        # Center intersection highlight
        center = Square(side_length=0.4, color=YELLOW, fill_opacity=0.3)
        center.move_to(ORIGIN)
        roads.add(center)
        
        return roads
    
    def play_both_modes(self, left_roads, right_roads):
        """Play both modes simultaneously."""
        # Left: Chaos
        chaos_cars = self.create_chaos_cars().shift(LEFT * 3.5)
        # Right: AI
        ai_cars = self.create_ai_cars().shift(RIGHT * 3.5)
        
        # Add all cars
        for car, _, _, _ in chaos_cars + ai_cars:
            self.add(car)
        
        # Animate chaos (simultaneous, uncoordinated)
        chaos_anims = []
        for car, start, end, _ in chaos_cars:
            speed = 0.7 + np.random.random() * 0.6
            anim = car.animate(run_time=3 / speed).move_to(end)
            chaos_anims.append(anim)
        
        # Animate AI (staggered, coordinated)
        ai_anims = []
        delays = [0, 0.8, 1.6, 2.4]
        for i, (car, start, end, _) in enumerate(ai_cars):
            anim = car.animate(run_time=2).move_to(end)
            ai_anims.append((anim, delays[i]))
        
        # Play chaos animations
        self.play(*chaos_anims, rate_func=linear)
        
        # Show collision
        collision = Text("💥", font_size=48, color=RED)
        collision.move_to(LEFT * 3.5)
        self.play(FadeIn(collision, scale=2))
        self.wait(0.3)
        self.play(FadeOut(collision))
        
        # Play AI animations with delays
        for anim, delay in ai_anims:
            self.wait(delay)
            self.play(anim)
        
        # Show success
        check = Text("✓", font_size=48, color=GREEN)
        check.move_to(RIGHT * 3.5)
        self.play(FadeIn(check, scale=2))
        self.wait(1)
        
        # Clean up
        for car, _, _, _ in chaos_cars + ai_cars:
            self.remove(car)
        self.remove(check)
    
    def create_chaos_cars(self):
        """Create cars for chaos mode."""
        cars = []
        colors = [RED, BLUE, GREEN, YELLOW]
        
        # 4 cars heading to center intersection
        positions = [
            ([-2.5, 0, 0], [2.5, 0, 0]),  # Left to right
            ([0, 2.5, 0], [0, -2.5, 0]),  # Top to bottom
            ([2.5, 0, 0], [-2.5, 0, 0]),  # Right to left
            ([0, -2.5, 0], [0, 2.5, 0]),  # Bottom to top
        ]
        
        for i, (start, end) in enumerate(positions):
            car = Car(color=colors[i], label=str(i+1))
            car.move_to(start)
            cars.append((car, start, end, 0))
        
        return cars
    
    def create_ai_cars(self):
        """Create cars for AI mode (same positions, different timing)."""
        return self.create_chaos_cars()
    
    def show_stats(self):
        """Show final statistics."""
        stats = VGroup(
            Text("CHAOS MODE:", font_size=28, color=RED),
            Text("• 3 Collisions", font_size=24, color=RED),
            Text("• 12s Average Wait", font_size=24, color=RED),
            Text(""),
            Text("AI MODE:", font_size=28, color=GREEN),
            Text("• 0 Collisions", font_size=24, color=GREEN),
            Text("• 4s Average Wait", font_size=24, color=GREEN),
        )
        stats.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        stats.to_edge(DOWN, buff=0.5)
        
        self.play(Write(stats))
        self.wait(3)


# Quick demo for testing
class QuickDemo(Scene):
    """A quick 30-second demo."""
    def construct(self):
        title = Text("AI Traffic Coordination", font_size=40, color=YELLOW)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))
        
        # Simple road with lane markings
        road = Line(LEFT * 3, RIGHT * 3, color=GRAY, stroke_width=10)
        center_line = Line(LEFT * 3, RIGHT * 3, color=YELLOW, stroke_width=2)
        white_line_top = DashedLine(LEFT * 3, RIGHT * 3, color=WHITE, stroke_width=1.5, dash_length=0.15)
        white_line_top.shift(UP * 0.1)
        white_line_bottom = DashedLine(LEFT * 3, RIGHT * 3, color=WHITE, stroke_width=1.5, dash_length=0.15)
        white_line_bottom.shift(DOWN * 0.1)
        
        road_group = VGroup(road, center_line, white_line_top, white_line_bottom)
        self.play(Create(road_group))
        
        # Show cars
        car1 = Car(color=RED, label="1")
        car1.move_to(LEFT * 3)
        car2 = Car(color=BLUE, label="2")
        car2.move_to(LEFT * 2)
        
        self.add(car1, car2)
        
        # Move with coordination
        self.play(
            car1.animate(run_time=2).shift(RIGHT * 4),
            car2.animate(run_time=2, rate_func=lambda t: smooth(0.5 + t * 0.5)).shift(RIGHT * 4)
        )
        
        success = Text("✓ Coordinated!", font_size=32, color=GREEN)
        self.play(Write(success))
        self.wait(2)

