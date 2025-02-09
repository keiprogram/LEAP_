import streamlit as st
import pandas as pd
import numpy as np

# アプリの設定
st.set_page_config(page_title="Enhanced Leap Basic Vocabulary Test")

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
    </style>
    """,
    unsafe_allow_html=True
)

# データ読み込み関数
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
def sidebar_settings():
    st.sidebar.title("テスト設定")
    test_type = st.sidebar.radio("テスト形式を選択", ['英語→日本語', '日本語→英語'], key="test_type")
    groups = words_df['Group'].unique()
    selected_group = st.sidebar.selectbox("カテゴリを選択", groups)

    range_start = st.sidebar.slider("単語範囲（開始）", 0, 1400, 0, step=100)
    range_end = range_start + 100

    num_questions = st.sidebar.slider("出題問題数を選択", 1, 50, 10)

    return test_type, selected_group, range_start, range_end, num_questions

def filter_data(selected_group, range_start, range_end):
    return words_df[(words_df['Group'] == selected_group) &
                    (words_df['No.'] >= range_start) &
                    (words_df['No.'] < range_end)]

def initialize_test(filtered_words_df, num_questions, test_type):
    selected_questions = filtered_words_df.sample(n=min(num_questions, len(filtered_words_df))).reset_index(drop=True)
    st.session_state.update({
        'test_started': True,
        'correct_answers': 0,
        'current_question': 0,
        'finished': False,
        'wrong_answers': [],
        'selected_questions': selected_questions,
        'total_questions': len(selected_questions),
        'current_question_data': selected_questions.iloc[0]
    })

    options = generate_options(selected_questions, test_type, selected_questions.iloc[0])
    st.session_state.options = options

def generate_options(filtered_words_df, test_type, question_data):
    if test_type == '英語→日本語':
        options = list(filtered_words_df['語の意味'].sample(3))
        options.append(question_data['語の意味'])
    else:
        options = list(filtered_words_df['単語'].sample(3))
        options.append(question_data['単語'])
    np.random.shuffle(options)
    return options

def update_question(answer, test_type):
    correct_answer = st.session_state.current_question_data['語の意味'] if test_type == '英語→日本語' else st.session_state.current_question_data['単語']
    question_word = st.session_state.current_question_data['単語'] if test_type == '英語→日本語' else st.session_state.current_question_data['語の意味']

    if answer == correct_answer:
        st.session_state.correct_answers += 1
    else:
        st.session_state.wrong_answers.append(( 
            st.session_state.current_question_data['No.'],
            question_word,
            correct_answer
        ))

    st.session_state.current_question += 1
    if st.session_state.current_question < st.session_state.total_questions:
        st.session_state.current_question_data = st.session_state.selected_questions.iloc[st.session_state.current_question]
        st.session_state.options = generate_options(
            st.session_state.selected_questions,
            test_type,
            st.session_state.current_question_data
        )
    else:
        st.session_state.finished = True

def display_results():
    correct_answers = st.session_state.correct_answers
    total_questions = st.session_state.total_questions
    accuracy = correct_answers / total_questions

    st.write(f"テスト終了！正解数: {correct_answers}/{total_questions}")
    st.progress(accuracy)

    st.metric("正解数", correct_answers)
    st.metric("不正解数", total_questions - correct_answers)

    st.write(f"正答率: {accuracy:.0%}")

    if st.session_state.wrong_answers:
        df_wrong_answers = pd.DataFrame(st.session_state.wrong_answers, columns=["問題番号", "単語", "語の意味"])
        st.markdown(df_wrong_answers.to_html(classes='results-table'), unsafe_allow_html=True)
    else:
        st.write("間違えた問題はありません。")

# メイン処理
def main():
    test_type, selected_group, range_start, range_end, num_questions = sidebar_settings()
    filtered_words_df = filter_data(selected_group, range_start, range_end)

    st.title("英単語テスト")
    if st.button('テストを開始する'):
        initialize_test(filtered_words_df, num_questions, test_type)

    if 'test_started' in st.session_state and not st.session_state.finished:
        question_data = st.session_state.current_question_data
        st.subheader(f"問題 {st.session_state.current_question + 1} / {st.session_state.total_questions}")
        st.subheader(f"{question_data['単語']}" if test_type == '英語→日本語' else f"{question_data['語の意味']}")

        for idx, option in enumerate(st.session_state.options):
            st.button(option, key=f"button_{st.session_state.current_question}_{idx}", on_click=update_question, args=(option, test_type))

    elif 'test_started' in st.session_state and st.session_state.finished:
        display_results()

if __name__ == "__main__":
    main()
