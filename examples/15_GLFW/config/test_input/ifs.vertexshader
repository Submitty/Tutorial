#version 330 core

// data flows in from the C++ program
layout(location = 0) in vec4 in_position;
layout(location = 1) in vec4 in_color;

// data flows out to the fragment shader
out vec4 ex_color;
                
// the transformation matrix is constant (not varying)
// when applied to this unit of geometry
uniform mat4 MVP;

void main(){
  
  // apply the transformation
  gl_Position =  MVP * in_position;
  
  // just pass the color to the fragment shader
  ex_color = in_color;

}

