import streamlit as st
import pandas as pd
import numpy as np

# アプリの設定
st.set_page_config(page_title="Enhanced Basic Vocabulary Test", page_icon='English Logo.png')

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
    dataframes = [pd.read_excel(path) for path in file_paths]
    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df.columns = ['Group', 'No.', '単語', 'CEFR', '語の意味', '用例（英語）', '用例（日本語）']
    return combined_df

words_df = load_data()

# サイドバー設定
st.sidebar.title("テスト設定")
test_type = st.sidebar.radio("テスト形式を選択", ['英語→日本語', '日本語→英語'], key="test_type")

# 単語範囲選択
ranges = [(i, i + 99) for i in range(0, 1401, 100)]
range_labels = [f"{start} - {end}" for start, end in ranges]
selected_range_label = st.sidebar.selectbox("単語範囲を選択", range_labels)
selected_range = ranges[range_labels.index(selected_range_label)]

# 出題問題数の選択
num_questions = st.sidebar.slider("出題問題数を選択", 1, 50, 10)

# サイドバーにリンクボタンを追加
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-top: 20px;">
        <p>こちらのアプリもお試しください</p>
        <a href="https://sisutann-f5r6e9hvuz3ubw5umd6m4i.streamlit.app/" target="_blank" 
        style="background-color: #6c757d; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold;">
        アプリを試す
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# データ抽出
filtered_words_df = words_df[(words_df['No.'] >= selected_range[0]) & (words_df['No.'] <= selected_range[1])]

st.image("English.png")
st.title("英単語テスト")
st.text("英単語テストができます")

# テスト開始処理
if st.button('テストを開始する'):
    st.session_state.update({
        'test_started': True,
        'correct_answers': 0,
        'current_question': 0,
        'finished': False,
        'results_log': [],
    })

    selected_questions = filtered_words_df.sample(min(num_questions, len(filtered_words_df))).reset_index(drop=True)
    st.session_state.update({
        'selected_questions': selected_questions,
        'total_questions': len(selected_questions),
        'current_question_data': selected_questions.iloc[0],
    })

    # 初回選択肢生成
    if test_type == '英語→日本語':
        options = list(selected_questions['語の意味'].sample(3))
        options.append(st.session_state.current_question_data['語の意味'])
    else:
        options = list(selected_questions['単語'].sample(3))
        options.append(st.session_state.current_question_data['単語'])

    np.random.shuffle(options)
    st.session_state.options = options
    st.session_state.answer = None

# 質問を進める関数
def update_question(answer):
    data = st.session_state.current_question_data
    if test_type == '英語→日本語':
        correct_answer = data['語の意味']
        question_word = data['単語']
    else:
        correct_answer = data['単語']
        question_word = data['語の意味']

    is_correct = answer == correct_answer
    if is_correct:
        st.session_state.correct_answers += 1

    st.session_state.results_log.append({
        "No.": data['No.'],
        "出題": question_word,
        "選択肢": answer,
        "正解": correct_answer,
        "結果": "◯" if is_correct else "×"
    })

    st.session_state.current_question += 1
    if st.session_state.current_question < st.session_state.total_questions:
        st.session_state.current_question_data = st.session_state.selected_questions.iloc[st.session_state.current_question]
        if test_type == '英語→日本語':
            options = list(st.session_state.selected_questions['語の意味'].sample(3))
            options.append(st.session_state.current_question_data['語の意味'])
        else:
            options = list(st.session_state.selected_questions['単語'].sample(3))
            options.append(st.session_state.current_question_data['単語'])
        np.random.shuffle(options)
        st.session_state.options = options
        st.session_state.answer = None
    else:
        st.session_state.finished = True

# 結果表示関数
def display_results():
    correct = st.session_state.correct_answers
    total = st.session_state.total_questions
    accuracy = correct / total

    st.write(f"テスト終了！正解数: {correct}/{total}")
    st.progress(accuracy)

    st.metric("正解数", correct)
    st.metric("不正解数", total - correct)
    st.write(f"正答率: {accuracy:.0%}")

    df_result = pd.DataFrame(st.session_state.results_log)
    st.markdown(df_result.to_html(classes='results-table', index=False), unsafe_allow_html=True)

# 問題表示ロジック
if 'test_started' in st.session_state and not st.session_state.finished:
    st.subheader(f"問題 {st.session_state.current_question + 1} / {st.session_state.total_questions} (No. {st.session_state.current_question_data['No.']})")
    st.subheader(st.session_state.current_question_data['単語'] if test_type == '英語→日本語' else st.session_state.current_question_data['語の意味'])

    progress = (st.session_state.current_question + 1) / st.session_state.total_questions
    st.progress(progress)

    st.markdown('<div class="choices-container">', unsafe_allow_html=True)
    for idx, option in enumerate(st.session_state.options):
        st.button(option, key=f"button_{st.session_state.current_question}_{idx}", on_click=update_question, args=(option,))
    st.markdown('</div>', unsafe_allow_html=True)

elif 'test_started' in st.session_state and st.session_state.finished:
    display_results()
