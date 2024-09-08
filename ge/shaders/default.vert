#version 330 core

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_position;
layout (location = 2) in float in_face_id;
layout (location = 3) in float in_ao;

out float shading;
out vec2 uv0;
out vec3 fragPos;

const float face_shading[6] = float[6](
	1.0, 0.5, //bottom top
	0.6, 0.7, //right left
	0.5, 0.8  //front back
);

//const float ao_values[4] = float[4](0.1, 0.25, 0.5, 1.0);
const float ao_values[4] = float[4](0.2, 0.5, 0.75, 1.0);

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

void main() {
	shading = face_shading[int(in_face_id)] * ao_values[int(in_ao)];
	uv0 = in_texcoord_0;
	fragPos = vec3(m_model * vec4(in_position, 1.0));
	gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}