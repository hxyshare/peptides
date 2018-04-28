# coding: utf-8
from __future__ import print_function
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.layers import LSTM,TimeDistributed,SimpleRNN
from keras.utils.data_utils import get_file
import numpy as np
from keras.layers import Masking, Embedding
from time import sleep
import random
import sys
import pickle as pkl

f3 = open('data_no_sw.pkl', 'rb')
loaded_data = pkl.load(f3)
data, label = \
    tuple(loaded_data[k] for k in
          ['data', 'label'])

    
num_class = 21
print ('vetorization completed')

x =  np.array(data)
y =  np.array(label)
print('Build model...')
model = Sequential()
#model.add(LSTM(512, return_sequences=True, input_shape=(maxlen, len(chars))))  # original one
model.add(Masking(mask_value=0,input_shape=(600,399)),name='masking')
model.add(LSTM(512, dropout=0.2, recurrent_dropout=0.2,input_dim=399,return_sequences=True)) #minesh witout specifying the input_length
model.add(LSTM(512, return_sequences=True)) #- original
model.add(Dropout(0.2))
model.add(TimeDistributed(Dense(num_class)))
model.add(Activation('softmax'))

model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

print ('model is made')

# train the model, output generated text after each iteration


def generator(data, lookback, delay, min_index, max_index,
              shuffle=False, batch_size=128, step=6):
    if max_index is None:
        max_index = len(data) - delay - 1
    i = min_index + lookback
    while 1:
        if shuffle:
            rows = np.random.randint(
                min_index + lookback, max_index, size=batch_size)
        else:
            if i + batch_size >= max_index:
                i = min_index + lookback
            rows = np.arange(i, min(i + batch_size, max_index))
            i += len(rows)

        samples = np.zeros((len(rows),
                           lookback // step,
                           data.shape[-1]))
        targets = np.zeros((len(rows),))
        for j, row in enumerate(rows):
            indices = range(rows[j] - lookback, rows[j], step)
            samples[j] = data[indices]
            targets[j] = data[rows[j] + delay][1]
            print('-----------',targets[j])
        yield samples, targets
        
train_gen = generator(x ,
                      lookback=lookback,
                      delay=delay,
                      min_index=0,
                      max_index=200000,
                      shuffle=True,
                      step=step, 
                      batch_size=batch_size)
print (model.summary())


for iteration in range(1, 6):
    print()
    print('-' * 50)
    print('Iteration', iteration)
    history=model.fit(x, y, batch_size=100, epochs=10,verbose=1)
    sleep(0.1) # https://github.com/fchollet/keras/issues/2110
    print ('loss is')
    print (history.history['loss'][0])
    print (history)
    print()    

    


# #### testing
# now you use the trained model to generat text.
# the  output shown in this notebook is for a model which is trained only for 1 iteration





