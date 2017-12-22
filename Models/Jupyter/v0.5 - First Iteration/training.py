## --------------------------------------- ##
    # Start image dimensions - 1080x720
    # Resize to - 80x40
    # NN LAYOUT:
        # INPUT       - 3200 input neurons
        # H1          - 256 neurons
        # H2          - 256 neurons
        # OUT         - 3  output neurons
## --------------------------------------- ##

import DataPreProcessing
import numpy as np
from sklearn.utils import shuffle
import tensorflow as tf

###### DATASET PREP ######

#Generate the dataset in the correct format

f_images = DataPreProcessing.DatasetProcessing("forward", 3000, "/Volumes/TRANSCEND/SDC/JupyterNotebookExamples/cardataset/training_set/Forward/")
f_images.generateDataset()

l_images = DataPreProcessing.DatasetProcessing("left", 3000, "/Volumes/TRANSCEND/SDC/JupyterNotebookExamples/cardataset/training_set/Left/")
l_images.generateDataset()

r_images = DataPreProcessing.DatasetProcessing("right", 3000, "/Volumes/TRANSCEND/SDC/JupyterNotebookExamples/cardataset/training_set/Right/")
r_images.generateDataset()

f_array = f_images.getImgArray()
f_lbl = f_images.getLblArray()

l_array = l_images.getImgArray()
l_lbl = l_images.getLblArray()

r_array = r_images.getImgArray()
r_lbl = r_images.getLblArray()

print(type(f_array))

#Concatenate all arrays

all_images_array = np.concatenate((f_array, l_array, r_array), axis=0)
all_labels_array = np.concatenate((f_lbl, l_lbl, r_lbl), axis=0)

#Reshuffle the new images

image_array, image_labels = shuffle(all_images_array, all_labels_array, random_state = 9000)

###### END - DATASET PREP ######

###### START TF TRAINING ######

#Defining Parameters
learning_rate = 0.001
training_epochs = 25
batch_size = 50
n_classes = 3
n_samples = 9000
n_input = 3200
n_hidden_1 = 256
n_hidden_2 = 256

#Defining the Weights
#Randomly assigned values from a normal distribution
#h1 - rows 396, cols 256
#h2 - rows 256, cols 256
#out - rows 256, cols 10
weights = {
        'h1':tf.Variable(tf.random_normal([n_input, n_hidden_1])),
        'h2':tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2])),
        'out':tf.Variable(tf.random_normal([n_hidden_2, n_classes]))
}

#Defining the Biases
#Randomly asigned values from a normal distribution
biases = {
        'b1':tf.Variable(tf.random_normal([n_hidden_1])),
        'b2':tf.Variable(tf.random_normal([n_hidden_2])),
        'out':tf.Variable(tf.random_normal([n_classes]))
}

#Defining the NN Training Function
def multilayer_perceptron(x, weights, biases):
    '''
    x: placeholder for data input
    weights: dict of weights
    biases: dict of bias values
    '''
    
    ##First hidden layer
    #(X * W) + B
    layer_1 = tf.add(tf.matmul(x, weights['h1']), biases['b1'])
    #RELU ((X * W) + B) -> f(x) = max(0,x)
    layer_1 = tf.nn.relu(layer_1)
    
    ##Second Hidden Layer
    #(X * W) + B
    layer_2 = tf.add(tf.matmul(layer_1,weights['h2']), biases['b2'])
    #RELU((X * W) + B) -> f(x) = max(0,x)
    layer_2 = tf.nn.relu(layer_2)
    
    ##Output Layer
    out_layer = tf.matmul(layer_2, weights['out']) + biases['out']
    
    return out_layer

#Defining the placeholders for x and y
#x - same as num of inputs
#y - output - same as classes
x = tf.placeholder('float', [None, n_input])
y = tf.placeholder('float', [None, n_classes])

#Setting up the model
pred = multilayer_perceptron(x, weights, biases)

#Define cost and optimiser functions
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

## TF TRAIN TIME
sess = tf.InteractiveSession()
init = tf.global_variables_initializer()
saver = tf.train.Saver()
sess.run(init)

#TRAIN TRAIN TRAIN!!
start_batch = 0
end_batch = batch_size

for epoch in range(training_epochs):
    
    #Resetting the average cost
    avg_cost = 0.0
    
    #Defining the total batch
    #9000/batch_size
    total_batch = int(n_samples/batch_size)
    
    for i in range(total_batch):
        #Grab the next batch data
        
        batch_x = image_array[start_batch:end_batch]
        batch_y = image_labels[start_batch:end_batch]
        
        #Optimisation and Loss values
        _, c = sess.run([optimizer, cost], feed_dict={x:batch_x, y:batch_y})
        
        avg_cost += c/total_batch
        
        start_batch += batch_size
        end_batch += batch_size
    
    start_batch = 0
    end_batch = batch_size
        
    print("Epoch {} Cost {:.4f}".format(epoch+1, avg_cost))

print("Model has completed {} epochs of training".format(training_epochs))
save_path = saver.save(sess, "model.ckpt")
print("Model Saved to File")

##TESTING ACCURACY ON TRAINING SET
correct_predictions = tf.equal(tf.argmax(pred,1), tf.argmax(y,1))
correct_predictions = tf.cast(correct_predictions, 'float')
accuracy = tf.reduce_mean(correct_predictions)
accuracy.eval({x: image_array, y: image_labels})
##100% on the training data - could mean it has possibly memorised it, we will conmpare with testing





