import streamlit as st
import speech_recognition as sr
import tempfile
import os

# Initialize recognizer
r = sr.Recognizer()

def capture_audio(lang):
    transcription = ""
    try:
        with sr.Microphone() as source:
            st.write("Calibrating for ambient noise... Please wait.")
            r.adjust_for_ambient_noise(source, duration=2)
            st.write("Speak now...")
            audio_data = r.listen(source, timeout=5)  # Increase timeout if necessary
            st.write("Processing...")
            transcription = r.recognize_google(audio_data, language=lang)
            st.session_state.transcription = transcription
            return audio_data
    except sr.WaitTimeoutError:
        st.session_state.transcription = "No speech detected, please try again."
    except sr.UnknownValueError:
        st.session_state.transcription = "Could not understand audio."
    except sr.RequestError as e:
        st.session_state.transcription = f"Could not request results; {e}"
    return None

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

    audio_data = None

    if st.button("Start Recording", key="record"):
        st.session_state.transcription = ""
        with st.spinner("Recording and processing..."):
            audio_data = capture_audio(lang_dict[lang])

    display_transcription()

    if audio_data is not None:
        try:
            # Save audio to a temporary file for playback
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.write(audio_data.get_wav_data())
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
