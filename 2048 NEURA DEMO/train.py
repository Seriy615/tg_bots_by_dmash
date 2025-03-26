import numpy as np
import tensorflow as tf
import pickle

# Load the first 150 pairs of training data
with open('training_data.pkl', 'rb') as file:
    training_data = pickle.load(file)

# Extract X_train (game board states) and Y_train (corresponding moves)
X_train, Y_train = zip(*training_data)

# Convert the data to NumPy arrays
X_train = np.array(X_train)
Y_train = np.array(Y_train)

# Define your neural network model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(16,)),  # Assuming flattened 4x4 board state
    tf.keras.layers.Dense(4, activation='softmax')  # Output layer with 4 outputs (one for each move)
])

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X_train, Y_train, epochs=10000, batch_size=32)  # Adjust epochs and batch size as needed
model.save('trained_2048_model.keras')
