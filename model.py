import tensorflow as tf
import tensorflow_datasets as tfds

pretrained_resnet = tf.keras.applications.resnet_v2.ResNet101V2(
    include_top=False,  # Enlever les scores Imagenet (a remplacer par les scores de nos classes)
    weights="imagenet",
    input_tensor=tf.keras.Input(shape=(224, 224, 3)),
    input_shape=(224, 224, 3),
    pooling=None,
    classes=10,  # Nombre de classes
    classifier_activation="softmax",
)
for layer in pretrained_resnet.layers:
    layer.trainable = False


resnet = tf.keras.Sequential()
resnet.add(
    tf.keras.layers.Lambda(
        tf.keras.applications.resnet_v2.preprocess_input, input_shape=(224, 224, 3)
    )
)
resnet.add(tf.keras.layers.Resizing(height=224, width=224))
resnet.add(tf.keras.layers.RandomFlip("horizontal", input_shape=(224, 224, 3)))
resnet.add(tf.keras.layers.RandomRotation(0.1))
resnet.add(tf.keras.layers.RandomZoom(0.1))
resnet.add(pretrained_resnet)
resnet.add(tf.keras.layers.Flatten())
resnet.add(tf.keras.layers.Dense(1024, activation="relu"))
resnet.add(tf.keras.layers.Dense(102, activation="softmax"))

resnet.build(input_shape=(None, 224, 224, 3))
resnet.summary()

resnet.compile(
    optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)

training_ds = tf.keras.preprocessing.image_dataset_from_directory(
    "./images",
    subset="training",
    seed=123,
    image_size=(224, 224),
    batch_size=16,
    validation_split=0.2,
)
validation_ds = tf.keras.preprocessing.image_dataset_from_directory(
    "./images",
    subset="validation",
    seed=123,
    image_size=(224, 224),
    batch_size=16,
    validation_split=0.2,
)


resnet.fit(training_ds, epochs=20, validation_data=validation_ds, shuffle=False)

resnet.save("models/resnet_fine_tuned")
