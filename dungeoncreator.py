import matplotlib.pyplot as plt
import numpy as np
import random
from matplotlib.colors import ListedColormap
import matplotlib.animation as animation

# Constants
MAP_WIDTH, MAP_HEIGHT = 50, 50
MIN_ROOM_SIZE, MAX_ROOM_SIZE = 5, 10
MAX_DEPTH = 5

# Tile Types
WALL, FLOOR, START, ENEMY, TREASURE, BOSS, HEALTH_POTION, PLAYER, GOLD = range(9)

# Color map for visualization
COLORS = {
    WALL: "black", FLOOR: "lightgray", START: "green", ENEMY: "red",
    TREASURE: "gold", BOSS: "purple", HEALTH_POTION: "blue", PLAYER: "lime", GOLD: "yellow"
}

# Player Class
class Player:
    def __init__(self, y, x):
        self.y, self.x = y, x
        self.health, self.gold, self.potions = 10, 0, 0
        self.attack_power = 2

    def move(self, dy, dx, dungeon):
        ny, nx = self.y + dy, self.x + dx
        if 0 <= ny < dungeon.shape[0] and 0 <= nx < dungeon.shape[1]:
            tile = dungeon[ny, nx]
            if tile in [FLOOR, START, ENEMY, TREASURE, BOSS, HEALTH_POTION, GOLD]:
                self.interact_with_tile(tile, ny, nx, dungeon)
                self.y, self.x = ny, nx

    def interact_with_tile(self, tile, ny, nx, dungeon):
        if tile == ENEMY:
            self.attack_enemy(ny, nx, dungeon)
        elif tile == TREASURE:
            self.gold += 5
            dungeon[ny, nx] = FLOOR
        elif tile == HEALTH_POTION:
            self.pick_up_potion(dungeon, ny, nx)
        elif tile == GOLD:
            self.gold += 10
            dungeon[ny, nx] = FLOOR
        elif tile == BOSS:
            self.attack_boss(ny, nx, dungeon)

    def attack_enemy(self, ny, nx, dungeon):
        print(f"You attacked an enemy! Your health is now {self.health}.")
        # Find the enemy at (ny, nx) and make it take damage
        enemy = next((e for e in enemies if e.y == ny and e.x == nx), None)
        if enemy:
            enemy.take_damage(2)  # Apply damage to the enemy

    def attack_boss(self, ny, nx, dungeon):
        self.health -= 5  # Boss is tougher
        print(f"You attacked the Boss! Your health is now {self.health}.")
        dungeon[ny, nx] = FLOOR
        self.gold += 50
        print("You defeated the Boss! You gained 50 gold.")

    def pick_up_potion(self, dungeon, ny, nx):
        if self.potions < 5:  # Limit potions to a maximum of 5
            self.potions += 1
            print(f"You picked up a health potion! You now have {self.potions} potions.")
            dungeon[ny, nx] = FLOOR  # Remove potion from dungeon
        else:
            print("You can't carry more potions.")

    def use_potion(self):
        if self.potions > 0:
            self.health += 5    # Heal the player by 5 health points
            if self.health > 10:
                self.health = 10
            self.potions -= 1
            print(f"You used a health potion! Your health is now {self.health}.")
        else:
            print("You have no potions to use!")


# Enemy Class
class Enemy:
    def __init__(self, y, x):
        self.y, self.x = y, x
        self.health = 5
        self.attack_power = 1

    def move(self, dungeon):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        random.shuffle(directions)  # Shuffle the directions to move randomly
        for dy, dx in directions:
            new_y, new_x = self.y + dy, self.x + dx
            if 0 <= new_y < dungeon.shape[0] and 0 <= new_x < dungeon.shape[1]:
                if dungeon[new_y, new_x] == FLOOR:  # The new tile must be a floor tile
                    dungeon[self.y, self.x] = FLOOR  # Remove enemy from old position
                    dungeon[new_y, new_x] = ENEMY  # Place enemy in new position
                    self.y, self.x = new_y, new_x
                    break  # Exit after moving once

    def attack(self, player):
        player.health -= self.attack_power
        print(f"An enemy attacks! Your health is now {player.health}.")

    def take_damage(self, damage):
        self.health -= damage
        print(f"Enemy takes {damage} damage! Enemy health is now {self.health}.")

    def die(self, dungeon):
        dungeon[self.y, self.x] = FLOOR  # Remove enemy from dungeon
        print(f'An enemy died! located at: ({self.y}, {self.x})')

# Room Class
class Room:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.center = (x + w // 2, y + h // 2)

# BSP Room Splitting
def split_bsp(x, y, w, h, depth=0):
    if depth >= MAX_DEPTH or w < MIN_ROOM_SIZE*2 or h < MIN_ROOM_SIZE*2:
        rw = random.randint(MIN_ROOM_SIZE, min(w, MAX_ROOM_SIZE))
        rh = random.randint(MIN_ROOM_SIZE, min(h, MAX_ROOM_SIZE))
        rx = x + random.randint(0, w - rw)
        ry = y + random.randint(0, h - rh)
        return [Room(rx, ry, rw, rh)]
    
    if w > h:
        split = random.randint(MIN_ROOM_SIZE, w - MIN_ROOM_SIZE)
        return split_bsp(x, y, split, h, depth + 1) + split_bsp(x + split, y, w - split, h, depth + 1)
    else:
        split = random.randint(MIN_ROOM_SIZE, h - MIN_ROOM_SIZE)
        return split_bsp(x, y, w, split, depth + 1) + split_bsp(x, y + split, w, h - split, depth + 1)

# Dungeon Generation
def generate_dungeon(seed=None):
    random.seed(seed)
    
    dungeon = np.zeros((MAP_HEIGHT, MAP_WIDTH), dtype=int)
    rooms = split_bsp(0, 0, MAP_WIDTH, MAP_HEIGHT)
    
    for room in rooms:
        dungeon[room.y:room.y+room.h, room.x:room.x+room.w] = FLOOR
    
    for i in range(len(rooms) - 1):
        x1, y1 = rooms[i].center
        x2, y2 = rooms[i+1].center
        if random.random() < 0.5:
            dungeon[y1, min(x1, x2):max(x1, x2)+1] = FLOOR
            dungeon[min(y1, y2):max(y1, y2)+1, x2] = FLOOR
        else:
            dungeon[min(y1, y2):max(y1, y2)+1, x1] = FLOOR
            dungeon[y2, min(x1, x2):max(x1, x2)+1] = FLOOR

    dungeon[rooms[0].center[1], rooms[0].center[0]] = START
    dungeon[rooms[-1].center[1], rooms[-1].center[0]] = BOSS

    num_enemies = 5
    enemy_rooms = random.sample(rooms[1:-1], num_enemies)  
    
    enemies = []
    for room in enemy_rooms:
        enemy_y = random.randint(room.y, room.y + room.h - 1)
        enemy_x = random.randint(room.x, room.x + room.w - 1)
        if dungeon[enemy_y, enemy_x] == FLOOR:
            dungeon[enemy_y, enemy_x] = ENEMY
            enemies.append(Enemy(enemy_y, enemy_x))
    


    # Place a treasure in a random room
    if len(rooms) > 3:
        dungeon[rooms[2].center[1], rooms[2].center[0]] = TREASURE

    for _ in range(5):
        rx, ry = random.choice(rooms).center
        if 0 <= ry < MAP_HEIGHT and 0 <= rx < MAP_WIDTH:
            dungeon[ry, rx] = HEALTH_POTION

    for _ in range(3):
        rx, ry = random.choice(rooms).center
        if 0 <= ry < MAP_HEIGHT and 0 <= rx < MAP_WIDTH:
            dungeon[ry, rx] = GOLD

    return dungeon, enemies

# Display Dungeon with Player
def display_dungeon_with_player(dungeon, enemies):
    start_pos = np.argwhere(dungeon == START)[0]
    player = Player(*start_pos)
    fig, ax = plt.subplots(figsize=(10, 10))

    color_list = list(COLORS.values())
    cmap = ListedColormap(color_list)

    dungeon_display = dungeon.copy()
    dungeon_display[player.y, player.x] = PLAYER

    img = ax.imshow(dungeon_display, cmap=cmap, interpolation="none", vmin=0, vmax=len(color_list)-1)
    ax.axis("off")
    ax.set_title(f"HP: {player.health} | Gold: {player.gold} | Potions: {player.potions}")

    # Keyboard input
    pressed_key = [None]  # Use a list so it can be modified inside nested function

    def on_key(event):
        if event.key in ["up", "down", "left", "right", "u"]:
            pressed_key[0] = event.key

    fig.canvas.mpl_connect("key_press_event", on_key)

    # Animation update function
    def update(frame):
        key = pressed_key[0]
        dy, dx = 0, 0
        print(f'Pressed key: {key}')  # Print the pressed key (for debugging, you can remove this line if not needed.key)

        if key == "up":
            dy = -1
        elif key == "down":
            dy = 1
        elif key == "left":
            dx = -1
        elif key == "right":
            dx = 1
        elif key == "u":
            print("Using a potion...")
            player.use_potion()

        if key in ["up", "down", "left", "right"]:
            player.move(dy, dx, dungeon)

        # Reset key after processing
        pressed_key[0] = None

        # Move enemies independently every frame
        for enemy in enemies:
            enemy.move(dungeon)
            if enemy.y == player.y and enemy.x == player.x:
                enemy.attack(player)
            
            if enemy.health <= 0:
                enemy.die(dungeon)
                enemies.remove(enemy)

        # Update the dungeon display
        dungeon_display[:, :] = dungeon
        dungeon_display[player.y, player.x] = PLAYER
        img.set_data(dungeon_display)
        ax.set_title(f"HP: {player.health} | Gold: {player.gold} | Potions: {player.potions}")

        if player.health <= 0:
            print("You have died! Game Over!")
            ani.event_source.stop()

        elif dungeon[player.y, player.x] == BOSS:
            print("You have defeated the Boss! You win!")
            ani.event_source.stop()

    # Start animation loop (update every 300ms)
    ani = animation.FuncAnimation(fig, update, cache_frame_data=False, interval=300)
    plt.show()

# Example usage
dungeon, enemies = generate_dungeon(seed=random.randint(0, 1000))
display_dungeon_with_player(dungeon, enemies)
