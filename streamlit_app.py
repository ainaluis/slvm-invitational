from collections import defaultdict
from pathlib import Path
import sqlite3
from io import BytesIO
from PIL import Image

import streamlit as st
import altair as alt
import pandas as pd


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="SLVM - INVITATIONAL",
    page_icon=":golf:", 
    layout="wide"
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

def obtain_image_object_from_path(path):
    with open(path, 'rb') as file:
        return file.read()

def obtain_image_from_image_object(image_object):
    return Image.open(BytesIO(image_blob))


def initialize_data(conn):
    """Initializes the results table with some data."""
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jugadors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            handicap_1 REAL,
            handicap_actual REAL,
            handicap_joc INTEGER,
            imatge BLOB
        )
        """
    )

    carlos = obtain_image_object_from_path("/workspaces/slvm-invitational/carlosvillaseca.jpg")
    pol = obtain_image_object_from_path("/workspaces/slvm-invitational/polsoler.png")
    uri = obtain_image_object_from_path("/workspaces/slvm-invitational/oriolluis.jpg")
    pep = obtain_image_object_from_path("/workspaces/slvm-invitational/pepluis.jpeg")
    toni = obtain_image_object_from_path("/workspaces/slvm-invitational/toniluis.jpg")
    ramon = obtain_image_object_from_path("/workspaces/slvm-invitational/ramonmiret.jpg")
    jordi = obtain_image_object_from_path("/workspaces/slvm-invitational/jordisoler.png")
    alex = obtain_image_object_from_path("/workspaces/slvm-invitational/alexmiret.png")


    cursor.execute(
        """
        INSERT INTO jugadors
            (nom, handicap_1, handicap_actual, handicap_joc, imatge)
        VALUES
            ("Carlos Villaseca", 12.1, 12.0, 12, ?),
            ("Pol Soler", 21.7, 21.7, 24, ?),
            ("Ramon Miret", 25.5, 25.5, 28, ?),
            ("Pep Luis", 7.9, 7.1, 6, ?),
            ("Toni Luis", 17.9, 17.6, 19, ?),
            ("Jordi Soler", 26.5, 26.5, 29, ?),
            ("Oriol Luis", 1.0, 1.0, -1, ?),
            ("Alex Miret", 42.0, 42.0, 38, ?)
        """, (carlos, pol, ramon, pep, toni, jordi, uri, alex)
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS resultats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dia TEXT,
            jugador1 TEXT,
            punts1 INTEGER,
            jugador2 TEXT,
            punts2 INTEGER,
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
            (dia, jugador1, punts1, jugador2, punts2, jugador3, punts3, jugador4, punts4)
        VALUES
            ("2025-03-15", "Aina", 2, "Pep", 0, NULL, NULL, NULL, NULL)
            """
    )
    conn.commit()

def load_data_jugadors(conn):
    """Loads the players data from the database."""
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM jugadors")
        data = cursor.fetchall()
    except:
        return None

    df = pd.DataFrame(
        data,
        columns=[
            "id",
            "nom",
            "handicap_1",
            "handicap_actual",
            "handicap_joc",
            "imatge"
        ],
    )
    return df

def load_data_results(conn):
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
            "jugador1",
            "punts1",
            "jugador2",
            "punts2",
            "jugador3",
            "punts3",
            "jugador4",
            "punts4"
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
                (dia, jugador1, punts1, jugador2, punts2, jugador3, punts3, jugador4, punts4)
            VALUES
                (:dia, :jugador1, :punts1, :jugador2, :punts2, :jugador3, :punts3, :jugador4, :punts4)
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
# Draw the actual page.

"""
# :golf: SLVM - Invitational 🏌🏽🏌🏽‍♂️


**Benvinguts a la web oficial de la lliga SLVM - Invitational!**

"""
# Connect to database and create table if needed
conn, db_was_just_created = connect_db()

# Initialize data.
if db_was_just_created:
    initialize_data(conn)
    st.toast("Database initialized with some sample data.")


def image_to_blob(image_path):
    with open(image_path, 'rb') as file:
        return file.read()


tabs = st.tabs(["Jugadors", "Classificació i Estadístiques", "Recull de tots els resultats"])

# --------------------------------------------------
with tabs[0]:
    jugadors = load_data_jugadors(conn)
    columns = st.columns([1, 1])
    for index, row in jugadors.iterrows():
        id_column = index%2
        with columns[id_column]:
            st.markdown(f"#### **{row['nom']}**")
            col1, col2 = st.columns([1, 3]) 

            with col1:
                st.image(row["imatge"], caption='', use_container_width=True)

            with col2:
                st.write(f"Handicap 01/01/2025: {row['handicap_1']}")
                st.write(f"Handicap actual: {row['handicap_actual']}")
                st.write(f"Handicap de joc: {row['handicap_joc']}")

        st.markdown("---")
# --------------------------------------------------
with tabs[1]:
    st.write("Estaístiques")

    ""
    ""
    ""

    st.subheader("Resultats", divider="red")





# --------------------------------------------------
with tabs[2]:
    st.info(
        """
        Utilitza la taula següent per afegir, eliminar i editar els resultats.
        No oblidis de guardar els resultats quan hagis acabat.
        """
    )

    # Load data from database
    df = load_data_results(conn)

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
        "Guarda els canvis",
        type="primary",
        disabled=not has_uncommitted_changes,
        # Update data in database
        on_click=update_data,
        args=(conn, df, st.session_state.results_table),
    )

