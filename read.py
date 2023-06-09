import os,time
from typing import List
from datetime import datetime
from files import Files,FileDOCX, FilePPTX, FilePDF, FilePDF_ReadUnable

def get_file_names(folder_path: str) -> List[str]:
    # 获取文件夹路径下的所有文件名
    file_names = []
    for file_name in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file_name)):
            file_names.append(file_name)
    return file_names

def sort_files(file_names: List[str]) -> List[str]:
    # 按文件名中的年份从大到小进行排序
    sorted_files = sorted(file_names, key=lambda x: extract_year(x), reverse=True)
    return sorted_files

def categorize_files(folder_path: str, file_names: List[str]) ->[List[Files], List[str]]:
    # 对文件名进行解析和归类
    categorized_files = []
    non_supported_files = []

    for file_name in file_names:
        file_path = os.path.join(folder_path, file_name)
        file_extension = os.path.splitext(file_name)[1].lower()

        if file_extension == '.pptx':
            file_obj = FilePPTX(folder_path)
            file_obj.file_name = file_name
            categorized_files.append(file_obj)
        elif file_extension == '.docx':
            file_obj = FileDOCX(folder_path)
            file_obj.file_name = file_name
            categorized_files.append(file_obj)
        elif file_extension == '.pdf':
            file_obj = FilePDF(folder_path)
            file_obj.file_name = file_name
            categorized_files.append(file_obj)
        else:
            non_supported_files.append(file_name)

    return categorized_files, non_supported_files

def extract_year(file_name: str) -> int:
    # 在文件名中查找年份，返回年份值，如果找不到年份则返回一个较小的值
    for year in range(1900, 2031):
        if str(year) in file_name:
            return year
    return 1800

def get_file_extension(file_name: str) -> str:
    # 获取文件的扩展名
    _, extension = os.path.splitext(file_name)
    return extension.lower()

def is_pdf_readable(file_path: str) -> bool:
    # 判断 PDF 文件是否可以复制文本
    # 这里可以使用适合的判断方式，比如检查文件是否加密或者是否有复制文本的权限
    # 这里只是一个示例，具体判断方式根据实际情况进行修改
    return True



def main():
    start_time = time.perf_counter()
    folder_path = r"C:\Users\Dell\Desktop\new"
    a = sort_files(get_file_names(folder_path))
    b,c = categorize_files(folder_path, a)
    print(b)
    print(c)
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print("程序执行时间：", execution_time, "秒")

if __name__ == "__main__":
    main()