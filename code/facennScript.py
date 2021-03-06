'''
Comparing single layer MLP with deep MLP (using TensorFlow)
'''

import numpy as np
import pickle
import time
from math import sqrt
from scipy.optimize import minimize

# Do not change this
def initializeWeights(n_in,n_out):
    """
    # initializeWeights return the random weights for Neural Network given the
    # number of node in the input layer and output layer

    # Input:
    # n_in: number of nodes of the input layer
    # n_out: number of nodes of the output layer
                            
    # Output: 
    # W: matrix of random initial weights with size (n_out x (n_in + 1))"""
    epsilon = sqrt(6) / sqrt(n_in + n_out + 1);
    W = (np.random.rand(n_out, n_in + 1)*2* epsilon) - epsilon;
    return W



# Replace this with your sigmoid implementation
def sigmoid(z):
    return  (1.0 / (1.0 + np.exp(-z))) 

# Replace this with your nnObjFunction implementation
def nnObjFunction(params, *args):
    n_input, n_hidden, n_class, training_data, training_label, lambdaval = args

    w1 = params[0:n_hidden * (n_input + 1)].reshape((n_hidden, (n_input + 1)))
    w2 = params[(n_hidden * (n_input + 1)):].reshape((n_class, (n_hidden + 1)))
    obj_val = 0

    # Your code here
    #Forward pass begin
    training_bias = np.ones((training_data.shape[0], 1), dtype = np.float64)
    training_data = np.concatenate((training_data, training_bias), axis=1)
    w1_grad = np.zeros(w1.shape, dtype = np.float64)
    w2_grad = np.zeros(w2.shape, dtype = np.float64)
    w1_trans = np.transpose(w1)
    w2_trans = np.transpose(w2)
    
    #Computing output from hidden layer nodes
    a = np.dot(training_data, w1_trans)
    z = sigmoid(a)
    z_bias = np.ones((training_data.shape[0], 1), dtype = np.float64)
    z = np.concatenate((z, z_bias), axis=1)
    
    #Computing output from output layer nodes
    b = np.dot(z, w2_trans)
    o = sigmoid(b)
    #Forward pass end
    
    #Calculating error begins
    y = np.zeros(o.shape, dtype = np.float64)
    for i in range(training_data.shape[0]):
        j = training_label[i]
        y[i,j] = 1.0
    
    neg_log_likelihood_eror = np.sum((y * np.log(o)) + ((1.0-y)*np.log(1.0-o)))
    obj_val = (-1.0/training_data.shape[0]) * neg_log_likelihood_eror
    #Calculating error ends
    
    #Backpropagation begins
    delta = np.subtract(o,y)
    delta_trans = np.transpose(delta)
    #Derivative of error function with respect to the weight from the hidden layer to output layer
    w2_grad = np.add(w2_grad, np.dot(delta_trans, z))
    
    product = np.dot(delta, w2[:, 0:n_hidden]) #Ignoring bias nodes
    w1_grad = np.add(w1_grad, np.dot(((1-z[:,0:n_hidden]) * z[:,0:n_hidden] * product).transpose(),training_data))
    #Derivative of error function with respect to the weight from the input layer to hidden layer
    
    #Final error function
    obj_val = (-1.0/training_data.shape[0]) * neg_log_likelihood_eror
    #Backpropagation ends
    
    #Regularization begins
    lambda_value = lambdaval/(2*training_data.shape[0])
    reg_term = lambda_value * (np.sum(np.square(w1)) + np.sum(np.square(w2)))
    obj_val = obj_val + reg_term
    
    w1_grad = np.add(w1_grad, (lambdaval*w1))/training_data.shape[0]
    w2_grad = np.add(w2_grad, (lambdaval*w2))/training_data.shape[0]
    #Regularization ends
    
    # Make sure you reshape the gradient matrices to a 1D array. for instance if your gradient matrices are grad_w1 and grad_w2
    # you would use code similar to the one below to create a flat array
    # obj_grad = np.concatenate((grad_w1.flatten(), grad_w2.flatten()),0)
    obj_grad = np.concatenate((w1_grad.flatten(), w2_grad.flatten()), 0)
    
    return (obj_val, obj_grad)
    
# Replace this with your nnPredict implementation
def nnPredict(w1,w2,data):
    bias = np.ones((data.shape[0], 1), dtype = np.float64)
    labels = np.zeros((data.shape[0],1))
    data = np.concatenate((data, bias), axis=1)
    w1_trans = np.transpose(w1)
    w2_trans = np.transpose(w2)
    
    #Forward pass begins
    #Computing output from hidden layer nodes
    a = np.dot(data, w1_trans)
    z = sigmoid(a)
    z_bias = np.ones((data.shape[0], 1), dtype = np.float64)
    z = np.concatenate((z, z_bias), axis=1)
    
    #Computing output from output layer nodes
    b = np.dot(z, w2_trans)
    o = sigmoid(b)
    #Forward pass ends
    
    labels = np.argmax(o, axis=1)
    
    return labels

# Do not change this
def preprocess():
    pickle_obj = pickle.load(file=open('face_all.pickle', 'rb'))
    features = pickle_obj['Features']
    labels = pickle_obj['Labels']
    train_x = features[0:21100] / 255
    valid_x = features[21100:23765] / 255
    test_x = features[23765:] / 255

    labels = labels[0]
    train_y = labels[0:21100]
    valid_y = labels[21100:23765]
    test_y = labels[23765:]
    return train_x, train_y, valid_x, valid_y, test_x, test_y

"""**************Neural Network Script Starts here********************************"""
train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()
#  Train Neural Network
# set the number of nodes in input unit (not including bias unit)
n_input = train_data.shape[1]
print(n_input)
# set the number of nodes in hidden unit (not including bias unit)
n_hidden = 256
# set the number of nodes in output unit
n_class = 2

# initialize the weights into some random matrices
initial_w1 = initializeWeights(n_input, n_hidden);
initial_w2 = initializeWeights(n_hidden, n_class);
# unroll 2 weight matrices into single column vector
initialWeights = np.concatenate((initial_w1.flatten(), initial_w2.flatten()),0)
# set the regularization hyper-parameter
lambdaval = 10;
args = (n_input, n_hidden, n_class, train_data, train_label, lambdaval)

#Train Neural Network using fmin_cg or minimize from scipy,optimize module. Check documentation for a working example
opts = {'maxiter' :50}    # Preferred value.

start = time.time();
nn_params = minimize(nnObjFunction, initialWeights, jac=True, args=args,method='CG', options=opts)
print("Time taken to train:", time.time() - start)

params = nn_params.get('x')
#Reshape nnParams from 1D vector into w1 and w2 matrices
w1 = params[0:n_hidden * (n_input + 1)].reshape( (n_hidden, (n_input + 1)))
w2 = params[(n_hidden * (n_input + 1)):].reshape((n_class, (n_hidden + 1)))

#Pickle dump
obj = [n_input, n_hidden, w1, w2, lambdaval]
pickle.dump(obj, open('params_faceScript.pickle', 'wb'))

#Test the computed parameters
predicted_label = nnPredict(w1,w2,train_data)
#find the accuracy on Training Dataset
print('\n Training set Accuracy:' + str(100*np.mean((predicted_label == train_label).astype(float))) + '%')
predicted_label = nnPredict(w1,w2,validation_data)
#find the accuracy on Validation Dataset
print('\n Validation set Accuracy:' + str(100*np.mean((predicted_label == validation_label).astype(float))) + '%')
predicted_label = nnPredict(w1,w2,test_data)
#find the accuracy on Validation Dataset
print('\n Test set Accuracy:' +  str(100*np.mean((predicted_label == test_label).astype(float))) + '%')
