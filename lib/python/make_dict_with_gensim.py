# -*- coding: utf-8 -*-
import csv
import os
from gensim import corpora, matutils, models
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import train_test_split
from collections import Counter

class MakeDictWithGensim:
  def __init__(self, csvName):
    self.base = os.path.dirname(os.path.abspath(__file__))
    self.dict_from_nouncsv = self.readNounCsv(os.path.normpath(os.path.join(self.base, "../../src/csv/"+csvName+".csv")))

  def readNounCsv(self, file):
    rawStopList = 'for a of the and to in [ ] + - , . ` / : ; | ( ) 〜 こと ごと １ & お ~ ... () :: 0235 " \' !'
    stoplist = set(rawStopList.split())
    nounCsv = []
    f = open(file, 'rt', encoding='utf-8')
    for row in csv.reader(f):
      unit_row = []
      for word in row:
        if word not in stoplist:
          unit_row.append(word)
      nounCsv.append(unit_row)
    return nounCsv

  def makeDict(self, txtName):
    dictionary = corpora.Dictionary(self.dict_from_nouncsv)
    if txtName == "qiitadicUser":
      dictionary.filter_extremes(no_below=2, no_above=0.2)
    else:
      dictionary.filter_extremes(no_below=3, no_above=0.2)
    dictionary.save_as_text(os.path.normpath(os.path.join(self.base, "../../src/txt/"+txtName+".txt")))
    return dictionary

  def vec_to_data(self,txtName):
    dictionary = self.makeDict(txtName)
    corpus = [dictionary.doc2bow(word) for word in self.dict_from_nouncsv]
    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=10)
    data = []
    for words in self.dict_from_nouncsv:
      vec = dictionary.doc2bow(words)
      vec2lsi = lsi[vec]
      dense = list(matutils.corpus2dense([vec2lsi], num_terms=len(lsi.projection.s)).T[0])
      data.append(dense)
    return data

if __name__ == '__main__':
  # Making corpus dictionary for training, user and latest articles' clustering.
  maked = MakeDictWithGensim('mecabNoun')
  whole_data = maked.vec_to_data("qiitadic")
  makedUser = MakeDictWithGensim('mecabNounUser')
  user_data = makedUser.vec_to_data('qiitadicUser')
  makedLatest = MakeDictWithGensim('mecabNounLatest')
  latest_data = makedLatest.vec_to_data('qiitadicLatest')

  estimator = RandomForestClassifier()
  data_train = []
  label_train = [1, 2, 2, 7, 8, 8, 8, 7, 10, 10, 8, 9, 2, 9, 9, 10, 9, 8, 10, 10, 10, 10, 1, 10, 1, 1, 2, 2, 8, 1, 1, 2, 1, 10, 9, 1, 10, 2, 10, 2, 1, 1, 2, 1, 1, 10, 10, 1, 1, 9, 1, 1, 2, 1, 2, 1, 3, 1, 1, 2, 1, 9, 8, 1, 1, 10, 9, 4, 9, 7, 1, 2, 1, 7, 1, 1, 1, 8, 8, 10, 10, 1, 10, 7, 10, 0, 4, 5, 6, 6, 7, 2, 1, 1, 2, 1, 1, 4, 2, 9, 1, 10, 5, 1, 1, 1, 1, 9, 1, 1, 10, 10, 1, 1, 9, 2, 10, 1, 10, 3, 2, 7, 9, 2, 1, 3, 0, 3, 1, 8, 1, 1, 1, 5, 10, 10, 5, 2, 2, 1, 5, 1, 2] 
  for num in range(0, 143):
    data_train.append(whole_data[num])
  estimator.fit(data_train, label_train)

  # Check 10 newest articles which match user favorite
  label_predict_user = estimator.predict(user_data)
  label_predict_latest = estimator.predict(latest_data)
  label_predicted_list_user = []
  label_predicted_list_latest = []
  
  for label in label_predict_user:
    label_predicted_list_user.append(label)
  counter = Counter(label_predicted_list_user)
  best_fav_catogory = counter.most_common()[0][0]
  keys = []
  labels = []
  i = 0
  for (key, label) in enumerate(label_predict_latest):
    if label == best_fav_catogory and i < 10:
      keys.append(key)
      labels.append(label)
      i = i+1

  # Display recommended article titles
  base = os.path.dirname(os.path.abspath(__file__))
  f = open(os.path.normpath(os.path.join(base, '../../src/txt/latest.txt')), 'r', encoding='utf-8')
  rows = csv.reader(f)
  articles = []
  for row in rows:
    articles.append(row)
  f2 = open(os.path.normpath(os.path.join(base, '../../src/txt/latest_url.txt')), 'r', encoding='utf-8')
  rows = csv.reader(f2)
  urls = []
  for row in rows:
    urls.append(row)
  for key in keys:
    print("======================================================")
    print(articles[key])
    print(urls[key])