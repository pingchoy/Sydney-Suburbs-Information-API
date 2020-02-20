import pandas as pd
from sklearn import linear_model
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from sklearn.utils import shuffle


class Predict(object):
    def __init__(self, school):
        self.school = school

    def predictasd(self, school_name):
        head_X_train, head_y_train, head_X_test, head_y_test = self.load_headcount("headcount.csv",
                                                                                   split_percentage=0.7)
        model = linear_model.LinearRegression()
        # model = linear_model.BayesianRidge(alpha_1=1e-06, alpha_2=1e-06, compute_score=False, copy_X=True,
        # #                                    fit_intercept=True, lambda_1=1e-06, lambda_2=1e-06, n_iter=300,
        # #                                    normalize=False, tol=0.001, verbose=False)
        model.fit(head_X_train, head_y_train)
        school_data_x = self.get_school_data('Bongongo Public School', "headcount.csv")
        y_pred = model.predict(head_X_test)

        # for i in range(len(head_y_test)):
        #     print("Expected:", head_y_test[i], "Predicted:", y_pred[i])
        #
        # # The mean squared error
        # print("Mean squared error: %.2f"
        #       % mean_squared_error(head_y_test, y_pred))

        y_pred = model.predict(school_data_x)
        print(y_pred[0])
        return y_pred[0]

    def load_headcount(self, school_path, split_percentage):
        df = pd.read_csv(school_path, index_col=0)

        df = shuffle(df)
        row = df.iloc[:, 2:]
        row.astype(int)

        head_count_x = df.iloc[:, 2:16].values

        head_count_y = df.iloc[:, 16].values

        # Split the dataset in train and test data
        # A random permutation, to split the data randomly

        split_point = int(len(head_count_x) * split_percentage)
        head_X_train = head_count_x[:split_point]

        head_y_train = head_count_y[:split_point]

        head_X_test = head_count_x[split_point:]
        head_y_test = head_count_y[split_point:]

        return head_X_train, head_y_train, head_X_test, head_y_test

    def get_school_data(self, name, school_path):
        df = pd.read_csv(school_path, index_col=0)
        school_data = df.loc[df['School_Name'] == name]
        school_data_x = school_data.iloc[:, 2:16].values

        return school_data_x