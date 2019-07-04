from datetime import datetime
import logging
import getsentiments
import getpoloticker
import contact
import settings
import model
import functions
import toemail
import emoji


def app():
    logging.basicConfig(filename=settings.NAME_LOG_FILE,
                        level=logging.INFO,
                        filemode='a',
                        format='%(asctime)s - %(threadName)10s -  %(levelname)8s - %(name)30s  - %(message)s')

    logger = logging.getLogger('App')
    logger.setLevel(logging.INFO)

    bot = contact.TBotNotify(settings.BOT_TOKEN)

    logger.info('App ----------------------------------> STARTED!')

    # ------------------------------ Update_data -----------------------------------------------------------

    getpoloticker.get_btc_data('USDT_BTC', date_from=(2015, 9, 1), name_table=settings.NAME_TABLE_BTC_DATA)
    logger.info('Update bitcoin data finished!')
    getsentiments.update_sentiment_data()
    logger.info('Update sentim data finished!')

    # ------------------------------ Getting prediction price ----------------------------------------------

    predict_price, mae, predict_price_plot, data = model.make_prediction()
    logger.info('Prediction has been finished!')

    # ------------------------------ Notify clients -------------------------------------------------------

    data['predict'] = predict_price_plot
    data_new = data[['date', 'close', 'predict']]
    data_new.iloc[-settings.SINCE_DAYS:].to_excel('predict_table.xlsx')
    functions.create_pic_plot(data_new.iloc[-settings.SINCE_DAYS:], 'plot.png')

    logger.info('Creating picture has been finished!')

    now_date = datetime.today().strftime('%Y-%m-%d')

    diff = predict_price[-1] - predict_price[-2]
    if diff > 0:
        decision = 'Buy'
        emo = ':chart_with_upwards_trend:'
    elif diff < 0:
        decision = 'Sell'
        emo = ':chart_with_downwards_trend:'
    else:
        decision = "I can't define direction"
        emo = ':question:'

    # message = (emoji.emojize(':date:', use_aliases=True) + 'DATE: %s \n' +
    #            emoji.emojize(':dollar:', use_aliases=True) + 'PREDICTION: %f \n' +
    #            emoji.emojize(':x:', use_aliases=True) + 'MA ERROR: %f  \n' +
    #            emoji.emojize('%s' % emo, use_aliases=True) + 'DECISION: %s') % (
    #               now_date, predict_price[-1], mae, decision)
    message = ' '.join([now_date, str(data_new.close.iloc[-1]), str(predict_price[-1][0])])

    toemail.send_email(message)
    logger.info('Email have sent successfully!')

    bot.send_message(message)
    logger.info('Telegram message have sent successfully!')

    # bot.send_plot('plot.png')
    # logger.info('Telegram plot have sent successfully!')

    logger.info('App ----------------------------------> FINISHED!')


if __name__ == '__main__':
    app()
