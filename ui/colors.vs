#version 150
uniform mat4 projection; // P
uniform mat4 view; // V
uniform mat4 transform; // ?

in vec3 vertPos;
in vec4 vertColor;

out vec4 fragColor;

void main()
{
    gl_Position = projection * view * transform * vec4(vertPos, 1);
    fragColor = vertColor;
}
