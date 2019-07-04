"""
This module is core of prediction system.

"""
import numpy as np
import functions
import settings
import logging
from sklearn.metrics import mean_absolute_error



def make_prediction():
    logger = logging.getLogger('App.model.make_prediction')

    core_predict = functions.PredictionCore()

    try:
        # download data from database
        btc_data, sent_data = core_predict.load_data(settings.NAME_DATABASE,
                                                     settings.NAME_TABLE_BTC_DATA,
                                                     settings.NAME_TABLE_SENT_DATA)
        logger.info('Data BTC and SENTIMENTS has been downloaded from DataBase.')

        # merge data btc with sentiments data
        sent_data = sent_data[['date', 'polarity']].groupby(sent_data['date']).mean()
        sent_data = sent_data.reset_index()
        data = btc_data.merge(sent_data, how='left')
        data = data.fillna(0)

        logger.info('Polarity merge to Dataset successfuly!.')

        # transform data to one scale and split data to train and test parts
        X_train, X_test, y_train, y_test = core_predict.prepare_data(data, 'close',
                                                                     ['close', 'volume', 'polarity'],
                                                                     settings.LOOK_BACK)
        logger.info('Data preprocess to look_back successfully.')

        model = core_predict.build_model(loss=settings.LOSS,
                                         optimizer=settings.OPTIMIZER,
                                         input_shape=(1, X_train.shape[2]),
                                         neurons=settings.NEURONS)
        logger.info('Model has been created!')

        model.fit(X_train, y_train,
                  batch_size=settings.BATCH_SIZE,
                  epochs=settings.EPOCHS,
                  validation_data=(X_test, y_test),
                  validation_split=0.1,
                  shuffle=False,
                  verbose=0)

        logger.info('Model has been fit.')

        y_predict_scaled = model.predict(X_test)
        logger.info('Model has made prediction.')

        y_predict = core_predict.scalers_features['close'].inverse_transform(y_predict_scaled.reshape(-1, 1))
        y_test = core_predict.scalers_features['close'].inverse_transform(y_test.reshape(-1, 1))

        # -------------------------------------------- Evaluate error -------------------------
        mae = mean_absolute_error(y_test, y_predict)

        # for creating plot
        y_predict_plot = np.empty_like(data['close'])
        y_predict_plot[:] = np.nan
        y_predict_plot[X_train.shape[0] + (settings.LOOK_BACK * 2):] = y_predict.reshape((y_predict.shape[0],))


        return y_predict, mae, y_predict_plot, data

    except Exception as e:
        logger.exception(e)
        raise SystemExit

if __name__ == '__main__':
    make_prediction()
