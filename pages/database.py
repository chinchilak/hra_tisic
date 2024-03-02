import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

DB_NAME = "./games.db"
TBL_NAME = "games"

def create_connection():
    return sqlite3.connect(DB_NAME)

def close_connection(conn):
    conn.close()

def create_table():
    conn = create_connection()
    with conn:
        conn.execute(f"""CREATE TABLE IF NOT EXISTS {TBL_NAME} (
                        Date DATE,
                        Round INTEGER,
                        Player TEXT,
                        Value INTEGER
                        )""")

def delete_table_data():
    conn = create_connection()
    c = conn.cursor()
    c.execute('DELETE FROM your_table')
    conn.commit()
    conn.close()

def save_game(conn, df):
    df.to_sql(TBL_NAME, conn, if_exists="append", index=False)

def view_data(conn):
    query = f"SELECT * FROM {TBL_NAME}"
    data = pd.read_sql(query, conn)
    st.write(data)

def view_unique_dates():
    conn = create_connection()
    query = f"SELECT DISTINCT Date FROM {TBL_NAME}"
    unique_dates = pd.read_sql(query, conn)
    return unique_dates

def get_data_by_date(selected_date):
    conn = create_connection()
    query = f"SELECT * FROM {TBL_NAME} WHERE Date = '{selected_date}'"
    data = pd.read_sql(query, conn)
    data.drop(columns=["Date"], inplace=True)
    return data

sel = st.selectbox("Games by date", view_unique_dates())
df = get_data_by_date(sel)

cols = st.columns([1,9])

with cols[0]:
    st.dataframe(df)

with cols[1]:
    line_chart = alt.Chart(df).mark_line().encode(
        x=alt.X('Round:O', axis=alt.Axis(title='Kolo', labelAngle=0), scale=alt.Scale(padding=0.05)),
        y=alt.Y('Value:Q', axis=alt.Axis(title='Hodnota'), scale=alt.Scale(padding=0.05)),
        color=alt.Color('Player:N', legend=alt.Legend(title='Hráči')))

    points = line_chart.mark_point(
        filled=True,
        size=100
    ).encode(
        x='Round:O',
        y='Value:Q',
        color=alt.Color('Player:N', legend=None)
    )

    text = line_chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-10,
        fontSize=18,
        fontWeight='bold'
    ).encode(
        text='Value:Q'
    )

    chart_with_elements = (line_chart + points + text).configure_axis(grid=False).configure_legend(orient='right')
    st.altair_chart(chart_with_elements, theme="streamlit", use_container_width=True)
