import tensorflow as tf
import numpy as np
import time
import argparse

from matplotlib.colors import rgb_to_hsv, hsv_to_rgb


def args_parser():
    parser = argparse.ArgumentParser(description='Perceptual Losses for Real-Time Style Transfer and Super-Resolution')
    parser.add_argument('model_dir')
    parser.add_argument('content_image')
    parser.add_argument('--out', default='images/result.jpg', help='Path to save transferred result', type=str)
    parser.add_argument('--keep_colors', default=False, action='store_true')
    return parser.parse_args()


def main():
    args = args_parser()

    content_image = tf.keras.preprocessing.image.img_to_array(
        tf.keras.preprocessing.image.load_img(args.content_image,
                                              target_size=(256, 256)))

    tf.reset_default_graph()
    eval_graph = tf.Graph()

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True

    with eval_graph.as_default() as g, tf.Session(config=config, graph=eval_graph) as sess:
        tf.saved_model.loader.load(sess, [tf.saved_model.tag_constants.SERVING], args.model_dir)
        inputs = g.get_tensor_by_name("inputs:0")
        outputs = g.get_tensor_by_name("outputs:0")
        c = sess.run(tf.expand_dims(content_image, axis=0))
        start = time.time()
        result = sess.run(tf.squeeze(outputs), feed_dict={inputs: c})
        end = time.time()
        print("Inference time: {time} seconds".format(time=end - start))

    if args.keep_colors:
        # retain original image color
        def use_original_color(original, result):
            result_hsv = rgb_to_hsv(result)
            orig_hsv = rgb_to_hsv(original)
            oh, os, ov = np.split(orig_hsv, axis=-1, indices_or_sections=3)
            rh, rs, rv = np.split(result_hsv, axis=-1, indices_or_sections=3)
            return hsv_to_rgb(np.concatenate([oh, os, rv], axis=-1))

        final_result = use_original_color(content_image.reshape((256, 256, 3)), result)
    else:
        final_result = result

    result_image = tf.keras.preprocessing.image.array_to_img(final_result)
    result_image.save(args.out)


main()
