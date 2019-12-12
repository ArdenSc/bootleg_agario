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
        self._x, self._y = x - width/2, y - height/2

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


class Player():
    _vx, _vy = 0, 0
    @staticmethod
    def build_hitbox(x, y, w, h):
        return {"x": x, "y": y, "w": w, "h": h, "type": "circle"}

    def __init__(self, x, y, size, speed, camera_x, camera_y):
        self._x, self._y, self._size, self._speed = x, y, size, speed
        self._camera_x, self._camera_y = camera_x, camera_y
        self._hitbox = self.build_hitbox(x, y, size, size)

    def update_camera_position(self, x, y):
        self._camera_x, self._camera_y = x, y

    def render(self):
        fill(0, 150, 255)
        circle(self._x - self._camera_x, self._y - self._camera_y, self._size)

    def receive_mouse_location(self, x, y):
        self._vx = ((self._camera_x + x) - self._x)/20
        self._vy = ((self._camera_y + y) - self._y)/20
        self._vx = self._speed if self._vx > self._speed else -self._speed if self._vx < -self._speed else self._vx
        self._vy = self._speed if self._vy > self._speed else -self._speed if self._vy < -self._speed else self._vy
    
    def receive_collision(self):
        self._size += 2
        

    def move(self):
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


class Food:
    destructible = True
    @staticmethod
    def build_hitbox(x, y, w, h):
        return {"x": x, "y": y, "w": w, "h": h, "type": "circle"}
    
    def __init__(self, x, y, size, camera_x, camera_y):
        self._x, self._y, self._size = x, y, size
        self._camera_x, self._camera_y = camera_x, camera_y
        self._hitbox = self.build_hitbox(x, y, size, size)

    def update_camera_position(self, x, y):
        self._camera_x, self._camera_y = x, y

    def render(self):
        fill(0, 255, 0)
        circle(self._x - self._camera_x, self._y - self._camera_y, self._size)
    
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
            if hasattr(entity2, 'destructible'):
                del entities[c.entities_in_view_index[i]]
                c.update_entities(entities)
            if hasattr(entity2, 'receive_collision'):
                entity2.receive_collision()
            entity1.receive_collision()


def setup():
    global keysPressed, entities, c
    size(1000, 1000)
    keysPressed = []
    entities = []
    c = Camera(MAP_W/2 - width/2, MAP_H/2 - height/2, width, height)
    for _ in range(MAP_W):
        entities.append(Food(random(MAP_W), random(MAP_H), 20, MAP_W/2 - width/2, MAP_H/2 - height/2))
    entities.append(Player(MAP_W/2, MAP_H/2, 50, 10, MAP_W/2 - width/2, MAP_H/2 - height/2))


def draw():
    background(255)
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
