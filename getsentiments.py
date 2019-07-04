import logging
import settings
import dbwork
import re
import tweepy
import pandas as pd

from textblob import TextBlob

def clean_text(text):
    '''
    Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text.lower()).split())


def get_polarity(text):
    # run polarity analysis on tweets

    text = clean_text(text)
    analysis = TextBlob(text)

    return analysis.sentiment.polarity


class TwitterData:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, name_db):
        self.db = dbwork.DataBase(name_db)
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

    def check_theme(self, text):

        for theme in settings.KEYWORDS_THEMES:
            if re.search(theme, text) is not None:
                return True
        return False

    def get_historical_tweets(self, accounts_names):
        """ Get historical tweets 3240 for one account
            Twitter only allows access to a users most recent 3240 tweets with this method
        """

        # authorize twitter, initialize tweepy
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth)
        outtweets = []
        for screen_name in accounts_names:
            alltweets = []
            new_tweets = api.user_timeline(screen_name=screen_name, count=200)
            alltweets.extend(new_tweets)

            oldest = alltweets[-1].id - 1
            while len(new_tweets) > 0:
                print("getting tweets before %s" % (oldest))
                new_tweets = api.user_timeline(screen_name=screen_name, count=400, max_id=oldest)
                alltweets.extend(new_tweets)
                oldest = alltweets[-1].id - 1
                print("...%s tweets downloaded so far" % (len(alltweets)))

            for tweet in alltweets:
                if self.check_theme(tweet.text):
                    outtweets.append((tweet.created_at.strftime('%Y-%m-%d'), get_polarity(tweet.text)))

        labels = ['date', 'polarity']
        df_tweets = pd.DataFrame.from_records(outtweets, columns=labels)

        df_tweets.to_sql(settings.NAME_TABLE_SENT_DATA, self.db.engine, if_exists='replace', index=False)

    def get_last_tweets(self, accounts_names):
        logger = logging.getLogger('App.getsent.get_last_tws')

        try:
            auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            api = tweepy.API(auth)
        except Exception as e:
            logger.exception(e)
            logger.error('Authentication with Twitter has not been done.')

        logger.info('Authentication successful!')
        try:
            outtweets = []
            for screen_name in accounts_names:
                alltweets = []
                new_tweets = api.user_timeline(screen_name=screen_name, count=200)
                alltweets.extend(new_tweets)

                for tweet in alltweets:
                    if self.check_theme(tweet.text):
                        outtweets.append((tweet.created_at.strftime('%Y-%m-%d'), get_polarity(tweet.text)))
        except Exception as e:
            logger.exception(e)
            logger.error('Getting tweets and polarization has not been finished!')

        logger.info('Getting tweets and polarization successful!')

        try:
            labels = ['date', 'polarity']
            df_tweets = pd.DataFrame.from_records(outtweets, columns=labels)
            df_tweets = df_tweets.sort_values(['date'])
            last_date = self.db.get_last_sent(settings.NAME_TABLE_SENT_DATA)[0][0]

            df_tweets = df_tweets.loc[df_tweets['date'] > last_date]
            df_tweets.to_sql(settings.NAME_TABLE_SENT_DATA, self.db.engine, if_exists='append', index=False)
        except Exception as e:
            logger.exception(e)
            logger.error('Data sentiments can not download to DB')

        logger.info('Data sentiments has been loaded.')



def update_sentiment_data():
    tw_data = TwitterData(settings.CONSUMER_KEY, settings.CONSUMER_SECRET,
                          settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET,
                          settings.NAME_DATABASE)
    tw_data.get_last_tweets(settings.NAMES_TWITTERS)


if __name__ == '__main__':
    update_sentiment_data()
