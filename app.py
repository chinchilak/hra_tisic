import streamlit as st
import altair as alt
import pandas as pd
import sqlite3
from datetime import datetime

PLAYER = "Player"
DB_NAME = "./games.db"
TBL_NAME = "games"


st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

def save_game(conn, df):
    df.to_sql(TBL_NAME, conn, if_exists="append", index=False)

def add_amount(index, value):
    original_value = st.session_state.running_totals[f"player{index}"]
    updated_value = original_value + int(value)
    st.session_state.running_totals[f"player{index}"] = updated_value
    st.session_state.additions_history[f"additions_history{index}"].append(int(value))
    st.session_state.input_value = 0


def generate_tick_marks_1(min_val, max_val, step_hash):
    marks = ""
    for i in range(min_val + step_hash, max_val, step_hash):
        marks += f"<span style='position:absolute;left:{i / max_val * 100}%;top:25%;transform:translateY(-50%) translateX(-50%) rotate(-90deg);color:#888;font-size:12pt;'>{i}</span>"
    return marks

def generate_tick_marks_2(min_val, max_val, step_hash):
    marks = ""
    for i in range(min_val, max_val + step_hash, step_hash):
        marks += f"<span style='position:absolute;left:{i / max_val * 100}%;top:75%;width:1px;height:10px;background-color:#888;transform:translateX(-50%);'></span>"
    return marks

def remove_last_value(player_index):
    history_key = f"additions_history{player_index}"
    if "additions_history" in st.session_state:
        if history_key in st.session_state["additions_history"]:
            if st.session_state["additions_history"][history_key]:
                value_removed = st.session_state["additions_history"][history_key][-1]
                st.session_state["additions_history"][history_key].pop()
                player_key = f"player{player_index}"
                if player_key in st.session_state["running_totals"]:
                    st.session_state["running_totals"][player_key] -= value_removed
                st.sidebar.success("Last value removed successfully!")
            else:
                st.sidebar.error(f"No values in history for player {player_index}.")
        else:
            st.sidebar.error(f"No history found for player {player_index}.")
    else:
        st.sidebar.error("No history found in session state.")


if 'running_totals' not in st.session_state:
    st.session_state.running_totals = {}

if 'additions_history' not in st.session_state:
    st.session_state.additions_history = {}

if 'input_value' not in st.session_state:
    st.session_state.input_value = 0


with st.sidebar:
    players = st.number_input("Player count", 1, 6, 2, 1)
    maximum = st.number_input("Maximum", 0, 10000, 3000, 500)
    step_hash = st.number_input("Hashmarks", 0, 10000, 100, 50)
    st.divider()
    if st.button("Reset Data"):
        st.session_state.running_totals = {}
        st.session_state.additions_history = {}
        st.session_state.input_value = 0
        for index in range(players):
            st.session_state[f"player{index}"] = 0

min_val = 0
max_val = maximum
step = 50

st.markdown("""
    <style>
    .StyledThumbValue {
        font-size: 18pt;
        top: -120px;
    }
    </style>
    """, unsafe_allow_html=True)


st.write(generate_tick_marks_1(min_val, max_val, step_hash), unsafe_allow_html=True)
st.write(generate_tick_marks_2(min_val, max_val, step_hash), unsafe_allow_html=True)
st.write("")
value = st.slider("inputvalue", min_val, max_val, step=step, format="%d", label_visibility="collapsed", key="input_value")



player_ids = [i for i in range(players)]
running_total = [0] * players

columns = st.columns(players)

for index, player, column in zip(player_ids, range(1, players + 1), columns):
    if f"player{index}" not in st.session_state.running_totals:
        st.session_state.running_totals[f"player{index}"] = 0

    if f"additions_history{index}" not in st.session_state.additions_history:
        st.session_state.additions_history[f"additions_history{index}"] = []
    
    with column:
        colsg = st.columns([2,0.25,2,0.25,2,2])
        
        nm = colsg[0].text_input("Name", f"{PLAYER} {index + 1}", key=f"name{index}", label_visibility="collapsed")

        colsg[2].button("Add", key=f"addbtn{index}", on_click=add_amount, args=(str(index),value), use_container_width=True)
        colsg[4].button("+350", key=f"add350{index}", on_click=add_amount, args=(str(index),350), use_container_width=True)
        colsg[5].button("+1000", key=f"add1000{index}", on_click=add_amount, args=(str(index),1000), use_container_width=True)

        colsg[0].markdown(f"### Score: :green[{st.session_state.running_totals[f'player{index}']}] / :red[{10_000 - int(st.session_state.running_totals[f'player{index}'])}]")
        try:
            colsg[2].markdown(f"#### Average: :blue[{st.session_state.running_totals[f'player{index}'] / len(st.session_state.additions_history.get(f'additions_history{index}')):.1f}]")
        except:
            pass
        try:
            colsg[4].markdown(f"#### Zero: :orange[{st.session_state.additions_history.get(f'additions_history{index}', []).count(0)}]  (:gray[{(st.session_state.additions_history.get(f'additions_history{index}', []).count(0)) / len(st.session_state.additions_history.get(f'additions_history{index}')):.2%}])")
        except:
            pass
        try:
            colsg[5].markdown(f"#### Top: :violet[{max(st.session_state.additions_history.get(f'additions_history{index}', []), default=None)}]")
        except:
            pass


df = pd.DataFrame.from_dict(st.session_state.additions_history, orient='index').T
if not df.empty:
    df.index = df.index + 1
    pids = [pid + 1 for pid in player_ids]
    plys = ["Player "] * len(pids)
    cols = [f"{player}{pid}" for player, pid in zip(plys, pids)]
    df.columns = cols

    df_melted = df.melt(var_name='group', value_name='value', ignore_index=False).reset_index()
else:
    df_melted = pd.DataFrame()

line_chart = alt.Chart(df_melted).mark_line().encode(
    x=alt.X('index:O', axis=alt.Axis(title='Kolo', labelAngle=0), scale=alt.Scale(padding=0.05)),
    y=alt.Y('value:Q', axis=alt.Axis(title='Hodnota'), scale=alt.Scale(padding=0.05)),
    color=alt.Color('group:N', legend=alt.Legend(title='Hráči')))

points = line_chart.mark_point(
    filled=True,
    size=100
).encode(
    x='index:O',
    y='value:Q',
    color=alt.Color('group:N', legend=None)
)

text = line_chart.mark_text(
    align='center',
    baseline='bottom',
    dy=-10,
    fontSize=18,
    fontWeight='bold'
).encode(
    text='value:Q'
)

chart_with_elements = (line_chart + points + text).configure_axis(grid=False).configure_legend(orient='right')
st.altair_chart(chart_with_elements, theme="streamlit", use_container_width=True)


with st.sidebar:
    st.divider()
    opts = [f"{PLAYER} {player_id + 1}" for player_id in player_ids]
    for idx, p in enumerate(opts):
        st.button(f"Remove Last Value for {p}", on_click=remove_last_value, args=(idx,), key=f"plyr{p}")
    st.divider()
    if st.button("Save game"):
        conn = sqlite3.connect(DB_NAME)

        df_db = df_melted
        formatted_datetime = datetime.now().strftime("%Y-%b-%d %H:%M")
        df_db.insert(loc=0, column="Date", value=formatted_datetime)
        df_db.columns = ["Date", "Round", "Player", "Value"]

        try:
            save_game(conn, df_melted)
            st.success("Game saved")
        except:
            st.error("Could not save game")

        conn.close()
