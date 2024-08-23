from math import tan, cos
from time import monotonic
from chunk import *
from settings import *

class Scene:
	def __init__(self,app):
		self.app = app
		self.world = {}
		
		self.write_camera_matrix_to_shader()
		
		self.factor_x = SPHERE_RADIUS / cos(half_x := H_FOV * 0.5)
		self.tan_x = tan(half_x)
		
		self.factor_y = SPHERE_RADIUS / cos(half_y := V_FOV * 0.5)
		self.tan_y = tan(half_y)
	
	def load(self):
		app = self.app
		
		chunk = Chunk(app, pos=(0,0,0))
		print('testing the new procedure by running it 20 times')
		t1_new = monotonic()
		for i in range(20):
			chunk.build_chunk_mesh()
		t2_new = monotonic()
		run_time_new = t2_new - t1_new
		print('new procedure took',run_time_new,'to run 20 times')
		
		
		for x in range(-CHUNK_SIZE * 1, CHUNK_SIZE * 2, CHUNK_SIZE):
			for z in range(-CHUNK_SIZE * 1, CHUNK_SIZE * 2, CHUNK_SIZE):
				self.world[(x,0,z)] = Chunk(app,pos=(x,0,z))
		
		self.build_chunk_meshes()	
	def build_chunk_meshes(self):
		for chunk in self.world.values():
			chunk.build_chunk_mesh()
	
	def write_camera_matrix_to_shader(self):
		self.app.default_program['m_proj'].write(self.app.camera.m_proj)
		
	def render(self):
		for chunk in self.world.values():
			if self.is_on_frustum(chunk.pos):
				chunk.render()
	
	def is_on_frustum(self,pos):
		sphere_vec = pos + glm.vec3(H_CHUNK_SIZE) - self.app.camera.position
		
		sz = glm.dot(sphere_vec, self.app.camera.forward)
		if not (NEAR - SPHERE_RADIUS <= sz <= FAR + SPHERE_RADIUS):
			return False
		
		sy = glm.dot(sphere_vec, self.app.camera.up)
		dist = self.factor_y + sz * self.tan_y
		if not (-dist <= sy <= dist):
			return False
		
		sx = glm.dot(sphere_vec, self.app.camera.right)
		dist = self.factor_x + sz * self.tan_x
		if not (-dist <= sx <= dist):
			return False
		
		return True
	
	def is_voxel_solid(self,x,y,z):
		x, y, z = int(x), int(y), int(z)
		
		if not 0 <= y < CHUNK_SIZE:
			return False
		
		cx = (x >> 5) << 5
		cz = (z >> 5) << 5
		
		rx = x - cx
		ry = y
		rz = z - cz
		
		return self.world[(cx,0,cz)].voxels[rx + CHUNK_SIZE * rz + CHUNK_AREA * ry] != 0