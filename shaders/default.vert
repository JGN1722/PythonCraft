#version 330 core

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_position;
layout (location = 2) in float in_face_id;

out float face_id;
out vec2 uv0;
out vec3 fragPos;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

void main() {
	face_id = in_face_id;
	uv0 = in_texcoord_0;
	fragPos = vec3(m_model * vec4(in_position, 1.0));
	gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}
