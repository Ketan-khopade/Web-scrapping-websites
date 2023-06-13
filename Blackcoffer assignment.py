#  importing required libraries
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import os
import string
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import re
from collections import Counter

# getting input data
data = pd.read_excel(r"D:\python DSA\classroom technogeeks\datasets\Input.xlsx")
# createing folder to save text files
os.makedirs('web_extraction_folder')


# creating func that scrap the website and store all info in text file inside upper folder
def func_for_web_extraction():
    for i in range(len(data)):
        file_path = os.path.join('web_extraction_folder',
                                 f"text_file.no-{data['URL_ID'][i]}")  # creating text file to save article
        html_data = requests.get(data['URL'][i]).text  # getting html content
        soup = BeautifulSoup(html_data, 'html.parser')  # using Beautiful soup for scraping
        try:
            heading = soup.find('h1').text  # trying to get article headline
        except:
            heading = ''
        try:
            article = ''
            for j in soup.find_all('article'):  # scraping a whole website
                for k in j.find_all('p'):
                    article += k.text
        except:
            article = ''
        with open(file_path, 'w', encoding='utf-8') as a:  # saving this text in file
            a.write(heading + '\n' + article)


func_for_web_extraction()
# creating list of all stopwords of that you gave us and nltk library
stopwords_list = ['Auditor', 'Currencies', 'DatesandNumbers', 'Generic', 'GenericLong', 'Geographic']
total_stopwords = stopwords.words('english')
for i in stopwords_list:
    file_path = os.open(f'StopWords/StopWords_{i}.txt', os.O_RDONLY)
    with open(file_path, 'r') as a:
        for j in a.readlines():
            if '|' in j:
                total_stopwords.extend(j.replace('\n', '').replace(' ', '').lower().split('|'))
            else:
                total_stopwords.append(j.replace('\n', '').lower())
total_stopwords = list(set(total_stopwords))
# creating list of negative and positive words

negative_words = []
positive_words = []
for i in ['negative-words', 'positive-words']:
    file_path = os.open(f'MasterDictionary/{i}.txt', os.O_RDONLY)
    with open(file_path, 'r') as a:
        for j in a.readlines():
            if i == 'negative-words':
                negative_words.append(j.replace('\n', '').lower())
            else:
                positive_words.append(j.replace('\n', '').lower())

            # creating functions that calculate total positive ,negative, polarity,syllable,complex_words,personal pronounce


def positive_scor(text):
    positive_sco = 0
    negative_sco = 0
    for i in text:
        if i in positive_words:
            positive_sco += 1
        elif i in negative_words:
            negative_sco += -1

    return [positive_sco, negative_sco * -1]


def polarity_scor(positive_score, negative_score):
    return round((positive_score - negative_score) / ((positive_score + negative_score) + 0.000001), 2)


def syllable_complexwords(word_token):
    syllable_count = 0
    complex_words_count = 0
    for i in word_token:
        if i.endswith('es') or i.endswith('ed'):
            word_dict = Counter(i[len(i) - 2])
            sum_count = sum([word_dict['a'], word_dict['e'], word_dict['i'], word_dict['o'], word_dict['u']])
            if sum_count > 2:
                complex_words_count += 1
                syllable_count += sum_count
            else:
                syllable_count += sum_count
        else:
            word_dict = Counter(i)
            sum_count = sum([word_dict['a'], word_dict['e'], word_dict['i'], word_dict['o'], word_dict['u']])
            if sum_count > 2:
                complex_words_count += 1
                syllable_count += sum_count
            else:
                syllable_count += sum_count
    return syllable_count, complex_words_count


def personal_pronoun(word_token):
    word_count = 0
    for i in word_token:
        if i in ['I', 'We', 'my', 'ours', 'us']:
            word_count += 1
    return word_count


# creating main function that they calculate all whole output table for all text files

def calc():
    output_array = []
    for i in range(len(data)):
        url = data['URL'][i]
        url_id = data['URL_ID'][i]
        try:  # try diffrent encoding if this two not works
            with open(f"web_extraction_folder/text_file.no-{data['URL_ID'][i]}", encoding='utf-8') as a:
                text = a.read()
        except:
            with open(f"web_extraction_folder/text_file.no-{data['URL_ID'][i]}", encoding='ansi') as a:
                text = a.read()
        sent_token = sent_tokenize(text.lower())
        text = re.sub('\s', ' ', text.translate(str.maketrans('', '', string.punctuation)))
        word_token = word_tokenize(text.lower())
        personal_pronouns = personal_pronoun(word_tokenize(text))
        for i in word_token:
            if i in total_stopwords:
                word_token.remove(i)
            else:
                pass
        if len(word_token) > 0:  # here we will get all values
            positive_score, negative_score = positive_scor(word_token)[0], positive_scor(word_token)[1]
            polarity_score = polarity_scor(positive_score, negative_score)
            subjectvity_scor = lambda x, y, z: (x + y) / ((z) + 0.000001)
            subjectvity_score = round(subjectvity_scor(positive_score, negative_score, len(word_token)), 2)
            avg_sent_len = sum([len(i.split(' ')) / len(sent_token) for i in sent_token]) / len(sent_token)
            syllable, complex_words = syllable_complexwords(word_token)[0], syllable_complexwords(word_token)[1]
            percent_complex_words = round(complex_words / len(word_token), 2) * 100
            fog_index = round(0.4 * (avg_sent_len + percent_complex_words), 2)
            avg_no_words_per_sent = round(len(word_token) / len(sent_token), 2)
            avg_word = round(sum([len(i) for i in word_token]) / len(word_token), 2)
            word_count = len(word_token)
            output_array.append(
                [url_id, url, positive_score, negative_score, polarity_score, subjectvity_score, avg_sent_len,
                 percent_complex_words,
                 fog_index, avg_no_words_per_sent, complex_words, word_count, syllable, personal_pronouns, avg_word])
        else:  # it is for if any file cant hhave any info
            output_array.append([url_id, url, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    return output_array


# creating pandas dataframe
output_data = pd.DataFrame(calc(), columns=['URL_ID', 'URL', 'POSITIVE_SCORE', 'NEGATIVE_SCORE', 'POLARITY_SCORE',
                                            'SUBJECTIVITY_SCORE', 'AVG_SENTENCE_LEN', 'PERCENTAGE_OF_COMPLEX',
                                            'FOG_INDEX', 'AVG_NO_OF_WORDS', 'COMPLEX_WORD_COUNT', 'WORD_COUNT',
                                            'SYALLABLE_PER_WORD', 'PERSONAL_PRONOUNS', 'AVG_WORD_LENGTH'])
# saving the excel file
output_data.to_excel('output_data.xlsx')
