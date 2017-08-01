import tflearn
import numpy as np
from tflearn.layers.conv import conv_2d, max_pool_2d, upsample_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from tflearn.layers.normalization import local_response_normalization
from tflearn.layers.recurrent import gru
import cv2

from screen_consts import WIDTH, HEIGHT
CHANNELS = 3
MODEL_NUMBER = 2
MODEL_NAME = 'autoencoder-'+str(MODEL_NUMBER)

input_img = input_data(shape=(HEIGHT, WIDTH, CHANNELS), name='input');print(input_img.shape)
INPUT = input_img
x = conv_2d(input_img, 16, (3, 3), activation='relu', padding='same');print(x.shape)
x = max_pool_2d(x, (2, 2), padding='same');print(x.shape)
x = conv_2d(x, 8, (3, 3), activation='relu', padding='same');print(x.shape)
x = max_pool_2d(x, (2, 2), padding='same');print(x.shape)
x = conv_2d(x, 8, (3, 3), activation='relu', padding='same');print(x.shape)
encoded = max_pool_2d(x, (2, 2), padding='same');print(encoded.shape)  # at this point the representation is (4, 4, 8) i.e. 128-dimensional

HIDDEN_STATE = encoded
print("middle")

x = conv_2d(encoded, 8, (3, 3), activation='relu', padding='same', name='input2');print(x.shape)
x = upsample_2d(x, (2, 2));print(x.shape)
x = conv_2d(x, 8, (3, 3), activation='relu', padding='same');print(x.shape)
x = upsample_2d(x, (2, 2));print(x.shape)
x = conv_2d(x, 16, (3, 3), activation='relu', padding='same');print(x.shape)
x = upsample_2d(x, (2, 2));print(x.shape)
decoded = conv_2d(x, CHANNELS, (3, 3), activation='sigmoid', padding='same');print(decoded.shape)
OUTPUT = decoded
autoencoder = regression(decoded, optimizer='momentum', loss='mean_square',
						 learning_rate=0.005, name='targets')
model = tflearn.DNN(autoencoder, checkpoint_path=MODEL_NAME,
					max_checkpoints=1, tensorboard_verbose=0, tensorboard_dir='log')

model.load("models/" + MODEL_NAME)

def encode (X):
    if len (X.shape) < 2:
        X = X.reshape (1, -1)

    tflearn.is_training (False, model.session)
    res = model.session.run (HIDDEN_STATE, feed_dict={INPUT.name:X})
    return res

def decode (X):
    if len (X.shape) < 2:
        X = X.reshape (1, -1)

    #just to pass something to place_holder
    zeros = np.zeros ((1,HEIGHT,WIDTH,CHANNELS))

    tflearn.is_training (False, model.session)
    res = model.session.run (OUTPUT, feed_dict={INPUT.name:zeros, HIDDEN_STATE.name:X})
    return res

def autoencode(img):
	img = img / 255.
	img = img.reshape(-1,HEIGHT, WIDTH, CHANNELS)
	#a = (model.predict(img))
	a = encode(img).reshape(52,40)
	return a#[0]

def autodecode(img):
	img = img / 255.
	img = img.reshape(-1,HEIGHT, WIDTH, CHANNELS)
	a = (model.predict(img))
	return a[0]