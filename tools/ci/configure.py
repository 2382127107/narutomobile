import urllib.request
import zipfile
import shutil

from utils import assets_dir

OCR_DOWNLOAD_URL = (
    "https://download.maafw.xyz/MaaCommonAssets/OCR/ppocr_v6/ppocr_v6-small.zip"
)


def configure_ocr_model():
    ocr_dir = assets_dir / "resource" / "base" / "model" / "ocr"

    if ocr_dir.exists():
        print("Found existing OCR directory, skipping download.")
        return

    print(f"Downloading OCR model from {OCR_DOWNLOAD_URL}...")
    ocr_dir.mkdir(parents=True, exist_ok=True)

    zip_path = assets_dir / "resource" / "base" / "model" / "ocr.zip"
    urllib.request.urlretrieve(OCR_DOWNLOAD_URL, zip_path)

    print("Extracting OCR model...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(ocr_dir)

    zip_path.unlink()

    # 下面是移除ocr.zip解压后的small文件夹,直接把onnx文件放在ocr目录下
    small_dir = ocr_dir / "small"
    if small_dir.exists() and small_dir.is_dir():
        print("Moving contents from 'small' subdirectory up to OCR root...")
        for item in small_dir.iterdir():
            target = ocr_dir / item.name
            shutil.move(str(item), str(target))
        small_dir.rmdir()

    print("OCR model configured successfully.")


if __name__ == "__main__":
    configure_ocr_model()
    print("OCR model configured.")
