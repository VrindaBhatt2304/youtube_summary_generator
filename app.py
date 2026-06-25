import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt="""You are a youtube video summarizer. 
          You will be taking the transcript text and summarize the entire video and provide the important summary in 250-500 words.
          ⚠️ CRITICAL SYSTEM INSTRUCTION: Regardless of what language the transcript text appears to be,
          you MUST output your entire response strictly and completely in English. Do not write a single word in any other language.
          Please provide the summary of the transcript given here : """

def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]

        yt_api = YouTubeTranscriptApi()
        transcript_list = yt_api.list(video_id)
        transcript = transcript_list.find_transcript(['en', 'hi', 'es', 'fr'])
        if transcript.is_translatable:
            transcript = transcript.translate('en')

        transcript_data = transcript.fetch()

        transcript_text = ""

        for item in transcript_data:
            transcript_text += " " + item.text

        return transcript_text
    except Exception as e:
        raise e

def generate_gemini_content(transcript_text, prompt):

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt + transcript_text)
    return response.text


st.title("🗒️ Youtube Transcript to Detailed Notes Converter")

youtube_link = st.text_input("Enter you Youtube URL here...")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text,prompt)
        st.markdown("📝 Detailed Summary : ")
        st.write(summary)