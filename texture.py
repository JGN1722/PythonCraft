import pygame as pg
import moderngl as mgl

class Texture:
	def __init__(self,ctx):
		self.ctx = ctx
		self.textures = {}
		self.textures[1] = self.get_texture(path='textures\\rock.png')
		self.textures[2] = self.get_texture(path='textures\\grass.png')
		self.textures[3] = self.get_texture(path='textures\\dirt.jpg')
		self.textures[4] = self.get_texture(path='textures\\wood.jpg')
		self.textures[5] = self.get_texture(path='textures\\leaves.jfif')
		self.textures[6] = self.get_texture(path='textures\\water.jpeg')
		
		self.texture_array = self.get_texture(path='textures\\tex_array_1.png')
	
	def get_texture(self,path, is_tex_array=False):
		texture = pg.image.load(path).convert()
		texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
		if is_tex_array:
			num_layers = 16 * texture.get_height() // texture.get_width()
			texture = self.ctx.texture_array(size=(texture.get_width(),texture.get_height() // num_layers, num_layers),components=4,data=pg.image.tostring(texture,'RGBA'))
		else:
			texture = self.ctx.texture(size=texture.get_size(), components=3, data=pg.image.tostring(texture,'RGB'))
		
		texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
		texture.build_mipmaps()
		
		texture.anisotropy = 32.0
		
		return texture
	
	def destroy(self):
		[tex.release() for tex in self.textures.values()]