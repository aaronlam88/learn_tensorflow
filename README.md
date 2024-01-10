# LEARN_TENSORFLOW

# Setup
## Database
You will need to setup database with following config:
```json
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'stock',
}
```
Or edit these values in the `stock/config.py`.

Currently, this project is using MySQL database. The schema for database setup can be found in `stock/stock_schema.sql`

## Python
If you prefer `venv` please follow instuction on https://docs.python.org/3/library/venv.html

All the required library can be found in `requirements.txt`. To install run
```bash
pip install -r requirements.txt
```

## AI
On VS Code you can install Cody AI to help with the coding process

# Run
## Data Retrieval
`stock/symbol_retrieval.py` will retrieve all the necessary data for the project.

`stock/symbol_update.py` will update the data in the database with the latest data.
