#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
Automatic Summarization: Generating News Headline Seq2Seq Model implementation
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import os
import random
import sys
import time

import numpy as np
from six.moves import xrange
import tensorflow as tf

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # parent folder
sys.path.append(parent_dir)

#from textsum import data_utils # absolute import
#from textsum import seq2seq_model # absolute import

import data_utils
import seq2seq_model

file_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(file_path, "news")
train_dir = os.path.join(file_path, "ckpt")

# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
# article length padded to 120 and summary padded to 30
buckets = [(120, 30), (200, 35), (300, 40), (400, 40), (500, 40)]

class LargeConfig(object):
    learning_rate = 1.0
    init_scale = 0.04
    learning_rate_decay_factor = 0.99
    max_gradient_norm = 5.0
    num_samples = 4096 # Sampled Softmax
    batch_size = 64
    size = 256 # Number of Node of each layer
    num_layers = 4
    # vocab_size = 50000
    # 现在的单词量
    vocab_size = 609788
    num_epoch = 200
    num_per_epoch = 300000

# class MediumConfig(object):
#     # learning_rate = 0.5
#     learning_rate = 0.005
#     init_scale = 0.04
#     learning_rate_decay_factor = 0.99
#     max_gradient_norm = 5.0
#     num_samples = 48 # Sampled Softmax
#     batch_size = 32
#     size = 64 # Number of Node of each layer
#     num_layers = 2
#     #vocab_size = 50
#     # 现在的单词量
#     vocab_size = 609788
#     num_epoch = 200
#     num_per_epoch = 32000

class MediumConfig(object):
    # learning_rate = 0.5
    learning_rate = 0.05
    init_scale = 0.04
    learning_rate_decay_factor = 0.99
    max_gradient_norm = 5.0
    num_samples = 2048 # Sampled Softmax
    batch_size = 64
    size = 64 # Number of Node of each layer
    num_layers = 2
    # vocab_size = 10000
    vocab_size = 609788
    num_epoch = 8
    num_per_epoch = 360000
    # num_per_epoch = 300000

# config = LargeConfig() # new Large Config, set to tf.app.flags
config = MediumConfig()

tf.app.flags.DEFINE_float("learning_rate", config.learning_rate, "Learning rate.")
tf.app.flags.DEFINE_float("learning_rate_decay_factor", config.learning_rate_decay_factor, "Learning rate decays by this much.")
tf.app.flags.DEFINE_float("max_gradient_norm", config.max_gradient_norm, "Clip gradients to this norm.")
tf.app.flags.DEFINE_integer("num_samples", config.num_samples, "Number of Samples for Sampled softmax")
tf.app.flags.DEFINE_integer("batch_size", config.batch_size, "Batch size to use during training.")
# 现在新增加几种参数
tf.app.flags.DEFINE_integer("num_epoch",config.num_epoch,"the epoch of the whole training")
tf.app.flags.DEFINE_integer("num_per_epoch",config.num_per_epoch,"the number of the epoch")

tf.app.flags.DEFINE_integer("size", config.size, "Size of each model layer.")
tf.app.flags.DEFINE_integer("num_layers", config.num_layers, "Number of layers in the model.")
tf.app.flags.DEFINE_integer("vocab_size", config.vocab_size, "vocabulary size.")

tf.app.flags.DEFINE_string("data_dir", data_path, "Data directory")
tf.app.flags.DEFINE_string("train_dir", train_dir, "Training directory.")
tf.app.flags.DEFINE_integer("max_train_data_size", 0, "Limit on the size of training data (0: no limit).")
tf.app.flags.DEFINE_integer("steps_per_checkpoint", 1000, "How many training steps to do per checkpoint.")
tf.app.flags.DEFINE_boolean("decode", False, "Set to True for interactive decoding.") # true for prediction
tf.app.flags.DEFINE_boolean("use_fp16", False, "Train using fp16 instead of fp32.")
tf.app.flags.DEFINE_string("gpu",'7',"the gpu number")

# define namespace for this model only
tf.app.flags.DEFINE_string("headline_scope_name", "headline_var_scope", "Variable scope of Headline textsum model")

FLAGS = tf.app.flags.FLAGS
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = tf.app.flags.FLAGS.gpu

def read_data(source_path, target_path, max_size=None):
  """Read data from source and target files and put into buckets.
  
  Args:
    source_path: path to the files with token-ids for the source language.
    target_path: path to the file with token-ids for the target language;
      it must be aligned with the source file: n-th line contains the desired
      output for n-th line from the source_path.
    max_size: maximum number of lines to read, all other will be ignored;
      if 0 or None, data files will be read completely (no limit).

  Returns:
    data_set: a list of length len(buckets); data_set[n] contains a list of
      (source, target) pairs read from the provided data files that fit
      into the n-th bucket, i.e., such that len(source) < buckets[n][0] and
      len(target) < buckets[n][1]; source and target are lists of token-ids.
  """
  data_set = [[] for _ in buckets]
  with tf.gfile.GFile(source_path, mode="r") as source_file:
    with tf.gfile.GFile(target_path, mode="r") as target_file:
      source, target = source_file.readline(), target_file.readline()
      counter = 0
      while source and target and (not max_size or counter < max_size):
        counter += 1
        if counter % 10000 == 0:
          print("  reading data line %d" % counter)
          sys.stdout.flush()
        source_ids = [int(x) for x in source.split()]
        target_ids = [int(x) for x in target.split()]
        target_ids.append(data_utils.EOS_ID)
        for bucket_id, (source_size, target_size) in enumerate(buckets):
          if len(source_ids) < source_size and len(target_ids) < target_size:
            data_set[bucket_id].append([source_ids, target_ids])
            break
        source, target = source_file.readline(), target_file.readline()
  return data_set

def create_model(session, forward_only):
  """Create headline model and initialize or load parameters in session."""
  # dtype = tf.float16 if FLAGS.use_fp16 else tf.float32
  # dtype = tf.float32
  initializer = tf.random_uniform_initializer(-config.init_scale, config.init_scale)
  # Adding unique variable scope to model
  with tf.variable_scope(FLAGS.headline_scope_name, reuse=None, initializer=initializer):
    model = seq2seq_model.Seq2SeqModel(
        FLAGS.vocab_size,
        FLAGS.vocab_size,
        buckets,
        FLAGS.size,
        FLAGS.num_layers,
        FLAGS.max_gradient_norm,
        FLAGS.batch_size,
        FLAGS.learning_rate,
        FLAGS.learning_rate_decay_factor,
        use_lstm = True, # LSTM instend of GRU
        num_samples = FLAGS.num_samples,
        forward_only=forward_only)

  ckpt = tf.train.get_checkpoint_state(FLAGS.train_dir)
  # print("the ckpt is {}".format(ckpt))
  if ckpt:
    model_checkpoint_path = ckpt.model_checkpoint_path
    print("Reading model parameters from %s" % model_checkpoint_path)
    saver = tf.train.Saver()
    saver.restore(session, tf.train.latest_checkpoint(FLAGS.train_dir))
    # saver.restore(session, FLAGS.train_dir+"/headline_large.ckpt-161161")
  else:
    print("Created model with fresh parameters.")
    session.run(tf.global_variables_initializer())
  print("finished the create the model")
  return model

def train():
  # Prepare Headline data.
  print("Preparing Headline data in %s" % FLAGS.data_dir)
  src_train, dest_train, src_dev, dest_dev, _, _ = data_utils.prepare_headline_data(FLAGS.data_dir, FLAGS.vocab_size)

  # device config for CPU usage
  # config = tf.ConfigProto(device_count={"CPU": 4}, # limit to 4 CPU usage
  #                  inter_op_parallelism_threads=1,
  #                  intra_op_parallelism_threads=2) # n threads parallel for ops

  config = tf.ConfigProto()
  config.gpu_options.allow_growth = True
  with tf.Session(config=config) as sess:
    # Create model.
    print("Creating %d layers of %d units." % (FLAGS.num_layers, FLAGS.size))
    model = create_model(sess, False)

    # Read data into buckets and compute their sizes.
    print ("Reading development and training data (limit: %d)."
           % FLAGS.max_train_data_size)
    dev_set = read_data(src_dev, dest_dev)
    train_set = read_data(src_train, dest_train, FLAGS.max_train_data_size)
    train_bucket_sizes = [len(train_set[b]) for b in xrange(len(buckets))]
    train_total_size = float(sum(train_bucket_sizes))

    # A bucket scale is a list of increasing numbers from 0 to 1 that we'll use
    # to select a bucket. Length of [scale[i], scale[i+1]] is proportional to
    # the size if i-th training bucket, as used later.
    trainbuckets_scale = [sum(train_bucket_sizes[:i + 1]) / train_total_size
                           for i in xrange(len(train_bucket_sizes))]

    # This is the training loop.
    # 显示时间用
    metrics = '  '.join(['\r{:.1f}%', '{}/{}', 'loss={:.3f}', 'gradients={:.3f}', '{}/{}'])
    bars_max = 20

    for current_step in range(FLAGS.num_epoch):
       print("\n")
       print('Epoch {}:'.format(current_step))
       epoch_trained = 0
       batch_loss = []
       batch_gradients = []
       time_start = time.time()
       # index_sum = 0
       while True:
          # Choose a bucket according to data distribution. We pick a random number
          # in [0, 1] and use the corresponding interval in trainbuckets_scale.
          random_number_01 = np.random.random_sample()
          bucket_id = min([i for i in xrange(len(trainbuckets_scale))
                           if trainbuckets_scale[i] > random_number_01])

          # Get a batch and make a step.
          encoder_inputs, decoder_inputs, target_weights = model.get_batch(
              train_set, bucket_id)

          step_gradients, step_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,
                                       target_weights, bucket_id, False)
          epoch_trained += FLAGS.batch_size
          batch_loss.append(step_loss)
          batch_gradients.append(step_gradients)
          time_now = time.time()
          time_spend = time_now - time_start
          time_estimate = time_spend / (epoch_trained / FLAGS.num_per_epoch)
          percent = min(100, epoch_trained / FLAGS.num_per_epoch) * 100
          # bars = math.floor(percent / 100 * bars_max)
          sys.stdout.write(metrics.format(
              percent,
              epoch_trained, FLAGS.num_per_epoch,
              # 对batch loss 取平均值
              np.mean(batch_loss),
              np.mean(batch_gradients),
              data_utils.time(time_spend), data_utils.time(time_estimate)
          ))
          print("\n")
          sys.stdout.flush()
          # index_sum += 1
          # if index_sum > 4:
          #     sys.exit()

          if FLAGS.num_per_epoch < epoch_trained:
              break

      # Once in a while, we save checkpoint, print statistics, and run evals.
       if current_step % FLAGS.steps_per_checkpoint == 0:

        # Save checkpoint and zero timer and loss.
        checkpoint_path = os.path.join(FLAGS.train_dir, "headline_large.ckpt")
        model.saver.save(sess, checkpoint_path, global_step=model.global_step)

def main(_):
  train()

if __name__ == "__main__":
  tf.app.run()
