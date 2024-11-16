import random

MASS_QUOTES = {
    'increase': [
        "A heavier ball cares less about air resistance - just like how a bowling ball falls faster than a feather!",
        "More mass means more momentum. Newton would be proud!",
        "The ball's getting chunky! More mass means it'll push through the air better.",
    ],
    'decrease': [
        "A lighter ball is more affected by air resistance - like a paper airplane!",
        "Less mass means the air has more influence. Watch how it slows down!",
        "Getting lighter! Now the air resistance will have a bigger effect.",
    ]
}

GRAVITY_QUOTES = {
    'increase': [
        "Welcome to Super-Earth! Where everything falls faster.",
        "More gravity means a stronger downward pull. Like being on Jupiter!",
        "The ground is getting extra grabby now!",
    ],
    'decrease': [
        "Getting close to Moon gravity! Astronauts would love this.",
        "Less gravity means the ball can fly further. Space-like!",
        "The ball almost feels like it's floating now!",
    ]
}

AIR_DENSITY_QUOTES = {
    'increase': [
        "Thick air! Like throwing a ball underwater.",
        "The air's getting soupy! More resistance means slower movement.",
        "Dense air makes the ball work harder to move!",
    ],
    'decrease': [
        "Thin air! Like throwing a ball on Mount Everest.",
        "Less air resistance means the ball can fly further!",
        "The air's getting thinner! Watch how it affects the trajectory.",
    ]
}

ANGLE_QUOTES = {
    'high': [
        "Aiming high! Perfect for maximum height.",
        "Going for the stars? High angles give more height but less distance.",
        "Like a rocket launch! Watch that vertical climb.",
    ],
    'medium': [
        "45 degrees - the sweet spot for maximum distance!",
        "The perfect balance between height and distance.",
        "This is the angle that mathematicians love!",
    ],
    'low': [
        "Low angle means more distance, less height.",
        "Like skipping stones on a pond!",
        "Fast and low - watch that horizontal speed!",
    ]
}

TREND_QUOTES = {
    'experimenting': [
        "I see you're experimenting! Try different combinations of mass, gravity and air density to see what happens!",
        "Keep exploring! Each combination of settings creates unique trajectories.",
        "That's the spirit of science - try new things and see what happens!"
    ]
}

def get_value_trend(current, history):
    if len(history) < 2:
        return 'stable'
    if all(x < y for x, y in zip(history, history[1:])):
        return 'increasing'
    if all(x > y for x, y in zip(history, history[1:])):
        return 'decreasing'
    return 'experimenting'

def get_angle_category(angle):
    if angle > 60:
        return 'high'
    elif angle < 30:
        return 'low'
    return 'medium'

def get_random_quote(category, subcategory):
    quotes = globals().get(f"{category}_QUOTES", {})
    quote_list = quotes.get(subcategory, [""])
    return random.choice(quote_list)