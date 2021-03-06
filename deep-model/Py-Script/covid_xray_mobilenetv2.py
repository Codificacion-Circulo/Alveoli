# -*- coding: utf-8 -*-
"""covid_xray-mobilenetv2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hVw0rTQZdBJTn2vPphBw6WsP8SqMmj1t
"""

!nvidia-smi

"""## Data"""

! mkdir ~/.kaggle
! cp kaggle.json ~/.kaggle/
! chmod 600 ~/.kaggle/kaggle.json

! pip install kaggle

! kaggle datasets download jtiptj/chest-xray-pneumoniacovid19tuberculosis

!unzip /content/chest-xray-pneumoniacovid19tuberculosis.zip

"""## Tensorflow"""

import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.python.keras.applications.mobilenet_v2 import MobileNetV2
from tensorflow.python.keras.applications.mobilenet_v2 import preprocess_input
#from tensorflow.python.keras.applications import densenet
#from tensorflow.python.keras.applications.densenet import preprocess_input
from tensorflow.python.keras.applications import vgg16
from tensorflow.python.keras.applications.vgg16 import preprocess_input
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator, load_img
from tensorflow.python.keras import layers, models, Model, optimizers
from tensorflow.python.keras.layers import GlobalAveragePooling2D,Dropout
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/train/
# %ls

category_names = sorted(os.listdir('/content/train'))
nb_categories = len(category_names)
img_pr_cat = []
for category in category_names:
    folder = '/content/train' + '/' + category
    img_pr_cat.append(len(os.listdir(folder)))

for subdir, dirs, files in os.walk('/content/train'):
    for file in files:
        img_file = subdir + '/' + file
        image = load_img(img_file)
        plt.figure()
        plt.title(subdir)
        plt.imshow(image)
        break

"""## Preprocess

"""

img_height, img_width = 224,224

train_data_dir  = '/content/train'
val_data_dir = '/content/val'
test_data_dir = '/content/test'

batch_size = 64
train_datagen =  ImageDataGenerator(
    shear_range = 0.2,
    zoom_range = 0.2,
    rescale=1./255,
    rotation_range=10, 
    width_shift_range=0.2, 
    height_shift_range=0.2,
    horizontal_flip=True, 
)
test_datagen =  ImageDataGenerator(rescale=1./255)
val_datagen =  ImageDataGenerator(rescale=1./255)

print('Total number of images for "training":')
train_generator = train_datagen.flow_from_directory(
train_data_dir,
target_size = (img_height, img_width),
batch_size=batch_size,
class_mode = "categorical")

print('Total number of images for "validation":')
val_generator = test_datagen.flow_from_directory(
val_data_dir,
target_size = (img_height, img_width),
batch_size=batch_size,
class_mode = "categorical",
shuffle=False)

print('Total number of images for "testing":')
test_generator = test_datagen.flow_from_directory(
test_data_dir,
target_size = (img_height, img_width),
batch_size=batch_size,
class_mode = "categorical",
shuffle=False)

"""
## Model

"""

learning_rate = 1e-3
epochs = 20

img_height, img_width = 224,224
base_model=MobileNetV2(weights='imagenet',pooling='avg',include_top=False, input_shape = (img_width, img_height, 3))
#conv_base = vgg16.VGG16(weights='imagenet', include_top=False, pooling='avg', input_shape = (img_width, img_height, 3))

for layer in base_model.layers:
    layer.trainable=False
#Not Training existing weights of Keras Model (Transfer Learning)

input_shape = (img_width, img_height, 3)

model = models.Sequential()
model.add(base_model)
model.add(Dropout(0.2))
model.add(layers.Dense(nb_categories, activation='softmax'))

model.compile(optimizer='adam',loss='categorical_crossentropy',metrics=['accuracy'])

test_generator.class_indices

history =model.fit(train_generator, epochs=epochs,validation_data=val_generator)

model.summary()

model.save('/content/model2-disease-classify.h5')

"""## Results"""

acc = history.history['accuracy']
loss = history.history['loss']
epochs = range(1,len(acc)+1)
plt.figure()
plt.plot(epochs, acc, 'b', label = 'Training accuracy')
plt.title('Training accuracy')
plt.legend()
plt.figure()
plt.plot(epochs, loss, 'r', label = 'Training loss')
plt.title('Training loss')
plt.legend()

loss_train = history.history['loss']
loss_val = history.history['val_loss']
epochs = range(1,21)
plt.plot(epochs, loss_train, 'g', label='Training loss')
plt.plot(epochs, loss_val, 'b', label='validation loss')
plt.title('Training and Validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

import itertools

classes = list(test_generator.class_indices.keys())
print('Classes: '+str(classes))

def plot_confusion_matrix(cm, classes, normalize=True, title='Confusion matrix', cmap=plt.cm.Greens):
    plt.figure(figsize=(10,10))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)
    if normalize:
        cm = cm.astype('float')/cm.sum(axis=1)[:, np.newaxis]
        cm = np.around(cm,decimals=2)
        cm[np.isnan(cm)] = 0.0
    thresh = cm.max()/2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

Y_pred = model.predict_generator(test_generator)
y_pred = np.argmax(Y_pred, axis=1)
target_names = classes
cm = confusion_matrix(test_generator.classes, y_pred)
plot_confusion_matrix(cm, target_names, normalize=False, title='Confusion Matrix')
print('Classification Report')
print(classification_report(test_generator.classes, y_pred, target_names=target_names))

np.mean(history.history['accuracy'])

score = model.evaluate_generator(train_generator,steps=3)
print('Train loss:',score[0])
print('Train accuracy:',score[1])

score = model.evaluate_generator(test_generator,steps=3)
print('Test loss:',score[0])
print('Test accuracy:',score[1])



