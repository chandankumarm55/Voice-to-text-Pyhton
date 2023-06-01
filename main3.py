import streamlit as st
import speech_recognition as sr



def main():
    st.title('Voice To text Conversion App')
    st.markdown('Say something by **Clicking** the button and then you can see the text')
    # Create a recognizer instance
    r = sr.Recognizer()
    
    # Microphone capture function
    def capture_audio(duration=5):
        with sr.Microphone() as source:
            st.write("Speak now...")
            audio = r.listen(source, timeout=duration)
        return audio
    
    # Button to initiate voice capture
    if st.button("Capture Voice"):
        audio = capture_audio(duration=10)  # Increase the duration to 10 seconds
        
        # Perform speech recognition
        try:
            text = r.recognize_google(audio)
            st.write("You said:", text)
        except sr.UnknownValueError:
            st.write("Could not understand audio")
        except sr.RequestError as e:
            st.write("Error: Could not request results from Speech Recognition service; {0}".format(e))
    

if __name__ == "__main__":
    main()
