# Audio Transcription and Summarization

A Python tool to extract audio from video, transcribe the audio, and provide a summary of the content using OpenAI's Whisper and GPT-3.5 models.

## Badges

![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/mojalil/ai-summary-cli)
![GitHub last commit](https://img.shields.io/github/last-commit/mojalil/ai-summary-cli)
![GitHub issues](https://img.shields.io/github/issues-raw/mojalil/ai-summary-cli)
![GitHub pull requests](https://img.shields.io/github/issues-pr/mojalil/ai-summary-cli)
![License](https://img.shields.io/github/license/mojalil/ai-summary-cli)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.6+
- FFmpeg
- An OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mojalil/ai-summary-cli.git
```

2. Navigate to the project directory:
```bash
cd your-repo-name
```

3. Install the required Python packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following content:
```plaintext
OPENAI_API_KEY='your_openai_api_key'
VIDEO_PATH='/path_to_video_file.mp4'
# Optional settings
RESET_TRANSCRIPTION=False
RESET_EXTRACT_AUDIO=False
OUTPUT_FOLDER='./output'
```

### Usage

Run the script with the following command:
```bash
python app.py
```

## Features

- Audio extraction from any MP4 video file.
- Audio transcription using OpenAI's Whisper model.
- Conversation summarization using OpenAI's GPT-3.5 model.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Errors

If you get `cannot import name ‘OpenAI’ from ‘openai` [Source](https://community.openai.com/t/cannot-import-name-openai-from-openai/486147). Run `pip install openai --upgrade`

## Acknowledgments

- OpenAI team for providing the API for Whisper and GPT-3.5 models.
