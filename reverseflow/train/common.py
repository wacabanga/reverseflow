from arrows import (Arrow, CompositeArrow, compose_comb_modular, compose_comb)
from arrows.port_attributes import is_param_port, is_error_port
from arrows.std_arrows import *
from arrows.config import floatX
from reverseflow.to_arrow import graph_to_arrow
from reverseflow.to_graph import arrow_to_graph, gen_input_tensors
from typing import List, Generator, Callable
import tensorflow as tf
from tensorflow import Graph, Tensor, Session
import os

def accumulate_losses(tensors: List[Tensor]) -> Tensor:
    """
    Mean of list of tensors of arbitrary size
    Args:
        tensors: list of tensors

    Returns:
        mean tensor
    """
    with tf.name_scope('loss'):
        return tf.add_n([tf.reduce_mean(t) for t in tensors]) / len(tensors)


def load_train_save(sess, options, sfx, save_dir):
    options_path = os.path.join(save_dir, "options")
    save_dict_csv(options_path, options)
    saver = tf.train.Saver()

    if options['load_params'] is True:
        saver.restore(sess, options['params_file'])
        # adt.load_params(options['params_file'])

    # if options['save_params'] is True:
    #     path = os.path.join(save_dir, "final" + sfx)
    #     # adt.save_params(path)

    if options['train'] is True:
        train(adt, pbt, sess, num_epochs=options['num_epochs'],
              sfx=sfx, save_dir=save_dir, save_every=options['save_every'],
              compress=options['compress'], saver=saver)

    return sess


def gen_fetch(sess: Session,
              debug=False,
              **kwargs):
    init = tf.initialize_all_variables()
    sess.run(init)

    fetch = {}
    if debug:
        fetch['check'] = tf.add_check_numerics_ops()

    return fetch


def gen_update_step(loss: Tensor) -> Tensor:
    with tf.name_scope('optimization'):
        # optimizer = tf.train.MomentumOptimizer(0.001,
        #                                        momentum=0.1)
        optimizer = tf.train.AdamOptimizer(0.001)
        update_step = optimizer.minimize(loss)
        return update_step


def train_loop(sess: Session,
               loss_updates: Sequence[Tensor],
               fetch,
               generators: Sequence[Generator],
               test_generators,
               loss_ratios: Sequence[int]=None,
               test_every=100,
               num_iterations=100000,
               callbacks=[],
               **kwargs):
    """Perform training
    Args:
        sess: Tensorflow session
        loss_updates: tensor to minimize
        input_tensors:
        output_tensors:
        input_data:
        num_iterations: number of iterations to run
        summary_gap:
        save_every: save data every save_every iterations
        test_every: evaluate test data set test_every iterations
        num_iterations: number of iterations
        output_callback: a function to be called with result from fetch
        sfx: String suffix to append to log data
        compress: Using numpy compression for paramter saving
        save_dir: Directory for saving logs
        saver: Tensorflow saver for saving
    """
    # Default 1 for loss_ratios and normalize
    loss_ratios = [1 for i in range(len(loss_updates))] if loss_ratios is None else loss_ratios
    loss_ratios = loss_ratios / np.sum(loss_ratios)

    # Prepare dict to be passed to callbacks
    callback_dict = {}
    callback_dict.update(kwargs)
    callback_dict.update({'sess': sess})

    # Main loop
    for i in range(num_iterations):
        # Generate input
        curr_fetch = {}
        curr_fetch.update(fetch)
        curr_fetch["update_loss"] = np.random.choice(loss_updates, p=loss_ratios)
        feed_dict = {}
        for gen in generators:
            sub_feed_dict = next(gen)
            feed_dict.update(sub_feed_dict)
        # Optimizeation Step
        fetch_res = sess.run(curr_fetch, feed_dict=feed_dict)
        for cb in callbacks:
            cb(fetch_res, feed_dict, i, **callback_dict)
        print("Iteration: ", i, " Loss: ", fetch_res['loss'])
        if "to_print" in fetch_res:
            print(fetch_res["to_print"])

        # Evaluate on test data every test_every iterations
        if i % test_every == 0:
            test_feed_dict = {}
            for gen in test_generators:
                sub_feed_dict = next(gen)
                test_feed_dict.update(sub_feed_dict)
            test_feed_dict = {k: v for k, v in test_feed_dict.items() if k != "update_step"}
            test_fetch_res = sess.run(fetch, feed_dict=test_feed_dict)
            print("Test Loss", test_fetch_res['loss'])
