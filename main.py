import os.path
import tensorflow as tf
import helper
import warnings
import time
from distutils.version import LooseVersion
import project_tests as tests




def load_vgg(sess, vgg_path):
    """
    Load Pretrained VGG Model into TensorFlow.
    :param sess: TensorFlow Session
    :param vgg_path: Path to vgg folder, containing "variables/" and "saved_model.pb"
    :return: Tuple of Tensors from VGG model (image_input, keep_prob, layer3_out, layer4_out, layer7_out)
    """
    vgg_tag = 'vgg16'
    vgg_input_tensor_name = 'image_input:0'
    vgg_keep_prob_tensor_name = 'keep_prob:0'
    vgg_layer3_out_tensor_name = 'layer3_out:0'
    vgg_layer4_out_tensor_name = 'layer4_out:0'
    vgg_layer7_out_tensor_name = 'layer7_out:0'

    #   Use tf.saved_model.loader.load to load the model and weights
    tf.saved_model.loader.load(sess, [vgg_tag], vgg_path)

    image_input = sess.graph.get_tensor_by_name(vgg_input_tensor_name)
    vgg_keep_prob = sess.graph.get_tensor_by_name(vgg_keep_prob_tensor_name)
    vgg_layer3 = sess.graph.get_tensor_by_name(vgg_layer3_out_tensor_name)
    vgg_layer4 = sess.graph.get_tensor_by_name(vgg_layer4_out_tensor_name)
    vgg_layer7 = sess.graph.get_tensor_by_name(vgg_layer7_out_tensor_name)

    return image_input, vgg_keep_prob, vgg_layer3, vgg_layer4, vgg_layer7


def layers(vgg_layer3_out, vgg_layer4_out, vgg_layer7_out, num_classes):
    """
    Create the layers for a fully convolutional network.  Build skip-layers using the vgg layers.
    :param vgg_layer7_out: TF Tensor for VGG Layer 3 output
    :param vgg_layer4_out: TF Tensor for VGG Layer 4 output
    :param vgg_layer3_out: TF Tensor for VGG Layer 7 output
    :param num_classes: Number of classes to classify
    :return: The Tensor for the last layer of output
    """

    vgg_layer7_skip = tf.layers.conv2d(vgg_layer7_out, num_classes, 1, strides=(1,1), padding='same',
                                        kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3),
                                        kernel_initializer=tf.truncated_normal_initializer(stddev=0.01))
    decoder_1 = tf.layers.conv2d_transpose(vgg_layer7_skip, num_classes, 4, strides=(2, 2), padding='same',
                                        kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3),
                                        kernel_initializer=tf.truncated_normal_initializer(stddev=0.01))

    vgg_layer4_skip = tf.layers.conv2d(vgg_layer4_out, num_classes, 1, strides=(1,1), padding='same',
                                        kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3),
                                        kernel_initializer=tf.truncated_normal_initializer(stddev=0.01))
    decoder_2 = tf.add(decoder_1, vgg_layer4_skip)

    decoder_3 = tf.layers.conv2d_transpose(decoder_2, num_classes, 4, strides=(2, 2),padding='same',
                                            kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3),
                                            kernel_initializer=tf.truncated_normal_initializer(stddev=0.01))

    vgg_layer3_skip = tf.layers.conv2d(vgg_layer3_out, num_classes, 1, strides=(1,1), padding='same',
                                        kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3),
                                        kernel_initializer=tf.truncated_normal_initializer(stddev=0.01))
    decoder_4 = tf.add(decoder_3, vgg_layer3_skip)

    decoder_5 = tf.layers.conv2d_transpose(decoder_4, num_classes, 16, strides=(8, 8),padding='same',
                                            kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3),
                                            kernel_initializer=tf.truncated_normal_initializer(stddev=0.01))

    return decoder_5


def optimize(nn_last_layer, correct_label, learning_rate, num_classes):
    """
    Build the TensorFLow loss and optimizer operations.
    :param nn_last_layer: TF Tensor of the last layer in the neural network
    :param correct_label: TF Placeholder for the correct label image
    :param learning_rate: TF Placeholder for the learning rate
    :param num_classes: Number of classes to classify
    :return: Tuple of (logits, train_op, cross_entropy_loss)
    """

    logits = tf.reshape(nn_last_layer, (-1, num_classes))
    labels = tf.reshape(correct_label, (-1, num_classes))

    cross_entropy_loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=labels))
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    training_op = optimizer.minimize(cross_entropy_loss)

    return logits, training_op, cross_entropy_loss


def train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image,
             correct_label, keep_prob, learning_rate):
    """
    Train neural network and print out the loss during training.
    :param sess: TF Session
    :param epochs: Number of epochs
    :param batch_size: Batch size
    :param get_batches_fn: Function to get batches of training data.  Call using get_batches_fn(batch_size)
    :param train_op: TF Operation to train the neural network
    :param cross_entropy_loss: TF Tensor for the amount of loss
    :param input_image: TF Placeholder for input images
    :param correct_label: TF Placeholder for label images
    :param keep_prob: TF Placeholder for dropout keep probability
    :param learning_rate: TF Placeholder for learning rate
    """
    sess.run(tf.global_variables_initializer())


    for epoch in range(epochs):
        start_time = time.time()
        training_loss = 0.0
        training_samples = 0.0

        for batch_x, batch_y in get_batches_fn(batch_size):
            _, loss = sess.run([train_op, cross_entropy_loss],
                feed_dict = {
                    input_image: batch_x,
                    correct_label: batch_y,
                    keep_prob: 0.75,
                    learning_rate: 0.0001
                })

            training_loss += loss
            training_samples += len(batch_x)

        print("EPOCH {} ...".format(epoch))
        print("Loss = {:.5f}".format(loss/training_samples))
        elapsed_time = time.time()-start_time
        print("Elapsed Time: %.2f sec" % elapsed_time)
        print()


DATA_DIR = './data'

def run():
    num_classes = 2
    epochs = 25
    batch_size = 2
    image_shape = (160, 576)
    runs_dir = './runs'

    # Download pretrained vgg model
    helper.maybe_download_pretrained_vgg(DATA_DIR)

    # OPTIONAL: Train and Inference on the cityscapes dataset instead of the Kitti dataset.
    # You'll need a GPU with at least 10 teraFLOPS to train on.
    #  https://www.cityscapes-dataset.com/

    with tf.Session() as sess:
        # Path to vgg model
        vgg_path = os.path.join(DATA_DIR, 'vgg')

        # Create function to get batches
        get_batches_fn = helper.gen_batch_function(os.path.join(DATA_DIR, 'data_road/training'), image_shape)

        # OPTIONAL: Augment Images for better results
        #  https://datascience.stackexchange.com/questions/5224/how-to-prepare-augment-images-for-neural-network

        #Load VGG layers
        input_image, vgg_keep_prob, vgg_layer3, vgg_layer4, vgg_layer7 = load_vgg(sess, vgg_path)

        #Add Conv layers onto VGG layers
        model_output = layers(vgg_layer3, vgg_layer4, vgg_layer7, num_classes)

        #Initialize training and loss operations
        correct_label = tf.placeholder(tf.float32, (None, image_shape[0], image_shape[1], num_classes));
        learning_rate = tf.placeholder(tf.float32)
        logits, training_op, cross_entropy_loss = optimize(model_output, correct_label, learning_rate, num_classes)

        # Train NN
        train_nn(sess, epochs, batch_size, get_batches_fn, training_op, cross_entropy_loss, input_image,
                     correct_label, vgg_keep_prob, learning_rate)

        # Save inference data using helper.save_inference_samples
        helper.save_inference_samples(runs_dir, DATA_DIR, sess, image_shape, logits, vgg_keep_prob, input_image)

        # OPTIONAL: Apply the trained model to a video

def run_tests():
    # Check TensorFlow Version
    assert LooseVersion(tf.__version__) >= LooseVersion('1.0'), 'Please use TensorFlow version 1.0 or newer.  You are using {}'.format(tf.__version__)
    print('TensorFlow Version: {}'.format(tf.__version__))

    # Check for a GPU
    if not tf.test.gpu_device_name():
        warnings.warn('No GPU found. Please use a GPU to train your neural network.')
    else:
        print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))

    tests.test_load_vgg(load_vgg, tf)
    tests.test_layers(layers)
    tests.test_optimize(optimize)
    tests.test_train_nn(train_nn)
    tests.test_for_kitti_dataset(DATA_DIR)

if __name__ == '__main__':
    run_tests()
    run()
