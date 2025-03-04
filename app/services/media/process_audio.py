from pydub import AudioSegment

# 音频压缩
def compress_audio(input_path, output_path, bitrate="64k"):
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="mp3", bitrate=bitrate)

# AES 加密
def encrypt_audio(input_path, output_path, key):
    cipher = Fernet(key)
    with open(input_path, "rb") as f:
        encrypted_data = cipher.encrypt(f.read())
    with open(output_path, "wb") as f:
        f.write(encrypted_data)
