import tensorflow as tf
import numpy as np
import pickle
import os
# from tensorflow.examples.tutorials.mnist import input_data
# mnist = input_data.read_data_sets("/tmp/data/", one_hot = True)
# from createMusicalFeaturesets import create_feature_sets_and_labels
train_x,train_y,test_x,test_y = pickle.load(open("notesData2.pickle", "rb"))


saveFile = "savedModels/musicModelpy27"


n_nodes_hl1 = 1000
n_nodes_hl2 = 1000
n_nodes_hl3 = 1000

n_classes = 2
batch_size = 10
hm_epochs = 9

input_data_size = len(train_x[0])# each train_x instance is one song, and so one lexicon of notes
print("DEBUG: input data size = "+str(input_data_size))

x = tf.placeholder('float')
y = tf.placeholder('float')

hidden_1_layer = {'f_fum':n_nodes_hl1,
                  'weight':tf.Variable(tf.random_normal([128, n_nodes_hl1])),
                  'bias':tf.Variable(tf.random_normal([n_nodes_hl1]))}

hidden_2_layer = {'f_fum':n_nodes_hl2,
                  'weight':tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
                  'bias':tf.Variable(tf.random_normal([n_nodes_hl2]))}

hidden_3_layer = {'f_fum':n_nodes_hl3,
                  'weight':tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_hl3])),
                  'bias':tf.Variable(tf.random_normal([n_nodes_hl3]))}

output_layer = {'f_fum':None,
                'weight':tf.Variable(tf.random_normal([n_nodes_hl3, n_classes])),
                'bias':tf.Variable(tf.random_normal([n_classes])),}



# Nothing changes
def neural_network_model(data):
    ####INPUT LAYER (HIDDEN LAYER 1)
    l1 = tf.add(tf.matmul(data,hidden_1_layer['weight']), hidden_1_layer['bias'])
    l1 = tf.nn.relu(l1)
    ####HIDDEN LAYER 2
    l2 = tf.add(tf.matmul(l1,hidden_2_layer['weight']), hidden_2_layer['bias'])
    l2 = tf.nn.relu(l2)
    ####HIDDEN LAYER 3
    l3 = tf.add(tf.matmul(l2,hidden_3_layer['weight']), hidden_3_layer['bias'])
    l3 = tf.nn.relu(l3)
    ####OUTPUT LAYER
    output = tf.matmul(l3,output_layer['weight']) + output_layer['bias']

    return output


def train_neural_network(x):
    prediction = neural_network_model(x)
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=y) )
    optimizer = tf.train.AdamOptimizer().minimize(cost)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # try:
        #     epoch = int(open(tf_log,'r').read().split('\n')[-2])+1
        #     print('STARTING EPOCH:',epoch)
        # except:
        #     epoch = 1
        batches_run = 0
        epoch = 1
        while epoch <= hm_epochs:
            # if epoch != 1:
            #     #saver.restore(sess,'/'+saveFile)
            #     print("Should Restore Saved File")
            epoch_loss = 1
            i=0
            while i < len(train_x):
                start = i
                end = i+batch_size
                batch_x = np.array(train_x[start:end])
                batch_y = np.array(train_y[start:end])
                _, c = sess.run([optimizer, cost], feed_dict={x: batch_x, y: batch_y})
                epoch_loss += c
                i+=batch_size
                batches_run +=1
                print('Batch run:',batches_run,'/',batch_size,'| Epoch:',
                      epoch,'| Batch Loss:',c,)
            saver.save(sess, saveFile)
            print("Should Save session in "+ saveFile )
            print('Epoch', epoch+1, 'completed out of',hm_epochs,'loss:', epoch_loss)
            # with open(tf_log,'a') as f:
            #     f.write(str(epoch)+'\n')
            epoch +=1
        correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        print('Trained',len(train_x),'samples.')
        print('Tested',len(test_x),'samples.')
        accPercent = accuracy.eval({x:test_x, y:test_y})*100
        print('Accuracy: '+ str(accPercent)+ '%')


saver = tf.train.Saver()
# tf_log = 'tf.log' ## SAVES EPOCH NUMBER
train_neural_network(x)


def test_neural_network():
    prediction = neural_network_model(x)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # for epoch in range(hm_epochs):
        #     try:
        #         y =2
        #         # saver.restore(sess,'/'+saveFile)
        #         print("Restoring "+ saveFile )
        #     except Exception as e:
        #         print(str(e))
        #     epoch_loss = 0

        correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct, 'float'))

        ## WHEN WE SAVE TESTING DATA SEPARATLY
        # feature_sets = []
        # labels = []
        # counter = 0
        # with open('processed-test-set.csv', buffering=20000) as f:
        #     for line in f:
        #         try:
        #             features = list(eval(line.split('::')[0]))
        #             label = list(eval(line.split('::')[1]))
        #             feature_sets.append(features)
        #             labels.append(label)
        #             counter += 1
        #         except:
        #             pass

        testx = np.array(test_x)
        testy = np.array(test_y)
        counter = len(test_x)
        print(testx,testy)
        print(test_x,test_y)
        print('******RESULTS******')
        print('Tested',counter,'samples.')
        print('Accuracy:', accuracy.eval({x:testx, y:testy}) )


#test_neural_network()


print ("\n\n\nFINISHED\n\n\n")
# x =os.remove("tf.log")
# print("removed :" + str(x))
