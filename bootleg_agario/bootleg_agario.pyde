MAP_W = 10000
MAP_H = 10000


class Camera():
    _entities_in_view = []
    _entities_in_view_index = []
    def __init__(self, x, y, w, h):
        self._x, self._y, self._w, self._h = x, y, w, h

    def update_entities(self, entities):
        self._entities_in_view = []
        self._entities_in_view_index = []
        for i, entity in enumerate(entities):
            if entity.x + entity.w/2 > self._x and entity.x - entity.w/2 < self._x + self._w:
                if entity.y + entity.h/2 > self._y and entity.y - entity.h/2 < self._y + self._h:
                    self._entities_in_view.append(entity)
                    self._entities_in_view_index.append(i)

    def move(self, x, y):
        self._x, self._y = int(x - width/2), int(y - height/2)

    def render_view(self):
        for entity in self._entities_in_view:
            entity.update_camera_position(self._x, self._y)
            entity.render()

    @property
    def entities_in_view(self):
        return self._entities_in_view

    @property
    def entities_in_view_index(self):
        return self._entities_in_view_index
    
    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y


class Player():
    _vx, _vy = 0, 0
    _speed = 6
    _fire_ticks = 0
    @staticmethod
    def build_hitbox(x, y, w, h):
        return {"x": x, "y": y, "w": w, "h": h, "type": "circle"}

    def __init__(self, id, x, y, size, camera_x, camera_y):
        self._id = id
        self._x, self._y, self._size = x, y, size
        self._camera_x, self._camera_y = camera_x, camera_y
        self._hitbox = self.build_hitbox(x, y, size, size)

    def update_camera_position(self, x, y):
        self._camera_x, self._camera_y = x, y

    def fire(self):
        global entities
        if self._size > 100 and self._fire_ticks == 0:
            self._fire_ticks = 30
            self._size -= self._size/10
            entities.insert(entities.index(next(i for i in entities if isinstance(i, Player))) - 1, DetachedFood(create_entity_id(), self._id, self._x, self._y, self._vx * 4, self._vy * 4, self._size/4, self._size/4, self._camera_x, self._camera_y))

    def render(self):
        self._fire_ticks -= 1 if self._fire_ticks > 0 else 0
        fill(0, 150, 255)
        circle(int(self._x) - self._camera_x, int(self._y) - self._camera_y, self._size)

    def receive_mouse_location(self, x, y):
        self._vx = ((self._camera_x + x) - self._x)/(self._speed * 4)
        self._vy = ((self._camera_y + y) - self._y)/(self._speed * 4)
        if sqrt(float(abs(self._vx))**2 + float(abs(self._vy))**2) > self._speed:
            speed_restriction_factor = float(self._speed) / sqrt(float(abs(self._vx))**2 + float(abs(self._vy))**2)
            self._vx = self._vx * speed_restriction_factor
            self._vy = self._vy * speed_restriction_factor

    def receive_keystrokes(self, keysPressed):
        if "w" in keysPressed:
            self.fire()

    def receive_collision(self, entity):
        if hasattr(entity, 'food_value') and hasattr(entity, 'destructible') and entity.destructible:
            self._size += entity.food_value

    def move(self):
        self._speed = 6 - float(self._size) / 250
        self._x += self._vx
        self._y += self._vy
        self._hitbox = self.build_hitbox(self._x, self._y, self._size, self._size)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def w(self):
        return self._size

    @property
    def h(self):
        return self._size
    
    @property
    def hitbox(self):
        return self._hitbox

    @property
    def id(self):
        return self._id


class Food(object):
    destructible = True
    @staticmethod
    def build_hitbox(x, y, w, h):
        return {"x": x, "y": y, "w": w, "h": h, "type": "circle"}

    def __init__(self, id, x, y, size, camera_x, camera_y):
        self._id = id
        self._x, self._y, self._size = x, y, size
        self._food_value = int(self._size / 20)
        self._camera_x, self._camera_y = camera_x, camera_y
        self._hitbox = self.build_hitbox(x, y, size, size)

    def update_camera_position(self, x, y):
        self._camera_x, self._camera_y = x, y

    def render(self):
        if 20 < self._size <= 40:
            fill(0, 0, 255)
        elif 40 < self._size <= 60:
            fill(255, 255, 0)
        else:
            fill(0, 255, 0)
        circle(int(self._x) - self._camera_x, int(self._y) - self._camera_y, self._size)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def w(self):
        return self._size

    @property
    def h(self):
        return self._size

    @property
    def hitbox(self):
        return self._hitbox

    @property
    def food_value(self):
        return self._food_value


class DetachedFood(Food):
    conditional_collisions = True
    _conditional_ticks = 60
    _deceleration_ticks = 0

    def __init__(self, id, spawned_from_id, x, y, vx, vy, size, food_value, camera_x, camera_y):
        self._id = id
        self._blacklisted_ids = [spawned_from_id]
        self._x, self._y, self._size = x, y, size
        self._vx, self._vy = vx, vy
        self._food_value = food_value
        self._camera_x, self._camera_y = camera_x, camera_y
        self._hitbox = self.build_hitbox(x, y, size, size)

    def move(self):
        self._deceleration_ticks += 1
        self._x += self._vx
        self._y += self._vy
        if self._deceleration_ticks > 3 and (self._vx != 0 or self._vy != 0):
            self._deceleration_ticks = 0
            self._vx += -1 if self._vx > 0 else 1 if self._vx < 0 else 0
            self._vy += -1 if self._vy > 1 else 1 if self._vy < 0 else 0
            self._vx = 0 if -1 < self._vx < 1 else self._vx
            self._vy = 0 if -1 < self._vy < 1 else self._vy

    def render(self):
        # This should work but doesn't because Processing is stupid
        # super(Food, self).render()
        if 20 < self._size <= 40:
            fill(0, 0, 255)
        elif 40 < self._size <= 60:
            fill(255, 255, 0)
        else:
            fill(0, 255, 0)
        circle(int(self._x) - self._camera_x, int(self._y) - self._camera_y, self._size)
        self._conditional_ticks -= 1 if self._conditional_ticks != 0 else 0
        if self._conditional_ticks == 0 and self.conditional_collisions:
            self.conditional_collisions = False
        

    @property
    def blacklisted_ids(self):
        return self._blacklisted_ids


def collision_scan(entity1):
    global entities
    i = -1
    while i < len(c.entities_in_view) - 1:
        i += 1
        hit = False
        entity2 = c.entities_in_view[i]
        if entity1 == entity2:
            continue
        # circle-circle
        if entity1.hitbox["type"] == "circle" and entity2.hitbox["type"] == "circle":
            if sqrt((entity1.hitbox["x"] - entity2.hitbox["x"])**2 + (entity1.hitbox["y"] - entity2.hitbox["y"])**2) <= entity1.hitbox["w"]/2 - entity2.hitbox["w"]/2:
                hit = True
        if hit:
            if hasattr(entity2, 'conditional_collisions') and entity2.conditional_collisions:
                if entity1.id in entity2.blacklisted_ids:
                    continue
            if hasattr(entity2, 'destructible') and entity2.destructible:
                print("deleted")
                del entities[c.entities_in_view_index[i]]
                c.update_entities(entities)
            if hasattr(entity2, 'receive_collision'):
                entity2.receive_collision()
            entity1.receive_collision(entity2)


def create_entity_id():
    global entity_ids
    new_id = 1 + entity_ids[-1] if len(entity_ids) != 0 else 1
    entity_ids.append(new_id)
    return new_id

def spawn_food():
    while len(entities) < 6000:
        entities.insert(entities.index(next(i for i in entities if isinstance(i, Player))) - 1, Food(create_entity_id(), random(MAP_W), random(MAP_H), 20, c.x, c.y))


def setup():
    global keysPressed, entities, entity_ids, c
    size(1000, 1000)
    keysPressed = []
    entities = []
    entity_ids = []
    c = Camera(MAP_W/2 - width/2, MAP_H/2 - height/2, width, height)
    for _ in range(MAP_W/3):
        entities.append(Food(create_entity_id(), random(MAP_W), random(MAP_H), 20, c.x, c.y))
    for _ in range(MAP_W/6):
        entities.append(Food(create_entity_id(), random(MAP_W), random(MAP_H), 40, c.x, c.y))
    for _ in range(MAP_W/9):
        entities.append(Food(create_entity_id(), random(MAP_W), random(MAP_H), 60, c.x, c.y))
    entities.append(Player(create_entity_id(), MAP_W/2, MAP_H/2, 50, c.x, c.y))


def draw():
    background(255)
    spawn_food()
    for entity in entities:
        if hasattr(entity, 'receive_keystrokes'):
            entity.receive_keystrokes(keysPressed)
        if hasattr(entity, 'receive_mouse_location'):
            entity.receive_mouse_location(mouseX, mouseY)
        if isinstance(entity, Player):
            collision_scan(entity)
        if hasattr(entity, 'move'):
            entity.move()
        if isinstance(entity, Player):
            c.move(entity.x, entity.y)
    c.update_entities(entities)
    c.render_view()


def keyPressed():
    global keysPressed
    if key not in keysPressed:
        keysPressed.append(key)


def keyReleased():
    global keysPressed
    if key in keysPressed:
        keysPressed.remove(key)
