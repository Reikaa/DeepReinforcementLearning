#!/usr/bin/env python3
''' Generate commands for tests '''

# variables to test
# 1. architecture
#   * layers
#   * autoencoder construction (default, denoising, marginalised)
#   * finetune model (normal softmax, incremental, reinforcement)
# 2. data set (mnist, cifar-10, cifar-100)
# 3. effect (none, noise)
# make the data first

# pretrain everything

data_sets = [ (784, 10, 'mnist') ]
arches = [ '500' ]
effects = [ 'noise' ]
seeds = list(range(0, 1))
models = [
    'adapting --policy RelevantPooler -mps 10000',
]

path_config = 'PATH=/usr/local/cuda-6.5/bin:$PATH '
ld_config = 'LD_LIBRARY_PATH=/usr/local/cuda-6.5/lib64:$LD_LIBRARY_PATH '

for input_layer_size, classes, data_set in data_sets:
    for arch in arches:
        for effect in effects:
            for seed in seeds:
                for model in models:
                    base_name = '_'.join([ str(x).replace(' ', '') for x in [data_set, arch.replace(' ', '-'), effect, seed, model] ])

                    data_stream = ' '.join(['./generate_distribution.py', '-q', 'data/' + data_set + '.pkl', '1000', '1000000', effect, str(seed) ])
                    train = ' | ' + path_config + ld_config  + './train.py -b 1000 -m ' + model + ' -al ' + str(input_layer_size) + ' '  + arch + ' ' + str(classes)  + ' -o ' + base_name

                    print('if [ ! -f "output/' + base_name + '/layers/0.npz" ]; then ' + data_stream + train + ' &> logs/' + base_name + '; fi')
