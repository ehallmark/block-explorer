import pandas as pd
from sqlalchemy import create_engine
from common.config import DATABASE_URL, ACCOUNT_ID
import json
from typing import Dict, Any
from datetime import datetime


NETWORKS = {
    'ethereum': 'ETH',
    'bsc': 'BNB',
    'polygon': 'MATIC'
}


def load_data() -> Dict[str, Any]:
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql_table(
        table_name='transfers',
        con=engine,
    ).set_index('hash')

    balances = pd.read_sql_table(
        table_name='balances',
        con=engine,
    ).set_index('network')

    prices = pd.read_sql_table(
        table_name='prices',
        con=engine,
    ).set_index('network')

    engine.dispose()

    network_dfs = df.groupby('network')
    data = {}
    for network, symbol in NETWORKS.items():
        network_data = {}
        data[network] = network_data
        tokens_acquired = {}
        tokens_sold = {}
        network_data['symbol'] = symbol
        network_data['acquired'] = tokens_acquired
        network_data['sold'] = tokens_sold
        network_data['amount'] = balances.loc[network]['amount']
        network_data['price'] = prices.loc[network]['price']
        group_df = network_dfs.get_group(network)
        network_data['totalGasUsed'] = group_df[['gasUsed']].astype(float).sum()['gasUsed']
        deposits = group_df[group_df.to == ACCOUNT_ID.lower()]
        withdrawals = group_df[group_df['from'] == ACCOUNT_ID.lower()]
        network_data['numDeposits'] = deposits.shape[0]
        network_data['numWithdrawals'] = withdrawals.shape[0]
        network_data['depositsValue'] = deposits[['value']].astype(float).sum()['value']
        network_data['withdrawalsValue'] = withdrawals[['value']].astype(float).sum()['value']

        deposited_tokens_df = deposits.groupby('tokenSymbol')
        withdrawn_tokens_df = withdrawals.groupby('tokenSymbol')

        timestamps = group_df['timeStamp'].astype(int).tolist()
        transaction_dates = {}
        for timestamp in timestamps:
            date = str(datetime.fromtimestamp(timestamp).date())
            if date not in transaction_dates:
                transaction_dates[date] = 0
            transaction_dates[date] += 1

        for token in deposited_tokens_df.groups.keys():
            token_df = deposited_tokens_df.get_group(token)
            decimals = token_df[['tokenDecimal']].astype(int).tokenDecimal.values.tolist()[0]
            tokens_acquired[token] = token_df[['value']].astype(float).sum()['value']/(10**decimals)

        for token in withdrawn_tokens_df.groups.keys():
            token_df = withdrawn_tokens_df.get_group(token)
            decimals = token_df[['tokenDecimal']].astype(int).tokenDecimal.values.tolist()[0]
            tokens_sold[token] = token_df[['value']].astype(float).sum()['value'] / (10 ** decimals)

        net_balances = {
            symbol: network_data['amount']
        }
        network_data['balance'] = net_balances
        for token, amount in tokens_acquired.items():
            net_balances[token] = amount - tokens_sold.get(token, 0)

        tokens = sorted(list(net_balances.keys()), key=lambda x: net_balances[x], reverse=True)
        network_data['tokenChart'] = json.dumps({
          'type': 'bar',
          'data': {
              'labels': tokens,
              'datasets': [{
                'label': 'Current Balance',
                'data': [net_balances[t] for t in tokens],
                'borderWidth': 1
              }]
            },
            'options': {
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Token Quantities'
                    }
                }
            }
        })

        dates = sorted(list(transaction_dates.keys()))
        network_data['txnTimeline'] = json.dumps({
          'type': 'line',
          'data': {
              'labels': dates,
              'datasets': [{
                'label': 'Number of Transactions',
                'data': [transaction_dates[date] for date in dates],
                'borderWidth': 1
              }]
            },
            'options': {
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Transaction Timeline'
                    }
                }
            }
        })

    return data


