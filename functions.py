import pandas as pd
import numpy as np
import dbwork
import matplotlib
import matplotlib.dates as mdates

# matplotlib.use('Agg')

from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler
from matplotlib import pyplot as plt
from datetime import datetime

np.random.seed(7)


def create_pic_plot(dataset, name_file):
    """ Creating plot of real and predict BTC price """

    fig, ax = plt.subplots()

    # transform dates to format matplotlib dates
    dates = dataset.date.values
    dates = list(map(lambda d: datetime.strptime(d, '%Y-%m-%d'), dates))
    dates = matplotlib.dates.date2num(dates)

    plt.plot(dates, dataset.close.values, label='Real price')
    plt.plot(dates, dataset.predict.values, label='Predict price')

    # choose format
    myFmt = mdates.DateFormatter('%m/%d')
    ax.xaxis.set_major_formatter(myFmt)
    plt.gcf().autofmt_xdate()

    plt.title('Prediction Price BTC')
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.savefig(name_file)


class PredictionCore:
    def __init__(self):
        pass

    def load_data(self, name_db, tab_btc, tab_sentiment):
        db = dbwork.DataBase(name_db)
        btc_data = pd.read_sql(tab_btc, db.engine)
        sent_data = pd.read_sql(tab_sentiment, db.engine)
        return btc_data, sent_data

    def create_dataset(self, dataset_back, look_back, dataset_uni):
        """ Transform data with look_back window for memory LSTM """

        dataX, dataY = [], []
        for i in range(len(dataset_back) - look_back):
            a = dataset_back[i:(i + look_back), 0]
            a = a.tolist()

            for j in range(len(dataset_uni)):
                a.append(dataset_uni[j][i:(i + look_back), 0].mean())

            dataX.append(a)
            dataY.append(dataset_back[i + look_back, 0])
        return np.array(dataX), np.array(dataY)

    def prepare_data(self, data, name_target, name_features, look_back):
        """ Preparing data for LSTM """

        if name_target not in name_features:
            print('Name target feature should be in list of name_features')
            return None

        features = self.get_features(data, name_features)
        self.scaled_features, self.scalers_features = self.get_scaled_features(features)

        data_target = self.scaled_features['close']
        self.scaled_features.pop('close', None)
        data_main = self.scaled_features

        train_size = int(len(data_target) * 0.90)
        train_target, test_target = data_target[0:train_size, :], data_target[train_size:len(data_target), :]
        train_main, test_main = self.get_split_features(data_main, train_size)

        X_train, y_train = self.create_dataset(train_target, look_back, train_main)
        X_test, y_test = self.create_dataset(test_target, look_back, test_main)

        X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
        X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

        return X_train, X_test, y_train, y_test

    def get_features(self, dataset, columns):
        """
        :param dataset: pandas dataframe
        :param columns: list of name columns
        :return: dict of features vectors
        """

        if type(columns) is not list:
            print('Parameter COLUMNS should be list object')
            raise Exception
        features = {}
        for column in columns:
            feature = dataset.loc[:, column].values
            features[column] = feature
        return features

    def get_scaled_features(self, features):
        """ To get transformed data in [0,1] """

        scaled_features = {}
        scalers_features = {}
        for name in features:
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_features[name] = scaler.fit_transform(features[name].reshape(-1, 1))
            scalers_features[name] = scaler
        return scaled_features, scalers_features

    def build_model(self, loss='mse', optimizer='rmsprop', input_shape=(1, 2), neurons=100, activation='linear'):
        model = Sequential()
        model.add(LSTM(neurons, input_shape=input_shape, return_sequences=True))
        model.add(LSTM(neurons, return_sequences=False))
        model.add(Dense(output_dim=1))
        model.add(Activation(activation=activation))
        model.compile(loss=loss, optimizer=optimizer)
        return model

    def get_split_features(self, features, train_size):
        train_main = []
        test_main = []
        for name in features:
            train_main.append(features[name][0:train_size, :])
            test_main.append(features[name][train_size:len(features[name]), :])
        return train_main, test_main
