import pygame
import pygame.freetype
from pygame.locals import *
import time
import random

BLACK = ( 0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class Apple:

	def __init__(self, surface, node_size, snake):		
		self._surface = surface
		self._node_size = node_size
		self._snake = snake
		self._xslots = self._surface.get_width()/self._node_size
		self._yslots = self._surface.get_height()/self._node_size
		self.reposition()
		
	def reposition(self):
		x = random.randrange(1,self._xslots)*self._node_size
		y = random.randrange(1,self._yslots)*self._node_size
		self._applerect = pygame.Rect(x,y,self._node_size,self._node_size)
		while self._applerect.collidelist(self._snake.get_nodes()) != -1:
			x = random.randrange(1,self._xslots)*self._node_size
			y = random.randrange(1,self._yslots)*self._node_size
			self._applerect = pygame.Rect(x,y,self._node_size,self._node_size)
			print("retrying")
			
	def check_collision(self):
		return self._applerect.colliderect(self._snake.get_head())
		
	def draw(self):
		r = self._node_size//2
		x = self._applerect.x + r
		y = self._applerect.y + r
		pygame.draw.circle(self._surface, BLUE, (x,y),r , 0)

class Snake:

	RIGHT = 0
	LEFT = 1
	UP = 2
	DOWN = 3
	
	def __init__(self, surface, node_size = 5, init_length = 5, slowness = 5):
		
		self.node_size = node_size
		self.slowness = slowness
		self._surface = surface
		self._nodes = []
		self._step = self.node_size
		self._direction = Snake.RIGHT		
		self._counter = 0
		
		for i in range(0,init_length):
			self.add_node()
	
	# Updates the snakes for every frame. Return -1 if there is collision
	def update(self):	
		
		if self._counter >= self.slowness:
	
			for i in range(len(self._nodes)-1,0,-1):
				self._nodes[i].left = self._nodes[i-1].left
				self._nodes[i].top = self._nodes[i-1].top
		
			if self._direction == 0:
				self._nodes[0].left = (self._nodes[0].left + self._step) % self._surface.get_width()
			elif self._direction == 1:
				self._nodes[0].left = (self._nodes[0].left - self._step) % self._surface.get_width()
			elif self._direction == 2:
				self._nodes[0].top = (self._nodes[0].top - self._step) % self._surface.get_height()
			else:
				self._nodes[0].top = (self._nodes[0].top + self._step) % self._surface.get_height()
				
			self._counter = 0
			
			# check for collisions
			if self._nodes[0].collidelist(self._nodes[3:]) > -1:
				return -1
		
		self._counter = self._counter + 1
		
			
	def change_direction(self, direction):
		self._direction = direction
		
	def increase_speed(self):
		self.slowness = self.slowness - 1
		if self.slowness < 0:
			self.slowness = 0
		print(self.slowness)
			
	def decrease_speed(self):
		self.slowness = self.slowness + 1
		print(self.slowness)
		
	def add_node(self):
		if len(self._nodes) > 0:
			self._nodes.append(self._nodes[-1].copy())
		else:
			self._nodes.append(pygame.Rect(0,0,self.node_size,self.node_size))
			
	def get_length(self):
		return len(self._nodes)
		
	def get_nodes(self):
		return self._nodes
		
	def get_head(self):
		return self._nodes[0]
	
	def draw(self):
		for i in range(0,len(self._nodes)):
			pygame.draw.rect(self._surface, RED, self._nodes[i], 1)
			

class App:
	
	def __init__(self, top_panel_height = 15, node_size = 10, game_surf_width = 340, game_surf_height = 280):
		self.top_panel_height = top_panel_height
		self.node_size = node_size
		self.calc_surfaces(game_surf_width, game_surf_height)
		self._running = True
		self._display_surf = None
		self._top_panel = None
		self._game_surf = None
		self._snake = None
		self._init_length = 40
		self._game_over = False
		self._font_go = None
		self._font_stats = None
		self._font_mess = None
		self._apple = None
		
	def calc_surfaces(self, game_surf_width, game_surf_height):
		# make game surface dimensions multiple of node_size for consistent rendering
		remainder = game_surf_width % self.node_size
		if remainder != 0:
			self.game_surf_width = game_surf_width - remainder
		else:
			self.game_surf_width = game_surf_width
			
		remainder = game_surf_height % self.node_size
		if remainder != 0:
			self.game_surf_height = game_surf_height - remainder
		else:
			self.game_surf_height = game_surf_height
			
		print("w: %d, h: %d" % (self.game_surf_width, self.game_surf_height))
		
		self._window_width = self.game_surf_width
		self._window_height = self.game_surf_height + self.top_panel_height
		
				
	def on_init(self):
		random.seed()
		pygame.init()		
		self._display_surf = pygame.display.set_mode((self._window_width, self._window_height))
		self._top_panel = pygame.Surface((self._window_width, self.top_panel_height))
		self._game_surf = pygame.Surface((self.game_surf_width, self.game_surf_height))
		pygame.display.set_caption('Snake')
		pygame.font.init()	
		self._font_go = pygame.font.SysFont("cantarell",40,bold=True)	
		self._font_stats = pygame.font.SysFont("cantarell",14,bold=True)
		self._font_mess = pygame.font.SysFont("cantarell",16)
		#self._font_stats = pygame.freetype.Font("/usr/share/fonts/cantarell/Cantarell-Regular.otf",15)
		self._snake = Snake(surface = self._game_surf, node_size = self.node_size, init_length = self._init_length)
		self._apple = Apple(surface = self._game_surf, node_size = self.node_size, snake = self._snake)
		self._running = True
		self._game_over = False
		self._paused = False
		
	def on_event(self,event):
		if event.type == KEYUP:
			if (event.key == K_z):
				self._snake.decrease_speed()				
			elif (event.key == K_x):
				self._snake.increase_speed()
			elif (event.key == K_s):
				self._snake.add_node()
			elif (event.key == K_ESCAPE):
				self._running = False
			elif (event.key == K_r):
				self._apple.reposition()
			elif (event.key == K_SPACE) and self._game_over:
				# restart
				self.on_init()
				
		elif event.type == KEYDOWN:
			if (event.key == K_RIGHT):
				self._snake.change_direction(Snake.RIGHT)
			elif (event.key == K_LEFT):
				self._snake.change_direction(Snake.LEFT)
			elif (event.key == K_UP):
				self._snake.change_direction(Snake.UP)
			elif (event.key == K_DOWN):
				self._snake.change_direction(Snake.DOWN)
			elif (event.key == K_p) and self._paused:
				self._paused = False
			elif (event.key == K_p):
				self._paused = True
				
		elif event.type == QUIT:
			self._running = False
			
	def on_loop(self):
		if not self._game_over:			
			if self._snake.update() == -1:
				self._game_over = True
			if self._apple.check_collision():
				print("ate an apple")
				self._apple.reposition()
				self._snake.add_node()
		
		
	def on_render(self):
		self._display_surf.fill(BLACK)
		self._top_panel.fill(GREEN)
		self._display_surf.blit(self._top_panel,(0,0))
		self._game_surf.fill(WHITE)
		self._snake.draw()
		self._apple.draw()
		self._display_surf.blit(self._game_surf,(0,self._top_panel.get_height()))
		
		self.render_text(self._font_stats, 'L:{} S:{}'.format(self._snake.get_length(), self._snake.slowness),
						WHITE, x=5, centery=self._top_panel.get_height()/2)
		
		if self._game_over:
			self.render_text(self._font_go,"GAME OVER",RED,
							center=(self._window_width/2, self._window_height/2))
			self.render_text(self._font_mess,"Press SPACE to restart or ESC to exit",RED,
							centerx=self._window_width/2,y=self._window_height-self._font_mess.get_height())
		pygame.display.flip()
		
	def render_text(self, font, text, color, **kwargs):
		textsurf = font.render(text,True,color)
		textrect = textsurf.get_rect(**kwargs)
		self._display_surf.blit(textsurf,textrect)
		
	def on_cleanup(self):
		pygame.quit()
		
	def on_execute(self):
		if self.on_init() == False:
			self._running = False
			
		while(self._running):
				
			# parse and handle events			
			for event in pygame.event.get():
				self.on_event(event)			
			
			if not self._paused:
				self.on_loop()
				self.on_render()
			time.sleep (20.0 / 1000.0)
            
		self.on_cleanup()
		
#if __name__ == "__main__":
theApp = App()
theApp.on_execute()     
            
		
		
		
