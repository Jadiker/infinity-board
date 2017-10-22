from __future__ import print_function
import mxnet as mx
import numpy as np
import mxnet.ndarray as nd
from mxnet import autograd
from mxnet import gluon
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler

ctx = mx.cpu()
batch_size = 3

def normalizeDataIntoNd(data, m):
    return nd.array([[(value*1.0 / m) for value in example] for example in data])

# data is in the form (listOfExamples, listOfTargetValues)
# For example, ([[1, 22, 3], [2, 33, 4], ...], [3, 10, ...])
def makeNet(data):
    global ctx
    global batch_size
    inX = data[0]
    m = max([max(example) for example in inX])
    # print(m)
    # TODO have this use normalizeData
    inX = [[(value*1.0 / m) for value in example] for example in inX]
    
    # print(inX)
            
    X = nd.array(inX)
    
    # print("before normal {}".format(X))
    
    # X = nd.concat([i/sum(X) for i in X])
    # print("after normal: {}".format(X))
    
    
    # noise = 0.01 * nd.random_normal(shape=(num_examples,))
    #y = real_fn(X) + noise
    y = nd.array(data[1])
    print(y)
    
    train_data = gluon.data.DataLoader(gluon.data.ArrayDataset(X, y),
                                          batch_size=batch_size, shuffle=True)
                                          
    print("random training data made!")
                                          
    net = gluon.nn.Sequential()
    
    num_fc = 1
    num_outputs = 1
        
    net = gluon.nn.Sequential()
    with net.name_scope():
        # net.add(gluon.nn.Dense(2))
        net.add(gluon.nn.Dense(1))
    
    net.collect_params().initialize(mx.init.Normal(sigma=1.), ctx=ctx)
    
    square_loss = gluon.loss.L2Loss()
    
    trainer = gluon.Trainer(net.collect_params(), 'sgd', {'learning_rate': 0.002})
    
    epochs = 100
    smoothing_constant = .01
    moving_loss = 0
    niter = 0
    loss_seq = []
    
    for e in range(epochs):
        print("Started!")
        for i, (data, label) in enumerate(train_data):
            data = data.as_in_context(ctx)
            label = label.as_in_context(ctx)
            with autograd.record():
                
                # print("Data! {}".format(data))
                output = net(data)
                loss = square_loss(output, label)
            loss.backward()
            trainer.step(batch_size)
    
            ##########################
            #  Keep a moving average of the losses
            ##########################
            niter +=1
            curr_loss = nd.mean(loss).asscalar()
            moving_loss = (1 - smoothing_constant) * moving_loss + (smoothing_constant) * curr_loss
    
            # correct the bias from the moving averages
            est_loss = moving_loss/(1-(1-smoothing_constant)**niter)
            loss_seq.append(est_loss)
    
        print("Epoch %s. Moving avg of MSE: %s" % (e, est_loss))
    
    '''
    print(inX)    
    print(inX[1])
    testVal1 = nd.array([inX[0]])
    testVal2 = nd.array([inX[1]])
    testVal3 = nd.array([inX[2]])
    print("Output of net on 0th:\n{}".format(net(testVal1)))
    print("Output of net on 1st:\n{}".format(net(testVal2)))
    print("Output of net on 2nd:\n{}".format(net(testVal3)))
    '''
    
    return (net, m)
