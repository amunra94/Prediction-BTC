import logging
import csv
import pandas as pd
import settings
import dbwork

from poloniex import Poloniex
from datetime import datetime




def get_polo_data2csv(currency_pair, period=86400, date_from=(2015, 1, 1), name_fout='bitcoin_data.csv'):
    date_from_utc = datetime(year=date_from[0], month=date_from[1], day=date_from[2]).timestamp()
    polo = Poloniex()
    data = polo.returnChartData(currency_pair, period, start=date_from_utc, end=9999999999)

    with open(name_fout, 'w', newline='') as fout:
        fields = tuple(data[0].keys())
        writer = csv.writer(fout)
        writer.writerow(fields)

        for row in data:
            values = list(row.values())
            values[0] = datetime.utcfromtimestamp(values[0]).strftime('%Y-%m-%d')
            writer.writerow(values)


def get_btc_data(currency_pair, period=86400, date_from=(2015, 1, 1), name_table='btc_data'):
    logger = logging.getLogger('App.getpolo.get_btc_data')

    try:
        date_from_utc = datetime(year=date_from[0], month=date_from[1], day=date_from[2]).timestamp()
        polo = Poloniex()
        data = polo.returnChartData(currency_pair, period, start=date_from_utc, end=9999999999)
    except Exception as e:
        logger.error('Getting bitcoin data from Poloniex!')

    logger.info('Data from Poloniex has been received!')

    fields = tuple(data[0].keys())
    rows = []

    for row in data:
        values = []
        for field in fields:
            if field == 'date':
                values.append(datetime.utcfromtimestamp(row[field]).strftime('%Y-%m-%d'))
            else:
                values.append(row[field])
        rows.append(values)

    df_data = pd.DataFrame.from_records(rows, columns=fields)
    db = dbwork.DataBase(settings.NAME_DATABASE)
    df_data.to_sql(name_table, db.engine, index=False, if_exists='replace')
    logger.info('Data BTC has been loaded into DATABASE.')


if __name__ == '__main__':
    get_btc_data('USDT_BTC', date_from=(2015, 9, 1), name_table=settings.NAME_TABLE_BTC_DATA)
