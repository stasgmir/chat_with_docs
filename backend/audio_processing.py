# backend/audio_processing.py
import tempfile
from pathlib import Path
from docling.document_converter import DocumentConverter, AudioFormatOption
from docling.datamodel.pipeline_options import AsrPipelineOptions
from docling.datamodel import asr_model_specs
from docling.datamodel.base_models import InputFormat
from docling.pipeline.asr_pipeline import AsrPipeline
import openai


def transcribe_audio(audio_bytes: bytes, filename: str) -> str:

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp_audio:
        tmp_audio.write(audio_bytes)
        tmp_audio_path = Path(tmp_audio.name)


    pipeline_options = AsrPipelineOptions()
    pipeline_options.asr_options = asr_model_specs.WHISPER_TURBO

    converter = DocumentConverter(
        format_options={
            InputFormat.AUDIO: AudioFormatOption(
                pipeline_cls=AsrPipeline,
                pipeline_options=pipeline_options,
            )
        }
    )


    result = converter.convert(tmp_audio_path)
    transcript = result.document.export_to_markdown()


    output_dir = Path("data/transcripts")
    output_dir.mkdir(parents=True, exist_ok=True)

    transcript_path = output_dir / f"{Path(filename).stem}.md"
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"✅ Транскрипция сохранена: {transcript_path}")

    return str(transcript_path)


def answer_question_from_transcript(transcript_path: str, api_key: str, question: str) -> str:


    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript_text = f.read()


    truncated_text = transcript_text[:12000]

    openai.api_key = api_key
    client = openai.OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты помощник, который отвечает на вопросы по транскрибированному аудио."},
            {"role": "user", "content": f"Вот текст расшифровки:\n\n{truncated_text}"},
            {"role": "user", "content": f"Вопрос: {question}"}
        ],
    )

    return completion.choices[0].message.content.strip()
