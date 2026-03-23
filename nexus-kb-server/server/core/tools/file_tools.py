import fitz
import os
def is_scanned_pdf(file_path):
  pdf_document = fitz.open(file_path)
  total_pages = pdf_document.page_count
  if (total_pages == 0):
    return False
  scanned_pages = 0
  for page_num in range(total_pages):
    page = pdf_document[page_num]
    images = page.get_images(full=True)
    if images:
      scanned_pages += 1
  pdf_document.close()
  if scanned_pages / total_pages > 0.5:
    return True
  else:
    return False

# 判断文件夹是否存在
def is_dir_exist(path: str) -> bool:
  return os.path.exists(path) and os.path.isdir(path)
# 判断文件是否存在
def is_file_exist(path: str) -> bool:
  return os.path.exists(path) and os.path.isfile(path)

# 如果文件夹不存在则创建该文件夹
def create_dir_if_not_exist(path: str) -> bool:
  if not is_dir_exist(path):
    os.makedirs(path)
    return True
  return False

def is_video(file_path):
    """
    根据文件扩展名判断是否为视频文件。
    支持的视频文件扩展名包括：.mp4, .avi, .mkv, .mov, .wmv, .flv, .webm
    """
    video_extensions = ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm']
    file_extension = file_path.lower().split('.')[-1]
    return file_extension in video_extensions
def is_audio(file_path):
    """
    根据文件扩展名判断是否为音频文件。
    支持的音频文件扩展名包括：.mp3, .wav, .ogg, .flac
    """
    audio_extensions = ['mp3', 'wav', 'ogg', 'flac']
    file_extension = file_path.lower().split('.')[-1]
    return file_extension in audio_extensions

def is_pdf(file_path):
    """
    根据文件扩展名判断是否为PDF文件。
    支持的PDF文件扩展名包括：.pdf
    """
    pdf_extensions = ['pdf']
    file_extension = file_path.lower().split('.')[-1]
    return file_extension in pdf_extensions

def is_ppt(file_path):
    """
    根据文件扩展名判断是否为PPT文件。
    支持的PPT文件扩展名包括：.ppt, .pptx, .pps, .ppsx
    """
    ppt_extensions = ['ppt', 'pptx', 'pps', 'ppsx']
    file_extension = file_path.lower().split('.')[-1]
    return file_extension in ppt_extensions

def is_word(file_path):
    """
    根据文件扩展名判断是否为Word文件。
    支持的Word文件扩展名包括：.doc, .docx
    """
    word_extensions = ['doc', 'docx']
    file_extension = file_path.lower().split('.')[-1]
    return file_extension in word_extensions

def is_markdown(file_path):
    return file_path.lower().endswith('.md')

if __name__ == "__main__":
    print(is_word('G:/App/wenkb/wenkb-server/documents/59cefa3443994b0f822f04f6e7ff0157.docx'))
