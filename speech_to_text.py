from openai import OpenAI
import os

# Connect to OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("====================================")
print("  ARTISAN VOICE-TO-TEXT PROTOTYPE")
print("====================================")

audio_path = input("\nEnter audio file path: ").strip()

try:
    with open(audio_path, "rb") as audio_file:

        transcription = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file
        )

    print("\n-------------------------------")
    print("TRANSCRIBED TEXT")
    print("-------------------------------")

    print(transcription.text)

except FileNotFoundError:
    print("\nERROR: Audio file not found.")
    print("Check the file path and try again.")

except Exception as e:
    print("\nERROR:")
    print(e)