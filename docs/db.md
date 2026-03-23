# Documentation for `projects/shared/db.py`

## Functions

### `get_connection`
Returns a connection to the PostgreSQL database.
Expects environment variables to be set, or defaults to a local dev setup.

### `init_db`
Initializes the database schema if it doesn't exist.

### `save_q_values`
Saves a dictionary of {(state, action): q_value} to the database.
Uses UPSERT to update existing records.

### `load_q_values`
Loads the Q-table from the database into a dictionary.
Returns: dict mapping (state, action) to q_value.

### `record_match`
Records a match result to the database.
