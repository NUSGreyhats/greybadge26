from adafruit_display_text import label
import displayio
import terminalio
import random
import time
import math

# Constants
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 240
PLAY_RADIUS = 110
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2

# Simple debouncing
class SimpleDebouncer:
    def __init__(self, debounce_time=0.05):
        self.debounce_time = debounce_time
        self.button_states = {}
        self.last_trigger_times = {}

    def register_button(self, button_id):
        self.button_states[button_id] = True
        self.last_trigger_times[button_id] = 0

    def check_button(self, button_id, current_state):
        current_time = time.monotonic()
        if current_time - self.last_trigger_times[button_id] < self.debounce_time:
            return False
        if button_id in self.button_states:
            previous_state = self.button_states[button_id]
            self.button_states[button_id] = current_state
            if previous_state and not current_state:
                self.last_trigger_times[button_id] = current_time
                return True
        return False

def create_player_bitmap():
    """Create a triangle bitmap for the player pointing right (0 degrees)"""
    size = 20
    bitmap = displayio.Bitmap(size, size, 2)
    center = size // 2
    
    # Draw triangle pointing right
    for y in range(size):
        for x in range(size):
            # Triangle vertices: right point, top-left, bottom-left
            # Right point at (size-2, center)
            # Top-left at (2, center-3)
            # Bottom-left at (2, center+3)
            
            if x >= 2 and x <= size - 2:
                # Calculate triangle boundaries
                top_y = center - 5 + (x - 2) * 5 // (size - 4)
                bottom_y = center + 5 - (x - 2) * 5 // (size - 4)
                
                if y >= top_y and y <= bottom_y:
                    bitmap[x, y] = 1
    
    return bitmap

def rotate_bitmap(original_bitmap, angle_degrees):
    """Rotate a bitmap by angle_degrees"""
    size = original_bitmap.width
    rotated = displayio.Bitmap(size, size, 2)
    center = size // 2
    
    # Convert angle to radians
    angle_rad = math.radians(-angle_degrees)  # Negative for clockwise rotation
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    # Rotate each pixel
    for y in range(size):
        for x in range(size):
            # Translate to center
            tx = x - center
            ty = y - center
            
            # Rotate
            rx = tx * cos_a - ty * sin_a
            ry = tx * sin_a + ty * cos_a
            
            # Translate back
            src_x = int(rx + center)
            src_y = int(ry + center)
            
            # Check bounds and copy pixel
            if 0 <= src_x < size and 0 <= src_y < size:
                if original_bitmap[src_x, src_y] == 1:
                    rotated[x, y] = 1
    
    return rotated

def create_asteroid_bitmap(size):
    """Create an irregular asteroid bitmap"""
    bitmap = displayio.Bitmap(size, size, 2)
    center = size // 2
    
    # Create irregular circle
    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Add some randomness to make it irregular
            noise = random.uniform(0.7, 1.3)
            if distance < (center - 1) * noise:
                bitmap[x, y] = 1
    
    return bitmap

def create_circle_bitmap(size):
    """Create a circle bitmap"""
    bitmap = displayio.Bitmap(size, size, 2)
    center = size // 2
    
    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            if dx * dx + dy * dy <= center * center:
                bitmap[x, y] = 1
    
    return bitmap

class GameObject:
    def __init__(self, x, y, bitmap, palette, game_group):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.heading = 0
        self.active = True
        self.size = max(bitmap.width, bitmap.height)
        self.game_group = game_group
        
        # Create sprite
        self.sprite = displayio.TileGrid(bitmap, pixel_shader=palette)
        self.sprite.x = int(x - self.size // 2)
        self.sprite.y = int(y - self.size // 2)
        self.game_group.append(self.sprite)

    def move(self):
        if not self.active:
            return
            
        self.x += self.dx
        self.y += self.dy
        self.wrap_circle()
        self.update_sprite_position()

    def wrap_circle(self):
        distance = math.sqrt((self.x - CENTER_X)**2 + (self.y - CENTER_Y)**2)
        if distance > PLAY_RADIUS:
            # Wrap to opposite side
            self.x = CENTER_X - (self.x - CENTER_X)
            self.y = CENTER_Y - (self.y - CENTER_Y)

    def update_sprite_position(self):
        if self.sprite:
            self.sprite.x = int(self.x - self.size // 2)
            self.sprite.y = int(self.y - self.size // 2)

    def is_collision(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance < (self.size + other.size) * 0.4

    def destroy(self):
        if self.sprite and self.sprite in self.game_group:
            self.game_group.remove(self.sprite)
        self.active = False

class Player(GameObject):
    def __init__(self, x, y, game_group):
        # Create player palette
        self.palette = displayio.Palette(2)
        self.palette[0] = 0x000000  # Transparent
        self.palette[1] = 0xFFFFFF  # White
        self.palette.make_transparent(0)
        
        # Create base bitmap and rotated versions
        self.base_bitmap = create_player_bitmap()
        self.rotated_bitmaps = {}
        
        # Pre-generate rotated bitmaps for common angles (every 15 degrees)
        for angle in range(0, 360, 15):
            self.rotated_bitmaps[angle] = rotate_bitmap(self.base_bitmap, angle)
        
        super().__init__(x, y, self.base_bitmap, self.palette, game_group)
        
        self.thrust = 0.8
        self.rotation_speed = 15
        self.max_speed = 4
        self.lives = 3
        self.size = 12
        self.last_sprite_heading = 0

    def turn_left(self):
        self.heading -= self.rotation_speed
        if self.heading < 0:
            self.heading += 360
        self.update_sprite_rotation()

    def turn_right(self):
        self.heading += self.rotation_speed
        if self.heading >= 360:
            self.heading -= 360
        self.update_sprite_rotation()

    def update_sprite_rotation(self):
        """Update the sprite to match the current heading"""
        # Find the closest pre-generated angle
        closest_angle = round(self.heading / 15) * 15
        if closest_angle >= 360:
            closest_angle = 0
        
        # Only update if the angle changed significantly
        if abs(closest_angle - self.last_sprite_heading) >= 15:
            # Remove old sprite
            if self.sprite in self.game_group:
                self.game_group.remove(self.sprite)
            
            # Create new sprite with rotated bitmap
            rotated_bitmap = self.rotated_bitmaps[closest_angle]
            self.sprite = displayio.TileGrid(rotated_bitmap, pixel_shader=self.palette)
            self.update_sprite_position()
            self.game_group.append(self.sprite)
            self.last_sprite_heading = closest_angle

    def accelerate(self):
        h_rad = math.radians(self.heading)
        self.dx += math.cos(h_rad) * self.thrust
        self.dy += math.sin(h_rad) * self.thrust
        
        # Limit speed
        speed = math.sqrt(self.dx**2 + self.dy**2)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.dx *= scale
            self.dy *= scale

    def hyperspace(self):
        # Random position within play area
        angle = random.uniform(0, 2 * math.pi)
        radius = (PLAY_RADIUS - 20) * math.sqrt(random.random())
        self.x = CENTER_X + radius * math.cos(angle)
        self.y = CENTER_Y + radius * math.sin(angle)
        self.dx *= 0.5
        self.dy *= 0.5

class Asteroid(GameObject):
    def __init__(self, x, y, size, game_group):
        # Create asteroid palette
        palette = displayio.Palette(2)
        palette[0] = 0x000000  # Transparent
        palette[1] = 0x8B4513  # Brown
        palette.make_transparent(0)
        
        bitmap_size = size * 15 + 4
        bitmap = create_asteroid_bitmap(bitmap_size)
        super().__init__(x, y, bitmap, palette, game_group)
        
        self.asteroid_size = size
        self.speed = 2 - size * 0.3
        self.heading = random.randint(0, 360)
        h_rad = math.radians(self.heading)
        self.dx = math.cos(h_rad) * self.speed
        self.dy = math.sin(h_rad) * self.speed

    def split(self):
        if self.asteroid_size > 1:
            # Create two smaller asteroids
            new_asteroids = []
            for i in range(2):
                new_ast = Asteroid(
                    self.x + random.randint(-10, 10), 
                    self.y + random.randint(-10, 10), 
                    self.asteroid_size - 1, 
                    self.game_group
                )
                new_asteroids.append(new_ast)
            return new_asteroids
        return []

class Missile(GameObject):
    def __init__(self, game_group):
        # Create missile palette
        palette = displayio.Palette(2)
        palette[0] = 0x000000  # Transparent
        palette[1] = 0xFFFF00  # Yellow
        palette.make_transparent(0)
        
        bitmap = create_circle_bitmap(4)
        super().__init__(0, 0, bitmap, palette, game_group)
        
        self.speed = 6
        self.active = False
        self.size = 4
        # Hide sprite initially
        self.sprite.x = -100
        self.sprite.y = -100

    def fire(self, player):
        if not self.active:
            self.x = player.x
            self.y = player.y
            self.heading = player.heading
            h_rad = math.radians(self.heading)
            self.dx = math.cos(h_rad) * self.speed
            self.dy = math.sin(h_rad) * self.speed
            self.active = True
            self.update_sprite_position()

    def move(self):
        if self.active:
            super().move()
            # Deactivate if out of bounds
            distance = math.sqrt((self.x - CENTER_X)**2 + (self.y - CENTER_Y)**2)
            if distance > PLAY_RADIUS:
                self.deactivate()

    def deactivate(self):
        self.active = False
        # Hide sprite
        self.sprite.x = -100
        self.sprite.y = -100

class Particle(GameObject):
    def __init__(self, game_group):
        # Create particle palette
        palette = displayio.Palette(2)
        palette[0] = 0x000000  # Transparent
        palette[1] = 0xFF4500  # Orange
        palette.make_transparent(0)
        
        bitmap = create_circle_bitmap(2)
        super().__init__(0, 0, bitmap, palette, game_group)
        
        self.life = 0
        self.max_life = 20
        self.size = 2
        self.active = False
        # Hide sprite initially
        self.sprite.x = -100
        self.sprite.y = -100

    def explode(self, x, y):
        self.x = x
        self.y = y
        self.heading = random.randint(0, 360)
        h_rad = math.radians(self.heading)
        speed = random.uniform(1, 4)
        self.dx = math.cos(h_rad) * speed
        self.dy = math.sin(h_rad) * speed
        self.life = self.max_life
        self.active = True
        self.update_sprite_position()

    def move(self):
        if self.active:
            super().move()
            self.life -= 1
            if self.life <= 0:
                self.deactivate()

    def deactivate(self):
        self.active = False
        # Hide sprite
        self.sprite.x = -100
        self.sprite.y = -100

def draw_border_bitmap():
    """Create a bitmap with the circular border"""
    bitmap = displayio.Bitmap(SCREEN_WIDTH, SCREEN_HEIGHT, 2)
    
    # Draw circular border
    for angle in range(0, 360, 2):
        rad = math.radians(angle)
        x = int(CENTER_X + PLAY_RADIUS * math.cos(rad))
        y = int(CENTER_Y + PLAY_RADIUS * math.sin(rad))
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
            bitmap[x, y] = 1
            # Make border thicker
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < SCREEN_WIDTH and 0 <= ny < SCREEN_HEIGHT:
                        bitmap[nx, ny] = 1
    
    return bitmap

def asteroids_game(hw_state):
    """Main function to run the asteroids game."""
    
    # Display setup
    display = hw_state["display"]
    fpga_buttons = hw_state["fpga_overlay"].set_mode_buttons()
    button_a = hw_state["btn_action"][0]
    button_b = hw_state["btn_action"][1]

    debouncer = SimpleDebouncer(debounce_time=0.05)
    for btn_id in ['left', 'up', 'center', 'down', 'right', 'a', 'b']:
        debouncer.register_button(btn_id)

    # Create main display group
    main_group = displayio.Group()
    
    # Create background bitmap
    background_bitmap = displayio.Bitmap(SCREEN_WIDTH, SCREEN_HEIGHT, 1)
    background_palette = displayio.Palette(1)
    background_palette[0] = 0x000000  # Black
    background_sprite = displayio.TileGrid(background_bitmap, pixel_shader=background_palette)
    main_group.append(background_sprite)
    
    # # Create border
    # border_bitmap = draw_border_bitmap()
    # border_palette = displayio.Palette(2)
    # border_palette[0] = 0x000000  # Transparent
    # border_palette[1] = 0x0000FF  # Blue
    # border_palette.make_transparent(0)
    # border_sprite = displayio.TileGrid(border_bitmap, pixel_shader=border_palette)
    # main_group.append(border_sprite)
    
    # Create game objects group
    game_group = displayio.Group()
    main_group.append(game_group)
    
    # Create UI text
    text_palette = displayio.Palette(2)
    text_palette[0] = 0x000000
    text_palette[1] = 0x00FF00
    
    w, h = terminalio.FONT.get_bounding_box()
    score_grid = displayio.TileGrid(terminalio.FONT.bitmap, tile_width=w, tile_height=h,
                                   pixel_shader=text_palette, width=12, height=1)
    score_grid.x = 60
    score_grid.y = 15
    score_text = terminalio.Terminal(score_grid, terminalio.FONT)
    main_group.append(score_grid)

    lives_grid = displayio.TileGrid(terminalio.FONT.bitmap, tile_width=w, tile_height=h,
                                   pixel_shader=text_palette, width=10, height=1)
    lives_grid.x = 38
    lives_grid.y = 30
    lives_text = terminalio.Terminal(lives_grid, terminalio.FONT)
    main_group.append(lives_grid)

    level_grid = displayio.TileGrid(terminalio.FONT.bitmap, tile_width=w, tile_height=h,
                                   pixel_shader=text_palette, width=10, height=1)
    level_grid.x = 26
    level_grid.y = 45
    level_text = terminalio.Terminal(level_grid, terminalio.FONT)
    main_group.append(level_grid)
    
    display.root_group = main_group

    # Game objects
    player = Player(CENTER_X, CENTER_Y, game_group)
    missile = Missile(game_group)
    asteroids = []
    particles = [Particle(game_group) for _ in range(8)]
    
    # Game state
    score = 0
    level = 1
    lives = 3
    
    # Start level
    def start_level():
        # Clear existing asteroids
        for asteroid in asteroids[:]:
            asteroid.destroy()
        asteroids.clear()
        
        # Create new asteroids
        for _ in range(level):
            attempts = 0
            while attempts < 20:  # Prevent infinite loop
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(PLAY_RADIUS * 0.4, PLAY_RADIUS * 0.8)
                x = CENTER_X + radius * math.cos(angle)
                y = CENTER_Y + radius * math.sin(angle)
                
                # Don't spawn too close to player
                if math.sqrt((x - player.x)**2 + (y - player.y)**2) > 40:
                    asteroids.append(Asteroid(x, y, 3, game_group))
                    break
                attempts += 1
    
    start_level()
    
    # Game loop
    try:
        while lives > 0:
            # Input handling
            if debouncer.check_button('left', fpga_buttons[0].value):
                player.turn_left()
            if debouncer.check_button('right', fpga_buttons[4].value):
                player.turn_right()
            if debouncer.check_button('up', fpga_buttons[1].value):
                player.accelerate()
            if debouncer.check_button('down', fpga_buttons[3].value):
                player.hyperspace()
            if debouncer.check_button('a', button_a.value) or debouncer.check_button('center', fpga_buttons[2].value):
                missile.fire(player)
            
            # Update game objects
            player.move()
            missile.move()
            
            # Update asteroids and check collisions
            for asteroid in asteroids[:]:
                asteroid.move()
                
                # Check player collision
                if player.is_collision(asteroid):
                    # Create explosion particles
                    for i in range(3):
                        for particle in particles:
                            if not particle.active:
                                particle.explode(asteroid.x + random.randint(-5, 5), 
                                               asteroid.y + random.randint(-5, 5))
                                break
                    
                    # Damage player
                    lives -= 1
                    player.update_sprite_position()
                    
                    # Split asteroid
                    new_asteroids = asteroid.split()
                    asteroid.destroy()
                    asteroids.remove(asteroid)
                    asteroids.extend(new_asteroids)
                    
                    break
                
                # Check missile collision
                if missile.active and missile.is_collision(asteroid):
                    # Create explosion particles
                    for i in range(2):
                        for particle in particles:
                            if not particle.active:
                                particle.explode(asteroid.x + random.randint(-3, 3), 
                                               asteroid.y + random.randint(-3, 3))
                                break
                    
                    # Score points
                    score += 100 * (4 - asteroid.asteroid_size)
                    
                    # Split asteroid
                    new_asteroids = asteroid.split()
                    asteroid.destroy()
                    asteroids.remove(asteroid)
                    asteroids.extend(new_asteroids)
                    
                    missile.deactivate()
                    break
            
            # Update particles
            for particle in particles:
                if particle.active:
                    particle.move()
            
            # Update UI
            score_text.write(f"\r\nScore: {score}")
            lives_text.write(f"\r\nLives: {lives}")
            level_text.write(f"\r\nLevel: {level}")
            
            # Check level completion
            if not asteroids:
                level += 1
                start_level()
            
            time.sleep(0.03)  # ~33 FPS
    
    except Exception as e:
        print(f"Game error: {e}")
        raise e
    
    # Game over screen
    go_palette = displayio.Palette(2)
    go_palette[0] = 0x000000
    go_palette[1] = 0xFF0000
    
    go_text1 = "GAME OVER"
    go_text2 = " Final Score:"
    go_text3 = f"{score}"
    go_text_area1 = label.Label(terminalio.FONT, text=go_text1, color=0xFF8800,
                            anchor_point=(0.5,0.5), anchored_position=(0,-12))
    go_text_area2 = label.Label(terminalio.FONT, text=go_text2, color=0xFF8800,
                            anchor_point=(0.5,0.5), anchored_position=(0,3))    
    go_text_area3 = label.Label(terminalio.FONT, text=go_text3, color=0xFF8800,
                            anchor_point=(0.5,0.5), anchored_position=(0,18))  
    go_text_group = displayio.Group(scale=2)
    go_text_group.append(go_text_area1)
    go_text_group.append(go_text_area2)
    go_text_group.append(go_text_area3) 
    main_group.append(go_text_group)

    go_text_group.x = CENTER_X
    go_text_group.y = CENTER_Y
    
    time.sleep(5)
    
    # Clear screen after button press
    # Remove all game objects
    for sprite in game_group:
        try:
            game_group.remove(sprite)
        except ValueError:
            pass  # Already removed

    for asteroid in asteroids[:]:
        asteroid.destroy()
    asteroids.clear()

    for particle in particles:
        particle.destroy()
    
    player.destroy()
    
    # Clear UI text
    score_text.write("\r\n" + " " * 12)
    lives_text.write("\r\n" + " " * 10)
    level_text.write("\r\n" + " " * 10)
    
    # Remove game over text
    if go_text_group in main_group:
        main_group.remove(go_text_group)
    
    return

# Entry point for the badge
def run_asteroids(hw_state):
    asteroids_game(hw_state)