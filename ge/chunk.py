import numpy as np
import glm
from settings import *

class Chunk:
	def __init__(self,app,pos=(0,0,0)):
		self.app = app
		self.pos = pos
		
		self.vbo = None
		self.vao = None
		self.m_model = glm.translate(glm.mat4(),pos)
		self.program = self.app.default_program
		self.write_in_m_model = self.program['m_model'].write
		self.voxels = self.build_voxels()
	
	def render(self):
		if self.vao:
			self.write_in_m_model(self.m_model)
			self.vao.render()
	
	def should_place_tree(self,x,z):
		return (x * (z << 1) + x + z) % 199 == 0
	
	def build_voxels(self):
		voxels = {}
		
		for x in range(CHUNK_SIZE):
			for z in range(CHUNK_SIZE):
				height = int(glm.simplex(glm.vec2(self.pos[0]+x, self.pos[2]+z) * 0.05) * 5) + 128
				
				for y in range(CHUNK_HEIGHT):
					position = x + CHUNK_SIZE * z + CHUNK_AREA * y
					
					#cave_noise = abs(glm.simplex(glm.vec3(self.pos[0]+x,self.pos[1]+y,self.pos[2]+z) * CAVE_SCALE) * CAVE_AMPLITUDE + glm.simplex(glm.vec3(-self.pos[0]+x,-self.pos[1]+y,-self.pos[2]+z) * CAVE_SCALE) * CAVE_AMPLITUDE)
					#cave_noise = abs(glm.simplex(glm.vec3(self.pos[0]+x,self.pos[1]+y,self.pos[2]+z) * CAVE_SCALE) * CAVE_AMPLITUDE)
					cave_noise = 0
				
					if y <= height:
						
						if cave_noise < CAVE_TRESHOLD:
							tex_id = 6 if y == height else 5 if y > height - 5 else 4
							if tex_id == 6 and height <= 126:
								tex_id = 7
							voxels[position] = tex_id
						else:
							voxels[position] = 0
					
					elif not position in voxels.keys():
						
							voxels[position] = 0
				
				if self.should_place_tree(self.pos[0]+x,self.pos[2]+z) and 0 <= x-H_TREE_WIDTH < x+H_TREE_WIDTH < CHUNK_SIZE and 0 <= z-H_TREE_WIDTH < z+H_TREE_WIDTH < CHUNK_SIZE:
					for i in range(height+1,height+6):
						voxels[x + CHUNK_SIZE * z + CHUNK_AREA * i] = 1
					
					for ix in range(x-H_TREE_WIDTH,x+H_TREE_WIDTH+1):
						for iz in range(z-H_TREE_WIDTH,z+H_TREE_WIDTH+1):
							for iy in range(height + 4, height + 7):
								if not (ix,iy,iz) in ((x-2,height+6,z-2),(x-2,height+6,z+2),(x+2,height+6,z-2),(x+2,height+6,z+2)):
									if 0 <= ix < CHUNK_SIZE and 0 <= iy < CHUNK_HEIGHT and 0 <= iz < CHUNK_SIZE:
										position = ix + CHUNK_SIZE * iz + CHUNK_AREA * iy
										if not position in voxels.keys() or voxels[position] == 0:
											 voxels[position] = 2
					
					iz = z
					iy = height + 7
					for ix in range(x-1,x+2):
						if 0 <= ix < CHUNK_SIZE and 0 <= iy < CHUNK_HEIGHT and 0 <= iz < CHUNK_SIZE:
							position = ix + CHUNK_SIZE * iz + CHUNK_AREA * iy
							if not position in voxels.keys() or voxels[position] == 0:
								voxels[position] = 2
					
					ix = x
					iy = height + 7
					for iz in range(z-1,z+2,2):
						if 0 <= ix < CHUNK_SIZE and 0 <= iy < CHUNK_HEIGHT and 0 <= iz < CHUNK_SIZE:
							position = ix + CHUNK_SIZE * iz + CHUNK_AREA * iy
							if not position in voxels.keys() or voxels[position] == 0:
								voxels[position] = 2
		
		return voxels
	
	def get_ao(self,x,y,z,voxels,plane):
		is_voxel_solid = self.app.scene.is_voxel_solid
		x += self.pos[0]
		y += self.pos[1]
		z += self.pos[2]
		
		if plane == 'Y':
			a = not is_voxel_solid(x,y,z-1)
			b = not is_voxel_solid(x-1,y,z-1)
			c = not is_voxel_solid(x-1,y,z)
			d = not is_voxel_solid(x-1,y,z+1)
			e = not is_voxel_solid(x,y,z+1)
			f = not is_voxel_solid(x+1,y,z+1)
			g = not is_voxel_solid(x+1,y,z)
			h = not is_voxel_solid(x+1,y,z-1)
			#print(a,b,c,d,e,f,g,h)
		
		elif plane == 'X':
			a = not is_voxel_solid(x,y,z-1)
			b = not is_voxel_solid(x,y-1,z-1)
			c = not is_voxel_solid(x,y-1, z)
			d = not is_voxel_solid(x,y-1,z+1)
			e = not is_voxel_solid(x,y,z+1)
			f = not is_voxel_solid(x,y+1,z+1)
			g = not is_voxel_solid(x,y+1,z)
			h = not is_voxel_solid(x,y+1,z-1)
		
		else:
			a = not is_voxel_solid(x-1,y,z)
			b = not is_voxel_solid(x-1,y-1,z)
			c = not is_voxel_solid(x,y-1,z)
			d = not is_voxel_solid(x+1,y-1,z)
			e = not is_voxel_solid(x+1,y,z)
			f = not is_voxel_solid(x+1,y+1,z)
			g = not is_voxel_solid(x,y+1,z)
			h = not is_voxel_solid(x-1,y+1,z)
		
		return (a + b + c), (g + h + a), (e + f + g), (c + d + e)
	
	@staticmethod
	def add_data(vertex_data,index,*vertices):
		for vertice in vertices:
			for attr in vertice:
				vertex_data[index] = attr
				index += 1
		return index
	
	def get_vertex_data(self):
		all_vertex_data = np.empty(CHUNK_VOLUME * 18 * 7, dtype='f4')
		index = 0
		
		world = self.app.scene.world
		pos_x, pos_z = self.pos[0], self.pos[2]
		keys = world.keys()
		
		minus_x_voxels = world[(pos_x-32,0,pos_z)].voxels if (pos_x-32,0,pos_z) in keys else None
		plus_x_voxels = world[(pos_x+32,0,pos_z)].voxels if (pos_x+32,0,pos_z) in keys else None
		minus_z_voxels = world[(pos_x,0,pos_z-32)].voxels if (pos_x,0,pos_z-32) in keys else None
		plus_z_voxels = world[(pos_x,0,pos_z+32)].voxels if (pos_x,0,pos_z+32) in keys else None
		
		border_offset = 0.002
		border_offset_2 = 0.004
		tex_height = 1 / 14
		tex_width = 1 / 3
		
		for x in range(CHUNK_SIZE):
			for z in range(CHUNK_SIZE):
				for y in range(CHUNK_HEIGHT):
					voxel_pos = x + CHUNK_SIZE * z + CHUNK_AREA * y
					id = self.voxels[voxel_pos]
					
					if not id:
						continue
					
					ty = tex_height * (id - 1 + 7) + border_offset
					tx = tex_width + border_offset
					
					# Up face
					if y == CHUNK_HEIGHT - 1 or not self.voxels[voxel_pos + CHUNK_AREA]:
						ao = self.get_ao(x,y+1,z,self.voxels,'Y')
						flip_id = ao[1] + ao[3] > ao[0] + ao[2]
						
						tx += tex_width
						v0 = (tx, ty,x, 1 + y, 1 + z,0,ao[3])
						v1 = (tx + tex_width - border_offset_2, ty + tex_height - border_offset_2,1 + x, 1 + y, z,0,ao[1])
						v2 = (tx, ty + tex_height - border_offset_2,x, 1 + y, z,0,ao[0])
						v3 = (tx, ty,x, 1 + y, 1 + z,0,ao[3])
						v4 = (tx + tex_width - border_offset_2, ty,1 + x, 1 + y, 1 + z,0,ao[2])
						v5 = (tx + tex_width - border_offset_2, ty + tex_height - border_offset_2,1 + x, 1 + y, z,0,ao[1])
						tx -= tex_width
						
						index = self.add_data(all_vertex_data,index,v0,v1,v2,v3,v4,v5)
					
					# Bottom face
					if not y == 0 and not self.voxels[voxel_pos - CHUNK_AREA]:
						ao = self.get_ao(x,y-1,z,self.voxels,'Y')
						flip_id = ao[1] + ao[3] > ao[0] + ao[2]
						
						tx -= tex_width
						v0 = (tx, ty + tex_height - border_offset_2,x, y, 1 + z,1,ao[3])
						v1 = (tx + tex_width - border_offset_2, ty,1 + x, y, z,1,ao[1])
						v2 = (tx + tex_width - border_offset_2, ty + tex_height - border_offset_2,1 + x, y, 1 + z,1,ao[2])
						v3 = (tx, ty + tex_height - border_offset_2,x, y, 1 + z,1,ao[3])
						v4 = (tx, ty,x, y, z,1,ao[0])
						v5 = (tx + tex_width - border_offset_2, ty,1 + x, y, z,1,ao[1])
						tx += tex_width
						
						index = self.add_data(all_vertex_data,index,v0,v1,v2,v3,v4,v5)
					
					# Front face
					if (z != CHUNK_SIZE - 1 and not self.voxels[voxel_pos + CHUNK_SIZE]) or (z == CHUNK_SIZE - 1 and plus_z_voxels and not plus_z_voxels[x + CHUNK_AREA * y]):
						ao = self.get_ao(x,y,z+1,self.voxels,'Z')
						flip_id = ao[1] + ao[3] > ao[0] + ao[2]
						
						v0 = (tx, ty,x, y, 1 + z,2,ao[0])
						v1 = (tx + tex_width - border_offset_2, ty + tex_height - border_offset_2,1 + x, 1 + y, 1 + z,2,ao[2])
						v2 = (tx, ty + tex_height - border_offset_2,x, 1 + y, 1 + z,2,ao[1])
						v3 = (tx, ty,x, y, 1 + z,2,ao[0])
						v4 = (tx + tex_width - border_offset_2, ty,1 + x, y, 1 + z,2,ao[3])
						v5 = (tx + tex_width - border_offset_2, ty + tex_height - border_offset_2,1 + x, 1 + y, 1 + z,2,ao[2])
						
						index = self.add_data(all_vertex_data,index,v0,v1,v2,v3,v4,v5)
					
					# Back face
					if (z != 0 and not self.voxels[voxel_pos - CHUNK_SIZE]) or (z == 0 and minus_z_voxels and not minus_z_voxels[x + CHUNK_SIZE * (CHUNK_SIZE - 1) + CHUNK_AREA * y]):
						ao = self.get_ao(x,y,z-1,self.voxels,'Z')
						flip_id = ao[1] + ao[3] > ao[0] + ao[2]
						
						v0 = (tx, ty,1 + x, y, z,3,ao[3])
						v1 = (tx + tex_width - border_offset_2, ty,x, y, z,3,ao[0])
						v2 = (tx + tex_width - border_offset_2, ty + tex_height - border_offset_2,x, 1 + y, z,3,ao[1])
						v3 = (tx + tex_width - border_offset_2, ty + tex_height - border_offset_2,x, 1 + y, z,3,ao[1])
						v4 = (tx, ty + tex_height - border_offset_2,1 + x, 1 + y, z,3,ao[2])
						v5 = (tx, ty,1 + x, y, z,3,ao[3])
						
						index = self.add_data(all_vertex_data,index,v0,v1,v2,v3,v4,v5)
					
					# Right face
					if (x != CHUNK_SIZE - 1 and not self.voxels[voxel_pos + 1]) or (x == CHUNK_SIZE - 1 and plus_x_voxels and not plus_x_voxels[CHUNK_SIZE * z + CHUNK_AREA * y]):
						ao = self.get_ao(x+1,y,z,self.voxels,'X')
						flip_id = ao[1] + ao[3] > ao[0] + ao[2]
						
						v0 = (tx, ty,1 + x, y, 1 + z,4,ao[3])
						v1 = (tx + tex_width - border_offset_2, ty + tex_height - border_offset_2,1 + x, 1 + y, z,4,ao[1])
						v2 = (tx, ty + tex_height - border_offset_2,1 + x, 1 + y, 1 + z,4,ao[2])
						v3 = (tx, ty,1 + x, y, 1 + z,4,ao[3])
						v4 = (tx + tex_width - border_offset_2, ty,1 + x, y, z,4,ao[0])
						v5 = (tx + tex_width - border_offset_2, ty + tex_height - border_offset_2,1 + x, 1 + y, z,4,ao[1])
						
						index = self.add_data(all_vertex_data,index,v0,v1,v2,v3,v4,v5)
					
					# Left face
					if (x != 0 and not self.voxels[voxel_pos - 1]) or (x == 0 and minus_x_voxels and not minus_x_voxels[CHUNK_SIZE - 1 + CHUNK_SIZE * z + CHUNK_AREA * y]):
						ao = self.get_ao(x-1,y,z,self.voxels,'X')
						flip_id = ao[1] + ao[3] > ao[0] + ao[2]
						
						v0 = (tx + tex_width - border_offset_2, ty + tex_height - border_offset_2,x, 1 + y, 1 + z,5,ao[2])
						v1 = (tx, ty + tex_height - border_offset_2,x, 1 + y, z,5,ao[1])
						v2 = (tx, ty,x, y, z,5,ao[0])
						v3 = (tx + tex_width - border_offset_2, ty + tex_height - border_offset_2,x, 1 + y, 1 + z,5,ao[2])
						v4 = (tx, ty,x, y, z,5,ao[0])
						v5 = (tx + tex_width - border_offset_2, ty,x, y, 1 + z,5,ao[3])
						
						index = self.add_data(all_vertex_data,index,v0,v1,v2,v3,v4,v5)
		
		return all_vertex_data[:index]
	
	def build_chunk_mesh(self):
		vertex_data = self.get_vertex_data()
		self.build_vao(vertex_data)
	
	def build_vao(self,vertex_data):
		vbo = self.app.ctx.buffer(vertex_data)
		self.vao = self.app.ctx.vertex_array(self.program, [
			(vbo, '2f 3f 1f 1f', 'in_texcoord_0', 'in_position', 'in_face_id', 'in_ao')
		])
