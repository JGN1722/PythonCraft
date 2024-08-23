#version 330 core

layout (location = 0) out vec4 fragColor;

in float face_id;
in vec2 uv0;
in vec3 fragPos;

uniform sampler2D u_texture_0;
uniform vec3 camPos;

// Fog parameters
uniform vec3 fogColor;
uniform float fogStart;
uniform float fogEnd;

void main() {
	float distance = length(fragPos - camPos);
	
	vec3 color = texture(u_texture_0, uv0).rgb;
	
	float faceFactor = 1.0 - (face_id / 10.0);
	color = color * faceFactor;
	
	// Calculate fog
	float fogFactor = clamp((fogEnd - distance) / (fogEnd - fogStart), 0.0, 1.0);
	color = mix(fogColor, color, fogFactor);
	
	fragColor = vec4(color, 1.0);
}
