import pygame
import math
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cannonball Simulation")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)

mass = 10.0
gravity = 9.8
air_density = 1.225
initial_velocity = 50
drag_coefficient = 0.47
ball_radius = 6

SIMULATION_WIDTH = 900
SIMULATION_HEIGHT = HEIGHT - 100

PIXELS_PER_METER = 10

ball_radius_meters = ball_radius / PIXELS_PER_METER

trajectory_points = []

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
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
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
                    if i == 0:
                        mass += 0.5
                    elif i == 1:
                        mass = max(0.5, mass - 0.5)
                    elif i == 2:
                        gravity += 1.0
                    elif i == 3:
                        gravity = max(0, gravity - 1.0)
                    elif i == 4:
                        air_density += 0.1
                    elif i == 5:
                        air_density = max(0, air_density - 0.1)
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

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
