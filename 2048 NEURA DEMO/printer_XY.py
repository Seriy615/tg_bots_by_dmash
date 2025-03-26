import pickle

# Load training data from the file
with open('training_data.pkl', 'rb') as file:
    loaded_training_data = pickle.load(file)

# Iterate through the loaded training data and print it
for idx, (X_train, Y_train) in enumerate(loaded_training_data):
    print(f"Example {idx + 1}:")
    print("X_train:")
    for i in range(0, len(X_train), 4):
        print(X_train[i:i+4])  # Print in 4x4 block format
    print(f"Y_train: {Y_train}")
    print()
