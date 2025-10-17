import streamlit as st
import pandas as pd
import random
from collections import Counter
import os

# --- Core Logic ---

@st.cache_data # This decorator caches the data, so it's only loaded once.
def analyze_mark_six_data():
    """Reads the CSV, counts number frequencies, and returns the counts."""
    # The file is expected to be in the same directory as the script.
    filepath = 'Mark_Six.csv'
    if not os.path.exists(filepath):
        st.error(f"Error: 'Mark_Six.csv' not found. Please make sure the file is in the same folder as the application.")
        return None
    try:
        df = pd.read_csv(filepath)
        # Analyze only the first 6 columns (main numbers)
        main_numbers_df = df.iloc[:, :6]
        all_numbers = main_numbers_df.values.flatten()
        return Counter(all_numbers)
    except Exception as e:
        st.error(f"Could not read or process the CSV file. Error: {e}")
        return None

def generate_weighted_combinations(number_counts, num_combinations=5, num_per_combo=6):
    """Generates weighted combinations based on past number frequency."""
    if not number_counts: return []
    
    population = list(number_counts.keys())
    weights = list(number_counts.values())
    
    combinations = []
    for _ in range(num_combinations):
        # Generate more than needed to ensure enough unique numbers
        potential_picks = random.choices(population, weights=weights, k=20)
        unique_picks = list(dict.fromkeys(potential_picks)) # Get unique numbers
        
        if len(unique_picks) >= num_per_combo:
            final_combination = sorted(unique_picks[:num_per_combo])
            combinations.append(final_combination)
    return combinations

def generate_banker_combinations(number_counts, bankers, num_combinations=5, num_per_combo=6):
    """Generates combinations with user-selected bankers and weighted legs."""
    legs_needed = num_per_combo - len(bankers)
    if legs_needed <= 0: return []

    # Create a new population for legs by removing the bankers
    leg_population = [num for num in number_counts.keys() if num not in bankers]
    leg_weights = [number_counts[num] for num in leg_population]
    
    combinations = []
    for _ in range(num_combinations):
        potential_legs = random.choices(leg_population, weights=leg_weights, k=15)
        unique_legs = list(dict.fromkeys(potential_legs))
        
        if len(unique_legs) >= legs_needed:
            final_legs = unique_legs[:legs_needed]
            final_combination = sorted(bankers + final_legs)
            combinations.append(final_combination)
        
    return combinations

# --- Streamlit Web App UI ---

st.set_page_config(page_title="Mark Six Analyzer", layout="wide")

st.title("六合彩號碼分析與生成器 (Mark Six Analyzer)")
st.caption("此工具根據歷史數據分析號碼頻率，生成建議組合。僅供娛樂參考。")

# Load the data
number_counts = analyze_mark_six_data()

if number_counts:
    # --- UI Tabs ---
    tab1, tab2 = st.tabs(["**數據分析建議 (Weighted Suggestions)**", "**膽拖選項 (Banker and Legs)**"])

    with tab1:
        st.header("根據歷史數據頻率生成建議組合")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("生成 5 組 **6** 個號碼", use_container_width=True, type="primary"):
                st.session_state.combinations = generate_weighted_combinations(number_counts, 5, 6)
                st.session_state.last_action = ('weighted', 6)
        with col2:
            if st.button("生成 5 組 **7** 個號碼", use_container_width=True, type="secondary"):
                st.session_state.combinations = generate_weighted_combinations(number_counts, 5, 7)
                st.session_state.last_action = ('weighted', 7)

    with tab2:
        st.header("膽拖 (Banker) 建議")
        st.write("請輸入 1-5 個您認為必出的號碼 (膽碼)，程式會根據數據分析補全剩餘的號碼 (腳)。")
        
        banker_input = st.text_input("請輸入膽碼 (以逗號/空格分隔):", placeholder="例如: 8, 15, 22")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("生成 **6** 個號碼的膽拖組合", use_container_width=True, type="primary"):
                try:
                    bankers = [int(n.strip()) for n in banker_input.replace(',', ' ').split() if n.strip()]
                    if not (1 <= len(bankers) <= 5):
                        st.warning("膽碼數量必須介於 1 到 5 之間。")
                    elif len(bankers) != len(set(bankers)):
                        st.warning("膽碼不能包含重覆的數字。")
                    else:
                        st.session_state.combinations = generate_banker_combinations(number_counts, bankers, 5, 6)
                        st.session_state.last_action = ('banker', 6, bankers)
                except ValueError:
                    st.error("輸入無效。請只輸入數字，並以逗號或空格分隔。")

        with col2:
            if st.button("生成 **7** 個號碼的膽拖組合", use_container_width=True, type="secondary"):
                try:
                    bankers = [int(n.strip()) for n in banker_input.replace(',', ' ').split() if n.strip()]
                    if not (1 <= len(bankers) <= 6): # Max 6 bankers for 7 numbers
                        st.warning("膽碼數量必須介於 1 到 6 之間。")
                    elif len(bankers) != len(set(bankers)):
                        st.warning("膽碼不能包含重覆的數字。")
                    else:
                        st.session_state.combinations = generate_banker_combinations(number_counts, bankers, 5, 7)
                        st.session_state.last_action = ('banker', 7, bankers)
                except ValueError:
                    st.error("輸入無效。請只輸入數字，並以逗號或空格分隔。")

    # --- Display Results ---
    if 'combinations' in st.session_state and st.session_state.combinations:
        st.divider()
        results_col, freq_col = st.columns([2, 1])

        with results_col:
            st.subheader("💡 建議組合")
            
            # Display generated combinations
            for i, combo in enumerate(st.session_state.combinations):
                combo_str = ' - '.join(f"{n:02d}" for n in combo)
                st.markdown(f"### <font color='blue'>組 {i+1}:</font> `{combo_str}`", unsafe_allow_html=True)
            
            # Redraw button
            if st.button("重新生成 (Redraw)", use_container_width=True):
                action = st.session_state.get('last_action')
                if action:
                    if action[0] == 'weighted':
                        st.session_state.combinations = generate_weighted_combinations(number_counts, 5, action[1])
                    elif action[0] == 'banker':
                        st.session_state.combinations = generate_banker_combinations(number_counts, action[2], 5, action[1])
                st.rerun()

        with freq_col:
            st.subheader("📊 十大熱門號碼")
            sorted_numbers = sorted(number_counts.items(), key=lambda item: item[1], reverse=True)
            freq_data = []
            for num, count in sorted_numbers[:10]:
                freq_data.append({"號碼 (Number)": int(num), "開出次數 (Frequency)": count})
            st.dataframe(freq_data, use_container_width=True)
