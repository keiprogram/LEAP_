import streamlit as st
import pandas as pd
import numpy as np

# アプリ設定
st.set_page_config(page_title="English Vocabulary Test", page_icon='English Logo.png')

# カスタムCSS
st.markdown(
    """
    <style>
    body { font-family: 'Arial', sans-serif; background-color: #f5f5f5; color: #333; }
    .choices-container button { background-color: #6c757d; color: white; border: 2px solid #6c757d; margin: 5px; padding: 10px; border-radius: 5px; font-weight: bold; cursor: pointer; }
    .choices-container button:hover { background-color: #495057; }
    .results-table { margin: 20px auto; border-collapse: collapse; width: 100%; background: white; }
    .results-table th { background-color: #6c757d; color: white; padding: 10px; }
    .results-table td { border: 1px solid #6c757d; padding: 8px; text-align: center; }
    .stProgress > div > div > div > div { background-color: #6c757d; }
    </style>
    """,
    unsafe_allow_html=True
)

# 単語帳選択
sheet_type = st.sidebar.selectbox(
    "単語帳を選択", ["リープベーシック", "緑リープ"]
)

# データ読み込み関数
@st.cache_data
def load_data(sheet_type):
    if sheet_type == "リープベーシック":
        file_paths = [
            "リープベーシック見出語・用例リスト(Part 1).xlsx",
            "リープベーシック見出語・用例リスト(Part 2).xlsx",
            "リープベーシック見出語・用例リスト(Part 3).xlsx",
            "リープベーシック見出語・用例リスト(Part 4).xlsx",
        ]
    else:
        file_paths = [
            "見出語・用例リスト(Part 1).xlsx",
            "見出語・用例リスト(Part 2).xlsx",
            "見出語・用例リスト(Part 3).xlsx",
            "見出語・用例リスト(Part 4).xlsx",
        ]
    dfs = [pd.read_excel(fp) for fp in file_paths]
    df = pd.concat(dfs, ignore_index=True)
    df.columns = ['Group', 'No.', '単語', 'CEFR', '語の意味', '用例（英語）', '用例（日本語）']
    return df

words_df = load_data(sheet_type)

# サイドバー設定
st.sidebar.title("テスト設定")
test_type = st.sidebar.radio("テスト形式", ['英語→日本語', '日本語→英語'])

# 範囲選択
max_no = int(words_df['No.'].max())
ranges = [(i+1, min(i+100, max_no)) for i in range(0, max_no, 100)]
labels = [f"No.{s}〜No.{e}" for s,e in ranges]
sel = st.sidebar.selectbox("単語範囲を選択", labels)
selected_range = ranges[labels.index(sel)]

# 出題数
num_q = st.sidebar.slider("出題数", 1, 50, 10)

# データ抽出
filtered = words_df[(words_df['No.']>=selected_range[0]) & (words_df['No.']<=selected_range[1])]

# メインUI
st.title("英単語テスト")
st.text("選択した単語帳: {} | 範囲: {} | 問題数: {}".format(sheet_type, sel, num_q))

# テスト開始
if st.button('テスト開始'):
    st.session_state.started = True
    st.session_state.questions = filtered.sample(min(num_q, len(filtered))).reset_index(drop=True)
    st.session_state.idx = 0
    st.session_state.correct = 0
    st.session_state.wrongs = []

# 回答処理
def answer(opt):
    q = st.session_state.questions.iloc[st.session_state.idx]
    correct = q['語の意味'] if test_type=='英語→日本語' else q['単語']
    if opt==correct:
        st.session_state.correct +=1
    else:
        st.session_state.wrongs.append((q['No.'], q['単語'], q['語の意味']))
    st.session_state.idx +=1

# テスト進行
if st.session_state.get('started') and st.session_state.idx < len(st.session_state.questions):
    q = st.session_state.questions.iloc[st.session_state.idx]
    prompt = q['単語'] if test_type=='英語→日本語' else q['語の意味']
    answer_col = '語の意味' if test_type=='英語→日本語' else '単語'
    pool = filtered[answer_col].drop_duplicates()
    opts = list(pool.sample(min(3,len(pool)))) + [q[answer_col]]
    np.random.shuffle(opts)
    st.subheader(f"問題 {st.session_state.idx+1} / {len(st.session_state.questions)}")
    st.write(prompt)
    for o in opts:
        if st.button(o): answer(o)

# 結果表示
elif st.session_state.get('started'):
    total = len(st.session_state.questions)
    st.success(f"テスト終了！ {st.session_state.correct}/{total} 正解")
    st.progress(st.session_state.correct/total)
    if st.session_state.wrongs:
        df_wrong=pd.DataFrame(st.session_state.wrongs,columns=['No.','単語','語の意味'])
        st.subheader('間違えた問題')
        st.table(df_wrong)
    else:
        st.write('全問正解！おめでとうございます！')
