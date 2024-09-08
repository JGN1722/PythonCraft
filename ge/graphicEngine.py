import pygame as pg
import moderngl as mgl
import sys
from time import monotonic

from settings import *
from scene import Scene

class GraphicsEngine:
	def __init__(self,win_size=(1600,900)):
		pg.init()
		
		self.WIN_SIZE = win_size
		
		pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
		pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
		pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
		
		pg.display.set_mode(self.WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)
		
		pg.event.set_grab(True)
		pg.mouse.set_visible(False)
		
		self.ctx = mgl.create_context()
		self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
		#self.ctx.enable(flags=mgl.DEPTH_TEST)
		
		self.clock = pg.time.Clock()
		self.time = 0
		self.delta_time = 0
		
		self.texture_array = get_texture(self.ctx,path='textures\\tex_array_1.png')
		self.default_program = get_program(self.ctx,'default')
		
		self.texture_array.use()
		

		self.default_program['fogColor'].value = SKY_COLOR
		self.default_program['fogStart'].value = FOG_START
		self.default_program['fogEnd'].value = FOG_END
		
		self.scene = Scene(self)
		self.scene.load()
	
	def check_events(self):
		for event in pg.event.get():
			if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
				self.default_program.release()
				self.texture_array.release()
				pg.quit()
				sys.exit()
	
	def update(self):
		self.scene.update()
	
	def render(self):
		self.ctx.clear(color=SKY_COLOR)
		self.scene.render()
		pg.display.flip()
	
	def get_time(self):
		self.time = pg.time.get_ticks() * 0.001
	
	def run(self):
		self.delta_time = 0
		i = 0
		f = 0
		while True:
			t1 = monotonic() * 1000
			self.check_events()
			self.update()
			self.render()
			t2 = monotonic() * 1000
			self.delta_time = t2 - t1
			
			i += 1
			f += self.delta_time
			if f > 1000:
				#pg.display.set_caption(str(i))
				f -= 1000
				i = 0

def get_program(ctx,shader_name):
	with open(f'shaders\\{shader_name}.vert') as file:
		vertex_shader = file.read()
	
	with open(f'shaders\\{shader_name}.frag') as file:
		fragment_shader = file.read()
	
	program = ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
	return program

def get_texture(ctx,path):
	texture = pg.image.load(path).convert()
	texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
	texture = ctx.texture(size=texture.get_size(), components=3, data=pg.image.tostring(texture,'RGB'))
	
	texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
	texture.build_mipmaps()
	
	texture.anisotropy = 32.0
	
	return texture

if __name__ == '__main__':
	app = GraphicsEngine(WIN_SIZE)
	app.run()