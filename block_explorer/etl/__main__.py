import requests
from common.config import BSCSCAN_API_KEY, ETHERSCAN_API_KEY, POLYGONSCAN_API_KEY, ACCOUNT_ID, DATABASE_URL
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List, Union
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import time


ETHERSCAN_URL = 'https://api.etherscan.io/api'
BSCSCAN_URL = 'https://api.bscscan.com/api'
POLYGONSCAN_URL = 'https://api.polygonscan.com/api'


def extract(last_block: int, url: str, key: str, symbol: str) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    transactions_url = f"{url}?module=account&action=txlist&address={ACCOUNT_ID}&startblock={last_block}&sort=asc&apikey={key}"
    transfers_url = f"{url}?module=account&action=tokentx&address={ACCOUNT_ID}&startblock={last_block}&sort=asc&apikey={key}"
    balance_url = f"{url}?module=account&action=balance&address={ACCOUNT_ID}&tag=latest&apikey={key}"
    last_price_url = f"{url}?module=stats&action={symbol.lower()}price&apikey={key}"
    return requests.get(transactions_url).json(), \
           requests.get(transfers_url).json(), \
           requests.get(balance_url).json(), \
           requests.get(last_price_url).json()


def transform(data: Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]) -> List[Union[pd.DataFrame, float]]:
    price_key = [k for k in data[3]['result'].keys() if k.endswith('usd')][0]
    return [
        pd.DataFrame(data=data[0]['result']),
        pd.DataFrame(data=data[1]['result']),
        float(data[2]['result']) / (10**18),
        float(data[3]['result'][price_key]),
    ]


def load(transformed_data: List[Union[pd.DataFrame, float]], engine: Engine, network: str) -> Tuple[Optional[int], float, float]:
    latest_blocks = []
    if len(transformed_data[0]) > 0:
        transformed_data[0].set_index('hash', inplace=True)
        transformed_data[0]['network'] = [network for _ in range(transformed_data[0].shape[0])]
        transformed_data[0].to_sql(
            name='transactions',
            con=engine,
            index=True,
            index_label='hash',
            chunksize=1,
            if_exists='append',
            method='multi',
        )
        latest_blocks.append(int(transformed_data[0][['blockNumber']].astype(int).max()['blockNumber']))

    if len(transformed_data[1]) > 0:
        transformed_data[1].set_index('hash', inplace=True)
        transformed_data[1]['network'] = [network for _ in range(transformed_data[1].shape[0])]
        transformed_data[1].to_sql(
            name='transfers',
            con=engine,
            index=True,
            index_label='hash',
            chunksize=1,
            if_exists='append',
            method='multi',
        )
        latest_blocks.append(int(transformed_data[1][['blockNumber']].astype(int).max()['blockNumber']))

    if len(latest_blocks) == 0:
        return None, transformed_data[2], transformed_data[3]
    else:
        return max(latest_blocks), transformed_data[2], transformed_data[3]


def set_last_block(block: Optional[int], engine: Engine, network: str):
    if block is None:
        return
    pd.DataFrame(data=[{'block': block}]).to_sql(
        name=f'last_block_{network}',
        con=engine,
        index=True,
        chunksize=1,
        if_exists='replace',
        method='multi',
    )


def get_last_block(engine: Engine, network: str) -> int:
    try:
        return int(pd.read_sql_table(
            table_name=f'last_block_{network}',
            con=engine,
        ).set_index('index', drop=True).values.tolist()[0][0])
    except Exception as e:
        # First run
        print(e)
        return 1


def set_current_balance(network: str, balance: float, engine: Engine):
    engine.execute("create table if not exists balances(network text primary key, amount double precision not null);")
    engine.execute(f"insert into balances (network, amount) values ('{network}', {balance}) on conflict (network) do update set amount=excluded.amount;")


def set_current_price(network: str, price: float, engine: Engine):
    engine.execute("create table if not exists prices(network text primary key, price double precision not null);")
    engine.execute(f"insert into prices (network, price) values ('{network}', {price}) on conflict (network) do update set price=excluded.price;")


if __name__ == '__main__':
    network_map = {
        'ethereum': (ETHERSCAN_URL, ETHERSCAN_API_KEY, 'eth'),
        'bsc': (BSCSCAN_URL, BSCSCAN_API_KEY, 'bnb'),
        'polygon': (POLYGONSCAN_URL, POLYGONSCAN_API_KEY, 'matic'),
    }
    sql_engine = create_engine(DATABASE_URL)

    for network, network_info in network_map.items():
        print('Pulling {} data'.format(network))
        last_block = get_last_block(sql_engine, network)
        print('Starting from block %s' % last_block)
        new_last_block, balance, price = load(transform(extract(last_block + 1, *network_info)), sql_engine, network)
        print('Reached block %s' % new_last_block)
        set_last_block(new_last_block, sql_engine, network)
        set_current_balance(network, balance, sql_engine)
        set_current_price(network, price, sql_engine)
        time.sleep(1)

    sql_engine.dispose()
