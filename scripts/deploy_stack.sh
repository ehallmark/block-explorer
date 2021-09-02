

source block_explorer/.env

export TF_VAR_sql_password="$SQL_PASSWORD"
export TF_VAR_bscscan_api_key="$BSCSCAN_API_KEY"
export TF_VAR_etherscan_api_key="$ETHERSCAN_API_KEY"
export TF_VAR_polygonscan_api_key="$POLYGONSCAN_API_KEY"
export TF_VAR_account_id="$ACCOUNT_ID"

cd terraform/

terraform init
terraform apply

cd ../