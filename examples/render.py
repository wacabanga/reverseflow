""" (Inverse) Rendering"""
import sys
import getopt
import tensorflow as tf
import numpy as np
import reverseflow.to_arrow
from reverseflow.util.misc import *
from reverseflow.util.tf import *

floatX = 'float32'


def rand_rotation_matrix(deflection=1.0, randnums=None, floatX='float32'):
    """
    Creates a random rotation matrix.
    deflection: the magnitude of the rotation. For 0, no rotation; for 1,
    competely random
    rotation. Small deflection => small perturbation.
    randnums: 3 random numbers in the range [0, 1]. If `None`, they will be
    auto-generated.


    From: realtimerendering.com/resources/GraphicsGems/gemsiii/rand_rotation.c
    """

    if randnums is None:
        randnums = np.random.uniform(size=(3,))

    theta, phi, z = randnums

    theta = theta * 2.0*deflection*np.pi  # Rotation about the pole (Z).
    phi = phi * 2.0*np.pi  # For direction of pole deflection.
    z = z * 2.0*deflection  # For magnitude of pole deflection.

    # Compute a vector V used for distributing points over the sphere
    # via the reflection I - V Transpose(V).  This formulation of V
    # will guarantee that if x[1] and x[2] are uniformly distributed,
    # the reflected points will be uniform on the sphere.  Note that V
    # has length sqrt(2) to eliminate the 2 in the Householder matrix.

    r = np.sqrt(z)
    Vx, Vy, Vz = V = (
        np.sin(phi) * r,
        np.cos(phi) * r,
        np.sqrt(2.0 - z)
        )

    st = np.sin(theta)
    ct = np.cos(theta)

    R = np.array(((ct, st, 0), (-st, ct, 0), (0, 0, 1)))

    # Construct the rotation matrix  ( V Transpose(V) - I ) R.

    M = (np.outer(V, V) - np.eye(3)).dot(R)
    return np.array(M, dtype=floatX)


# n random matrices
def rand_rotation_matrices(n: int, floatX='float32'):
    return np.stack([rand_rotation_matrix(floatX=floatX) for i in range(n)])


# Genereate values in raster space, x[i,j] = [i,j]
def gen_fragcoords(width: int, height: int):
    """Create a (width * height * 2) matrix, where element i,j is [i,j]
       This is used to generate ray directions based on an increment"""
    raster_space = np.zeros([width, height, 2], dtype=floatX)
    for i in range(width):
        for j in range(height):
            raster_space[i, j] = np.array([i, j], dtype=floatX) + 0.5
    return raster_space


# Append an image filled with scalars to the back of an image.
def stack(intensor, width: int, height: int, scalar):
    scalars = np.ones([width, height, 1], dtype=floatX) * scalar
    return np.concatenate([intensor, scalars], axis=2)


def switch(cond, a, b):
    return cond*a + (1-cond)*b


def dot(a, b):
    """Dot product of two a and b"""
    print("A", a)
    print("B", b)
    c = tf.reduce_sum(a * b)
    print("C", c.get_shape())
    return c


def norm(x):
    return np.linalg.norm(x, 2, axis=3)


def make_ro(r, raster_space, width, height):
    """Symbolically render rays starting with raster_space according to geometry
      e  defined by """
    nmatrices = r.shape[0]
    resolution = np.array([width, height], dtype=floatX)
    # Normalise it to be bound between 0 1
    norm_raster_space = raster_space / resolution
    # Put it in NDC space, -1, 1
    screen_space = -1.0 + 2.0 * norm_raster_space
    # Make pixels square by mul by aspect ratio
    ndc_space = screen_space * np.array([resolution[0]/resolution[1], 1.0],
                                        dtype=floatX)
    # Ray Direction

    # Position on z-plane
    ndc_xyz = stack(ndc_space, width, height, 1.0)*0.5  # Change focal length

    # Put the origin farther along z-axis
    ro = np.array([0, 0, 1.5], dtype=floatX)

    # Rotate both by same rotation matrix
    ro_t = np.dot(np.reshape(ro, (1, 3)), r)
    ndc_t = np.dot(np.reshape(ndc_xyz, (1, width, height, 3)), r)
    print(ndc_t.shape, width, height, nmatrices)
    ndc_t = np.reshape(ndc_t, (width, height, nmatrices, 3))
    ndc_t = np.transpose(ndc_t, (2, 0, 1, 3))

    # Increment by 0.5 since voxels are in [0, 1]
    ro_t = ro_t + 0.5
    ndc_t = ndc_t + 0.5
    # Find normalise ray dirs from origin to image plane
    unnorm_rd = ndc_t - np.reshape(ro_t, (nmatrices, 1, 1, 3))
    rd = unnorm_rd / np.reshape(norm(unnorm_rd), (nmatrices, width, height, 1))
    return rd, ro_t


def gen_img(voxels, rotation_matrix, width, height, nsteps, res):
    """Renders n voxel grids in m different views
    voxels : (n, res, res, res)
    rotation_matrix : (m, 4)
    returns (n, m, width, height))
    """
    raster_space = gen_fragcoords(width, height)
    rd, ro = make_ro(rotation_matrix, raster_space, width, height)
    a = 0 - ro  # c = 0
    b = 1 - ro  # c = 1
    nmatrices = rotation_matrix.shape[0]
    tn = np.reshape(a, (nmatrices, 1, 1, 3))/rd
    tff = np.reshape(b, (nmatrices, 1, 1, 3))/rd
    tn_true = np.minimum(tn, tff)
    tff_true = np.maximum(tn, tff)
    # do X
    tn_x = tn_true[:, :, :, 0]
    tff_x = tff_true[:, :, :, 0]
    tmin = 0.0
    tmax = 10.0
    t0 = tmin
    t1 = tmax
    t02 = np.where(tn_x > t0, tn_x, t0)
    t12 = np.where(tff_x < t1, tff_x, t1)
    # y
    tn_x = tn_true[:, :, :, 1]
    tff_x = tff_true[:, :, :, 1]
    t03 = np.where(tn_x > t02, tn_x, t02)
    t13 = np.where(tff_x < t12, tff_x, t12)
    # z
    tn_x = tn_true[:, :, :, 2]
    tff_x = tff_true[:, :, :, 2]
    t04 = np.where(tn_x > t03, tn_x, t03)
    t14 = np.where(tff_x < t13, tff_x, t13)

    # Shift a little bit to avoid numerial inaccuracies
    t04 = t04*1.001
    t14 = t14*0.999

    nvoxgrids = voxels.get_shape()[0]
    print("hello", nvoxgrids)
    left_over = np.ones((nvoxgrids, nmatrices * width * height,))
    step_size = (t14 - t04)/nsteps
    orig = np.reshape(ro, (nmatrices, 1, 1, 3)) \
        + rd * np.reshape(t04, (nmatrices, width, height, 1))
    xres = yres = zres = res

    orig = np.reshape(orig, (nmatrices * width * height, 3))
    rd = np.reshape(rd, (nmatrices * width * height, 3))
    step_sz = np.reshape(step_size, (nmatrices * width * height, 1))
    print(voxels)
    voxels = tf.reshape(voxels, [-1])

    for i in range(nsteps):
        # print "step", i
        pos = orig + rd*step_sz*i
        voxel_indices = np.floor(pos*res)
        pruned = np.clip(voxel_indices, 0, res-1)
        p_int = pruned.astype('int32')
        indices = np.reshape(p_int, (nmatrices*width*height, 3))
        flat_indices = indices[:, 0] + res * \
            (indices[:, 1] + res * indices[:, 2])
        # print("ishape", flat_indices.shape, "vshape", voxels.get_shape())
        # attenuation = voxels[:, indices[:,0],indices[:,1],indices[:,2]]
        attenuation = tf.gather(voxels, flat_indices)
        print("attenuation", attenuation.get_shape(), step_sz.shape)
        reshaped_step_sz = step_sz.reshape(nmatrices * width * height)
        left_over = left_over*tf.exp(-attenuation * reshaped_step_sz)

    img = left_over
    img_shape = tf.TensorShape((nvoxgrids, nmatrices, width, height))
    pixels = tf.reshape(img, img_shape)
    mask = t14 > t04
    # print(mask.reshape())
    return pixels
    # return tf.select(mask.reshape(img_shape), pixels, tf.ones_like(pixels)),
    # rd, ro, tn_x, tf.ones(img_shape), orig, voxels


def default_options():
    options = {}
    options['width'] = 128
    options['height'] = 128
    options['res'] = 32
    options['nsteps'] = 6
    options['nvoxgrids'] = 1
    options['nviews'] = 1
    print(options)
    return options

def generate_graph(nviews, nvoxgrids, width, height, res, nsteps):
    rotation_matrices = rand_rotation_matrices(nviews)
    voxel_input = tf.placeholder(tf.float32, shape=(nvoxgrids, res, res, res))
    img_output = gen_img(voxel_input, rotation_matrices, width, height, nsteps,
                        res)
    return voxel_input, img_output


def render_voxel(voxel, img_output, voxel_input):
    sess = tf.Session()
    output_img = sess.run(img_output, feed_dict={voxel_input: voxel})
    return output_img


def standalone(options):
    import matplotlib.pyplot as plt
    options = default_options()
    voxel_input, img_output = generate_graph(**options)
    img = render_voxel(random_voxel(options['res']), img_output, voxel_input)
    g = tf.get_default_graph()
    tf.train.SummaryWriter('/home/zenna/repos/wacabanga/reverseflow/log', g)
    plt.imshow(img.reshape(options['width'], options['height']))
    plt.show()


def random_voxel(res):
    voxel_grids = np.load("/home/zenna/data/ModelNet40/alltrain32.npy")
    random_voxel = np.random.randint(0, voxel_grids.shape[0])
    return voxel_grids[random_voxel].reshape(1, res, res, res)


def test_render():
    options = default_options()
    voxel_input, img_output = generate_graph(**options)
    import pdb; pdb.set_trace()

    img = render_voxel(random_voxel(options['res']), img_output, voxel_input)

    reverseflow.to_arrow.graph_to_arrow([img_output])
    return img

if __name__ == "__main__":
    # standalone(default_options())
    test_render()
