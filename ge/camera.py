import glm
import pygame as pg
from math import ceil
from settings import *

class Camera:
	def __init__(self,app,position=(0,0,4),yaw=-90,pitch=0):
		self.app = app
		self.program = app.default_program
		self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]
		self.position = glm.vec3(position)
		self.up = glm.vec3(0,1,0)
		self.right = glm.vec3(1,0,0)
		self.forward = glm.vec3(0,0,1)
		
		self.velocity = glm.vec3(0,0,0)
		self.up_force = 0
		
		self.yaw = yaw
		self.pitch = pitch
		
		self.m_view = self.get_view_matrix()
		
		self.m_proj = self.get_projection_matrix()
	
	def rotate(self):
		rel_x, rel_y = pg.mouse.get_rel()
		self.yaw += rel_x * SENSITIVITY
		self.pitch -= rel_y * SENSITIVITY
		self.pitch = max(-89, min(89, self.pitch))
	
	def get_projection_matrix(self):
		return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)
	
	def get_view_matrix(self):
		return glm.lookAt(self.position, self.position + self.forward, self.up)
	
	def update(self):
		self.rotate()
		self.move()
		self.update_camera_vectors()
		self.m_view = self.get_view_matrix()
		pg.display.set_caption(str((int(self.position.x),int(self.position.y),int(self.position.z))))
		self.program['m_view'].write(self.m_view)
		self.program['camPos'].write(self.position)

class Camera_fly(Camera):
	def __init__(self,app,position=(0,0,4),yaw=-90,pitch=0):
		super().__init__(app,position,yaw,pitch)
	
	def update_camera_vectors(self):
		yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)
		
		self.forward.x = glm.cos(yaw) * glm.cos(pitch)
		self.forward.y = glm.sin(pitch)
		self.forward.z = glm.sin(yaw) * glm.cos(pitch)
		
		self.forward = glm.normalize(self.forward)
		self.right = glm.normalize(glm.cross(self.forward,glm.vec3(0,1,0)))
		self.up = glm.normalize(glm.cross(self.right,self.forward))
	
	def move(self):
		velocity = SPEED * self.app.delta_time
		keys = pg.key.get_pressed()
		if keys[pg.K_UP]:
			self.position += self.forward * velocity
		if keys[pg.K_DOWN]:
			self.position -= self.forward * velocity
		if keys[pg.K_RIGHT]:
			self.position += self.right * velocity
		if keys[pg.K_LEFT]:
			self.position -= self.right * velocity
		if keys[pg.K_q]:
			self.position += self.up * velocity
		if keys[pg.K_e]:
			self.position -= self.up * velocity




class Camera_walk(Camera):
	def __init__(self,app,position=(0,0,4),yaw=-90,pitch=0):
		super().__init__(app,position,yaw,pitch)
		self.is_on_ground = False
		self.up_force = 0
	
	def move(self):
		velocity = SPEED * self.app.delta_time
		gravity = GRAVITY * self.app.delta_time
		
		keys = pg.key.get_pressed()
		
		self.is_on_ground = self.app.scene.is_voxel_solid(self.position[0],self.position[1] - 2,self.position[2])
		
		#gravity
		if not self.is_on_ground:
			self.position -= self.up * gravity
		
		#going up when jumping
		if self.up_force:
			self.position += glm.vec3(0,self.up_force,0) * velocity
			self.up_force -= 0.1
			if self.up_force < -TERMINAL_VELOCITY:
				self.up_force = -TERMINAL_VELOCITY
		
		
		if self.is_on_ground:
			self.up_force = 0

				
		# Horizontal movement in the plane (x, z)
		if keys[pg.K_UP]:
			self.position += glm.vec3(self.forward.x, 0, self.forward.z) * velocity
			if self.app.scene.is_voxel_solid(self.position[0],self.position[1] - 1,self.position[2]) or self.app.scene.is_voxel_solid(self.position[0],self.position[1],self.position[2]):
				self.position -= glm.vec3(self.forward.x, 0, self.forward.z) * velocity
		if keys[pg.K_DOWN]:
			self.position -= glm.vec3(self.forward.x, 0, self.forward.z) * velocity
			if self.app.scene.is_voxel_solid(self.position[0],self.position[1] - 1,self.position[2]) or self.app.scene.is_voxel_solid(self.position[0],self.position[1],self.position[2]):
				self.position += glm.vec3(self.forward.x, 0, self.forward.z) * velocity
		if keys[pg.K_RIGHT]:
			self.position += self.right * velocity
			if self.app.scene.is_voxel_solid(self.position[0],self.position[1] - 1,self.position[2]) or self.app.scene.is_voxel_solid(self.position[0],self.position[1],self.position[2]):
				self.position -= self.right * velocity
		if keys[pg.K_LEFT]:
			self.position -= self.right * velocity
			if self.app.scene.is_voxel_solid(self.position[0],self.position[1] - 1,self.position[2]) or self.app.scene.is_voxel_solid(self.position[0],self.position[1],self.position[2]):
				self.position += self.right * velocity
		
		#Jump
		if keys[pg.K_SPACE] and self.is_on_ground:
			self.up_force = JUMP_STRENGTH
	
	def update_camera_vectors(self):
		yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)
		
		# Forward vector, constrained to the horizontal plane for walking
		self.forward.x = glm.cos(yaw)
		self.forward.y = 0  # No vertical movement for walking
		self.forward.z = glm.sin(yaw)
		
		self.forward = glm.normalize(self.forward)
		self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
		
		# Keep up vector fixed
		self.up = glm.vec3(0, 1, 0)
