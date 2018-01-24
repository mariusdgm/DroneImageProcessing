# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys

import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
import re
import time
import threading
from queue import Queue

import drawResults



def load_graph(model_file):
    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    return graph

def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
				input_mean=0, input_std=255):
    input_name = "file_reader"
    output_name = "normalized"
    file_reader = tf.read_file(file_name, input_name)
    if file_name.endswith(".png"):
        image_reader = tf.image.decode_png(file_reader, channels = 3,
                                            name='png_reader')
    elif file_name.endswith(".gif"):
        image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                              name='gif_reader'))
    elif file_name.endswith(".bmp"):
        image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
    else:
        image_reader = tf.image.decode_jpeg(file_reader, channels = 3,
                                            name='jpeg_reader')
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0);
    resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.Session()
    result = sess.run(normalized)

    return result

def load_labels(label_file):
    label = []
    proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
    for l in proto_as_ascii_lines:
        label.append(l.rstrip())
    return label

def main(folderPath):
    folder_name = folderPath
    file_name = ''
    model_file = "tf_files/retrained_graph.pb"
    label_file = "tf_files/retrained_labels.txt"
    input_height = 299
    input_width = 299
    input_mean = 0
    input_std = 255
    input_layer = "Mul"
    output_layer = "final_result"

    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", help="folder to be processed")
    parser.add_argument("--image", help="image to be processed")
    parser.add_argument("--graph", help="graph/model to be executed")
    parser.add_argument("--labels", help="name of file containing labels")
    parser.add_argument("--input_height", type=int, help="input height")
    parser.add_argument("--input_width", type=int, help="input width")
    parser.add_argument("--input_mean", type=int, help="input mean")
    parser.add_argument("--input_std", type=int, help="input std")
    parser.add_argument("--input_layer", help="name of input layer")
    parser.add_argument("--output_layer", help="name of output layer")
    args = parser.parse_args()

    if args.graph:
        model_file = args.graph
    if args.folder:
        folder_name = args.folder
    if args.image:
        file_name = args.image
    if args.labels:
        label_file = args.labels
    if args.input_height:
        input_height = args.input_height
    if args.input_width:
        input_width = args.input_width
    if args.input_mean:
        input_mean = args.input_mean
    if args.input_std:
        input_std = args.input_std
    if args.input_layer:
        input_layer = args.input_layer
    if args.output_layer:
        output_layer = args.output_layer

    write_lock = threading.Lock()

    readQue = Queue()
    labelQue = Queue()

    tensorImage = []

    def readImageJob(worker):
        file_name = os.path.join(folder_name, worker)
        nameAndRead = (worker, read_tensor_from_image_file(file_name,
                                    input_height=input_height,
                                    input_width=input_width,
                                    input_mean=input_mean,
                                    input_std=input_std))
        with write_lock:
            tensorImage.append(nameAndRead)



    def threaderRead():
    	while True:
    		worker = readQue.get()
    		readImageJob(worker)
    		readQue.task_done()

    def verticalMovementCheck(x):
        return{
            '0': 0,
            '1': 1,
            '2': -1
    }.get(x, 0)     # 0 is default if x not found

    def horizontalMovementCheck(x):
        return{
            '0': 0,
            '1': -1,
            '2': 1
    }.get(x, 0)

    resultFile = open(os.path.join(folder_name,"results.txt"), "w+")

    imageList = []
    for f in os.listdir(folder_name):
        #print(f)
        if f == "movementLog.txt":
            moveList = []
            try:
                moveFile = open(os.path.join(folder_name, f), "r")
                line = moveFile.readline()
                while line:
                    moveList.append((line[0],line[1]))
                    line = moveFile.readline()

            finally:
                moveFile.close()


        if f.endswith(".jpeg") or f.endswith(".jpg"):
            imageList.append(f)

    positionList = []
    currentX = 0
    currentY = 0
    for row in moveList:
        newPos = (currentY + verticalMovementCheck(row[0]), currentX + horizontalMovementCheck(row[1]))
        positionList.append(newPos)
        currentY += verticalMovementCheck(row[0])
        currentX += horizontalMovementCheck(row[1])

    imageList.sort(key=lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split('(\d+)', s)])
    #print(imageList)
    startTime = time.time()

    graph = load_graph(model_file)

    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name);
    output_operation = graph.get_operation_by_name(output_name);

    startTime = time.time()

    for x in range(9):
    	t = threading.Thread(target = threaderRead)
    	t.daemon = True
    	t.start()

    for worker in imageList:
        readQue.put(worker)

    readQue.join()

    tensorImage.sort(key=lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split('(\d+)', s[0])])

    cnt = 0
    with tf.Session(graph=graph) as sess:
        for f in imageList:
            print('Progress: ', str(round(cnt*100/len(imageList))) + '%')

            results = sess.run(output_operation.outputs[0],
                            {input_operation.outputs[0]: tensorImage[cnt][1]})
            results = np.squeeze(results)

            top_k = results.argsort()[-5:][::-1]
            labels = load_labels(label_file)
            for i in top_k:
                resultFile.write(f + ", ")
                resultFile.write(labels[i] + ", ")

                verticalPos, horizontalPos = positionList[cnt]
                resultFile.write(str(verticalPos) + ", ")
                resultFile.write(str(horizontalPos))
                resultFile.write("\n")
                cnt += 1
                break #exit after highest score


    print('Progress: ' + '100' + '%')
    print('Classification process took: ', round(time.time()-startTime), ' seconds for ', cnt, 'images')
    resultFile.close()

    drawResults.main(folder_name)
    quit()

if __name__ == "__main__":
    main(sys.argv)
