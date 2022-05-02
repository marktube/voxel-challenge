from scene import Scene
import taichi as ti
from taichi.math import *

night_mode = True
exposure = 1.0 + night_mode * 4.

scene = Scene(exposure=10)
scene.set_floor(-10, (0.4, 0.8, 0.0))
scene.set_directional_light((1, 1, 0), 0.2, vec3(1.0, 1.0, 1.0) / exposure)
scene.set_background_color(vec3(0.6, 0.8, 1.0) / exposure)

@ti.func
def create_moon(pos, radius, color):
    for I in ti.grouped(ti.ndrange((-radius, radius), (-radius, radius), (-radius, radius))):
        if I.norm() < radius:
           scene.set_voxel(pos + I, 2, color)

@ti.func
def create_butterfly(pos, sz, axis, angle, color):
    xscale = 5
    yscale = 4
    for I in ti.grouped(ti.ndrange((-sz, sz), (-sz, sz))):
        tmp = vec2([I[0],I[1]])
        tmp[0] = tmp[0] / sz * xscale
        tmp[1] = tmp[1] / sz * yscale -0.5
        pol_r = tmp.norm()
        pol_theta = ti.asin(tmp[1] / pol_r) + 4*ti.math.pi
        sdf = pol_r - ( ti.exp(ti.sin(pol_theta))-2*ti.cos(4*pol_theta)+ti.pow(ti.sin(2*pol_theta-ti.math.pi)/24,5) )
        if sdf < 0:
            scene.set_voxel(pos + ti.math.rotate3d(vec3(I, pol_r),axis,angle), 2, color/pol_r)
            scene.set_voxel(pos + ti.math.rotate3d(vec3(I, pol_r-1), axis, angle), 2, color / pol_r)

@ti.func
def create_moutain(pos, sz, height):
    pass

@ti.func
def create_heart(pos, sz, rotate, color):
    pass


@ti.kernel
def initialize_voxels():
    # Your code here! :-)
    # ti.math.pi
    # ti.exp()
    # ti.sin()
    # ti.cos()
    # ti.pow()
    create_butterfly(vec3(10,0,0), 15, vec3(-1, 1, 1), radians(30), vec3(0.1, 0.3, 0.8))
    create_butterfly(vec3(-20, 0, 0), 10, vec3(1, 1, 1), radians(-30), vec3(0.8, 0.2, 0.1))
    if night_mode:
        create_moon(ivec3(40, 40, -40), 10, vec3(1.0, 1.0, 0.1))

initialize_voxels()

scene.finish()

