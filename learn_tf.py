import tensorflow as tf
from tensorflow.keras import layers, models

# Define a simple neural network
model = models.Sequential([
    layers.Dense(128, activation='relu', input_shape=(input_size,)),
    layers.Dropout(0.2),
    layers.Dense(num_classes, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Train the model with your data
model.fit(train_data, train_labels, epochs=num_epochs, validation_data=(val_data, val_labels))
