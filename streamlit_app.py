from collections import defaultdict
from pathlib import Path
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="SLVM - INVITATIONAL",
    page_icon=":golf:", 
)


# -----------------------------------------------------------------------------
# Declare some useful functions.


def connect_db():
    """Connects to the sqlite database."""

    DB_FILENAME = Path(__file__).parent / "resultats.db"
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created


def initialize_data(conn):
    """Initializes the results table with some data."""
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS resultats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dia TEXT NOT NULL,
            jugador1 TEXT NOT NULL,
            punts1 INTEGER NOT NULL,
            jugador2 TEXT NOT NULL,
            punts2 INTEGER NOT NULL,
            jugador3 TEXT,
            punts3 INTEGER,
            jugador4 TEXT,
            punts4 INTEGER
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO resultats
            (id, dia, jugador1, punts1, jugador2, punts2, jugador3, punts3, jugador4, punts4)
        VALUES
            -- Beverages
            (0, "15-03-2025", "Aina", 2, "Pep", 0, NULL, NULL, NULL, NULL)
            """
    )
    conn.commit()


def load_data(conn):
    """Loads the results data from the database."""
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM resultats")
        data = cursor.fetchall()
    except:
        return None

    df = pd.DataFrame(
        data,
        columns=[
            "id",
            "dia",
            "jugador 1",
            "punts 1",
            "jugador 2",
            "punts 2",
            "jugador 3",
            "punts 3",
            "jugador 4",
            "punts 4"
        ],
    )

    df['dia'] = pd.to_datetime(df['dia'])

    return df


def update_data(conn, df, changes):
    """Updates the results data in the database."""
    cursor = conn.cursor()

    if changes["edited_rows"]:
        deltas = st.session_state.results_table["edited_rows"]
        rows = []

        for i, delta in deltas.items():
            row_dict = df.iloc[i].to_dict()
            row_dict.update(delta)
            rows.append(row_dict)

        cursor.executemany(
            """
            UPDATE resultats
            SET
                dia = :dia,
                jugador1 = :jugador1,
                punts1 = :punts1,
                jugador2 = :jugador2,
                punts2 = :punts2,
                jugador3 = :jugador3,
                punts3 = :punts3,
                jugador4 = :jugador4,
                punts4 = :punts4,
            WHERE id = :id
            """,
            rows,
        )

    if changes["added_rows"]:
        cursor.executemany(
            """
            INSERT INTO resultats
                (id, dia, jugador1, punts1, jugador2, punts2, jugador3, punts3, jugador4, punts4)
            VALUES
                (:id, :dia, :jugador1, :punts1, :jugador2, :punts2, :jugador3, :punts3, :jugador4, :punts4)
            """,
            (defaultdict(lambda: None, row) for row in changes["added_rows"]),
        )

    if changes["deleted_rows"]:
        cursor.executemany(
            "DELETE FROM resultats WHERE id = :id",
            ({"id": int(df.loc[i, "id"])} for i in changes["deleted_rows"]),
        )

    conn.commit()


# -----------------------------------------------------------------------------
# Draw the actual page, starting with the inventory table.

# Set the title that appears at the top of the page.
"""
# :golf: SLVM - Invitational 🏌🏽🏌🏽‍♂️


**Benvinguts a la web oficial de la lliga SLVM - Invitational!**

"""
st.info(
    """
    Utilitza la taula següent per afegir, eliminar i editar els resultats.
    No oblidis de guardar els resultats quan hagis acabat.
    """
)

# Connect to database and create table if needed
conn, db_was_just_created = connect_db()

# Initialize data.
if db_was_just_created:
    initialize_data(conn)
    st.toast("Database initialized with some sample data.")

# Load data from database
df = load_data(conn)

# Display data with editable table
edited_df = st.data_editor(
    df,
    disabled=["id"],  # Don't allow editing the 'id' column.
    num_rows="dynamic",  # Allow appending/deleting rows.
    column_config={
        # Show dollar sign before price columns.
        "dia": st.column_config.DateColumn(format="DD-MM-YYYY"),
    },
    key="results_table",
)

has_uncommitted_changes = any(len(v) for v in st.session_state.results_table.values())

st.button(
    "Commit changes",
    type="primary",
    disabled=not has_uncommitted_changes,
    # Update data in database
    on_click=update_data,
    args=(conn, df, st.session_state.results_table),
)


# -----------------------------------------------------------------------------
# Now some cool charts

# Add some space
""
""
""

st.subheader("Resultats", divider="red")




# # -----------------------------------------------------------------------------


