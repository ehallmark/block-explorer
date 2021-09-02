from dotenv import load_dotenv
import os

env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

if os.path.isfile(env_file):
    load_dotenv(env_file)


BSCSCAN_API_KEY = os.environ.get('BSCSCAN_API_KEY')
ETHERSCAN_API_KEY = os.environ.get('ETHERSCAN_API_KEY')
POLYGONSCAN_API_KEY = os.environ.get('POLYGONSCAN_API_KEY')
ACCOUNT_ID = os.environ['ACCOUNT_ID']
DATABASE_URL = os.environ['DATABASE_URL']
