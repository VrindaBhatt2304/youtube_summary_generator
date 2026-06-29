import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
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
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except Exception:
            try:
                transcript = transcript_list.find_generated_transcript(['en', 'hi', 'es', 'fr'])
            except Exception:
                  raise Exception("This video does not have any manual English or auto-generated captions available.")

        transcript_data = transcript.fetch()

        transcript_text = ""

        for item in transcript_data:
            transcript_text += " " + item.text

        return transcript_text
    except Exception as e:
        raise e

def generate_gemini_content(transcript_text, prompt):
    try:
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt + transcript_text, safety_settings=safety_settings)
        
        if not response.candidates:
            return "⚠️ Summary failed: The YouTube transcript was completely blocked by Google's content filters."
            
        if response.candidates[0].finish_reason.name == "SAFETY":
            return "⚠️ Summary failed: The YouTube transcript triggered Google's safety filters and was blocked."
            
        return response.text
    except Exception as e:
        return f"An error occurred while generating content: {str(e)}"


st.title("🗒️ Youtube Transcript to Detailed Notes Converter")

youtube_link = st.text_input("Enter your Youtube URL here...")

if youtube_link:
    try:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", width='stretch')
    except IndexError:
        st.warning("Please enter a valid YouTube link format (containing '?v=')")

if st.button("Get Detailed Notes"):
    if youtube_link:
        with st.spinner("Fetching transcript and summarizing..."):
            try:
                transcript_text = extract_transcript_details(youtube_link)

                if transcript_text:
                    summary = generate_gemini_content(transcript_text, prompt)
                    st.markdown("📝 **Detailed Summary :** ")
                    st.write(summary)
            except Exception as e:
                st.error(f"Could not retrieve transcript: {str(e)}. Make sure the video has captions available.")
    else:
        st.warning("Please provide a URL first.")
