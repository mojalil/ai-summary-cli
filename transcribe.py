import whisper
import whisper
    
model = whisper.load_model("small")

# transcribe funciton that takes audio file and returns text
def transcribe(audio_file):
    print(f"Transcribing audio file: {audio_file}")
    result = model.transcribe(audio_file, fp16=False)
    return result["text"]

