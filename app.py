import streamlit as st
import io

import asyncio
import tempfile
import os

import requests
import numpy as np
from PIL import Image, ImageFilter
from deep_translator import GoogleTranslator
import edge_tts
import PyPDF2
from groq import Groq
import pandas as pd
import matplotlib.pyplot as plt
import tempfile, re , subprocess , json
import pytesseract
import random

st.title("Ai student assistant")

st.sidebar.title("Tools")

tool = st.sidebar.radio("Select a tool to use" , {"Chatbot" , "quiz" , "Summarizer" , "ai imager", "Weather" , "extractor sound and video" , "extractor image"} )

if tool == "Chatbot":
    st.header("Chatbot")
        
    # client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    client = Groq(api_key="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")

    st.title("🤖 My Chatbot")

    audio = st.audio_input("Record...")

    prompt = st.chat_input("Write your text here...")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    messages = [{"role": "system", "content": "your are a helpful assistant"}]
                    for msg in st.session_state.messages:
                        messages.append({"role": msg["role"], "content": msg["content"]})
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=messages,
                        max_tokens=7000,
                        temperature=0.7
                    )
                    answer = response.choices[0].message.content
                except Exception as e:
                    answer = e
            st.write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

    if audio:
        if st.button("Send"):
            with st.spinner("Converting to text..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio.read())
                    path = tmp.name
                try:
                    with open(path, "rb") as f:
                        transcript = client.audio.transcriptions.create(
                            model="whisper-large-v3",
                            file=(os.path.basename(path), f),
                            response_format="text"
                        )
                finally:
                    os.unlink(path)

            if not transcript or len(transcript.strip()) < 2:
                st.error("Try again")
            else:
                st.session_state.messages.append({"role": "user", "content": transcript})
                with st.chat_message("user"):
                    st.write(f"{transcript}")

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            messages = [{"role": "system", "content": "You are a helpful assistant"}]
                            for msg in st.session_state.messages:
                                messages.append({"role": msg["role"], "content": msg["content"]})

                            response = client.chat.completions.create(
                                model="openai/gpt-oss-120b",
                                messages=messages,
                                max_tokens=7000,
                                temperature=0.7
                            )
                            answer = response.choices[0].message.content

                        except Exception as e:
                            answer = e

                    st.write(answer)

                st.session_state.messages.append({"role": "assistant", "content": answer})

elif tool == "quiz":
    st.header("quiz")
    # =========================================================
    # PAGE
    # =========================================================

    st.set_page_config(
        page_title="Study AI",
        page_icon="📚",
        layout="wide"
    )

    # =========================================================
    # QUIZ DATA
    # =========================================================

    if "quizzes" not in st.session_state:

        st.session_state.quizzes = []

        for i in range(10):

            st.session_state.quizzes.append({
                "name": f"Quiz {i + 1}",
                "subject": "",
                "topic": "",
                "question_type": "Multiple Choice",
                "question_count": 10,
                "text": "",
                "questions": [],
                "score": None
            })

    # =========================================================
    # HEADER
    # =========================================================

    st.title("📚 Study AI")

    st.write(
        "Create and manage up to 10 quizzes."
    )

    st.divider()

    # =========================================================
    # SIDEBAR
    # =========================================================

    st.sidebar.title("📚 My Quizzes")

    selected_quiz = st.sidebar.selectbox(
        "Select Quiz",
        range(10),
        format_func=lambda x:
            st.session_state.quizzes[x]["name"]
    )

    quiz = st.session_state.quizzes[selected_quiz]

    # =========================================================
    # QUIZ SETTINGS
    # =========================================================

    st.header(f"📝 {quiz['name']}")

    col1, col2 = st.columns(2)

    with col1:

        quiz["name"] = st.text_input(
            "Quiz Name",
            value=quiz["name"]
        )

        quiz["subject"] = st.text_input(
            "Subject",
            value=quiz["subject"],
            placeholder="Example: Science"
        )

    with col2:

        quiz["topic"] = st.text_input(
            "Quiz Topic",
            value=quiz["topic"],
            placeholder="Example: Water Cycle"
        )

        quiz["question_count"] = st.number_input(
            "Number of Questions",
            min_value=3,
            max_value=50,
            value=quiz["question_count"]
        )

    # =========================================================
    # QUESTION TYPE
    # =========================================================

    quiz["question_type"] = st.selectbox(
        "Question Type",
        [
            "Multiple Choice",
            "True / False",
            "Fill in the Blank",
            "All Types"
        ],
        index=[
            "Multiple Choice",
            "True / False",
            "Fill in the Blank",
            "All Types"
        ].index(quiz["question_type"])
    )

    # =========================================================
    # IMAGE
    # =========================================================

    st.divider()

    st.header("📷 Study Material")

    uploaded_file = st.file_uploader(
        "Upload an image for this quiz",
        type=["png", "jpg", "jpeg"],
        key=f"upload_{selected_quiz}"
    )

    if uploaded_file:

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Uploaded Study Material",
            width=500
        )

        if st.button(
            "🔎 Extract Text",
            key=f"extract_{selected_quiz}"
        ):

            with st.spinner("Reading image..."):

                text = pytesseract.image_to_string(
                    image,
                    lang="eng"
                )

            if text.strip():

                quiz["text"] = text

                st.success(
                    "Text extracted successfully!"
                )

            else:

                st.warning(
                    "No readable text found."
                )

    # =========================================================
    # TEXT
    # =========================================================

    if quiz["text"]:

        st.divider()

        st.header("📝 Study Text")

        quiz["text"] = st.text_area(
            "Edit the text if needed",
            value=quiz["text"],
            height=250,
            key=f"text_{selected_quiz}"
        )

    # =========================================================
    # GENERATE QUIZ
    # =========================================================

    st.divider()

    st.header("🧠 Quiz Generator")

    if st.button(
        "🚀 Generate Quiz",
        key=f"generate_{selected_quiz}",
        use_container_width=True
    ):

        if not quiz["subject"]:

            st.warning(
                "Please enter the subject first."
            )

        elif not quiz["topic"]:

            st.warning(
                "Please enter the quiz topic."
            )

        elif not quiz["text"]:

            st.warning(
                "Please upload an image and extract the text."
            )

        else:

            sentences = re.split(
                r"[.!?]\s+",
                quiz["text"]
            )

            sentences = [
                s.strip()
                for s in sentences
                if len(s.split()) >= 5
            ]

            if len(sentences) < 3:

                st.warning(
                    "Not enough text to create questions."
                )

            else:

                selected_sentences = random.choices(
                    sentences,
                    k=quiz["question_count"]
                )

                questions = []

                for sentence in selected_sentences:

                    words = sentence.split()

                    if len(words) < 5:
                        continue

                    answer_index = random.randrange(
                        len(words)
                    )

                    answer = words[answer_index]

                    question_words = words.copy()

                    question_words[
                        answer_index
                    ] = "_____"

                    question = " ".join(
                        question_words
                    )

                    questions.append({
                        "question": question,
                        "answer": answer,
                        "type": quiz["question_type"]
                    })

                quiz["questions"] = questions

                quiz["score"] = None

                st.success(
                    f"Created {len(questions)} questions!"
                )

    # =========================================================
    # START QUIZ
    # =========================================================

    if quiz["questions"]:

        st.divider()

        st.header("🎯 Your Quiz")

        answers = []

        for i, question in enumerate(
            quiz["questions"]
        ):

            st.subheader(
                f"Question {i + 1}"
            )

            st.write(
                question["question"]
            )

            answer = st.text_input(
                "Your Answer",
                key=f"answer_{selected_quiz}_{i}"
            )

            answers.append(answer)

        if st.button(
            "🏆 Submit Quiz",
            key=f"submit_{selected_quiz}",
            use_container_width=True
        ):

            score = 0

            for i, question in enumerate(
                quiz["questions"]
            ):

                user_answer = (
                    answers[i]
                    .strip()
                    .lower()
                )

                correct_answer = (
                    question["answer"]
                    .strip()
                    .lower()
                )

                if user_answer == correct_answer:

                    score += 1

            quiz["score"] = score

    # =========================================================
    # SCORE
    # =========================================================

    if quiz["score"] is not None:

        total = len(quiz["questions"])

        st.divider()

        st.header("🏆 Result")

        st.metric(
            "Score",
            f"{quiz['score']} / {total}"
        )

        percentage = (
            quiz["score"] / total
        ) * 100

        if percentage == 100:

            st.balloons()

            st.success(
                "🎉 Perfect Score!"
            )

        elif percentage >= 50:

            st.info(
                "👍 Good job! Keep practicing."
            )

        else:

            st.warning(
                "📚 Keep studying and try again."
            )

    # =========================================================
    # QUIZ OVERVIEW
    # =========================================================

    st.divider()

    st.header("📚 My 10 Quizzes")

    for i, q in enumerate(
        st.session_state.quizzes
    ):

        subject = q["subject"] or "No subject"

        topic = q["topic"] or "No topic"

        score = (
            f"{q['score']} / {len(q['questions'])}"
            if q["score"] is not None
            else "Not taken"
        )

        with st.expander(
            f"{i + 1}. {q['name']}"
        ):

            st.write(
                f"**Subject:** {subject}"
            )

            st.write(
                f"**Topic:** {topic}"
            )

            st.write(
                f"**Question Type:** "
                f"{q['question_type']}"
            )

            st.write(
                f"**Questions:** "
                f"{q['question_count']}"
            )

            st.write(
                f"**Score:** {score}"
            )
elif tool == "Summarizer":
    st.header("summarizer")

        
    st.title("Sumurize app")

    # client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    client = Groq(api_key="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")

    file =st.file_uploader("Upload your file here", type = ["txt" , "pdf" , "docx"])



    if file is not None:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        pdf_text = ""

        for page in pdf_reader.pages:
            pdf_text += page.extract_text() or ""
        if pdf_text.strip():
            st.info(f"extracted from {len(pdf_reader.pages)} pages")
            text_from_pdf = pdf_text
        else:
            st.warning("No text found in the PDF file.")
            text_from_pdf = ""

    else:
        text_from_pdf = ""

    text = st.text_area("Enter your text here", height = 200, value = text_from_pdf)

    if st.button("Summarize"):
        if text.strip():
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize this text clearly and briefly:\n\n{text}"
                    }
                ]
            )

            summary = response.choices[0].message.content

            st.subheader("Summary")
            st.write(summary)

        else:
            st.warning("Please enter some text first.")

    st.markdown("---")
    st.markdown("Made with Mazen Ahmed Beialy")

elif tool == "ai imager":
    st.header("ai imager")
    def filer_vintage(img):
        arr = np.array(img , dtype=np.float32)
        arr[:,:,0] = np.clip(arr[:,:,0]*1.1+20,0,225)
        arr[:,:,1] = np.clip(arr[:,:,1]*0.9+10,0,225)
        arr[:,:,2] = np.clip(arr[:,:,2]*0.75,0,225)
        return Image.fromarray(arr.astype(np.uint8))

    def filterbw(img):
        return img.convert("L").convert("RGB")

    def filtersharp(img):
        return img.filter(ImageFilter.SHARPEN)

    def warm(img):
        arr = np.array(img , dtype=np.float32)
        arr[:,:,0] = np.clip(arr[:,:,0]+40,0,225)
        arr[:,:,2] = np.clip(arr[:,:,2]-40,0,225)
        return Image.fromarray(arr.astype(np.uint8))

    def cinema(img):
        arr = np.array(img , dtype=np.float32)
        arr[:,:,0] = np.clip(arr[:,:,0]*0.9,0,225)
        arr[:,:,2] = np.clip(arr[:,:,2]*1.2,0,225)
        return Image.fromarray(arr.astype(np.uint8))

    filters={
        "none":None,
        "vintage":filer_vintage,
        "black and white":filterbw,
        "sharpen":filtersharp,
        "warm":warm,
        "cinema":cinema
        }
    st.title("فلتر صورتك")

    file=st.file_uploader("Choose the image", type=["png","jpg","jpeg"])

    if file :
        img=Image.open(file).convert("RGBA")

        st.subheader("Original image")
        st.image(img , caption="Person")




        subheader="Choose filter"
        choice=st.radio(
                    "",list(filters.keys()),
                    horizontal=True
        )

        filtered =img.convert("RGB")
        if filters[choice]:
            filtered=filters[choice](filtered)
        st.subheader("Filtered image")
        st.image(filtered)

        buffer = io.BytesIO()
        filtered.save(buffer, format="PNG")


        st.download_button(
                    label="📥 Download Image",
                    data=buffer.getvalue(),
                    file_name="filtered_image.png",
                    mime="image/png"
                )

elif tool == "Weather":
    st.header("weather")
    import streamlit as st
    import requests
    import pandas as pd
    import matplotlib.pyplot as plt

    st.set_page_config(page_title="Weather App", page_icon="🌦️")

    st.title("🌦️ Weather App")

    st.sidebar.title("🌍 Weather App")

    st.sidebar.info("""
    Developed by Mazen Ahmed Beialy

    Python + Streamlit
    """)

    city = st.text_input("Enter city name", "Cairo")

    favorite = st.sidebar.selectbox(
        "⭐ Favorite Cities",
        ["Choose...", "Cairo", "Alexandria", "London", "Paris", "Tokyo"]
    )

    if favorite != "Choose...":
        city = favorite

    if st.button("🔍 Search"):

        url = f"https://wttr.in/{city}?format=j1"

        try:
            with st.spinner("Loading weather..."):

                response = requests.get(url, timeout=10)
                data = response.json()

                current = data["current_condition"][0]

                st.success(f"Weather in {city}")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("🌡️ Temperature", f"{current['temp_C']} °C")
                    st.metric("💧 Humidity", f"{current['humidity']} %")

                with col2:
                    st.metric("🌬️ Wind Speed", f"{current['windspeedKmph']} km/h")
                    st.metric("☁️ Weather", current["weatherDesc"][0]["value"])

                icon = current["weatherIconUrl"][0]["value"]
                st.image(icon, width=120)

                st.subheader("ℹ️ More Information")

                st.write(f"🌡️ Feels Like: {current['FeelsLikeC']} °C")
                st.write(f"👁️ Visibility: {current['visibility']} km")
                st.write(f"🧭 Wind Direction: {current['winddir16Point']}")
                st.write(f"🌬️ Pressure: {current['pressure']} mb")
                st.write(f"☀️ UV Index: {current['uvIndex']}")

                st.subheader("📅 3-Day Forecast")

                for day in data["weather"]:
                    st.write(
                        f"🌡️ Max: {day['maxtempC']}°C | "
                        f"Min: {day['mintempC']}°C"
                    )

                forecast = []

                for day in data["weather"]:
                    forecast.append({
                        "Date": day["date"],
                        "Max Temp": int(day["maxtempC"]),
                        "Min Temp": int(day["mintempC"])
                    })

                df = pd.DataFrame(forecast)

                st.subheader("📈 Temperature Chart")

                fig, ax = plt.subplots()

                ax.plot(df["Date"], df["Max Temp"], marker="o", label="Max")
                ax.plot(df["Date"], df["Min Temp"], marker="o", label="Min")

                ax.set_ylabel("Temperature (°C)")
                ax.legend()

                st.pyplot(fig)

                st.subheader("📋 Forecast Table")
                st.dataframe(df, use_container_width=True)

        except Exception:
            st.error("City not found or no internet connection.")      

elif tool == "extractor sound and video":
    st.header("extractor sound and video")
    st.title("استخراج النص")

    # client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    client = Groq(api_key="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")

    st.title("رفع ملف فيديو او صوت")

    uploaded=st.file_uploader("ارفع فيديو او ملف صوتي", type=["mp4","mp3", "wav","m4a","ogg","Webm"])

    def transcribe_audio_file(path):
        with open(path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model = "whisper-large-v3",
                file=(os.path.basename(path) , f),
                response_format="text"
            )
        return transcription

    if uploaded:
        if uploaded.size / 1024**2 > 25:
            st.error("حجم الملف أكبر من 25 ميجابايت")
        elif st.button("استخراج النص", key="file_btn" ):
            with st.spinner("جاري استخراج النص..."):
                ext= os.path.splitext(uploaded.name)[-1].lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
                    tmp_file.write(uploaded.read())
                    tmp_file_path = tmp_file.name
                try:
                    transcription = transcribe_audio_file(tmp_file_path)
                finally:
                    os.remove(tmp_file_path)
                if not transcription or len(transcription.strip()) == 5:
                    st.error("حدث خطأ أثناء استخراج النص")
                else:
                    st.subheader("النص المستخرج")
                    st.write(transcription)
                    st.download_button("تحميل النص", transcription, file_name="transcription.txt")                                                                                                                                                                                                                                                                         



    def parse_json3_sub(path):
        with open(path, "r" , encoding = "utf-8") as f:
            data = json.load(f)
            lines=[]
            for event in data.get("events" , []):
                for seg in event.get("segs" , []):
                    word = seg.get("utf8" , "").strip()
                    if word and word != "\n":
                        lines.append(word)
            full_text = " ".join(lines)
            return re.sub(r"\s+", " " , full_text).strip()




    def get_yt_transcript(url):
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, "subs")
        for lang in ["ar" , "en"]:
            cmd = [
                        "yt-dlp", "--no-playlist", "--skip-download",
                        "--write-subs", "--write-auto-subs",
                        "--sub-format", "json3",
                        "-o", output_path,
                    ]
            if lang:
                cmd +=["--sub-langs", lang]
            cmd.append(url)
            subprocess.run(cmd,capture_output=True , text= True)

            for f in os.listdir(temp_dir):
                if f.endswith(".json3"):
                    sub_path=os.path.join(temp_dir , f)
                    text = parse_json3_sub(sub_path)
                for file in os.listdir(temp_dir):
                    try:
                        os.unlink(os.path.join(temp_dir , file))
                    except:
                        pass
                    if text.strip():
                        return text

        raise ValueError("There is no subtitles found for this url")

                    


    st.markdown("---")

    st.title("رابط يوتيوب")

    st.subheader("يستخرج النص مباشره من الترجمه الموجوده في الفيديو")

    youtube_url=st.text_input("رابط يوتيوب", placeholder="https://www.youtube.com/watch?v=example")

    if youtube_url:
        if st.button("استخراج النص من يوتيوب", key="youtube_btn"):
            with st.spinner("جاري البحث عن الترجمة..."):
                try:
                    transcription = get_yt_transcript(youtube_url)

                    if transcription:
                        st.success("تم استخراج النص بنجاح ")
                        st.subheader("النص المستخرج")
                        st.text_area(
                            "النص",
                            transcription,
                            height=400
                        )

                        st.download_button(
                            " تحميل النص",
                            transcription,
                            file_name="youtube_transcription.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("لم يتم العثور على ترجمة للفيديو.")

                except Exception as e:
                    st.error(f"حدث خطأ: {e}")


    st.markdown("---")
    st.markdown("Made with Mazen Ahmed Beialy")

elif tool == "extractor image":
    st.header("extractor image")
    # =========================================================
    # PAGE
    # =========================================================

    st.set_page_config(
        page_title="Text Extractor",
        page_icon="📷",
        layout="wide"
    )

    st.title("📷 استخراج النص من الصورة")

    st.write(
        "ارفع صورة وسيقوم التطبيق باستخراج النص الموجود بداخلها."
    )

    # =========================================================
    # UPLOAD IMAGE
    # =========================================================

    uploaded_file = st.file_uploader(
        "📤 Upload Image",
        type=["png", "jpg", "jpeg", "webp"]
    )

    # =========================================================
    # IMAGE
    # =========================================================

    if uploaded_file:

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="الصورة المرفوعة",
            width=600
        )

        # =====================================================
        # EXTRACT TEXT
        # =====================================================


        if st.button(
            "🔎 استخراج النص",
            use_container_width=True
        ):


            with st.spinner("جاري قراءة الصورة..."):

                text = pytesseract.image_to_string(
                    image,
                    lang="eng"
                )

            if text.strip():


                st.success("✅ تم استخراج النص بنجاح!")


                st.subheader("📝 النص المستخرج")


                st.text_area(
                    "النص",
                    text,
                    height=400
                )


                # =================================================
                # DOWNLOAD
                # =================================================


                st.download_button(
                    "⬇️ تحميل النص",
                    text,
                    file_name="extracted_text.txt",
                    mime="text/plain",
                    use_container_width=True
                )


            else:

                st.warning(
                    "⚠️ لم يتم العثور على نص واضح داخل الصورة."
                )


    # =========================================================
    # FOOTER
    # =========================================================


    st.markdown("---")

    st.markdown(
        "Made with Mazen Ahmed Beialy"
    )