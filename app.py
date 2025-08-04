import os
import cv2
import subprocess
import streamlit as st
import re

# ========= Utility =========
def sanitize_filename(url):
    # Replace non-alphanumeric characters with underscores
    return re.sub(r'\W+', '_', url)

# ========= Download video =========
def download_video_ytdlp(youtube_url):
    video_id = sanitize_filename(youtube_url)[-10:]  # Use last part of URL
    output_filename = f"video_{video_id}.mp4"

    st.info(f"📥 Downloading video to '{output_filename}'...")

    command = [
        "yt-dlp",
        "-f", "best",
        "-o", output_filename,
        youtube_url
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        st.error("❌ Failed to download the video. Please check the URL and try again.")
        return None

    return output_filename

# ========= Extract frames =========
def extract_frames(video_path, output_folder="frames", frame_skip=1):
    os.makedirs(output_folder, exist_ok=True)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        st.error("❌ Error: Cannot open video file.")
        return []

    frame_count = 0
    saved_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    progress = st.progress(0)

    while True:
        success, frame = cap.read()
        if not success:
            break

        if frame_count % frame_skip == 0:
            frame_filename = os.path.join(output_folder, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
            saved_count += 1

        frame_count += 1
        progress.progress(min(1.0, frame_count / total_frames))

    cap.release()
    st.success(f"✅ Done! {saved_count} frames saved in '{output_folder}'.")
    return [os.path.join(output_folder, f) for f in sorted(os.listdir(output_folder)) if f.endswith(".jpg")]

# ========= Streamlit UI =========
st.set_page_config(page_title="🎞️ YouTube Frame Extractor", layout="centered")
st.title("🎞️ YouTube Video Frame Extractor")

youtube_url = st.text_input("🔗 Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
frame_skip = st.number_input("📸 Frame skip (1 = every frame, 2 = every other...)", min_value=1, value=1)

if st.button("🚀 Download & Extract Frames"):
    if youtube_url.strip():
        with st.spinner("⏳ Processing..."):
            video_path = download_video_ytdlp(youtube_url.strip())
            if video_path:
                frames = extract_frames(video_path, output_folder="extracted_frames", frame_skip=frame_skip)

                if frames:
                    st.write("### 🖼️ Sample Extracted Frames:")
                    for frame_file in frames[:5]:
                        st.image(frame_file, width=300)
    else:
        st.warning("⚠️ Please enter a valid YouTube URL.")

 