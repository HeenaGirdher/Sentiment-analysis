# -*- coding: utf-8 -*-
"""Final_project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GfX37D2uX0nnPyJbN8zEIGVodoXfQR3-

###**Import the required packages**
"""

from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import nltk
import re
import pickle
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

user_agent_desktop = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '\
'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 '\
'Safari/537.36'
headers = { 'User-Agent': user_agent_desktop}

"""###**Get the reviews from Amazon**"""

cookie={}
cust_name = []
cust_rate= []
review_content= []
for i in range(1,388):
    names = []
    rating = []
    review= []
    link1='https://www.amazon.in/inches-Ready-UltraAndroid-32GA-Black/product-reviews/B07XMD275Q/ref=cm_cr_getr_d_paging_btm_next_4?ie=UTF8&reviewerType=all_reviews&pageNumber='+str(i)
    page=requests.get(link1, cookies=cookie, headers=headers)
    soup=bs(page.content)
    names=soup.find_all('span',class_='a-profile-name')
    for i in range(0,len(names)):
        cust_name.append(names[i].get_text())
    cust_name.pop(0)
    cust_name.pop(0)
    rating = soup.find_all('i',class_='review-rating')
    for i in range(0,len(rating)):
      cust_rate.append(rating[i].get_text())
    cust_rate.pop(0)
    cust_rate.pop(0)
    review = soup.find_all('span',{"data-hook":"review-body"})
    for i in range(0,len(review)):
      review_content.append(review[i].get_text())
    print(link1)

print(len(cust_name))
print(len(cust_rate))
print(len(review_content))

df = pd.DataFrame()
df

df['Customer Name']=cust_name
df['Ratings']=cust_rate
df['Reviews']=review_content
df

df.to_csv('reviews.csv',index=False, header=True)

df.isnull().sum() #check for null values

"""###**Text Preprocessing** """

import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))
wordnet = WordNetLemmatizer()

def change_text(sentence):
  sentence=str(sentence)
  sentence=sentence.lower()  #convert into lower case
  sentence=re.sub(r"http\S+"," ",sentence) #remove hyperlinks
  cleanr = re.compile('<.*?>')   #remove html tags
  cleantext = re.sub(cleanr, ' ', sentence)
  cleantext=re.sub(r'\d+', '', cleantext) #remove numbers
  cleantext=re.sub(r'[^\w\s]', '', cleantext) #remove punctuations from text
  cleantext=cleantext.strip()  # Remove leading and trailing '\n'
  cleantext=" ".join(cleantext.split())  #remove whitespaces
  word_tokens = nltk.word_tokenize(cleantext)
  word_tokens=[wordnet.lemmatize(word) for word in word_tokens if word not in stop_words] 
  cleantext=" ".join(word_tokens)
  return cleantext

df['Reviews']=df['Reviews'].apply(change_text)

df['Reviews']

type(df.Ratings)

"""##**Explore data**

###**Extract Ratings**
"""

def extract_ratings(ratings):
  ratings=re.sub('out of 5 stars','',str(ratings))
  ratings=int(float(ratings))
  return ratings
df['Ratings']=df['Ratings'].apply(extract_ratings)
df['Ratings']

"""###**Word Cloud of the Good ratings**"""

from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test = train_test_split(df['Reviews'],df['Ratings'],test_size = 0.2 , random_state = 0)

good = x_train[y_train[y_train > 3].index]
neutral = x_train[y_train[y_train == 3].index]
bad = x_train[y_train[y_train <= 2].index]

import matplotlib.pyplot as plt
from wordcloud import WordCloud 
plt.figure(figsize = (20,20)) # # Text Reviews with Good Ratings
wc = WordCloud(min_font_size = 3,  max_words = 3000 , width = 1600 , height = 800).generate(" ".join(good))
plt.imshow(wc,interpolation = 'bilinear')

"""###**Word Cloud of the bad ratings**"""

plt.figure(figsize = (20,20)) # Text Reviews with Poor Ratings
wc = WordCloud(min_font_size = 3,  max_words = 3000 , width = 1600 , height = 800).generate(" ".join(bad))
plt.imshow(wc,interpolation = 'bilinear')

"""###**WordCloud of the Neutral ratings**"""

plt.figure(figsize = (20,20)) # Text Reviews with Poor Ratings
wc = WordCloud(min_font_size = 3,  max_words = 3000 , width = 1600 , height = 800).generate(" ".join(neutral))
plt.imshow(wc,interpolation = 'bilinear')

"""###**Bar plot of the Ratings**"""

# Commented out IPython magic to ensure Python compatibility.
from matplotlib import pyplot
# %matplotlib inline

star = df['Ratings'].value_counts()
print("*** Rating distribution ***")
print(star)
star.sort_index(inplace=True)
star.plot(kind='bar',title='Amazon customer ratings',figsize=(6,6),style='Solarize_light2')

"""###**Pie chart of the Ratings**"""

df['Ratings'].value_counts().plot.pie()

"""###**WordCloud of all stopwords present in the text**"""

#Word cloud for all reviews
from wordcloud import WordCloud, STOPWORDS 
stopwords = set(STOPWORDS)       
text = " ".join(review for review in df['Reviews'])
wordcloud = WordCloud(width=1000, height=1000,stopwords=stopwords, background_color='white').generate(text) 
  # Plot the WordCloud image.You can also give the size of the WordCloud image using the figsize paramter                        
plt.figure(figsize = (8, 8), facecolor = None) 
plt.imshow(wordcloud) 
plt.axis("off") 
plt.tight_layout(pad = 0) 
plt.show()

"""###**Find the polarity of each review**"""

pip install vaderSentiment

# Create quick lambda functions to find the polarity of each review
#from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
sid_obj = SentimentIntensityAnalyzer() 
df['Reviews']= df['Reviews'].astype(str) 
pol = lambda x: sid_obj.polarity_scores(x)
df['Polarity'] = df['Reviews'].apply(pol)

df

def define_sentiment(pol):
  if pol['compound']>=0.05:
    return 'Positive'
  elif pol['compound']<=-0.05:
    return 'Negative'
  else:
      return 'Neutral'

df['Sentiment']=df['Polarity'].apply(define_sentiment)
df

df.to_csv('sentiment.csv', index=False, header=True)

df['Sentiment'].value_counts()

"""###**WordCloud of the Positive Sentiments**"""

from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test = train_test_split(df['Reviews'],df['Sentiment'],test_size = 0.2 , random_state = 0)
good = x_train[y_train[y_train == "Positive"].index]
neutral = x_train[y_train[y_train == "Neutral"].index]
bad = x_train[y_train[y_train == "Negative"].index]

import matplotlib.pyplot as plt
from wordcloud import WordCloud 
plt.figure(figsize = (20,20)) # # Text Reviews with Good Ratings
wc = WordCloud(min_font_size = 3,  max_words = 3000 , width = 1600 , height = 800).generate(" ".join(good))
plt.imshow(wc,interpolation = 'bilinear')

"""###**WordCloud of the Negative Sentiments**"""

import matplotlib.pyplot as plt
from wordcloud import WordCloud 
plt.figure(figsize = (20,20)) # # Text Reviews with Good Ratings
wc = WordCloud(min_font_size = 3,  max_words = 3000 , width = 1600 , height = 800).generate(" ".join(bad))
plt.imshow(wc,interpolation = 'bilinear')

"""###**WordCloud of the Neutral Sentiments**"""

import matplotlib.pyplot as plt
from wordcloud import WordCloud 
plt.figure(figsize = (20,20)) # # Text Reviews with Good Ratings
wc = WordCloud(min_font_size = 3,  max_words = 3000 , width = 1600 , height = 800).generate(" ".join(neutral))
plt.imshow(wc,interpolation = 'bilinear')

"""###**Bar Chart of the Sentiments**"""

df['Sentiment'].value_counts().plot.bar(title='Amazon Customer Reviews')

"""###**Pie Chart of the Sentiments**"""

df['Sentiment'].value_counts().plot.pie()

"""###**Classification of Sentiments**"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report

tfidf=TfidfVectorizer(max_features=5000) 
X=tfidf.fit_transform(df['Reviews']) 
pickle.dump(tfidf, open('transform.pkl','wb'))
y=df['Sentiment']

X.shape, y.shape

X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.3,random_state=0)

pip install imblearn

from imblearn.over_sampling import SMOTE
smote=SMOTE()

X_train_smote, y_train_smote= smote.fit_sample(X_train.astype('float'), y_train)

from collections import Counter
print("Before SMOTE:", Counter(y_train))
print("After SMOTE", Counter(y_train_smote))

from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import ComplementNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import SGDClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

"""###**Logistic Regression**"""

kfold = KFold(n_splits=10)
LR = LogisticRegression()
results = cross_val_score(LR, X_train_smote.todense(), y_train_smote, cv=kfold, scoring='accuracy')
print('Training Accuracy: %.3f' % (results.mean()*100.0))
LR.fit(X_train_smote.todense(), y_train_smote)
predictions = LR.predict(X_test)
print("Testing Accuracy:%.3f" % (accuracy_score(y_test, predictions)*100.0))
print('Confusion Matrix:\n',confusion_matrix(y_test, predictions))
print('Classification report\n', classification_report(y_test, predictions))

"""###**LinearDiscriminantAnalysis**

"""

kfold = KFold(n_splits=10)
LDA = LinearDiscriminantAnalysis()
results = cross_val_score(LDA, X_train_smote.todense(), y_train_smote, cv=kfold, scoring='accuracy')
print('Training Accuracy: %.3f' % (results.mean()*100.0))
LDA.fit(X_train_smote.todense(), y_train_smote)
predictions = LDA.predict(X_test)
print('Testing Accuracy:%.3f' % (accuracy_score(y_test, predictions)*100.0))
print('Confusion Matrix:\n',confusion_matrix(y_test, predictions))
print('Classification report\n', classification_report(y_test, predictions))

"""###**K-Nearest Neighbors**"""

kfold = KFold(n_splits=10)
KNN = KNeighborsClassifier()
results = cross_val_score(KNN, X_train_smote.todense(), y_train_smote, cv=kfold, scoring='accuracy')
print("Training Accuracy: %.3f" % (results.mean()*100.0))
KNN.fit(X_train_smote.todense(), y_train_smote)
predictions = KNN.predict(X_test.todense())
print("Testing Accuracy:%.3f" % (accuracy_score(y_test, predictions)*100.0))
print('Confusion Matrix:\n',confusion_matrix(y_test, predictions))
print('Classification report\n', classification_report(y_test, predictions))

"""###**Decision Tree**"""

kfold = KFold(n_splits=10)
CART = DecisionTreeClassifier()
results = cross_val_score(CART, X_train_smote.todense(), y_train_smote, cv=kfold, scoring='accuracy')
print("Training Accuracy: %.3f" % (results.mean()*100.0))
CART.fit(X_train_smote.todense(), y_train_smote)
predictions = CART.predict(X_test)
print("Testing Accuracy:%.3f" % (accuracy_score(y_test, predictions)*100.0))
print('Confusion Matrix:\n',confusion_matrix(y_test, predictions))
print('Classification report\n', classification_report(y_test, predictions))

"""###**Gaussian Naive Bayes**"""

kfold = KFold(n_splits=10)
GNB = GaussianNB()
results = cross_val_score(GNB, X_train_smote.todense(), y_train_smote, cv=kfold, scoring='accuracy')
print("Training Accuracy: %.3f" % (results.mean()*100.0))
GNB.fit(X_train_smote.todense(), y_train_smote)
predictions = GNB.predict(X_test.todense())
print("Testing Accuracy:%.3f" % (accuracy_score(y_test, predictions)*100.0))
print('Confusion Matrix:\n',confusion_matrix(y_test, predictions))
print('Classification report\n', classification_report(y_test, predictions))

"""###**Multinomial Naive Bayes**"""

kfold = KFold(n_splits=10)
MNB = MultinomialNB()
results = cross_val_score(MNB, X_train_smote.todense(), y_train_smote, cv=kfold, scoring='accuracy')
print("Training Accuracy: %.3f" % (results.mean()*100.0))
MNB.fit(X_train_smote.todense(), y_train_smote)
predictions = MNB.predict(X_test)
print("Testing Accuracy:%.3f" % (accuracy_score(y_test, predictions)*100.0))
print('Confusion Matrix:\n',confusion_matrix(y_test, predictions))
print('Classification report\n', classification_report(y_test, predictions))

"""###**Complement Naive Bayes**"""

kfold = KFold(n_splits=10)
CNB = ComplementNB()
results = cross_val_score(CNB, X_train_smote.todense(), y_train_smote, cv=kfold, scoring='accuracy')
print("Training Accuracy: %.3f" % (results.mean()*100.0))
CNB.fit(X_train_smote.todense(), y_train_smote)
predictions = CNB.predict(X_test)
print("Testing Accuracy:%.3f" % (accuracy_score(y_test, predictions)*100.0))
print('Confusion Matrix:\n',confusion_matrix(y_test, predictions))
print('Classification report\n', classification_report(y_test, predictions))

"""###**Bernoulli Naive Bayes**"""

kfold = KFold(n_splits=10)
BNB = BernoulliNB()
results = cross_val_score(BNB, X_train_smote.todense(), y_train_smote, cv=kfold, scoring='accuracy')
print("Training Accuracy: %.3f" % (results.mean()*100.0))
BNB.fit(X_train_smote.todense(), y_train_smote)
predictions = BNB.predict(X_test)
print("Testing Accuracy:%.3f" % (accuracy_score(y_test, predictions)*100.0))
print('Confusion Matrix:\n',confusion_matrix(y_test, predictions))
print('Classification report\n', classification_report(y_test, predictions))

"""###**Support Vector Machine**"""

kfold = KFold(n_splits=10)
SV = SVC()
results = cross_val_score(SV, X_train_smote.todense(), y_train_smote, cv=kfold, scoring='accuracy')
print("Training Accuracy: %.3f" % (results.mean()*100.0))
SV.fit(X_train_smote.todense(), y_train_smote)
predictions = SV.predict(X_test.todense())
print("Testing Accuracy:%.3f" % (accuracy_score(y_test, predictions)*100.0))
print('Confusion Matrix:\n',confusion_matrix(y_test, predictions))
print('Classification report\n', classification_report(y_test, predictions))

"""###**Stochastic Gradient Descent**"""

kfold = KFold(n_splits=10)
sgd_clf = SGDClassifier()
results = cross_val_score(sgd_clf, X_train_smote, y_train_smote, cv=kfold, scoring='accuracy')
print("Training Accuracy: %.3f" % (results.mean()*100.0))
sgd_clf.fit(X_train_smote, y_train_smote)
predictions = sgd_clf.predict(X_test)
print("Testing Accuracy:%.3f" % (accuracy_score(y_test, predictions)*100.0))
print('Confusion Matrix:\n',confusion_matrix(y_test, predictions))
print('Classification report\n', classification_report(y_test, predictions))

"""###**Gradient Boosting Classifier**"""

kfold = KFold(n_splits=10)
gb_clf = GradientBoostingClassifier()
results = cross_val_score(gb_clf, X_train_smote, y_train_smote, cv=kfold, scoring='accuracy')
print("Training Accuracy: %.3f" % (results.mean()*100.0))
gb_clf.fit(X_train_smote, y_train_smote)
predictions = gb_clf.predict(X_test)
print("Testing Accuracy:%.3f" % (accuracy_score(y_test, predictions)*100.0))
print('Confusion Matrix:\n',confusion_matrix(y_test, predictions))
print('Classification report\n', classification_report(y_test, predictions))

"""###**Random Forest**"""

from sklearn.ensemble import RandomForestClassifier
kfold = KFold(n_splits=10)
rf_clf = RandomForestClassifier()
results = cross_val_score(rf_clf, X_train_smote, y_train_smote, cv=kfold, scoring='accuracy')
print("Training Accuracy: %.3f" % (results.mean()*100.0))
rf_clf.fit(X_train_smote, y_train_smote)
predictions = rf_clf.predict(X_test)
print("Testing Accuracy:%.3f" % (accuracy_score(y_test, predictions)*100.0))
print('Confusion Matrix:\n',confusion_matrix(y_test, predictions))
print('Classification report\n', classification_report(y_test, predictions))

"""##**Save Model to disk**"""

pickle.dump(sgd_clf, open('nlp_model.pkl','wb'))