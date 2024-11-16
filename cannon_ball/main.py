import pygame
import math
import os
import sys
import asyncio
print("Python path:", sys.path) 
print("Starting game initialization...")
print("Current directory:", os.getcwd()) 
print("Files in current directory:", os.listdir())

try:
    from learning_quotes import *
    print("✓ Successfully imported learning_quotes.py")
except ImportError as e:
    print("✗ Failed to import learning_quotes.py:", str(e))
    print("Python path:", sys.path)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

WIDTH, HEIGHT = 1200, 800

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)

initial_velocity = 50
drag_coefficient = 0.47
ball_radius = 6
PIXELS_PER_METER = 10
ball_radius_meters = ball_radius / PIXELS_PER_METER

SIMULATION_WIDTH = 800
SIMULATION_HEIGHT = HEIGHT - 100

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (70, 70, 200)
        self.hover_color = (90, 90, 220)
        self.is_hovered = False
        self.radius = 10

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        
        pygame.draw.rect(screen, color, self.rect, border_radius=self.radius)
        
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        percent = (self.value - self.min_val) / (self.max_val - self.min_val)
        pos = self.rect.x + percent * self.rect.width
        pygame.draw.circle(screen, WHITE, (int(pos), self.rect.centery), 10)
        
        font = pygame.font.SysFont(None, 24)
        text = f"Angle: {int(self.value)}°"
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(centerx=self.rect.centerx, bottom=self.rect.top - 5)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        global should_update_quotes
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                rel_x = event.pos[0] - self.rect.x
                percent = max(0, min(1, rel_x / self.rect.width))
                new_value = self.min_val + percent * (self.max_val - self.min_val)
                if new_value != self.value:
                    self.value = new_value
                    should_update_quotes = True
                else:
                    should_update_quotes = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                should_update_quotes = True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            percent = max(0, min(1, rel_x / self.rect.width))
            self.value = self.min_val + percent * (self.max_val - self.min_val)

button_width = 120
button_height = 40
button_spacing = 15
start_x = SIMULATION_WIDTH + 20
start_y = 20

buttons = [
    Button(start_x, start_y, button_width, button_height, "Mass +"),
    Button(start_x + button_width + button_spacing, start_y, button_width, button_height, "Mass -"),
    Button(start_x, start_y + button_height + button_spacing, button_width, button_height, "Gravity +"),
    Button(start_x + button_width + button_spacing, start_y + button_height + button_spacing, button_width, button_height, "Gravity -"),
    Button(start_x, start_y + 2 * (button_height + button_spacing), button_width, button_height, "Air Density +"),
    Button(start_x + button_width + button_spacing, start_y + 2 * (button_height + button_spacing), button_width, button_height, "Air Density -"),
]

buttons[0].color = buttons[1].color = (70, 150, 70)
buttons[0].hover_color = buttons[1].hover_color = (90, 170, 90)

buttons[2].color = buttons[3].color = (150, 70, 70)
buttons[2].hover_color = buttons[3].hover_color = (170, 90, 90)

buttons[4].color = buttons[5].color = (70, 70, 150)
buttons[4].hover_color = buttons[5].hover_color = (90, 90, 170)

angle_slider = Slider(start_x, HEIGHT - 80, 2 * button_width + button_spacing, 20, 0, 90, 45)

def reset_ball():
    global position, velocity, trajectory_points
    angle_rad = math.radians(angle_slider.value)
    velocity = [
        initial_velocity * math.cos(angle_rad),
        initial_velocity * math.sin(angle_rad)
    ]
    position = [
        50 / PIXELS_PER_METER,
        ball_radius_meters
    ]
    trajectory_points = []

reset_ball()
running = True
dt = 1/30

mass_history = []
gravity_history = []
air_density_history = []
last_angle = 45
should_update_quotes = False
explanation = []

def get_explanation_text():
    print("Attempting to get explanation text")
    global mass_history, gravity_history, air_density_history, last_angle
    angle = int(angle_slider.value)
    
    try:
        if abs(angle - last_angle) > 5:
            angle_quote = get_random_quote('ANGLE', get_angle_category(angle))
            print("Got angle quote:", angle_quote)
            last_angle = angle
        else:
            angle_quote = ""

        mass_history = (mass_history + [mass])[-3:]
        gravity_history = (gravity_history + [gravity])[-3:]
        air_density_history = (air_density_history + [air_density])[-3:]

        explanation = [f"At {angle}° launch angle: {angle_quote}" if angle_quote else f"At {angle}° launch angle:"]
        
        if len(mass_history) > 1:
            explanation.append("")
            trend = 'increase' if mass_history[-1] > mass_history[-2] else 'decrease'
            explanation.append(f"• Mass ({mass:.1f}kg): {get_random_quote('MASS', trend)}")
        
        if len(gravity_history) > 1:
            explanation.append("")
            trend = 'increase' if gravity_history[-1] > gravity_history[-2] else 'decrease'
            explanation.append(f"• Gravity ({gravity:.1f} m/s²): {get_random_quote('GRAVITY', trend)}")
        
        if len(air_density_history) > 1:
            explanation.append("")
            trend = 'increase' if air_density_history[-1] > air_density_history[-2] else 'decrease'
            explanation.append(f"• Air density ({air_density:.3f} kg/m³): {get_random_quote('AIR_DENSITY', trend)}")

        if len(mass_history) > 2 and get_value_trend(mass, mass_history) == 'experimenting':
            explanation.append("")
            explanation.append("")
            explanation.append(get_random_quote('TREND', 'experimenting'))

        print("Successfully generated explanation")
        return explanation
    except Exception as e:
        print("Error in get_explanation_text:", str(e))
        import traceback
        print("Traceback:", traceback.format_exc())
        return ["Error: " + str(e)]

def draw_wrapped_text(screen, text, font, color, rect):
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0
    
    for word in words:
        word_surface = font.render(word + ' ', True, color)
        word_width = word_surface.get_width()
        
        if current_width + word_width <= rect.width:
            current_line.append(word)
            current_width += word_width
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width
    
    if current_line:
        lines.append(' '.join(current_line))
    
    y = rect.top
    for line in lines:
        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (rect.left, y))
        y += font.get_height() + 2

async def main():
    print("Starting initialization...")
    pygame.init()
    global screen, mass, gravity, air_density, position, velocity, trajectory_points
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Cannonball Simulation")

    mass = 10.0
    gravity = 9.8
    air_density = 1.225
    position = [50 / PIXELS_PER_METER, ball_radius_meters]
    velocity = [0, 0]
    trajectory_points = []

    print("Screen initialized...")
    
    global running
    running = True
    
    reset_ball()
    
    print("Starting game loop...")
    
    global explanation
    explanation = get_explanation_text()
    
    while running:
        screen.fill(BLACK)
        
        pygame.draw.rect(screen, WHITE, (0, 0, SIMULATION_WIDTH, SIMULATION_HEIGHT), 2)
        
        pygame.draw.rect(screen, GREEN, (0, SIMULATION_HEIGHT - 5, SIMULATION_WIDTH, 5))
        
        if len(trajectory_points) > 1:
            pygame.draw.lines(screen, GRAY, False, trajectory_points, 2)

        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.update(mouse_pos)

        for button in buttons:
            button.draw(screen)
        angle_slider.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for i, button in enumerate(buttons):
                    if button.is_clicked(mouse_pos):
                        global should_update_quotes
                        should_update_quotes = True
                        if i == 0:
                            mass += 0.5
                            mass_history.append(mass)
                        elif i == 1:
                            mass = max(0.5, mass - 0.5)
                            mass_history.append(mass)
                        elif i == 2:
                            gravity += 1.0
                            gravity_history.append(gravity)
                        elif i == 3:
                            gravity = max(0, gravity - 1.0)
                            gravity_history.append(gravity)
                        elif i == 4:
                            air_density += 0.1
                            air_density_history.append(air_density)
                        elif i == 5:
                            air_density = max(0, air_density - 0.1)
                            air_density_history.append(air_density)
                        reset_ball()
                angle_slider.handle_event(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                angle_slider.handle_event(event)
            elif event.type == pygame.MOUSEMOTION:
                angle_slider.handle_event(event)

        velocity_magnitude = math.hypot(velocity[0], velocity[1])

        cross_sectional_area = math.pi * (ball_radius_meters ** 2)

        if velocity_magnitude != 0:
            drag_force_x = -0.5 * drag_coefficient * air_density * cross_sectional_area * (velocity[0] / velocity_magnitude) * velocity_magnitude**2
            drag_force_y = -0.5 * drag_coefficient * air_density * cross_sectional_area * (velocity[1] / velocity_magnitude) * velocity_magnitude**2
        else:
            drag_force_x = 0
            drag_force_y = 0

        acceleration_x = drag_force_x / mass
        acceleration_y = drag_force_y / mass - gravity

        velocity[0] += acceleration_x * dt
        velocity[1] += acceleration_y * dt

        position[0] += velocity[0] * dt
        position[1] += velocity[1] * dt

        x_pixel = int(position[0] * PIXELS_PER_METER)
        y_pixel = SIMULATION_HEIGHT - int(position[1] * PIXELS_PER_METER)

        if 0 <= x_pixel <= SIMULATION_WIDTH and 0 <= y_pixel <= SIMULATION_HEIGHT:
            trajectory_points.append((x_pixel, y_pixel))

        if 0 <= x_pixel <= SIMULATION_WIDTH and 0 <= y_pixel <= SIMULATION_HEIGHT:
            pygame.draw.circle(screen, WHITE, (x_pixel, y_pixel), ball_radius)

        if position[1] <= ball_radius_meters:
            reset_ball()

        font = pygame.font.SysFont(None, 28)
        stats = [
            f"Mass: {mass:.1f} kg",
            f"Gravity: {gravity:.1f} m/s²",
            f"Air Density: {air_density:.3f} kg/m³"
        ]
        for i, text in enumerate(stats):
            text_surface = font.render(text, True, WHITE)
            screen.blit(text_surface, (start_x, start_y + 3 * (button_height + button_spacing) + i * 30))

        if should_update_quotes:
            explanation = get_explanation_text()
            should_update_quotes = False

        text_box = pygame.Rect(
            start_x, 
            start_y + 5 * (button_height + button_spacing),
            WIDTH - start_x - 40,
            HEIGHT - (start_y + 5 * (button_height + button_spacing)) - 40
        )

        font = pygame.font.SysFont(None, 24)
        y_position = text_box.top
        line_spacing = font.get_height() + 20

        for line in explanation:
            if line.strip():
                draw_wrapped_text(screen, line, font, WHITE, 
                    pygame.Rect(text_box.left, y_position, text_box.width, text_box.height))
                y_position += line_spacing
            else:
                y_position += line_spacing // 2

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == '__main__':
    asyncio.run(main())