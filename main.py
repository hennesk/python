import pygame
pygame.init()
screenWidth, screenHeight = 16*100,9*100
gameScreen = pygame.display.set_mode((screenWidth,screenHeight))
clock = pygame.time.Clock()
entitiesOnScreen = []

class spritesheet(object):
    def __init__(self, filename, rows, cols):
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.rows = rows
        self.cols = cols
        self.totalCellCount = rows * cols
        self.rect = self.sheet.get_rect()

        width = self.cellWidth = self.rect.width // cols
        height = self.cellHeight = self.rect.height // rows
        hw,hh = self.cellCenter = (width // 2, height // 2)
        self.cells=list([(index % cols * width, index // cols * height, width, height) for index in range(self.totalCellCount)])
        # self.handle = list([ (0,0),(-hw,0),(-width,0),(0,-hh),(-hw,-hh),(-width,-hh),(0,-height),(-hw,-height),(-width,-height) ])
    def drawCell(self,surface,cellindex,x,y):
        surface.blit(self.sheet,(x,y),self.cells[cellindex])    
    def draw_all(self,surface,x,y):
        surface.blit(self.sheet,(x,y))
class player(object):
    def __init__(self, initalX, intialY, filename, spriteRows, spriteCols):
        self.spritesheet = spritesheet(filename, spriteRows, spriteCols)
        self.x = initalX - (self.spritesheet.cellWidth // 2)
        self.y = intialY - (self.spritesheet.cellHeight // 2)
        self.z = 0
        self.ticksToIdle = 600
        self.vel = 5
        self.facing = 0
        self.idleCount = 0
        self.walkCount = 0 
        self.isMoving = False
        self.lastX = self.x
        self.lastY = self.y
        self.removeMe = False        
    def walk(self, direction):
        self.facing = direction
        # self.isMoving = True      
        self.walkCount += 1
        self.idleCount = 0
        if self.walkCount == 60:
            self.walkCount = 0
        if direction == 0:
            self.y += self.vel
        if direction == 1:
            self.x -= self.vel
        if direction == 2:
            self.y -= self.vel
        if direction == 3:
            self.x += self.vel
        # Screen bounding
        if self.x > (screenWidth - self.spritesheet.cellWidth):
            self.x = screenWidth - self.spritesheet.cellWidth
        if self.y > (screenHeight - self.spritesheet.cellHeight):
            self.y = screenHeight - self.spritesheet.cellHeight
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0      
        # TODO figure this out      
        if (self.x != self.lastX) or (self.y != self.lastY):
            self.isMoving = True
        self.lastX = self.x
        self.lastY = self.y

    def idle(self):
        self.isMoving = False
        if self.idleCount < (self.ticksToIdle -1):
            self.idleCount += 1

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            entitiesOnScreen.append(projectile(self.x + (self.spritesheet.cellWidth // 2), self.y + (self.spritesheet.cellHeight // 2), 9, (255,255,255), self.facing))
        # TODO better handling of diagonals incrementing walkCount
        if keys[pygame.K_DOWN]:            
            self.walk(0)
        if keys[pygame.K_LEFT]:        
            self.walk(1)
        if keys[pygame.K_UP]:
            self.walk(2)
        if keys[pygame.K_RIGHT]:
            self.walk(3)
        elif not (keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP]):
            self.idle()

    def draw(self, gameScreen):
        offset = 0
        offset += self.facing*10
        if self.isMoving:
            offset += 40
            offset += self.walkCount // 6
        else:
            if not (self.facing == 2) and self.idleCount > 450:
                offset += ((self.idleCount - 450) // 50)
        self.spritesheet.drawCell(gameScreen, offset, self.x, self.y)
class enemy(object):
    def __init__(self, x, y, width, height, end):
        self.x = x
        self.y = y
        self.z = 0
        self.width = width
        self.height = height
        self.end = end
        self.path = [self.x, self.end]
        # self.walkCount = 0
        self.vel = 3
        self.removeMe = False

    def draw(self,gameScreen):
        self.move()
        pygame.draw.rect(gameScreen, (255,0,0), (self.x, self.y, self.width, self.height))
    
    def update(self):
        self.move()

    def move(self):
        if self.vel > 0:
            if self.x + self.vel < self.path[1]:
                self.x += self.vel
            else:
                self.vel *= -1
                self.walkCount = 0
        else:
            if self.x - self.vel > self.path[0]:
                self.x += self.vel
            else:
                self.vel *= -1
                self.walkCount = 0
class projectile(object):
    def __init__(self,x,y,radius,color,facing):
        self.x = x
        self.y = y
        self.z = 2
        self.radius = radius
        self.color = color
        self.facing = facing
        self.vel = 10
        self.removeMe = False
        
    def update(self):        
        if ((self.x > screenWidth) or (self.x < 0) or (self.y > screenHeight) or (self.y < 0)):
            self.removeMe = True
        if self.facing == 0: 
            self.y += self.vel
        if self.facing == 1: 
            self.x -= self.vel
        if self.facing == 2: 
            self.y -= self.vel
        if self.facing == 3: 
            self.x += self.vel

    def draw(self, gameScreen):
        pygame.draw.circle(gameScreen, self.color, (self.x, self.y), self.radius)

def redrawScreen():
    gameScreen.fill((0,0,0))    
    for ent in entitiesOnScreen:
        ent.draw(gameScreen)
    pygame.display.update()
def getZVal(val):    
    return val.z
def updateEntities():
    for ent in entitiesOnScreen:
        ent.update()
        if ent.removeMe:
            entitiesOnScreen.pop(entitiesOnScreen.index(ent))
    entitiesOnScreen.sort(key = getZVal, reverse = True )

entitiesOnScreen.append(player(screenWidth//2,screenHeight//2,"C:\\GitHub\\python\\link.png", 8, 10))
entitiesOnScreen.append(enemy(0,0,50,50,200))
entitiesOnScreen.append(enemy(0,60,50,50,500))
## Main loop of execution
run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    title_str = "First Game -- FPS: " + str(clock.get_fps()//1)
    # title_str = "Game1"
    pygame.display.set_caption(title_str)    
    updateEntities()
    redrawScreen()
pygame.quit()            