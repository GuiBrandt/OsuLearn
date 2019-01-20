#!/usr/bin/env python
# coding: utf-8

# # OsuLearn
# ##### Machine Learning para jogar mapas de osu!
# 
# ^^^
# 
# Isso aí, tô sem mais nada pra fazer, bora criar uma IA que joga osu! )o)

# ## Importar umas coisas...

# In[1]:


# Machine Learning
import tensorflow as tf
import tensorflow.keras as keras

# Dados
import numpy as np
import pandas as pd

# Plotagem
import matplotlib.pyplot as plt

# Utilidades
import os
import re
import math
import glob

from importlib import reload

# Lógica do osu!
import osu.rulesets.beatmap
import osu.rulesets.replay
import osu.rulesets.hitobjects as hitobjects

import osulearn.dataset


# ## Constantes
# 
# Aqui tem uns caminhos para os arquivos que precisamos:

# In[2]:


# Pasta do osu!
OSU_FOLDER = "C:/Users/guigb/AppData/Local/osu!"


# ## Dados para treinamento...

# In[3]:


data_files = osulearn.dataset.all_files(OSU_FOLDER, verbose=True)
data_files.applymap(os.path.basename)


# In[4]:


dataset = osulearn.dataset.load(data_files, verbose=2)


# In[ ]:


print()
    
try:
    input_data = pd.read_pickle('.data/input_data.hdf5')
    
except:
    print("Processing Input Data...")
    print("_" * 80)
    print()
    input_data = osulearn.dataset.input_data(dataset, verbose=True)
    input_data.to_pickle('.data/input_data.hdf5')
    print()
    
try:
    target_data = pd.read_pickle('.data/target_data.dat')
except:    
    print("Processing Target Data...")
    print("_" * 80)
    print()
    target_data = osulearn.dataset.target_data(dataset, verbose=True)
    target_data.to_pickle('.data/target_data.dat')
    print()

X = np.reshape(input_data.values, (-1, osulearn.dataset.CHUNK_LENGTH, len(osulearn.dataset.INPUT_FEATURES)))
y = np.reshape(target_data.values, (-1, osulearn.dataset.CHUNK_LENGTH, len(osulearn.dataset.OUTPUT_FEATURES)))

X.shape, y.shape


# ## Modelo de rede neural
# 
# Agora começa a festa...

# In[ ]:


from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, CuDNNLSTM as LSTM, Input, GaussianNoise

map_input = Input(shape=X.shape[1:], name='map_info')

lstm = LSTM(64, kernel_initializer='normal', return_sequences=True)(map_input)

pos = Dense(64, kernel_initializer='normal', activation='linear')(lstm)
pos = GaussianNoise(0.2)(pos)
pos = Dense(16, kernel_initializer='normal', activation='linear')(pos)
pos = Dense(y.shape[2], kernel_initializer='normal', activation='linear', name='position')(pos)

model = Model(inputs=map_input, outputs=pos)
model.compile(optimizer='adam', loss='mae')
model.summary()

try:
    model.load_weights(".data/model.hdf5")
except Exception as e:
    print()
    print("Failed to load weights: ", e)


# In[ ]:


from random import randint
from sklearn.model_selection import train_test_split

ITERATIONS = 8
EPOCHS = 8

try:
    loss
except NameError:
    loss = []
    
for i in range(ITERATIONS):
    print("Iteration #%d" % (i + 1))
    print("_" * 80)
    print()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=randint(0, 100))
    h = model.fit(X_train, y_train, batch_size=1024, epochs=EPOCHS, verbose=1)
    loss += h.history['loss']
    print()

model.save_weights(".data/model.hdf5")


# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')

plt.plot(loss)
plt.show()


# In[ ]:


def plot_info(*compare):
    get_ipython().run_line_magic('matplotlib', 'inline')
    
    plt.ylim((-1, 1))
    for data in compare:
        plt.plot([(x, y) for x, y in data])
    plt.show()


# In[ ]:


predicted_pos = model.predict(X)

#plot_info(y, predicted_pos)
    
for i in range(50):
    print(i)
    plot_info(y[i], predicted_pos[i])


# In[ ]:


reload(osulearn)
reload(osulearn.dataset)

BEATMAPS_FOLDER = 'C:\\Program Files (x86)\\Jogos\\osu!\\Songs\\'
#BEATMAP = glob.glob(BEATMAPS_FOLDER + "\\**\\*Quantum Entanglement*.osu")[0]
#BEATMAP = glob(BEATMAPS_FOLDER + "\\**\\*My Love*Insane*.osu")[0]
BEATMAP = glob.glob(BEATMAPS_FOLDER + "\\**\\*Uta*Himei*.osu")[0]
#BEATMAP = glob.glob(BEATMAPS_FOLDER + "\\**\\*DAYBREAK*Horizon[]]*.osu")[0]
print(BEATMAP)
beatmap = osu.rulesets.beatmap.load(BEATMAP)

xx = osulearn.dataset.input_data(beatmap)
xx = np.reshape(xx.values, (-1, osulearn.dataset.CHUNK_LENGTH, len(osulearn.dataset.INPUT_FEATURES)))

plt.plot(np.concatenate(xx))
plt.show()

predicted = model.predict(xx)

np.save('osu/replay.npy', np.concatenate(predicted))
print("Done.")


# 

# In[ ]:




