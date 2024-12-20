# -*- coding: utf-8 -*-
"""
Original file is located at
    https://colab.research.google.com/drive/1sR4KNbc69RJjidddsucGWi10VY03lydA
"""

#Import all necessary libraries
import tensorflow
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam

import pickle
import numpy as np
import os

from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Access the specific file in Google Drive

file_path = '/content/drive/My Drive/Sherlock Holmes.txt'

# Check if the file exists and read its content
try:
    with open(file_path, 'r') as file:
        content = file.read()
        print("File content:\n", content[:500])  # Display first 500 characters
except FileNotFoundError:
    print(f"File not found at path: {file_path}")

"""# Text Preprocessing

"""

#Splits the content string into lines based on newline characters and stores it in lines list
lines = content.split('\n')

#Combines all lines of text from lines list into the data string variable, seperated by a space
data = ""
for i in lines:
  data = ' '.join(lines)

#Cleans that data by removing unnecessary characters such as new lines, carriage returns, byte order marks, and double quotes
data = data.replace('\n', '').replace('\r', '').replace('\ufeff', '').replace('"', '').replace('"', '')

#Splits the text into individual words, then rejoins them into a single string with spaces between them
data = data.split()
data = ' '.join(data)

#Display the first 1000 characters in the cleaned data
data[:1000]

"""# Tokenization"""

#Creates a tokenizer object to convert text into numerical sequences for the model
tokenizer = Tokenizer()

#Analyzes the data and builds a vocabulary of unique words/tokens found in the text
tokenizer.fit_on_texts([data])

#Saves the trained tokenizer so we can load it later without having to retrain it
pickle.dump(tokenizer, open('token.pk1', 'wb'))

"""# Converting to Sequence of Numbers"""

#Converts the cleaned text data and converts it into a sequence of numbers
#Each number represents a specific word from the voacbulary and stores it in the sequence_data variable
sequence_data = tokenizer.texts_to_sequences([data])[0]

print(sequence_data[:10])

print(len(sequence_data))

#Determines the total number of unique words in the text
#Add 1 to the length to accommodate a reserved index
vocabSize = len(tokenizer.word_index)+1
vocabSize

"""# Converting the Data"""

#Takes the words and breaks it down into overlapping sequences of 4 words each
#The sequences are stored in the list
#The end goal is to create sequences of four words to be fed into the model
sequence = []
for i in range(3, len(sequence_data)):
  words = sequence_data[i-3:i+1]
  sequence.append(words)

print(len(sequence))

sequence = np.array(sequence)
print(sequence)

# Divide into the independent (input data) and dependent features (output data)
x = []
y = []

#loop through sequence to prepare features for model training
for i in sequence:
  #pass the first 3 data values into the x list
  x.append(i[0:3])
  #predict the last data value and add to the y list
  y.append(i[3])

#convert the lists into np arrays to make data compatible with ML libraries
x = np.array(x)
y = np.array(y)

#convert the y array to categorical data to help with classification
y = to_categorical(y, num_classes=vocabSize)

"""# Building the LSTM model"""

#initialize the model
model = Sequential()

#pass the embedding layer using vocab size for input_dim and 10 for output_dim
#maps the input words
model.add(Embedding(input_dim = vocabSize, output_dim = 10, input_length = len(sequence)))

#add 1st LSTM layer having 1000 parameters and return sequences as a memory
#retains memory for subsequent layers
model.add(LSTM(1000, return_sequences=True))

#add the 2nd LSTM model with 1000 parameters
#summarizes the sequence info
model.add(LSTM(1000))

#add a dense layer to make the data 0s and 1s
#utilizes the relu function to learn complex patterns
model.add(Dense(1000, activation="relu"))

#add final layer to output probabilities for each vocabulary class
#uses softmax activation because the data is multi-class
model.add(Dense(vocabSize, activation="softmax"))

#explicitly initialize the model using build()
model.build(input_shape=(None, 3))
#display architecture and parameters of the model
model.summary()

"""# Training the model"""

#import the modelcheckpoint callback class. saves the model during training
from tensorflow.keras.callbacks import ModelCheckpoint

#create a model checkpoint instance using the file. It also monitors the loss
#monitors loss and saves only the best model to prevent overwriting
checkpoint = ModelCheckpoint("Sherlock Holmes.keras", monitor="loss", verbose=1, save_best_only=True)

#compile the model with categorical crossentropy for the loss function, multi-class classification
#use Adam optimizer, an optimization algorithm that adjusts LR dynamically during training
model.compile(loss="categorical_crossentropy", optimizer = Adam(learning_rate = .001))

#train the model on the x and y, for 2 epochs
model.fit(x, y, epochs = 2, batch_size=64, callbacks=[checkpoint])

"""# Resources





*   https://sourestdeeds.github.io/pdf/Deep%20Learning%20with%20Python.pdf
*   https://www.tensorflow.org/guide/keras
*   https://docs.python.org/3/library/pickle.html




"""

from tensorflow.keras.models import load_model

model = load_model('Sherlock Holmes.keras')
tokenizer = pickle.load(open('token.pk1', 'rb'))

def predict_word(model, tokenizer, text):
  sequence = tokenizer.texts_to_sequences([text])
  sequence = np.array(sequence)
  preds = np.argmax(model.predict(sequence))
  predicted_word = ""
  for key, value in tokenizer.word_index.items():
    if value == preds:
      predicted_word = key
      break
  print(predicted_word)
  return predicted_word

predict_word(model, tokenizer, "Once in a")

"""Explanation of predict_word function

Logical Flow: The code is designed to load a trained model and tokenizer, then predict the next word in a text sequence based on the input.
Functionality: It uses a neural network model trained on text data (e.g., "Sherlock Holmes") to generate predictions.

Usability: The function predict_word is modular and can be reused with different inputs.

Does the Code Make Sense?

The core logic is sound: It loads a trained model and tokenizer, processes the input text, predicts the next word's class index, and maps it back to a word.
Issue: predict_classes is deprecated and will throw an error in TensorFlow 2.6+ versions. The corrected prediction line should be:

preds = np.argmax(model.predict(sequence), axis=-1)

Once updated for compatibility, the code is valid and functional for its intended purpose.

from tensorflow.keras.models import load_model
import pickle
import numpy as np

# Load the previously saved trained model
# 'Sherlock Holmes.keras' contains the trained neural network for text prediction.
model = load_model('Sherlock Holmes.keras')

# Load the tokenizer object that was saved earlier using pickle
# The tokenizer is used to encode and decode text into numerical sequences.
tokenizer = pickle.load(open('token.pk1', 'rb'))

def predict_word(model, tokenizer, text):
    '''
    Predict the next word in a sequence based on the trained model and tokenizer.

    Parameters:
    - model: Trained Keras sequential model used for predictions.
    - tokenizer: Tokenizer object for encoding/decoding text.
    - text: Input text string to predict the next word.

    Returns:
    - str: Predicted next word in the sequence.
    '''
    # Convert the input text into a numerical sequence using the tokenizer
    sequence = tokenizer.texts_to_sequences([text])
    
    # Ensure the sequence is in NumPy array format for compatibility with the model
    sequence = np.array(sequence)
    
    # Predict the class index of the next word using the model
    # Note: `predict_classes` is deprecated in newer TensorFlow versions.
    preds = np.argmax(model.predict(sequence), axis=-1)
    
    # Initialize an empty string to store the predicted word
    predicted_word = ""
    
    # Search through the tokenizer's word-to-index mapping to find the predicted word
    for key, value in tokenizer.word_index.items():
        if value == preds:  # If the index matches the prediction
            predicted_word = key  # Assign the word to `predicted_word`
            break  # Exit the loop once the word is found
    
    # Print the predicted word
    print(predicted_word)
    
    # Return the predicted word
    return predicted_word

# Call the function to predict the next word after the phrase "A Case of"
predict_word(model, tokenizer, "A Case of")
"""
