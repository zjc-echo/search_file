import read,re,time
from files import Files,FileDOCX, FilePPTX, FilePDF, FilePDF_ReadUnable
import files
import string,unicodedata
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, QThreadPool

def process_file_content(file_content):
    # 提取页码
    page_num = file_content[0]
    # 提取文本内容
    content = file_content[1]
    # 去除换行符和空白字符
    content = content.replace('\n', '')
    content = content.translate(str.maketrans('', '', string.whitespace))
    return page_num, content

def process_documents(documents):
    processed_documents = []
    for doc in documents:
        page_num = doc[0]
        content = doc[1]
        processed_content = process_file_content([page_num, content])
        processed_documents.append(processed_content)
    return processed_documents

def extract_text_around_position(text, position):
    # 向前检索
    start_index = position
    count = 0
    while start_index > 0 and count < 30 and not is_sentence_separator(text[start_index - 1]):
        start_index -= 1
        count += 1
    
    # 向后检索
    end_index = position
    count = 0
    while end_index < len(text) - 1 and count < 30 and not is_sentence_separator(text[end_index + 1]):
        end_index += 1
        count += 1
    
    extracted_text = text[start_index:end_index+1]
    # 去除开头和结尾的标点符号
    extracted_text = remove_punctuation_from_start_and_end(extracted_text)
    return extracted_text

def is_sentence_separator(char):
    # 判断字符是否为句子分隔符号，包括句号、分号、冒号、感叹号、问号
    return char in ['。', '；', '：', '！', '？']

def remove_punctuation_from_start_and_end(text):
    # 去除开头和结尾的标点符号
    while text and is_punctuation(text[0]):
        text = text[1:]
    while text and is_punctuation(text[-1]):
        text = text[:-1]
    return text

def is_punctuation(char):
    # 判断字符是否为标点符号，包括英文和中文标点符号
    category = unicodedata.category(char)
    if category.startswith('P') or category.startswith('S'):
        return True
    return False

def find_keyword_positions(text, keyword):
    positions = []
    start_index = 0
    while True:
        # 在文本中查找关键词的位置
        index = text.find(keyword, start_index)
        if index == -1:
            # 如果找不到关键词，结束循环
            break
        else:
            # 记录关键词的位置
            positions.append(index)
            # 更新起始位置，继续查找下一个关键词位置
            start_index = index + len(keyword)
    return positions

def search_keywords(keywords, documents):
    # 实现搜索功能
    keywords[0][1] = True
    results = []
    # 第一步：在文档中搜索第一个关键词
    first_keyword = keywords[0][0]
    len_first_keyword = len(first_keyword)
    first_list = []
    for doc in documents:
        page_num = doc[0]
        content = doc[1]
        # 获取第一个关键词的位置
        keyword_positions = find_keyword_positions(content, first_keyword)
        for position in keyword_positions:
            # 调用 extract_text_around_position 函数并获取文本内容
            extracted_text = extract_text_around_position(content, position)
            # 去除开头和结尾的标点符号
            extracted_text = remove_punctuation_from_start_and_end(extracted_text)
            # 存储结果：页码、提取的文本内容、关键词位置
            first_list.append([page_num, extracted_text, [find_keyword_positions(extracted_text, first_keyword)[0],len_first_keyword],[-2,0],[-2,0]])

    results = first_list

    second_keyword, second_keyword_bool  = keywords[1][0], keywords[1][1]
    len_second_keyword = len(second_keyword)
    if second_keyword:
        if second_keyword_bool:
            for item in results:
                item[3][1] = len_second_keyword
                content = item[1]
                if second_keyword in content:
                    position = find_keyword_positions(content, second_keyword)[0]
                    item[3][0] = position
                else:
                    item[3][0] = -1
        else:
            for item in results:
                content = item[1]
                if second_keyword in content:
                    item[3][0] = -1
                else:
                    item[3][0] = -2

    third_keyword, third_keyword_bool = keywords[2][0], keywords[2][1]
    len_third_keyword = len(third_keyword)
    if third_keyword:
        if third_keyword_bool:
            for item in results:
                item[4][1] = len_third_keyword
                content = item[1]
                if third_keyword in content:
                    position = find_keyword_positions(content, third_keyword)[0]
                    item[4][0] = position
                else:
                    item[4][0] = -1
        else:
            for item in results:
                content = item[1]
                if third_keyword in content:
                    item[4][0] = -1
                else:
                    item[4][0] = -2

     # 移除结果中存在关键词位置为-1的项
    results = [item for item in results if item[3][0] != -1 and item[4][0] != -1]
    return results

def search(keywords,folder_path):
    search_details = []
    file_name_list = read.get_file_names(folder_path)
    sorted_file_name_list = read.sort_files(file_name_list)
    documents_classes,others_documents = read.categorize_files(folder_path, sorted_file_name_list) 
    for documents_class in documents_classes:
        documents_class.get_file_details()
        file_details = process_documents(documents_class.file_list)
        search_list = search_keywords(keywords, file_details)
        search_details.append([documents_class.file_name,keywords,search_list])
    return search_details

def main():
    start_time = time.perf_counter()
    folder_path = r"C:\Users\Dell\Desktop\new"
    keywords = [['算力网络',True],['枢纽',True],['',True]]
    search_details = search(keywords, folder_path)
    print(search_details)
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print("程序执行时间：", execution_time, "秒")

if __name__ == "__main__":
    main()

