import displayio
import terminalio
import random
import time
from array import array

### Tetris v1.2.1 - Add hold piece ########################
# KNOWN BUGS
# 1. When game ends, the game screen will get shifted to the top left corner

# Simple Non-blocking Music Player
class BackgroundMusicPlayer:
    def __init__(self, hw_state):
        self.hw_state = hw_state
        self.is_playing = False
        self.note_start_time = 0
        self.current_note_duration = 0.3  # Default note duration
        self.note_frequencies = [523, 587, 659, 698, 784, 880, 988]  # C5, D5, E5, F5, G5, A5, B5
        self.melody = []
        self.original_melody = []  # Store original durations
        self.current_note_index = 0
        self.buzzer_active = False
        self.tempo_multiplier = 1.0  # Speed multiplier for the music

    def set_simple_melody(self):
        """Set the correct Tetris theme melody (Korobeiniki) at base tempo"""
        # Notes in E minor key with proper frequencies
        self.note_frequencies = [
            330,   # E4  - index 0
            370,   # F#4 - index 1
            392,   # G4  - index 2
            440,   # A4  - index 3
            494,   # B4  - index 4
            523,   # C5  - index 5
            587,   # D5  - index 6
            659,   # E5  - index 7
            698,   # F#5 - index 8
            784,   # G5  - index 9
            880,   # A5  - index 10
            988,   # B5  - index 11
            1047,  # C6  - index 12
            1175   # D6  - index 13
        ]

        # Store original melody durations (before tempo adjustment) - SLOWER BASE TEMPO
        # Each tuple is (note_index, duration_in_seconds), -1 = pause
        # Slower base: Quarter note = 0.4s, eighth note = 0.2s, half note = 0.8s
        self.original_melody = [
            # Main theme (CORRECTED): E-B-C-D-C-B-A-A-C-E-D-C-B-B-C-D-E-C-A-A
            (7, 0.4), (4, 0.2), (5, 0.2), (6, 0.4), (5, 0.2), (4, 0.2),
            (3, 0.4), (3, 0.2), (5, 0.2), (7, 0.4), (6, 0.2), (5, 0.2),
            (4, 0.6), (5, 0.2), (6, 0.4), (7, 0.4), (5, 0.4), (3, 0.4), (3, 0.8),

            # Second part: D-F#-A-G-F#-E-E-C-E-D-C-B-B-C-D-E-C-A-A
            (6, 0.6), (8, 0.2), (10, 0.4), (9, 0.2), (8, 0.2),
            (7, 0.6), (5, 0.2), (7, 0.4), (6, 0.2), (5, 0.2),
            (4, 0.6), (5, 0.2), (6, 0.4), (7, 0.4), (5, 0.4), (3, 0.4), (3, 0.8),

            # Repeat main theme
            (7, 0.4), (4, 0.2), (5, 0.2), (6, 0.4), (5, 0.2), (4, 0.2),
            (3, 0.4), (3, 0.2), (5, 0.2), (7, 0.4), (6, 0.2), (5, 0.2),
            (4, 0.6), (5, 0.2), (6, 0.4), (7, 0.4), (5, 0.4), (3, 0.4), (3, 0.8),

            # Final section
            (6, 0.6), (8, 0.2), (10, 0.4), (9, 0.2), (8, 0.2),
            (7, 0.6), (5, 0.2), (7, 0.4), (6, 0.2), (5, 0.2),
            (4, 0.6), (5, 0.2), (6, 0.4), (7, 0.4), (5, 0.4), (3, 0.4), (3, 1.2),

            (-1, 2.4)  # Longer pause before loop (slower)
        ]

        # Apply current tempo to create the active melody
        self.apply_tempo()

    def apply_tempo(self):
        """Apply current tempo multiplier to the melody"""
        self.melody = []
        for note_index, duration in self.original_melody:
            adjusted_duration = duration / self.tempo_multiplier
            adjusted_duration = max(0.05, adjusted_duration)
            self.melody.append((note_index, adjusted_duration))

    def update_tempo_for_level(self, level):
        """Update music tempo based on game level"""
        self.tempo_multiplier = min(2.5, 1.0 + (level) * 0.3)
        if self.original_melody:
            self.apply_tempo()
            print(f"Music tempo updated to {self.tempo_multiplier:.1f}x for level {level}")

    def start_music(self):
        self.set_simple_melody()
        if self.melody:
            self.current_note_index = 0
            self.is_playing = True
            self.start_current_note()

    def start_current_note(self):
        if self.current_note_index < len(self.melody):
            note_index, duration = self.melody[self.current_note_index]
            self.current_note_duration = duration
            self.note_start_time = time.monotonic()
            self.stop_buzzer()
            if note_index >= 0 and note_index < len(self.note_frequencies):
                try:
                    self.hw_state["buzzer"].frequency = self.note_frequencies[note_index]
                    self.hw_state["buzzer"].duty_cycle = 25000
                    self.buzzer_active = True
                except Exception as e:
                    print(f"Buzzer error: {e}")

    def stop_buzzer(self):
        if self.buzzer_active:
            try:
                self.hw_state["buzzer"].duty_cycle = 0
                self.buzzer_active = False
            except:
                pass

    def update(self):
        if not self.is_playing:
            return
        current_time = time.monotonic()
        if current_time - self.note_start_time >= self.current_note_duration:
            self.stop_buzzer()
            self.current_note_index += 1
            if self.current_note_index >= len(self.melody):
                self.current_note_index = 0
            self.start_current_note()

    def stop(self):
        self.is_playing = False
        self.stop_buzzer()

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

class NESRandomizer:
    """NES Tetris randomization - reroll if same as previous piece"""
    def __init__(self):
        self.last_piece = None
    def get_next_piece(self):
        piece = random.randint(0, 6)
        if piece == self.last_piece:
            piece = random.randint(0, 6)
        self.last_piece = piece
        return piece

class Brick:
    BRICKS = b'\xf0\x66\x4e\x36\x63\x71\x74'
    ROTATIONS = [
        (1, 0, 0, 1, -1, -1),
        (0, 1, -1, 0, -1, 0),
        (-1, 0, 0, -1, -2, 0),
        (0, -1, 1, 0, -2, -1),
    ]
    def __init__(self, kind):
        self.x = 1
        self.y = 2
        self.color = kind % 7 + 1
        self.rotation = 0
        self.kind = kind

    def draw(self, image, color=None):
        if color is None:
            color = self.color
        data = self.BRICKS[self.kind]
        rot = self.ROTATIONS[self.rotation]
        mask = 0x01
        for y in range(2):
            y_adj = y + rot[5]
            for x in range(4):
                x_adj = x + rot[4]
                if data & mask:
                    try:
                        image[self.x + x_adj * rot[0] + y_adj * rot[1],
                              self.y + x_adj * rot[2] + y_adj * rot[3]] = color
                    except IndexError:
                        pass
                mask <<= 1

    def hit(self, image, dx=0, dy=0, dr=0):
        data = self.BRICKS[self.kind]
        rot = self.ROTATIONS[(self.rotation + dr) % 4]
        mask = 0x01
        for y in range(2):
            y_adj = y + rot[5]
            for x in range(4):
                x_adj = x + rot[4]
                if data & mask:
                    try:
                        if image[self.x + dx + x_adj * rot[0] + y_adj * rot[1],
                                 self.y + dy + x_adj * rot[2] + y_adj * rot[3]]:
                            return True
                    except IndexError:
                        return True
                mask <<= 1
        return False


    def copy(self):
        """Create a copy of this brick"""
        new_brick = Brick(self.kind)
        new_brick.x = self.x
        new_brick.y = self.y
        new_brick.rotation = self.rotation
        return new_brick


def brick_game(hw_state):
    """Setup the game display and run game"""

    # -------------------- DISPLAY SETUP --------------------
    display = hw_state["display"]
    fpga_buttons = hw_state["fpga_overlay"].set_mode_buttons()
    button_a = hw_state["btn_action"][0]
    button_b = hw_state["btn_action"][1]

    debouncer = SimpleDebouncer(debounce_time=0.035)
    for btn_id in ['left', 'up', 'center', 'down', 'right', 'a', 'b']:
        debouncer.register_button(btn_id)

    nes_randomizer = NESRandomizer()

    music_player = BackgroundMusicPlayer(hw_state)
    if button_b.value == True:
        music_player.start_music()

    palette = displayio.Palette(10)
    palette[0] = 0x7f7f7f  # Background
    palette[1] = 0x00ffff  # I piece - Cyan
    palette[2] = 0xffff00  # O piece - Yellow
    palette[3] = 0x800080  # T piece - Purple
    palette[4] = 0x00ff00  # S piece - Green
    palette[5] = 0xff0000  # Z piece - Red
    palette[6] = 0x0000ff  # J piece - Blue
    palette[7] = 0xff7f00  # L piece - Orange
    palette[8] = 0xbbbbbb  # Ghost piece - Light grey
    palette[9] = 0xffffff  # Hold piece border - White

    text_palette = displayio.Palette(2)
    text_palette[0] = 0x222222
    text_palette[1] = 0xffeedd

    # Setup terminal tilegrids for score, level, and description
    w, h = terminalio.FONT.get_bounding_box()
    text_grid = displayio.TileGrid(terminalio.FONT.bitmap, tile_width=w, tile_height=h,
                                   pixel_shader=text_palette, width=8, height=1)
    text_grid.x = 96
    text_grid.y = 50
    text = terminalio.Terminal(text_grid, terminalio.FONT)

    # Add level text display
    level_grid = displayio.TileGrid(terminalio.FONT.bitmap, tile_width=w, tile_height=h,
                                    pixel_shader=text_palette, width=8, height=1)
    level_grid.x = 96
    level_grid.y = 70
    level_text = terminalio.Terminal(level_grid, terminalio.FONT)

    # Add description text for endgame message
    desc_grid = displayio.TileGrid(terminalio.FONT.bitmap, tile_width=w, tile_height=h,
                                   pixel_shader=text_palette, width=25, height=1)
    desc_grid.x = -30
    desc_grid.y = 130
    desc_text = terminalio.Terminal(desc_grid, terminalio.FONT)

    # Add hold piece display text
    hold_grid = displayio.TileGrid(terminalio.FONT.bitmap, tile_width=w, tile_height=h,
                                   pixel_shader=text_palette, width=8, height=1)
    hold_grid.x = -50
    hold_grid.y = -15
    hold_text = terminalio.Terminal(hold_grid, terminalio.FONT)

    screen = displayio.Bitmap(10, 20, 10)
    preview = displayio.Bitmap(4, 4, 10)
    hold_area = displayio.Bitmap(4, 4, 10)

    bricks_group = displayio.Group(scale=8)
    bricks_group.append(displayio.TileGrid(screen, pixel_shader=palette, x=0, y=-4))
    bricks_group.append(displayio.TileGrid(preview, pixel_shader=palette, x=12, y=0))
    bricks_group.append(displayio.TileGrid(hold_area, pixel_shader=palette, x=-8, y=0))

    root = displayio.Group()
    root.append(bricks_group)
    root.append(text_grid)
    root.append(level_grid)
    root.append(desc_grid)
    root.append(hold_grid)

    # Center game on display (we had a circular screen)
    root.x = 80
    root.y = 70
    display.root_group = root

    # --------------- Helper functions for ghost ---------------
    def clear_ghost():
        """Erase all ghost pixels (color index 8) from the board."""
        for y in range(screen.height):
            for x in range(screen.width):
                if screen[x, y] == 8:
                    screen[x, y] = 0

    def draw_ghost(current_brick):
        """Draw a translucent preview of where the brick will land."""
        # Compute drop distance
        drop = 0
        while not current_brick.hit(screen, 0, drop + 1):
            drop += 1
        if drop == 0:
            return  # No ghost if brick already resting

        # Temporarily shift brick, draw, then restore
        original_y = current_brick.y
        current_brick.y += drop
        current_brick.draw(screen, 8)  # Draw using ghost color
        current_brick.y = original_y
    
    def clear_preview():
        """Clear the entire preview area"""
        for y in range(preview.height):
            for x in range(preview.width):
                preview[x, y] = 0

    # --------------- Hold piece functions ---------------
    def clear_hold_area():
        """Clear the hold area display"""
        for y in range(hold_area.height):
            for x in range(hold_area.width):
                hold_area[x, y] = 0

    def draw_hold_piece(held_piece):
        """Draw the held piece in the hold area"""
        clear_hold_area()
        # draw_hold_border()
        if held_piece is not None:
            # Create a temporary brick positioned in the hold area
            temp_brick = Brick(held_piece.kind)
            temp_brick.x = 1
            temp_brick.y = 1
            temp_brick.rotation = 0  # Always show pieces in default rotation (buggy)
            temp_brick.draw(hold_area)

    def perform_hold(current_brick, held_piece, next_brick_func, can_hold):
        """Handle the hold piece swap"""
        if not can_hold:
            return current_brick, held_piece, False  # Prevent holding twice in a row
        
        if held_piece is None:
            # First time holding - store current piece and get next
            held_piece = Brick(current_brick.kind)
            new_current = next_brick_func()
            return new_current, held_piece, False  # Can't hold again until next piece
        else:
            # Swap current with held
            temp_kind = current_brick.kind
            new_current = Brick(held_piece.kind)
            new_current.x = screen.width // 2
            new_current.y = 2
            held_piece = Brick(temp_kind)
            return new_current, held_piece, False  # Can't hold again until next piece

    # --------------- Game mechanics ---------------
    def get_gravity_delay(score):
        level = score // 4  # Level up every 4 points (was every 100)
        return max(0.02, 0.35 - (level * 0.02))

    # Initialize hold piece system
    held_piece = None
    can_hold = True  # Can hold the current piece

    brick = None
    score = 0
    next_brick = Brick(nes_randomizer.get_next_piece())
    tick = time.monotonic() + get_gravity_delay(score)

    last_inputs = [1] * 10

    # Initialize hold display
    hold_text.write("HOLD")
    draw_hold_piece(held_piece)

    try:
        while True:
            music_player.update()

            # Spawn new brick if needed
            if brick is None:
                current_level = score // 4
                text.write("\r\n%08d" % score)
                level_text.write("\r\nLEVEL %d" % current_level)
                clear_preview()
                brick = next_brick
                brick.x = screen.width // 2
                brick.y = 2
                next_brick = Brick(nes_randomizer.get_next_piece())
                next_brick.draw(preview)
                can_hold = True  # Reset hold availability for new piece
                
                if brick.hit(screen, 0, 0):
                    desc_text.write("!!!!Thanks for playing!!!")
                    time.sleep(1)
                    root.x = 0
                    root.y = 0
                    music_player.stop()
                    return
            
            # Gravity timing
            if tick <= time.monotonic():
                tick = time.monotonic() + get_gravity_delay(score)

            # Input handling until next gravity tick
            while True:
                current_time = time.monotonic()
                music_player.update()
                if tick <= current_time:
                    break

                # ----- RENDER CYCLE START -----
                clear_ghost()           # Remove prior ghost
                brick.draw(screen, 0)   # Erase current brick

                # Debounced input reading
                if debouncer.check_button('left', fpga_buttons[0].value):
                    if not brick.hit(screen, -1, 0):
                        brick.x -= 1
                        last_inputs.append(0); last_inputs.pop(0) # input history
                if debouncer.check_button('right', fpga_buttons[4].value):
                    if not brick.hit(screen, 1, 0):
                        brick.x += 1
                        last_inputs.append(4); last_inputs.pop(0)
                if debouncer.check_button('down', fpga_buttons[3].value): # Soft drop
                    if not brick.hit(screen, 0, 1):
                        brick.y += 1
                        last_inputs.append(3); last_inputs.pop(0)
                if debouncer.check_button('a', button_a.value): # Rotate counter clockwise
                    if not brick.hit(screen, 0, 0, 1):
                        brick.rotation = (brick.rotation + 1) % 4
                        last_inputs.append(5); last_inputs.pop(0)
                if debouncer.check_button('b', button_b.value): # Rotate clockwise
                    if not brick.hit(screen, 0, 0, -1):
                        brick.rotation = (brick.rotation - 1) % 4
                        last_inputs.append(6); last_inputs.pop(0)
                if debouncer.check_button('center', fpga_buttons[2].value): # Hard drop
                    while not brick.hit(screen, 0, 1):
                        brick.y += 1
                if debouncer.check_button('up', fpga_buttons[1].value): # hold piece
                    # Hold piece functionality
                    if can_hold:
                        def get_next():
                            return next_brick
                        brick, held_piece, can_hold = perform_hold(brick, held_piece, get_next, can_hold)
                        # If we swapped with empty hold, need to generate new next piece
                        if held_piece is not None and held_piece.kind == next_brick.kind:
                            next_brick = Brick(nes_randomizer.get_next_piece())
                            clear_preview()
                            next_brick.draw(preview)
                        draw_hold_piece(held_piece)
                        last_inputs.append(1); last_inputs.pop(0)

                # Draw ghost first, then brick
                draw_ghost(brick)
                brick.draw(screen)

                time.sleep(0.075)
                # ----- RENDER CYCLE END -----

            # ----- APPLY GRAVITY / LOCK DOWN -----
            clear_ghost()              # Ensure ghost not present before line checks
            brick.draw(screen, 0)      # Remove brick for collision test
            if brick.hit(screen, 0, 1):
                brick.draw(screen)     # Lock brick in place
                combo = 0
                for y in range(screen.height):
                    for x in range(screen.width):
                        if not screen[x, y]:
                            break
                    else:
                        combo += 1
                        score += combo
                        for yy in range(y, 0, -1):
                            for x in range(screen.width):
                                screen[x, yy] = screen[x, yy - 1]
                brick = None
            else:
                brick.y += 1
                brick.draw(screen)
    except Exception as e:
        music_player.stop()
        raise e
