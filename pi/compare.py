## Compare the different approaches
import pi
from pi import invert
from pi import analysis
import numpy as np
from pi.optim import min_param_error, min_fx_y, gen_y, gen_loss_model, nnet
from pi.optim import enhanced_pi, gen_loss_evaluator
from pi.util import *
import pi.templates.res_net
from pi.invert import invert

import tensorflow as tf
from tensorflow import float32


def nnet_enhanced_pi(g, gen_graph, inv_inp_gen, param_types, param_gen,
                     check_loss, batch_size, sess, max_time, logdir):
    ## Inverse Graph
    with g.name_scope('nnet_enhanced_pi'):
        in_out_ph = gen_graph(g, batch_size, True)
        shrunk_params = {k: tf.placeholder(v['dtype'], shape=v['shape'])
                         for k, v in param_types.items()}
        inv_results = invert(in_out_ph['outputs'], shrunk_params=shrunk_params)
        inv_g, inv_inputs, inv_outputs_map = inv_results

        inv_outputs_map_canonical = {k: inv_outputs_map[v.name]
                                     for k, v in in_out_ph['inputs'].items()}

        writer = tf.train.SummaryWriter(logdir, inv_g)

        # Train
        result = enhanced_pi(inv_g, inv_inputs, inv_inp_gen,
                             shrunk_params, param_gen,
                             inv_outputs_map_canonical,
                             check_loss, sess, max_time=max_time)
        return result


def compare(g, gen_graph, fwd_f, param_types, param_gen, options):
    # Preferences
    batch_size = options['batch_size']
    max_time = options['max_time']
    logdir = options['logdir']

    domain_loss_hists = {}
    total_times = {}
    std_loss_hists = {}

    ## Vreate evaluator
    sess = tf.Session(graph=g)
    in_out_var = gen_graph(g, batch_size, False)
    loss_op, absdiffs, mean_loss_per_batch_op, mean_loss_per_batch, target_outputs = gen_loss_model(in_out_var, sess)
    check_loss = gen_loss_evaluator(loss_op, mean_loss_per_batch, target_outputs, in_out_var["inputs"], sess)

    inv_inp_gen = infinite_input(gen_graph, batch_size)

    if options['nnet_enhanced_pi']:
        result = nnet_enhanced_pi(g, gen_graph, inv_inp_gen, param_types, param_gen,
                                  check_loss, batch_size, sess, max_time, logdir)
        domain_loss_hist, std_loss_hist, total_time = result
        domain_loss_hists["nnet_enhanced_pi"] = domain_loss_hist
        total_times["nnet_enhanced_pi"] = total_time
        std_loss_hists["nnet_enhanced_pi"] = std_loss_hist
