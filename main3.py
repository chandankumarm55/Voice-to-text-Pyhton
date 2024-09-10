import streamlit as st
import speech_recognition as sr
import tempfile
import os
import io
import wave
import time
from pydub import AudioSegment
from pydub.playback import play
import pyaudio
import numpy as np

# Initialize recognizer
r = sr.Recognizer()

# Function to save numpy array to a WAV file
def save_wav(file_stream, audio_data, sample_rate):
    with wave.open(file_stream, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)

# Function to capture audio using pyaudio and pydub
def capture_audio(lang):
    transcription = ""
    audio_data = None
    try:
        # Recording settings
        sample_rate = 44100  # Sample rate for recording
        buffer_duration = 1  # Duration of buffer recording in seconds
        silence_threshold = -40  # Silence detection threshold in dBFS
        silence_duration = 2  # Duration to wait for silence in seconds

        st.write("Calibrating for ambient noise... Please wait.")
        st.write("Speak now...")

        # Initialize PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=int(sample_rate * buffer_duration))

        st.write("Listening...")
        audio_chunks = []
        silence_start_time = time.time()
        
        while True:
            # Read audio data
            chunk = stream.read(int(sample_rate * buffer_duration))
            audio_chunks.append(chunk)
            audio_data = b''.join(audio_chunks)
            
            # Convert chunk to AudioSegment
            audio_segment = AudioSegment.from_raw(io.BytesIO(chunk), sample_width=2, frame_rate=sample_rate, channels=1)
            
            # Check if the audio level is below a threshold (indicating silence)
            volume = audio_segment.dBFS
            if volume < silence_threshold:
                if time.time() - silence_start_time > silence_duration:
                    st.write("Processing...")
                    break
            else:
                silence_start_time = time.time()

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Convert audio data to a WAV file-like object
        audio_file = io.BytesIO()
        save_wav(audio_file, audio_data, sample_rate)
        audio_file.seek(0)
        
        # Process audio data
        with sr.AudioFile(audio_file) as audio_source:
            audio_data = r.record(audio_source)
            try:
                transcription = r.recognize_google(audio_data, language=lang)
                st.session_state.transcription = transcription
            except sr.UnknownValueError:
                # Continue recording if unable to recognize
                pass
            except sr.RequestError as e:
                st.session_state.transcription = f"Could not request results; {e}"

    except sr.WaitTimeoutError:
        st.session_state.transcription = "No speech detected, please try again."
    except sr.UnknownValueError:
        st.session_state.transcription = "Could not understand audio."
    except sr.RequestError as e:
        st.session_state.transcription = f"Could not request results; {e}"
    return audio_file

def display_transcription():
    if "transcription" in st.session_state:
        st.markdown(f"**I heard the following sentence:**")
        st.markdown(f"<div style='font-size: 20px; font-weight: bold; color: #333;'>{st.session_state.transcription}</div>", unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Voice to Text Conversion App", page_icon="🗣️", layout="wide")

    st.title('Voice to Text Conversion App')
    st.markdown('Click **Start Recording** to begin speaking. The app will automatically stop when you stop speaking.')

    # Language selection
    lang = st.selectbox(
        "Select the language:",
        (
            "English", "Hindi", "Kannada", "Tamil", "Telugu", "Bengali", 
            "Gujarati", "Marathi", "Malayalam", "Punjabi", "Odia", 
            "Urdu", "Assamese", "Malay", "Nepali"
        ),
        index=0
    )

    # Language code mapping
    lang_dict = {
        "English": "en-US",
        "Hindi": "hi-IN",
        "Kannada": "kn-IN",
        "Tamil": "ta-IN",
        "Telugu": "te-IN",
        "Bengali": "bn-IN",
        "Gujarati": "gu-IN",
        "Marathi": "mr-IN",
        "Malayalam": "ml-IN",
        "Punjabi": "pa-IN",
        "Odia": "or-IN",
        "Urdu": "ur-IN",
        "Assamese": "as-IN",
        "Malay": "ms-MY",
        "Nepali": "ne-NP"
    }

    if st.button("Start Recording", key="record"):
        st.session_state.transcription = ""
        st.session_state.audio_data = None
        with st.spinner("Recording and processing..."):
            st.write("Recording started...")
            audio_file = capture_audio(lang_dict[lang])
            st.session_state.audio_data = audio_file
            st.write("Recording stopped.")
        
    display_transcription()

    if "audio_data" in st.session_state and st.session_state.audio_data is not None:
        try:
            # Save audio to a temporary file for playback
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.close()  # Close the file to ensure it's properly saved
                save_wav(temp_audio_file.name, st.session_state.audio_data.getvalue(), 44100)
                temp_audio_path = temp_audio_file.name

            st.audio(temp_audio_path)  # Play the audio file

            # Download transcription as a text file
            st.download_button(
                label="Download Transcription",
                data=st.session_state.transcription,
                file_name="transcription.txt",
                mime="text/plain",
                key="download"
            )

            # Clean up temporary audio file
            os.remove(temp_audio_path)

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
