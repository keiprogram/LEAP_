import streamlit as st
import pandas as pd
import numpy as np

# アプリの設定
st.set_page_config(page_title="Enhanced Basic Vocabulary Test", page_icon="English Logo.png")

# カスタムCSSでUIを改善
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f5f5f5;
        color: #333;
    }
    .choices-container button {
        background-color: #6c757d;
        color: white;
        border: 2px solid #6c757d;
        margin: 5px;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        cursor: pointer;
    }
    .choices-container button:hover {
        background-color: #495057;
        color: white;
    }
    .test-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px auto;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .results-table {
        margin: 20px auto;
        border-collapse: collapse;
        width: 100%;
        background-color: white;
        color: #333;
    }
    .results-table th {
        background-color: #6c757d;
        color: white;
        padding: 10px;
    }
    .results-table td {
        border: 1px solid #6c757d;
        padding: 8px;
        text-align: center;
    }
    .stProgress > div > div > div > div {
        background-color: #6c757d;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Excelデータを読み込む関数
@st.cache_data
def load_data():
    file_paths = [
        "リープベーシック見出語・用例リスト(Part 1).xlsx",
        "リープベーシック見出語・用例リスト(Part 2).xlsx",
        "リープベーシック見出語・用例リスト(Part 3).xlsx",
        "リープベーシック見出語・用例リスト(Part 4).xlsx",
    ]
    dataframes = [pd.read_excel(file_path) for file_path in file_paths]
    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df.columns = ['Group', 'No.', '単語', 'CEFR', '語の意味', '用例（英語）', '用例（日本語）']
    return combined_df

words_df = load_data()

# サイドバー設定
st.sidebar.title("テスト設定")
test_type = st.sidebar.radio("テスト形式を選択", ['英語→日本語', '日本語→英語'], key="test_type")

# 単語範囲選択を1〜1400に設定
range_start = st.sidebar.slider("単語範囲（開始）", 1, 1400, 1, step=100)
range_end = st.sidebar.slider("単語範囲（終了）", range_start, 1400, range_start + 100, step=100)

# 選択した範囲に基づいてデータを抽出
filtered_words_df = words_df[(words_df['No.'] >= range_start) & (words_df['No.'] <= range_end)]

# 出題問題数のスライダー（範囲内の単語数に基づく上限を設定）
num_questions = st.sidebar.slider(
    "出題問題数を選択",
    1,
    min(50, len(filtered_words_df)),  # 最大50問または範囲内の単語数の少ない方
    10
)

# テスト開始ボタンの処理
if st.button('テストを開始する'):
    st.session_state.update({
        'test_started': True,
        'correct_answers': 0,
        'current_question': 0,
        'finished': False,
        'wrong_answers': [],
    })

    # ランダムに問題を選択
    selected_questions = filtered_words_df.sample(n=num_questions).reset_index(drop=True)
    st.session_state.update({
        'selected_questions': selected_questions,
        'total_questions': len(selected_questions),
        'current_question_data': selected_questions.iloc[0],
    })

    # 初回の選択肢を生成
    if test_type == '英語→日本語':
        options = list(filtered_words_df['語の意味'].sample(3))
        options.append(st.session_state.current_question_data['語の意味'])
    else:
        options = list(filtered_words_df['単語'].sample(3))
        options.append(st.session_state.current_question_data['単語'])

    np.random.shuffle(options)
    st.session_state.options = options
    st.session_state.answer = None

# その他のロジック（質問表示、結果表示）は元のコードに準じます
