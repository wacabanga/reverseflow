import os
import sys
import tensorflow as tf
from arrows.compositearrow import CompositeArrow
from arrows.port_attributes import make_in_port, make_out_port
from arrows import AddArrow
from arrows.tfarrow import TfLambdaArrow
from tflearn.layers import fully_connected
from reverseflow.train.gan import set_gan_arrow, g_from_g_theta
import matplotlib.pyplot as plt
from reverseflow.invert import invert
from arrows.apply.propagate import propagate
import numpy as np
from wacacore.util.io import handle_args
from arrows import Arrow
from reverseflow.to_graph import gen_input_tensors, arrow_to_graph
from wacacore.train.common import (train_loop, updates, variable_summaries,
                                   setup_file_writers, get_variables)
from reverseflow.train.gan import train_gan_arr


def SumNArrow(ninputs: int):
  """
  Create arrow f(x1, ..., xn) = sum(x1, ..., xn)
  Args:
    n: number of inputs
  Returns:
    Arrow of n inputs and one output
  """
  assert ninputs > 1
  c = CompositeArrow(name="SumNArrow")
  light_port = c.add_port()
  make_in_port(light_port)

  for _ in range(ninputs - 1):
    add = AddArrow()
    c.add_edge(light_port, add.in_port(0))
    dark_port = c.add_port()
    make_in_port(dark_port)
    c.add_edge(dark_port, add.in_port(1))
    light_port = add.out_port(0)

  out_port = c.add_port()
  make_out_port(out_port)
  c.add_edge(add.out_port(0), out_port)

  assert c.is_wired_correctly()
  assert c.num_in_ports() == ninputs
  return c


def gan_shopping_arrow_pi(nitems: int, options) -> CompositeArrow:
  """Gan on shopping basket"""
  n_fake_samples = options['n_fake_samples']
  n_samples = n_fake_samples + 1
  batch_size = options['batch_size']
  # nitems = options['nitems']
  fwd = SumNArrow(nitems)
  inv = invert(fwd)
  info = propagate(inv)

  def gen_func(args):
    # import pdb; pdb.set_trace()
    """Generator function"""
    with tf.variable_scope("generator", reuse=False):
      inp = tf.concat(args, axis=1)
      inp = fully_connected(inp, inv.num_param_ports(), activation='elu')
      inps = tf.split(inp, axis=1, num_or_size_splits=inv.num_param_ports())
      return inps

  def disc_func(args):
    # import pdb; pdb.set_trace()
    """Discriminator function """
    with tf.variable_scope("discriminator", reuse=False):
      inp = tf.concat(args, axis=2)
      inp = fully_connected(inp, n_samples, activation='sigmoid')
      return [inp]

  # Make a conditional generator from the inverse\
  num_non_param_in_ports = inv.num_in_ports() - inv.num_param_ports()
  g_theta = TfLambdaArrow(inv.num_in_ports() - inv.num_param_ports() + 1,
                          inv.num_param_ports(), func=gen_func)
  cond_gen = g_from_g_theta(inv, g_theta)

  disc = TfLambdaArrow(nitems, 1, func=disc_func)
  gan_arr = set_gan_arrow(fwd, cond_gen, disc, n_fake_samples, 2,
                          x_shapes=[(batch_size, 1) for i in range(nitems)],
                          z_shape=(batch_size, 1))

  return gan_arr


def gan_shopping_arrow_compare(nitems: int, options) -> CompositeArrow:
  """Comparison for Gan, g is straight neural network"""
  n_fake_samples = options['n_fake_samples']
  n_samples = n_fake_samples + 1
  batch_size = options['batch_size']
  # nitems = options['nitems']
  fwd = SumNArrow(nitems)

  def gen_func(args):
    # import pdb; pdb.set_trace()
    """Generator function"""
    with tf.variable_scope("generator", reuse=False):
      inp = tf.concat(args, axis=1)
      inp = fully_connected(inp, nitems, activation='elu')
      inps = tf.split(inp, axis=1, num_or_size_splits=nitems)
      return inps

  def disc_func(args):
    # import pdb; pdb.set_trace()
    """Discriminator function """
    with tf.variable_scope("discriminator", reuse=False):
      inp = tf.concat(args, axis=2)
      inp = fully_connected(inp, n_samples, activation='sigmoid')
      return [inp]

  cond_gen = TfLambdaArrow(2, nitems, func=gen_func)
  disc = TfLambdaArrow(nitems, 1, func=disc_func)
  gan_arr = set_gan_arrow(fwd, cond_gen, disc, n_fake_samples, 2,
                          x_shapes=[(batch_size, 1) for i in range(nitems)],
                          z_shape=(batch_size, 1))

  return gan_arr


def make_nice_plots(fetch_data, feed_dict, i: int, **kwargs):
  """Call back for plotting x and y samples in training"""
  if 'test_fetch_res' in fetch_data:
    plt.figure()
    xyz_data = fetch_data['test_fetch_res']['xyz']
    print("VARS!", [np.var(xyz_data[i]) for i in range(len(xyz_data))])
    print("Sum check!", sum([xyz_data[i][0] for i in range(len(xyz_data))]))
    plt.scatter(xyz_data[0], xyz_data[1])
    plt.savefig('scatter_{}.png'.format(i))


def gan_arr_tf_stuff(gan_arr: Arrow, nitems: int, options):
  """Extract tensorflow graph anfrom gan arrow"""
  n_fake_samples = options['n_fake_samples']
  n_samples = n_fake_samples + 1
  batch_size = options['batch_size']

  tf.reset_default_graph()
  with tf.name_scope(gan_arr.name):
      input_tensors = gen_input_tensors(gan_arr, param_port_as_var=False)
      output_tensors = arrow_to_graph(gan_arr, input_tensors)

  fetch = {}
  x_tens = input_tensors[0:nitems]
  z_ten = input_tensors[nitems]
  perm_ten = input_tensors[nitems + 1]
  d_loss, g_loss = output_tensors[0:2]
  xyz = output_tensors[2:]
  fetch['xyz'] = xyz

  def train_gen():
    """Generator for x, z and permutation"""
    while True:
      data = {}
      x_ten_data = {x_tens[i]: np.random.randn(batch_size, 1) for i in range(nitems)}
      data.update(x_ten_data)
      data[z_ten] = np.random.randn(batch_size, 1)
      perm = np.arange(n_samples)
      np.random.shuffle(perm)
      data[perm_ten] = perm
      yield data

  def test_gen():
    """Generator for x, z and permutation"""
    while True:
      data = {}
      x_ten_data = {x_tens[i]: np.ones(shape=(batch_size, 1)) * 7.0 for i in range(nitems)}
      data.update(x_ten_data)
      data[z_ten] = np.random.randn(batch_size, 1)
      perm = np.arange(n_samples)
      np.random.shuffle(perm)
      data[perm_ten] = perm
      yield data

  callbacks = [make_nice_plots]
  callbacks = []
  train_gan_arr(d_loss, g_loss, [train_gen()], [test_gen()], callbacks,
                fetch, options)


def default_options():
  "Default options for pdt training"
  options = {}
  options['num_iterations'] = (int, 100)
  options['save_every'] = (int, 100)
  options['batch_size'] = (int, 512)
  options['gpu'] = (bool, False)
  options['dirname'] = (str, "dirname")
  options['n_fake_samples'] = (int, 1)
  options['datadir'] = (str, os.path.join(os.environ['DATADIR'], "rf"))
  return options


def run_shopping_gan(options):
  """Generate the arrow and do the training"""
  nitems = 2
  gan_arr = gan_shopping_arrow_pi(nitems, options)
  # gan_arr = gan_shopping_arrow_compare(nitems, options)
  gan_arr_tf_stuff(gan_arr, nitems, options)


def main():
  if "--hyper" in sys.argv:
    hyper_search()
  else:
    cust_opts = default_options()
    options = handle_args(sys.argv[1:], cust_opts)
    if options['gpu']:
      print("Using GPU")
      run_shopping_gan(options)
    else:
      print("Using CPU")
      with tf.device('/cpu:0'):
        run_shopping_gan(options)


if __name__ == '__main__':
  main()
