"""Test generalization"""
import numpy as np
import subprocess
from typing import Sequence
from arrows.util.misc import dict_prod, extract
import time

def log_partition(xs: Sequence, n_cells: int=10):
    # FIXME: Make overlapping sets and cell size double
    """Partition xs into a n_cells cells of logarithmically increasing size"""
    indices = np.round(np.logspace(0, np.log10(len(xs)-1), n_cells))
    print(indices)
    start_i = 0
    partition = []
    for end_i in indices:
        partition.append(xs[start_i: end_i])
        start_i = end_i
    return partition


def test_generalization(run_me, options=None):
    """Train parametric inverse and vanilla neural network with different
    amounts of data and see the test_error
    """
    options = {} if options is None else options
    batch_sizes = [1, 4, 40, 100]
    for batch_size in batch_sizes:
        options['batch_size'] = batch_size
        run_me(options)

def string_dict(d):
    new_d = {}
    for key, value in d.items():
        if isinstance(value, (list, tuple, np.ndarray)):
            new_val = []
            for val in value:
                str_val = str(val)
                if str_val[:9] == '<function':
                    new_val.append(str_val.split(' ')[1])
                else:
                    new_val.append(str_val)
            new_d[key] = new_val
        else:
            val_string = str(value)
            if val_string[:9] == '<function':
                val_string = val_string.split(' ')[1]
            new_d[key] = val_string
    return str(new_d)

def test_everything(run_me, options, var_option_keys, prefix='', nrepeats=1):
    """Train parametric inverse and vanilla neural network with different
    amounts of data and see the test_error
    Args:
        run_me: function to call, should execute test and save stuff
        Options: Options to be passed into run_me
        var_option_keys: Set of keys, where options['keys'] is a sequence
            and we will vary over cartesian product of all the keys

    """
    _options = {}
    _options.update(options)
    var_options = extract(var_option_keys, options)

    for i in range(nrepeats):
        var_options_prod = dict_prod(var_options)
        the_time = time.time()
        for j, prod in enumerate(var_options_prod):
            dirname = "%s_%s_%s_%s" % (prefix, str(the_time), i, j)
            _options['dirname'] = dirname
            _options.update(prod)
            if options['script']:
                command = 'sbatch -gres=gpu:1 -n1 ./runscript.sh ' + str(run_me) + ' ' + string_dict(_options)
                subprocess.call(command)
            run_me(_options)
