# Импортируем необходимые библиотеки
from sentence_transformers import SentenceTransformer, util
import numpy as np
import pandas as pd

# Загружаем предобученную модель для векторизации текста
# Модель "paraphrase-multilingual-MiniLM-L12-v2" поддерживает несколько языков, включая русский
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

#Набор данных
faq_df = pd.read_excel('faq_new2.xlsx')
texts = [faq_df["ответы"].tolist()][0]
tegs = [faq_df["тэги"].tolist()][0]

banword = ["он, мы, его, вы, вам, вас, ее, что, который, их, все, они, я, весь, мне, меня, таким, для, на, по, со, из, от, до, без, над, под, за, при, после, во, же, то, бы, всего, итого, даже, да, нет, ой, ого, эх, браво, здравствуйте, спасибо, извините".replace(",","").split()][0]
def text_clear(query:str):
    ignorechars = r''',:\—=/|'%*"?<>!-_'''
    print(query)
    query = str(query).lower()
    queryC = ""
    for i in query:
        if i not in ignorechars:
            queryC += i

    banwordC = ""
    for i in queryC.split():
        if i not in banword:
            banwordC += i+" "
    return banwordC

tegsC = [text_clear(i) for i in tegs]

text_embeddings = model.encode(tegsC, convert_to_tensor=True)
def semantic_search(query, embeddings, textS, top_n=3):
    # Векторизуем запрос
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Вычисляем косинусное сходство между запросом и каждым текстом
    similarities = util.pytorch_cos_sim(query_embedding, embeddings)[0]

    # Получаем индексы наиболее похожих текстов
    top_results = np.argsort(similarities.cpu().numpy())[-top_n:][::-1]
    # Печатаем результаты
    print("Запрос:", query)
    print("Наиболее похожие тексты:")
    if float(similarities[top_results[0]]) > 0.65:
        print(texts[top_results[0]], similarities[top_results[0]])
        return texts[top_results[0]]

def start_ai(queryC):
    response = semantic_search(queryC, text_embeddings, tegsC)
    return response

query = "здравствуйте, я не сдал егэ"
#queryC = text_clear(query)

#semantic_search(queryC, text_embeddings, textsC)