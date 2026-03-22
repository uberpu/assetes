import os
import psycopg2
from psycopg2.extras import DictCursor

def get_connection():
    """
    Returns a connection to the PostgreSQL database.
    Expects environment variables to be set, or defaults to a local dev setup.
    """
    conn = psycopg2.connect(
        host=os.environ.get('PGHOST', 'localhost'),
        database=os.environ.get('PGDATABASE', 'postgres'),
        user=os.environ.get('PGUSER', 'postgres'),
        password=os.environ.get('PGPASSWORD', 'postgres'),
        port=os.environ.get('PGPORT', '5432')
    )
    return conn

def init_db():
    """
    Initializes the database schema if it doesn't exist.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Create Q-table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS q_table (
                    state VARCHAR(9) NOT NULL,
                    action INTEGER NOT NULL,
                    q_value FLOAT NOT NULL,
                    PRIMARY KEY (state, action)
                )
            ''')

            # Create Match Results table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS match_results (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    agent_x VARCHAR(50) NOT NULL,
                    agent_o VARCHAR(50) NOT NULL,
                    winner VARCHAR(1),
                    total_moves INTEGER NOT NULL
                )
            ''')
        conn.commit()
    finally:
        conn.close()

def save_q_values(q_dict):
    """
    Saves a dictionary of {(state, action): q_value} to the database.
    Uses UPSERT to update existing records.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for (state, action), q_value in q_dict.items():
                cur.execute('''
                    INSERT INTO q_table (state, action, q_value)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (state, action)
                    DO UPDATE SET q_value = EXCLUDED.q_value
                ''', (state, action, q_value))
        conn.commit()
    finally:
        conn.close()

def load_q_values():
    """
    Loads the Q-table from the database into a dictionary.
    Returns: dict mapping (state, action) to q_value.
    """
    conn = get_connection()
    q_dict = {}
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT state, action, q_value FROM q_table")
            for row in cur.fetchall():
                q_dict[(row['state'], row['action'])] = row['q_value']
    except psycopg2.errors.UndefinedTable:
        # Table might not exist yet
        pass
    finally:
        conn.close()
    return q_dict

def record_match(agent_x, agent_o, winner, total_moves):
    """
    Records a match result to the database.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO match_results (agent_x, agent_o, winner, total_moves)
                VALUES (%s, %s, %s, %s)
            ''', (agent_x, agent_o, winner, total_moves))
        conn.commit()
    finally:
        conn.close()
