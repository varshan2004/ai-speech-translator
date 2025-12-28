from pipeline.speech_pipeline import SpeechPipeline

pipeline = SpeechPipeline()

result = pipeline.process_audio(
    audio_path=r"D:\infosys springboard\asr\audio\english\test\sample-000000.wav",  # use RAW STRING
    target_lang="ta"
)

print("ORIGINAL TEXT:")
print(result["original_text"])
print("\nTRANSLATED TEXT:")
print(result["translated_text"])
print("\nAUDIO FILE:")
print(result["audio_path"])
