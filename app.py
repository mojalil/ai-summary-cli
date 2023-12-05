import os
import subprocess
import math
from openai import OpenAI
from datetime import datetime
from transcribe import transcribe

# Load .env file
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RESET_TRANSCRIPTION = os.getenv("RESET_TRANSCRIPTION", "False") == "True"
RESET_EXTRACT_AUDIO = os.getenv("RESET_EXTRACT_AUDIO", "False") == "True"
RESET_SUMMARY = os.getenv("RESET_SUMMARY", "False") == "True"
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "./output")
ARCHIVE_FOLDER = os.getenv("ARCHIVE_FOLDER", "./archive")
LOCAL_MODE = os.getenv("LOCAL_MODE", "False") == "True"

audio_file_path = os.path.join(OUTPUT_FOLDER, "audio.wav")
transcription_file_path = os.path.join(OUTPUT_FOLDER, "transcription.txt")
summary_file_path = os.path.join(OUTPUT_FOLDER, "summary.txt")

# Print the current settings
print("Current settings:")
print(f"RESET_TRANSCRIPTION: {RESET_TRANSCRIPTION}")
print(f"RESET_EXTRACT_AUDIO: {RESET_EXTRACT_AUDIO}")
print(f"RESET_SUMMARY: {RESET_SUMMARY}")
print(f"VIDEO_PATH: {os.getenv('VIDEO_PATH')}")

# If Reset Extract audio is true, delete the audio file and all chunks if they exist
if RESET_EXTRACT_AUDIO:
    print("Deleting audio file and chunks...")
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)
    for f in os.listdir(OUTPUT_FOLDER):
        if f.startswith("chunk_"):
            os.remove(os.path.join(OUTPUT_FOLDER, f))

# If reset transcription is true, move the transcription file to the archive folder if it exists.
if RESET_TRANSCRIPTION and os.path.exists(transcription_file_path):
    print("Moving transcription file...")
    if not os.path.exists(ARCHIVE_FOLDER):
        os.makedirs(ARCHIVE_FOLDER)
    os.rename(transcription_file_path, os.path.join(ARCHIVE_FOLDER, f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"))

# If reset summary is true, move the summary file to the archive folder if it exists.
if RESET_SUMMARY and os.path.exists(summary_file_path):
    print("Moving summary file...")
    if not os.path.exists(ARCHIVE_FOLDER):
        os.makedirs(ARCHIVE_FOLDER)
    os.rename(summary_file_path, os.path.join(ARCHIVE_FOLDER, f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"))


# Function to extract audio from video using ffmpeg
def extract_audio(video_path, audio_path=audio_file_path):
    subprocess.run(
        ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"]
    )
    return audio_path

def transcribe_audio(audio_path):
    chunks = split_audio(audio_path)
    transcription = transcribe_audio_chunks(chunks)
    return transcription

# Function to summarize text using OpenAI. Add optional context variable to add context to the text
def summarize_text(text, context=""):
    print("Summarizing text...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[{"role": "system", "content": "You are a professional blogger and author. For long conversations You are to create a very detailed summary that is at least 2 pages long of the conversation and must include names, people, places , tools, organisations and any important sound bytes. The final piece should be in markdown format and have headings, sub headings, conclusion, sentiment  and finally next steps. Here is a detailed format ##Introduction ##Topics ##Key Points ##Conclusion  ##Sentiment ##All Questions Asked ##Next Steps" + context}, 
                  {"role": "user", "content": text}],
    )
    return response.choices[0].message.content

# Function to split audio file into smaller chunks
def split_audio(audio_path, max_size_mb=24):  # Set just under the 25MB limit to be safe
    print(f"Starting to split the audio file: {audio_path}")
    # Size in bytes
    max_size = max_size_mb * 1024 * 1024
    # Get the duration of the original audio file
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", audio_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    total_duration_seconds = float(result.stdout)
    print(f"Total duration of audio: {total_duration_seconds} seconds")

    # Calculate the number of chunks needed by dividing the total size by max size
    original_file_size = os.path.getsize(audio_path)
    print(f"Original file size: {original_file_size} bytes")
    if original_file_size <= max_size:
        print("No need to split the audio as it is within the size limit.")
        return [audio_path]

    num_chunks = math.ceil(original_file_size / max_size)
    chunk_duration = total_duration_seconds / num_chunks
    print(f"Splitting the audio into {num_chunks} chunks of {chunk_duration} seconds each.")

    # Split the file using ffmpeg
    output_template = "chunk_%03d.wav"
    subprocess.run([
        "ffmpeg", "-i", audio_path, "-f", "segment",
        "-segment_time", str(chunk_duration), "-c", "copy", output_template, "-y"
    ])

    # Get all the chunk file names
    chunks = [f for f in os.listdir(".") if f.startswith("chunk_")]
    print(f"Created {len(chunks)} chunks.")
    return chunks

# Function to transcribe audio chunks
def transcribe_audio_chunks(chunks, local=LOCAL_MODE):
    print(f"Transcribing audio chunks locally: {local}")
    print("Transcribing audio chunks...")
    # Sort the chunk files to maintain the correct order
    sorted_chunks = sorted(chunks, key=lambda x: int(x.split('_')[1].split('.')[0]))
    combined_transcription = ""
    for i, chunk in enumerate(sorted_chunks, 1):
        # Print the current chunk being transcribed and the time
        print(f"Transcribing chunk {i}/{len(sorted_chunks)}: {chunk} at {datetime.now().strftime('%H:%M:%S')}")

        # transcribe locally
        if local:
            transcript = transcribe(chunk)
            print(f"Transcription complete: {len(transcript)}")
            combined_transcription += transcript
        # transcribe using OpenAI
        else:
            with open(chunk, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
                combined_transcription += transcript.text + " "
    return combined_transcription.strip()

# Get video path from .env file
video_path = os.getenv("VIDEO_PATH")
# Your OpenAI API key goes here
openai_api_key = os.getenv("OPENAI_API_KEY")

# Step 1: Extract Audio if audio file doesn't exist. If it does exist, skip this step and load the file
if not os.path.exists(audio_file_path) or RESET_EXTRACT_AUDIO:
    audio_path = extract_audio(video_path)
else:
    audio_path = audio_file_path

# # Step 2: Transcribe Audio if transcription file doesn't exist. If it does exist, skip this step and load the file
if not os.path.exists(transcription_file_path) or RESET_TRANSCRIPTION:
    print("Transcribing audio...")
    transcription = transcribe_audio(audio_path)
    print(f'Transcription complete {len(transcription)}')
    #  Save the transcription into a text document
    with open(transcription_file_path, "w") as f:
        f.write(transcription)
else:
    # Load the transcription from a text document
    print("Loading transcription from file...")
    with open(transcription_file_path, "r") as f:
        transcription = f.read()

print("Transcription:", transcription)


# Step 3: Summarize the Transcription
summary = summarize_text(transcription)

print(f'Summary complete {len(summary)}')

# Save the summary into a text document
with open(summary_file_path, "w") as f:
     f.write(summary)

print("Summary:", summary)
