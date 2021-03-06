from scene import Scene
import taichi as ti
from taichi.math import *

night_mode = True
exposure = 1.0 + night_mode * 9.

scene = Scene(exposure=10)
scene.set_floor(-1, (0.0, 0.3, 0.5))
scene.set_directional_light((1, 1, 0), 0.2, vec3(1.0, 1.0, 1.0) / exposure)
scene.set_background_color(vec3(0.6, 0.8, 1.0) / exposure)


@ti.func
def create_butterfly(pos, sz, axis, angle, amplitude, color):
    xscale = 3
    yscale = 2.6
    for I in ti.grouped(ti.ndrange((-sz, sz), (-sz, sz))):
        tmp = vec2([I[0]+0.5,I[1]+0.5])
        tmp[0] = tmp[0] / sz * xscale
        tmp[1] = tmp[1] / sz * yscale + 0.55
        pol_r = tmp.norm()
        pol_theta = ti.asin(tmp[1] / pol_r) + 4 * ti.math.pi
        sdf = pol_r - ( ti.exp(ti.sin(pol_theta))-2*ti.cos(4*pol_theta)+ti.pow(ti.sin(2*pol_theta-ti.math.pi)/24,5) )
        if sdf < 0:
            scene.set_voxel(pos + ti.math.rotate3d(vec3(I, ti.abs(I[0])*ti.pow(I.norm()/(ti.sqrt(2)*sz), 1 / amplitude) ), axis, angle), 2,
                            color / pol_r)
            scene.set_voxel(pos + ti.math.rotate3d(vec3(I, ti.abs(I[0])*ti.pow(I.norm()/(ti.sqrt(2)*sz), 1 / amplitude) + 1), axis, angle), 2,
                            color / pol_r)



@ti.func
def create_moutain(pos, sz, height, color):
    sigma = vec2(0.3, 0.1)
    mu = vec2(0,0)
    for I in ti.grouped(ti.ndrange((-sz, sz), (-sz, sz))):
        y_axis = height * ti.exp(-(ti.pow(I[0]/sz*2,2)/ti.pow(sigma[0],2)+ti.pow(I[1]/sz*2,2)/ti.pow(sigma[1],2))/2) / (2 * ti.math.pi * ti.sqrt(sigma[0] * sigma[1]))
        for i in range(y_axis):
            if i > 40: color = vec3(1.0,1.0,1.0)
            scene.set_voxel(pos + ivec3(I[0], i, I[1]), 1, color)

@ti.func
def create_cloud(pos, sz, height, color):
    sigma = vec2(0.6, 0.3)
    for I in ti.grouped(ti.ndrange((-sz+5, sz+5), (-sz, sz))):
        y_axis = height * ti.exp(
            -(ti.pow(I[0] / sz, 2) / ti.pow(sigma[0], 2) + ti.pow(I[1] / sz, 2) / ti.pow(sigma[1], 2)) / 2) / (
                             2 * ti.math.pi * ti.sqrt(sigma[0] * sigma[1]))
        for i in range(y_axis):
            scene.set_voxel(pos + ivec3(I[0], i, I[1]), 1, color)


@ti.func
def create_heart(pos, sz, color):
    '''
    3-3*sin(@theta)+sin(@theta)*sqrt(abs(cos(@theta)))/(sin(@theta)+1.6)
    @theta=[0, 2 @ pi, 33], color = red, shade = middle)
    '''
    for I in ti.grouped(ti.ndrange((-sz, sz), (-sz, sz))):
        tmp = vec2([I[0]+0.5,I[1]+0.5])
        tmp[0] = tmp[0] / sz * 4
        tmp[1] = tmp[1] / sz * 4.5 - 1.5
        pol_r = tmp.norm()
        pol_theta = ti.asin(tmp[1] / pol_r)
        sdf = pol_r-(3-3*ti.sin(pol_theta)+(ti.sin(pol_theta)*ti.sqrt(ti.abs(ti.cos(pol_theta)))/(ti.sin(pol_theta)+1.6)))
        if sdf < 0:
            z_axis = sz * ti.exp(-(ti.pow(I[0]/sz,2)/0.25+ti.pow(I[1]/sz,2)/0.25)/2) / (0.5 * ti.math.pi)
            for i in range(-z_axis, z_axis):
                scene.set_voxel(pos + ivec3(I, i), 2, color/exposure)

@ti.kernel
def initialize_voxels():
    # Your code here! :-)
    # ti.math.pi
    # ti.exp()
    # ti.sin()
    # ti.cos()
    # ti.pow()
    # create stars
    '''for I in ti.grouped(ti.ndrange((-64, 63), (-64, 63), (-64, -60))):
        if ti.random() < 0.003: scene.set_voxel(I, 2, vec3(1.0, 1.0, 0.1))'''
    create_butterfly(vec3(10,-40,40), 15, vec3(-1, 1, 1), radians(30), 1.5, vec3(0.1, 0.3, 0.8))
    create_butterfly(vec3(-20, -40, 40), 10, vec3(1, 1, 1), radians(-30), 1.8, vec3(0.8, 0.2, 0.1))
    create_moutain(vec3(0,-64,0),128,60,vec3(0,0.3,0.2))
    create_cloud(vec3(0,10,0), 20 , 20, vec3(1.0,1.0,1.0))
    if night_mode:
        create_heart(ivec3(40, 40, -40), 20, vec3(0.8, 0.1, 0.2))

initialize_voxels()

scene.finish()

