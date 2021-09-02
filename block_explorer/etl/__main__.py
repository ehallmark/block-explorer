import requests
from common.config import BSCSCAN_API_KEY, ETHERSCAN_API_KEY, POLYGONSCAN_API_KEY, ACCOUNT_ID, DATABASE_URL
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import time


ETHERSCAN_URL = 'https://api.etherscan.io/api'
BSCSCAN_URL = 'https://api.bscscan.com/api'
POLYGONSCAN_URL = 'https://api.polygonscan.com/api'


def extract(last_block: int, url: str, key: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    transactions_url = f"{url}?module=account&action=txlist&address={ACCOUNT_ID}&startblock={last_block}&sort=asc&apikey={key}"
    transfers_url = f"{url}?module=account&action=tokentx&address={ACCOUNT_ID}&startblock={last_block}&sort=asc&apikey={key}"
    return requests.get(transactions_url).json(), requests.get(transfers_url).json()


def transform(data: Tuple[Dict[str, Any], Dict[str, Any]]) -> List[pd.DataFrame]:
    return [pd.DataFrame(
        data=d['result']
    ) for d in data]


def load(transformed_data: pd.DataFrame, engine: Engine, network: str) -> Optional[int]:
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
        return None
    else:
        return max(latest_blocks)


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


if __name__ == '__main__':
    network_map = {
        'ethereum': (ETHERSCAN_URL, ETHERSCAN_API_KEY),
        'bsc': (BSCSCAN_URL, BSCSCAN_API_KEY),
        'polygon': (POLYGONSCAN_URL, POLYGONSCAN_API_KEY),
    }
    sql_engine = create_engine(DATABASE_URL)

    for network, network_info in network_map.items():
        print('Pulling {} data'.format(network))
        last_block = get_last_block(sql_engine, network)
        print('Starting from block %s' % last_block)
        new_last_block = load(transform(extract(last_block + 1, *network_info)), sql_engine, network)
        print('Reached block %s' % new_last_block)
        set_last_block(new_last_block, sql_engine, network)
        time.sleep(1)

    sql_engine.dispose()
