import base64
import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title='Diabetes Risk Check', page_icon='🩺', layout='wide')

saved = joblib.load('diabetes_model.joblib')
model, threshold, columns = saved['model'], saved['threshold'], saved['columns']

hero_img = base64.b64encode(open('images/hero.jpg', 'rb').read()).decode()

# ---------- Look: style + header ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=League+Spartan:wght@500;700&display=swap');
.block-container { max-width: 1300px !important; padding: 1rem 1rem 3rem !important; }
[data-testid="stAppViewContainer"] { background: linear-gradient(160deg, #D5D3F3 0%, #E6F3F7 100%); }
[data-testid="stHeader"] { background: transparent; }
h1, h2, h3 { font-family: 'League Spartan', sans-serif !important; color: #413074 !important; }
.hero { background: linear-gradient(90deg, #413074 30%, rgba(65,48,116,0.15) 85%),
        url(data:image/jpeg;base64,HERO_IMG) right center / cover;
        border-radius: 22px; padding: 48px 56px; display: flex; align-items: center;
        gap: 28px; margin-bottom: 18px; }
.hero svg { width: 120px; height: 120px; flex-shrink: 0; }
.hero .title { font-family: 'League Spartan', sans-serif; font-size: 56px; font-weight: 700;
        color: white; line-height: 1.1; }
.hero p { color: #ECECFA; font-size: 20px; margin: 8px 0 0; }
@media (max-width: 800px) {
  .hero { padding: 24px; gap: 14px;
          background: linear-gradient(rgba(65,48,116,0.88), rgba(65,48,116,0.88)),
          url(data:image/jpeg;base64,HERO_IMG) center / cover; }
  .hero svg { width: 64px; height: 64px; }
  .hero .title { font-size: 30px; }
  .hero p { font-size: 15px; }
}
.chips { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-bottom: 20px; }
.chip { background: white; color: #413074; border-radius: 999px; padding: 6px 16px; font-size: 14px; }
.card-title { font-family: 'League Spartan', sans-serif; font-size: 24px; font-weight: 700;
        color: #413074; margin-bottom: 6px; }
.badge { background: #ECECFA; border-radius: 12px; padding: 4px 10px; margin-right: 10px; }
[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"] { background: white;
        border-radius: 18px; border: 1px solid #CFCDEB; padding: 8px 10px;
        box-shadow: 0 4px 14px rgba(65,48,116,0.08); }
[data-testid="stFormSubmitButton"] button { background: #413074; color: white; border: none;
        border-radius: 14px; padding: 14px; font-size: 20px; width: 100%; }
[data-testid="stFormSubmitButton"] button:hover { background: #0FB7B8; color: white; }
.result { border-radius: 18px; padding: 26px; color: #2B2350; font-size: 17px; }
.rtitle { font-family: 'League Spartan', sans-serif; font-size: 34px; font-weight: 700; margin-bottom: 6px; }
.low { background: #E3F6F6; border-left: 8px solid #0FB7B8; }
.mid { background: #FFF4DC; border-left: 8px solid #F2B134; }
.high { background: #FDEBE0; border-left: 8px solid #E8793A; }
.meter-wrap { position: relative; margin: 30px 0 4px; }
.meter { display: flex; height: 14px; border-radius: 99px; overflow: hidden; }
.seg { flex: 1; }
.s1 { background: #0FB7B8; }
.s2 { background: #F2B134; }
.s3 { background: #E8793A; }
.pin { position: absolute; top: -24px; transform: translateX(-50%); font-size: 20px; color: #413074; }
.labels { display: flex; justify-content: space-between; font-size: 13px; color: #413074; }
.bmi { background: white; border-radius: 18px; padding: 26px; text-align: center;
       color: #413074; border: 1px solid #CFCDEB; }
.bmi b { display: block; font-family: 'League Spartan', sans-serif; font-size: 44px; }
.habits { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 14px; margin: 18px 0; }
.habit { background: white; border-radius: 16px; padding: 18px; text-align: center;
         color: #2B2350; border: 1px solid #CFCDEB; }
.habit span { font-size: 36px; display: block; margin-bottom: 6px; }
</style>
<div class="hero">
<svg viewBox="0 0 64 64">
<path d="M24 6h16v18h18v16H40v18H24V40H6V24h18z" fill="none" stroke="white" stroke-width="3"/>
<ellipse cx="32" cy="24" rx="4" ry="8" fill="#0FB7B8"/>
<ellipse cx="24" cy="30" rx="3.5" ry="7" fill="#0FB7B8" transform="rotate(-40 24 30)"/>
<ellipse cx="40" cy="30" rx="3.5" ry="7" fill="#C9C5F0" transform="rotate(40 40 30)"/>
<line x1="32" y1="44" x2="32" y2="32" stroke="#0FB7B8" stroke-width="2"/>
</svg>
<div>
<div class="title">Diabetes Risk Check</div>
<p>Answer a few quick questions and get a simple, friendly result.</p>
</div>
</div>
<div class="chips">
<span class="chip">⏱️ Takes about 1 minute</span>
<span class="chip">🔒 Your answers are not stored</span>
<span class="chip">🩺 Not a medical test</span>
</div>
""".replace('HERO_IMG', hero_img), unsafe_allow_html=True)

values = {}

def title(icon, text):
    st.markdown(f'<div class="card-title"><span class="badge">{icon}</span>{text}</div>',
                unsafe_allow_html=True)

def toggles(questions):
    # each question: (text, default) where default 0 = off (No), 1 = on (Yes)
    st.caption('Switch on for "Yes"')
    for col, (text, default) in questions.items():
        values[col] = 1 if st.toggle(text, value=bool(default)) else 0

# ---------- Form: 3 cards side by side ----------
with st.form('form', border=False):
    left, center, right = st.columns(3, gap='medium')

    with left:
        with st.container(border=True):
            title('👤', 'About you')
            gender = st.selectbox('Gender', ['Female', 'Male'])
            ages = ['18-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54',
                    '55-59', '60-64', '65-69', '70-74', '75-79', '80 or older']
            age = st.selectbox('Age group', ages, index=6)
            h, w = st.columns(2)
            height = h.number_input('Height (cm)', 100, 220, 170)
            weight = w.number_input('Weight (kg)', 30, 250, 70)
            values['Sex'] = 1 if gender == 'Male' else 0
            values['Age'] = ages.index(age) + 1
        with st.container(border=True):
            title('🏠', 'Background')
            edu = ['Never attended school', 'Grades 1-8', 'Grades 9-11',
                   'High school graduate', 'Some college', 'College graduate']
            income = ['Under $10k', '$10k-15k', '$15k-20k', '$20k-25k',
                      '$25k-35k', '$35k-50k', '$50k-75k', '$75k or more']
            values['Education'] = edu.index(st.selectbox('Education', edu, index=3)) + 1
            values['Income'] = income.index(st.selectbox('Yearly income', income, index=4)) + 1

    with center:
        with st.container(border=True):
            title('❤️', 'Your health')
            health = ['Excellent', 'Very good', 'Good', 'Fair', 'Poor']
            general = st.selectbox('How would you rate your health in general?', health, index=2)
            values['GenHlth'] = health.index(general) + 1
            values['PhysHlth'] = st.number_input('Days in the last 30 when your body did not feel well',
                                                 0, 30, 0, help='Type 0 if none')
            values['MentHlth'] = st.number_input('Days in the last 30 when your mood was not good',
                                                 0, 30, 0, help='Type 0 if none')
            toggles({
                'DiffWalk': ('Difficulty walking or climbing stairs', 0),
                'HighBP': ('Told you have high blood pressure', 0),
                'HighChol': ('Told you have high cholesterol', 0),
                'CholCheck': ('Cholesterol checked in the last 5 years', 1),
                'Stroke': ('Ever had a stroke', 0),
                'HeartDiseaseorAttack': ('Ever had heart disease or a heart attack', 0),
            })

    with right:
        with st.container(border=True):
            title('🏃', 'Lifestyle')
            toggles({
                'Smoker': ('Smoked at least 100 cigarettes in your life', 0),
                'PhysActivity': ('Physical activity in the last 30 days', 1),
                'Fruits': ('Eat fruit at least once a day', 1),
                'Veggies': ('Eat vegetables at least once a day', 1),
                'HvyAlcoholConsump': ('Drink a lot of alcohol (14+ drinks a week for men, 7+ for women)', 0),
            })
        with st.container(border=True):
            title('🏥', 'Health care')
            toggles({
                'AnyHealthcare': ('Have any health insurance', 1),
                'NoDocbcCost': ('Needed a doctor in the last year but could not afford it', 0),
            })

    go = st.form_submit_button('See my result')

# ---------- Result ----------
if go:
    bmi = weight / (height / 100) ** 2
    values['BMI'] = bmi
    person = pd.DataFrame([values])[columns]
    prob = model.predict_proba(person)[0, 1]

    if prob >= threshold:
        css, icon, level, pos = 'high', '🟠', 'Higher risk', 83
        text = ('Your answers are similar to those of many people who have diabetes. '
                'This does <b>not</b> mean you have it. A simple blood sugar test at a clinic '
                'can check, so consider booking one soon.')
    elif prob >= 0.30:
        css, icon, level, pos = 'mid', '🟡', 'Medium risk', 50
        text = ('Some of your answers are linked to diabetes. '
                'It is a good idea to keep an eye on your health and have a check-up.')
    else:
        css, icon, level, pos = 'low', '🟢', 'Lower risk', 17
        text = ('Your answers are not strongly linked to diabetes. '
                'Keep up your healthy habits and have regular check-ups.')

    card = (f'<div class="result {css}"><div class="rtitle">{icon} {level}</div>{text}'
            '<div class="meter-wrap"><div class="meter"><div class="seg s1"></div>'
            '<div class="seg s2"></div><div class="seg s3"></div></div>'
            f'<div class="pin" style="left:{pos}%">▼</div></div>'
            '<div class="labels"><span>Lower</span><span>Medium</span><span>Higher</span></div></div>')

    r1, r2 = st.columns([3, 1], gap='medium')
    r1.markdown(card, unsafe_allow_html=True)
    r2.markdown(f'<div class="bmi">Your BMI<b>{bmi:.1f}</b></div>', unsafe_allow_html=True)

    st.markdown("""
<div class="habits">
<div class="habit"><span>🥗</span>Eat more vegetables and fewer sugary drinks</div>
<div class="habit"><span>🚶</span>Move your body every day, even a short walk</div>
<div class="habit"><span>😴</span>Get enough sleep</div>
<div class="habit"><span>🩺</span>Check your blood sugar and blood pressure from time to time</div>
</div>
""", unsafe_allow_html=True)

    with st.expander('🔎 How does this work?'):
        st.write('The tool looks mostly at your general health, BMI, age, blood pressure, '
                 'and cholesterol. It learned from a large US health survey. '
                 'It shows patterns, not causes.')

st.caption('Research estimate only. Not a medical diagnosis. Please talk to a doctor about your health.')