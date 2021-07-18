'''With k=3, this is a K Nearest Neighbors algorithm. The MNIST handwritten digits dataset was used to train
this model, including 50,000 images in the training set and 10,000 in the testing set.
The model is then saved as a knn.sav file using Pickle. '''
import numpy as np
from sklearn import datasets
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier
import pickle

k = 3
class KNN:

    def __init__(self, k):
        self.mnist = datasets.fetch_openml('mnist_784', data_home='mnist_dataset/')
        self.data, self.target = self.mnist.data, self.mnist.target
        # To make the data sets, create an array of indices the size of MNIST.
        # We can apply this array to distort the MNIST data since it is in random order.
        self.indx = np.random.choice (len (self.target), 70000, replace=False)
        # Getting the classifier started
        self.classifier = KNeighborsClassifier (n_neighbors=k)

    # method for generating the test datasets
    def mk_dataset (self, size):
        """produces a dataset of size "size" from which photographs and targets are retrieved
            This is used to construct the dataset that the model will keep, as well as to experiment with different
                dataset sizes in the model..
                    """
        train_img = [self.data[i] for i in self.indx[:size]]
        train_img = np.array(train_img)
        train_target = [self.target[i] for i in self.indx[:size]]
        train_target = np.array(train_target)

        return train_img, train_target

    def skl_knn (self):
        """k: test data: the data/targets used to test the classifier stored data: the data/targets
            used to classify the test data number of nearest neighbors to use in classification
        """
        fifty_x, fifty_y = self.mk_dataset(50000)
        test_img = [self.data[i] for i in self.indx[60000:70000]]
        test_img1 = np.array(test_img)
        test_target = [self.target[i] for i in self.indx[60000:70000]]
        test_target1 = np.array(test_target)
        self.classifier.fit (fifty_x, fifty_y)

        y_pred = self.classifier.predict(test_img1)
        pickle.dump (self.classifier, open('knn.sav', 'wb') )
        print(classification_report (test_target1, y_pred) )
        print ("KNN Classifier model saved as knn.sav!")