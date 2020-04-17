# Link
1. github https://github.com/davidsandberg/facenet/
2. conversion blog https://medium.com/analytics-vidhya/facenet-on-mobile-cb6aebe38505

# file description

* `20180402-114759.zip` model files (.pb[contain training materials] / .ckpt provided from github link)  

## step 1. rewrite graph

```python
def rewriteGraph():
    from models import inception_resnet_v1
    traning_checkpoint = 'models/model-20180402-114759.ckpt-275'
    eval_checkpoint = 'models/facenet_inference.ckpt'

    data_input = tf.placeholder(name='input', dtype=tf.float32, shape=[None, 160, 160, 3])
    output, _ = inception_resnet_v1.inference(data_input, keep_probability=0.8, phase_train=False, bottleneck_layer_size=512)
    label_batch= tf.identity(output, name='label_batch')
    embeddings = tf.identity(output, name='embeddings')

    init = tf.global_variables_initializer()
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.15)
    with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False)) as sess:

        sess.run(init)
        saver = tf.train.Saver()
        saver.restore(sess, traning_checkpoint)
        save_path = saver.save(sess, eval_checkpoint)
        print('Model saved in file: %s' % save_path)

    print('Converting to pb ...')
 ```
 
 ## step 2. freeze graph 

<details>
  <summary>facenet/src/freeze_graph.py</summary>

  ```python
 
 """Imports a model metagraph and checkpoint file, converts the variables to constants
and exports the model as a graphdef protobuf
"""
# MIT License
# 
# Copyright (c) 2016 David Sandberg
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.framework import graph_util
import tensorflow as tf
import argparse
import os
import sys
import facenet
from six.moves import xrange  # @UnresolvedImport

from models import inception_resnet_v1


def main(args):
    with tf.Graph().as_default():
        with tf.Session() as sess:
            # Load the model metagraph and checkpoint
            print('Model directory: %s' % args.model_dir)
            meta_file, ckpt_file = facenet.get_model_filenames(os.path.expanduser(args.model_dir))

            print('Metagraph file: %s' % meta_file)
            print('Checkpoint file: %s' % ckpt_file)

            model_dir_exp = os.path.expanduser(args.model_dir)
            saver = tf.train.import_meta_graph(os.path.join(model_dir_exp, meta_file), clear_devices=True)
            tf.get_default_session().run(tf.global_variables_initializer())
            tf.get_default_session().run(tf.local_variables_initializer())
            saver.restore(tf.get_default_session(), os.path.join(model_dir_exp, ckpt_file))

            # Retrieve the protobuf graph definition and fix the batch norm nodes
            input_graph_def = sess.graph.as_graph_def()

            # Freeze the graph def
            output_graph_def = freeze_graph_def(sess, input_graph_def, 'embeddings,label_batch')

        # Serialize and dump the output graph to the filesystem
        with tf.gfile.GFile(args.output_file, 'wb') as f:
            f.write(output_graph_def.SerializeToString())
        print("%d ops in the final graph: %s" % (len(output_graph_def.node), args.output_file))

def freeze_graph_def(sess, input_graph_def, output_node_names):
    for node in input_graph_def.node:
        if node.op == 'RefSwitch':
            node.op = 'Switch'
            for index in xrange(len(node.input)):
                if 'moving_' in node.input[index]:
                    node.input[index] = node.input[index] + '/read'
        elif node.op == 'AssignSub':
            node.op = 'Sub'
            if 'use_locking' in node.attr: del node.attr['use_locking']
        elif node.op == 'AssignAdd':
            node.op = 'Add'
            if 'use_locking' in node.attr: del node.attr['use_locking']
    
    # Get the list of important nodes
    whitelist_names = []
    for node in input_graph_def.node:
        if (node.name.startswith('InceptionResnet') or node.name.startswith('embeddings') or 
                node.name.startswith('image_batch') or node.name.startswith('label_batch') or
                node.name.startswith('phase_train') or node.name.startswith('Logits')):
            whitelist_names.append(node.name)

    # Replace all the variables in the graph with constants of the same values
    output_graph_def = graph_util.convert_variables_to_constants(
        sess, input_graph_def, output_node_names.split(","),
        variable_names_whitelist=whitelist_names)
    return output_graph_def
  
def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('model_dir', type=str, 
        help='Directory containing the metagraph (.meta) file and the checkpoint (ckpt) file containing model parameters')
    parser.add_argument('output_file', type=str, 
        help='Filename for the exported graphdef protobuf (.pb)')
    return parser.parse_args(argv)

if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))

 ```
 
 </details>
 
 ## Step 3. convert to tflite (quantize)
 
 ```python
 
def convert_tflite():
    cmd = ['tflite_convert',
           '--output_file', 'models/facenet.tflite',
           '--graph_def_file', 'models/frozen_facenet.pb',
           '--input_arrays', 'input',
           '--input_shapes','1,160,160,3',
           '--output_arrays', 'embeddings',
           '--output_format', 'TFLITE',
           '--mean_values', '128',
           '--std_dev_values','128',
           '--default_ranges_min', '0',
           '--default_ranges_max', '6',
           '--inference_type', 'QUANTIZED_UINT8',
           '--inference_input_type', 'QUANTIZED_UINT8']
    print(' '.join(cmd))
    proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    try:
        outs, errs = proc.communicate()
    except:
        import traceback
        print(traceback.format_exc())
        proc.kill()
        outs, errs = proc.communicate()
    print(outs.decode())
    print(errs.decode())
```

## Step 4. Testing on tflite
```
def test():
    # Load TFLite model and allocate tensors.
    interpreter = tf.lite.Interpreter(model_path='model.tflite')
    interpreter.allocate_tensors()
    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    # Test model on random input data.
    input_shape = input_details[0]['shape']


    print('INPUTS: ')
    print(input_details)
    print('OUTPUTS: ')
    print(output_details)

    init = tf.global_variables_initializer()
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.15)
    with tf.Graph().as_default() as g:
        with tf.gfile.FastGFile('models/frozen_facenet.pb','rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, input_map=None, name='')
            sess = tf.Session(graph=g, config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
            facenet = lambda  x: sess.run('embeddings:0', feed_dict = {'input:0':(x.astype(float)-128)*0.0078125 })
            
            
    mean = []
    std = []
    _max = []
    for i in range(10):
        input_data = np.random.randint(0,255,size=input_shape,dtype=np.uint8)
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index']) * 0.02352122248888
        output_data_pb = facenet(input_data)
        diff = output_data - output_data_pb
        mean.append(np.mean(diff))
        std.append(np.std(diff))
        _max.append(np.max(diff))
    print('diff mean',np.mean(mean))
    print('diff std',np.mean(std))
    print('diff max',np.mean(_max))
    """
    facenet
    input quantize mean std: (X - 128.) /128
    output quantize mean std: (X - 0.) * 0.02319412224888
    """
```
 
