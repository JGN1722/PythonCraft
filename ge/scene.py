from math import tan, cos
import threading

from camera import *
from chunk import *
from settings import *

class Scene:
	def __init__(self,app):
		self.app = app
		self.camera = Camera_fly(self.app,position=INITIAL_CAMERA_POSITION)
		self.center_chunk = self.world_pos_to_chunk_pos(INITIAL_CAMERA_POSITION)
		self.world = {}
		
		self.write_camera_matrix_to_shader()
		
		self.factor_x = SPHERE_RADIUS / cos(half_x := H_FOV * 0.5)
		self.tan_x = tan(half_x)
		
		self.factor_y = SPHERE_RADIUS / cos(half_y := V_FOV * 0.5)
		self.tan_y = tan(half_y)
	
	def load(self):
		app = self.app
		
		for x in range(self.center_chunk[0] - CHUNK_SIZE,self.center_chunk[0] + (CHUNK_SIZE << 1),CHUNK_SIZE):
			for z in range(self.center_chunk[2] - CHUNK_SIZE,self.center_chunk[2] + (CHUNK_SIZE << 1),CHUNK_SIZE):
				self.world[(x,0,z)] = Chunk(app,pos=(x,0,z))
		
		self.build_chunk_meshes()
	
	def build_chunk_meshes(self):
		for chunk in self.world.values():
			chunk.build_chunk_mesh()
	
	def write_camera_matrix_to_shader(self):
		self.app.default_program['m_proj'].write(self.camera.m_proj)
	
	def update(self):
		self.camera.update()
		player_chunk_pos = self.world_pos_to_chunk_pos(self.camera.position)
		if not player_chunk_pos == self.center_chunk:
			center_chunk = (self.center_chunk[0],0,self.center_chunk[2])
			world_generation_thread = threading.Thread(target=self.generate_infinite_world,args=(center_chunk,player_chunk_pos),daemon=True)
			self.center_chunk = player_chunk_pos
			world_generation_thread.start()
			#self.generate_infinite_world(self.center_chunk, player_chunk_pos)
			#self.center_chunk = player_chunk_pos
	
	def generate_infinite_world(self,center_chunk,player_chunk_pos):
		app = self.app
		
		#generate new chunks, assuming the player doesn't move more than 1 chunk / frame
		if player_chunk_pos[0] < center_chunk[0]:
			
			x = center_chunk[0] - (CHUNK_SIZE << 1)
			for z in range(center_chunk[2] - CHUNK_SIZE, center_chunk[2] + (CHUNK_SIZE << 1),CHUNK_SIZE):
				self.world[(x,0,z)] = Chunk(app,pos=(x,0,z))
			
			#build the new meshes and rebuild the old ones
			x = center_chunk[0] - (CHUNK_SIZE << 1)
			z = center_chunk[2]
			self.world[(x,0,z)].vbo = self.world[(x,0,z)].get_vertex_data()
			self.world[(x,0,z + CHUNK_SIZE)].vbo = self.world[(x,0,z + CHUNK_SIZE)].get_vertex_data()
			self.world[(x,0,z - CHUNK_SIZE)].vbo = self.world[(x,0,z - CHUNK_SIZE)].get_vertex_data()
			for z in range(center_chunk[2] - CHUNK_SIZE, center_chunk[2] + (CHUNK_SIZE << 1),CHUNK_SIZE):
				self.world[(x + CHUNK_SIZE,0,z)].vbo = self.world[(x + CHUNK_SIZE,0,z)].get_vertex_data()
				
				self.world[(x + CHUNK_SIZE * 3,0,z)].vao.release()
				del self.world[(x + CHUNK_SIZE * 3,0,z)]
		
		elif player_chunk_pos[0] > center_chunk[0]:
			
			x = center_chunk[0] + (CHUNK_SIZE << 1)
			for z in range(center_chunk[2] - CHUNK_SIZE, center_chunk[2] + (CHUNK_SIZE << 1),CHUNK_SIZE):
				self.world[(x,0,z)] = Chunk(app,pos=(x,0,z))
			
			#build the new meshes and rebuild the old ones
			x = center_chunk[0] + (CHUNK_SIZE << 1)
			z = center_chunk[2]
			self.world[(x,0,z)].vbo = self.world[(x,0,z)].get_vertex_data()
			self.world[(x,0,z + CHUNK_SIZE)].vbo = self.world[(x,0,z + CHUNK_SIZE)].get_vertex_data()
			self.world[(x,0,z - CHUNK_SIZE)].vbo = self.world[(x,0,z - CHUNK_SIZE)].get_vertex_data()
			for z in range(center_chunk[2] - CHUNK_SIZE, center_chunk[2] + (CHUNK_SIZE << 1),CHUNK_SIZE):
				self.world[(x,0,z)].vbo = self.world[(x,0,z)].get_vertex_data()
				self.world[(x - CHUNK_SIZE,0,z)].vbo = self.world[(x - CHUNK_SIZE,0,z)].get_vertex_data()
				
				self.world[(x - CHUNK_SIZE * 3,0,z)].vao.release()
				del self.world[(x - CHUNK_SIZE * 3,0,z)]
		
		elif  player_chunk_pos[2] < center_chunk[2]:
			
			z = center_chunk[2] - (CHUNK_SIZE << 1)
			for x in range(center_chunk[0] - CHUNK_SIZE, center_chunk[0] + (CHUNK_SIZE << 1),CHUNK_SIZE):
				self.world[(x,0,z)] = Chunk(app,pos=(x,0,z))
			
			#build the new meshes and rebuild the old ones
			z = center_chunk[2] - (CHUNK_SIZE << 1)
			x = center_chunk[0]
			self.world[(x,0,z)].vbo = self.world[(x,0,z)].get_vertex_data()
			self.world[(x + CHUNK_SIZE,0,z)].vbo = self.world[(x + CHUNK_SIZE,0,z)].get_vertex_data()
			self.world[(x - CHUNK_SIZE,0,z)].vbo = self.world[(x - CHUNK_SIZE,0,z)].get_vertex_data()
			for x in range(center_chunk[0] - CHUNK_SIZE, center_chunk[0] + (CHUNK_SIZE << 1),CHUNK_SIZE):
				self.world[(x,0,z)].vbo = self.world[(x,0,z)].get_vertex_data()
				self.world[(x,0,z + CHUNK_SIZE)].vbo = self.world[(x,0,z + CHUNK_SIZE)].get_vertex_data()
				
				self.world[(x,0,z + CHUNK_SIZE * 3)].vao.release()
				del self.world[(x,0,z + CHUNK_SIZE * 3)]
		
		else:
			
			z = center_chunk[2] + (CHUNK_SIZE << 1)
			for x in range(center_chunk[0] - CHUNK_SIZE, center_chunk[0] + (CHUNK_SIZE << 1),CHUNK_SIZE):
				self.world[(x,0,z)] = Chunk(app,pos=(x,0,z))
			
			#build the new meshes and rebuild the old ones
			z = center_chunk[2] + (CHUNK_SIZE << 1)
			x = center_chunk[0]
			self.world[(x,0,z)].vbo = self.world[(x,0,z)].get_vertex_data()
			self.world[(x + CHUNK_SIZE,0,z)].vbo = self.world[(x + CHUNK_SIZE,0,z)].get_vertex_data()
			self.world[(x - CHUNK_SIZE,0,z)].vbo = self.world[(x - CHUNK_SIZE,0,z)].get_vertex_data()
			for x in range(center_chunk[0] - CHUNK_SIZE, center_chunk[0] + (CHUNK_SIZE << 1),CHUNK_SIZE):
				self.world[(x,0,z - CHUNK_SIZE)].vbo = self.world[(x,0,z - CHUNK_SIZE)].get_vertex_data()
				
				self.world[(x,0,z - CHUNK_SIZE * 3)].vao.release()
				del self.world[(x,0,z - CHUNK_SIZE * 3)]
			
	def render(self):
		for chunk in self.world.values():
			if chunk.vbo is not None:
				chunk.build_vao(chunk.vbo)
				chunk.vbo = None
			if self.is_on_frustum(chunk.pos):
				chunk.render()
	
	def is_on_frustum(self,pos):
		sphere_vec = pos + glm.vec3(H_CHUNK_SIZE) - self.camera.position
		
		sz = glm.dot(sphere_vec, self.camera.forward)
		if not (NEAR - SPHERE_RADIUS <= sz <= FAR + SPHERE_RADIUS):
			return False
		
		sy = glm.dot(sphere_vec, self.camera.up)
		dist = self.factor_y + sz * self.tan_y
		if not (-dist <= sy <= dist):
			return False
		
		sx = glm.dot(sphere_vec, self.camera.right)
		dist = self.factor_x + sz * self.tan_x
		if not (-dist <= sx <= dist):
			return False
		
		return True
	
	@staticmethod
	def world_pos_to_chunk_pos(pos):
		x, y, z = pos
		x, z = int(x), int(z)
		return (x>>5)<<5,0,(z>>5)<<5
	
	def is_voxel_solid(self,x,y,z):
		x, y, z = int(x), int(y), int(z)
		
		if not 0 <= y < CHUNK_HEIGHT:
			return False
		
		cx = (x >> 5) << 5
		cz = (z >> 5) << 5
		
		if not (cx,0,cz) in self.world.keys():
			return False
		
		rx = x - cx
		ry = y
		rz = z - cz
		
		return self.world[(cx,0,cz)].voxels[rx + CHUNK_SIZE * rz + CHUNK_AREA * ry] != 0