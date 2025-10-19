# backend/pdf_utils.py
import tempfile, os, re, cv2
from pdf2image import convert_from_path
import layoutparser as lp
import  numpy as np
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


ocr_agent = lp.TesseractAgent(languages="eng+rus")


model_publay = lp.Detectron2LayoutModel(
    'lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.6],
    label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
)



def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ").replace("\x0c", " ").strip()
    text = re.sub(r"-\s*\n\s*", "", text)
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\b\d+\b", "", text)
    return text.strip()



def extract_text_chunks(file_bytes: bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name

    docs = []
    try:

        images = convert_from_path(tmp_path)
        print(f" Конвертировано {len(images)} страниц PDF в изображения.")

        for page_idx, image in enumerate(images):
            image_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)[..., ::-1]

            layout = model_publay.detect(image_rgb)
            text_blocks = [b for b in layout if b.type in ["Text", "Title", "List"]]

            page_text = []
            for block in text_blocks:
                segment_image = block.pad(5, 5, 5, 5).crop_image(image_rgb)
                text = ocr_agent.detect(segment_image).strip()
                if text:
                    page_text.append(text)

            if page_text:
                combined = " ".join(page_text)
                clean = clean_text(combined)
                docs.append(Document(page_content=clean, metadata={"page": page_idx}))


        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", " "],
        )
        chunks = splitter.split_documents(docs)
        print(f"Извлечено {len(chunks)} фрагментов текста.")
        return chunks

    except Exception as e:
        raise RuntimeError(f"Ошибка при OCR-анализе PDF: {e}") from e

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
