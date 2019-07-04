# Prediction-BTC
Prototype for prediction bitcoin price with using time-series data from Poloniex and news about Bitcoin from Twitter and other resources.

# Architecture

1. Gathering and load data into database SQLite
2. Preprocessing time-series data like price, volume for LSTM-model
3. Preprocessing text data for NLP model
4. Aggregate data from database in dataframe for train and predict
5. Make prediction and sent result to email and telegram bot for clients

# Manage configuration
I create private access for me with telegram bot for running project, getting information about user and much more.


