"""Test of different methods of maximising completeness"""
import matplotlib.pyplot as plt
import tensorflow as tf
import tensortemplates as tt
from tensortemplates import res_net
import numpy as np

# Interactive plotting
plt.ion()
EPS = 1e-5

def norm(tensor):
    sqr = tf.square(tensor) + EPS
    return tf.sqrt(tf.reduce_sum(sqr, reduction_indices=1) + EPS) + EPS


def circle_loss(tensor, c=0.0):
    s = 0.5
    norms = norm(tensor) + EPS
    sdfs = tf.maximum(0.0, norms-s) + tf.maximum(0.0, s-c-norms) + EPS
    return tf.reduce_mean(sdfs) + EPS

axis = plt.axis([-1, 1, -1, 1])
scatter = None
def update_plot(theta_samples):
    global scatter
    if scatter is None:
        scatter = plt.scatter(theta_samples[:,0], theta_samples[:,1])
    else:
        scatter.set_offsets(theta_samples)
    plt.pause(0.05)


def gen_update_step(loss):
    with tf.name_scope('optimization'):
        # optimizer = tf.train.MomentumOptimizer(0.001,
        #                                        momentum=0.05)
        optimizer = tf.train.AdamOptimizer(0.002)
        update_step = optimizer.minimize(loss)
        return update_step


def var_loss(phi, g):
    op, params = g(phi)
    theta_samples = op[0]
    mean = tf.reduce_mean(theta_samples, reduction_indices=0) + EPS
    diffs = theta_samples - mean + EPS
    sqr_diffs = tf.reduce_sum(tf.abs(diffs), reduction_indices=1) + EPS
    loss = -tf.reduce_mean(sqr_diffs) + EPS
    return theta_samples, loss


def rnd_pairwise_dist_loss(phi, g, permutation):
    op, params = g(phi)
    theta_samples = op[0]
    theta_pemute = tf.gather(theta_samples, permutation)
    diff = theta_pemute - theta_samples + EPS
    sqrdiff = tf.abs(diff)
    euclids = tf.reduce_sum(sqrdiff, reduction_indices=1) + EPS
    return theta_samples, -(tf.reduce_mean(euclids) + EPS)

def non_iden(permutation):
    return [p for i, p in enumerate(permutation) if i != p]


def non_iden_idx(permutation):
    return [i for i, p in enumerate(permutation) if i != p]

def non_equal(x, y):
    assert len(x) == len(y)
    new_x = []
    new_y = []
    for i in range(len(x)):
        if x[i] != y[i]:
            new_x.append(x[i])
            new_y.append(y[i])
    return new_x, new_y

def rnd_nn_mean_dist(phi, g, shape):
    op, params = g(phi)
    # sess = tf.InteractiveSession()
    # init = tf.initialize_all_variables()
    # sess.run(init)
    theta_samples = op[0]
    theta_samples = tf.reshape(theta_samples, shape)
    # theta_samples[0].eval(session=sess, feed_dict={phi:np.random.rand(256,2)})
    shapes = [1]*len(theta_samples.shape)
    shapes[0] = theta_samples.shape[0]
    thetas = tf.tile(theta_samples, tf.stack(shapes))

    n_thetas = shape[0]
    # construct both permutations to get all pairwise distances
    permutation = np.tile(np.arange(n_thetas), n_thetas)
    permutation_idx = np.repeat(np.arange(n_thetas), n_thetas)
    permutation, permutation_idx = non_equal(permutation, permutation_idx)  # eliminate corresponding indices if equal

    theta_shrunk = tf.gather(thetas, permutation)
    theta_pemute = tf.gather(thetas, permutation_idx)
    # FIXME fails starting from here

    theta_shrunk = tf.reshape(theta_shrunk, (n_thetas, n_thetas-1, *theta_shrunk.get_shape().as_list()[1:]))
    theta_pemute = tf.reshape(theta_pemute, (n_thetas, n_thetas-1, *theta_pemute.get_shape().as_list()[1:]))
    all_dist = tf.reduce_sum(tf.abs(theta_pemute - theta_shrunk), axis=2)
    nn_dist = tf.reduce_min(all_dist, axis=1)
    nn_mean = tf.reduce_mean(nn_dist)
    # nn_mean.eval(session=sess, feed_dict={phi:np.random.rand(256,2)})
    return theta_samples, -nn_mean


def rnd_pairwise_min_dist(phi, g, permutation, permutation_idx, n_dist, shape):
    op, params = g(phi)
    theta_samples = op[0]
    theta_samples = tf.reshape(theta_samples, shape)
    shapes = [1]*len(theta_samples.shape)
    shapes[0] = theta_samples.shape[0]
    thetas = tf.tile(theta_samples, tf.stack(shapes))
    # configured thetas to be size^2 array tensor as n_dist is up to size^2

    permutation = permutation[:n_dist]
    permutation_idx = permutation_idx[:n_dist]
    theta_shrunk = tf.gather(thetas, permutation_idx)
    theta_pemute = tf.gather(thetas, permutation)
    # got correspinding theta tensors to compute pairwise min distance
    diff = theta_pemute - theta_shrunk + EPS
    sqrdiff = tf.abs(diff)
    euclids = tf.reduce_sum(sqrdiff, reduction_indices=1) + EPS
    rp = tf.reduce_min(euclids)
    return theta_samples, -rp


def rnd_pairwise_gap_ratio(phi, g, permutation, permutation_idx, n_dist, shape):
    op, params = g(phi)
    theta_samples = op[0]
    theta_samples = tf.reshape(theta_samples, shape)
    shapes = [1]*len(theta_samples.shape)
    shapes[0] = theta_samples.shape[0]
    thetas = tf.tile(theta_samples, tf.stack(shapes))
    # configured thetas to be size^2 array tensor as n_dist is up to size^2

    permutation = permutation[:n_dist]
    permutation_idx = permutation_idx[:n_dist]
    theta_shrunk = tf.gather(thetas, permutation_idx)
    theta_pemute = tf.gather(thetas, permutation)
    # got corresponding theta tensors to compute pairwise min distance
    diff = theta_pemute - theta_shrunk + EPS
    sqrdiff = tf.abs(diff)
    euclids = tf.reduce_sum(sqrdiff, reduction_indices=1) + EPS
    rp = tf.reduce_min(euclids)/2 + EPS
    RRp = tf.reduce_max(euclids) + EPS
    return theta_samples, -(RRp / rp)



def train(sdf,
          batch_size=512,
          phi_ndim=2,
          theta_ndim=2,
          template=res_net.template,
          template_options={}):

    phi_shape = (batch_size, phi_ndim)
    theta_shape = (batch_size, theta_ndim)
    phi = tf.placeholder(shape=phi_shape, dtype='float32',name="phi")
    permutation = tf.placeholder(shape=(None), dtype='int32')
    permutation_idx = tf.placeholder(shape=(None), dtype='int32')
    def g(phi):
        return template([phi],
                        inp_shapes=[phi_shape],
                        out_shapes=[theta_shape],
                        **template_options)

    # used for pairwise min distance
    n_dist = batch_size**2//4
    theta_samples, loss1 = rnd_nn_mean_dist(phi, g, (batch_size, theta_ndim))
    loss2 = sdf(theta_samples, 0.1)
    # loss = loss2
    lmbda = 0.5
    loss2 = lmbda*loss2
    loss = loss1 + loss2
    # # loss = loss1
    variables = tf.all_variables()
    # sess = tf.InteractiveSession()
    # init = tf.initialize_all_variables()
    # sess.run(init)
    #
    # loss1.eval(session=sess, feed_dict={phi: np.random.rand(256, 2)})
    gradients1 = tf.gradients(loss1, variables)
    gradients2 = tf.gradients(loss2, variables)
    lossgradient = tf.gradients(loss, [loss1, loss2])
    sub_losses = [loss1, loss2]
 97371b5a2f2c38b90ad0d5f663958aa486d7b58d
    update_step = gen_update_step(loss)
    fetches = {'loss': loss,
               'sub_losses': sub_losses,
               'update_step': update_step,
               'gradients1': gradients1,
               'gradients2': gradients2,
               'lossgradient': lossgradient,
               'theta_samples': theta_samples}

    train_loop(loss, update_step, phi, permutation, permutation_idx, fetches)

def sumsum(xs):
    return np.sum([np.sum(x) for x in xs])


def train_loop(loss, update_step, phi, permutation, permutation_idx, fetches, n_iterations=50000,
               batch_size=256):
    sess = tf.Session()
    init = tf.initialize_all_variables()
    sess.run(init)
    sfx = str(time.time())
    for i in range(n_iterations):
        if i % 10 == 0:
            file_path = os.path.join(path,"%s_%s.png" % (sfx, i))
            plt.savefig(file_path)
        phi_samples = np.random.rand(*phi.get_shape().as_list())
        perm_data = np.arange(batch_size**2)
        np.random.shuffle(perm_data)
        non_iden_perm_data = non_iden(perm_data)
        perm_data_idx = non_iden_idx(perm_data)
        output = sess.run(fetches,
                          feed_dict={phi: phi_samples,
                                     permutation: non_iden_perm_data,
                                     permutation_idx: perm_data_idx})
        print("Loss: ", output['loss'])
        print("Losses: ", output['sub_losses'])
        print("gradients min_dist_loss: ", sumsum(output['gradients1']))
        print("gradients circle_loss: ", sumsum(output['gradients2']))
        print("loss gradient", output['lossgradient'])
        update_plot(output['theta_samples'])


options = {'layer_width': 5,
           'nblocks': 1,
           'block_size': 2,
           'reuse': False}

train(circle_loss, template_options=options)
