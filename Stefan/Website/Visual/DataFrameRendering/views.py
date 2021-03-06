from django.shortcuts import HttpResponse
from django.shortcuts import render
import pandas as pd
from django.views.generic import ListView
import json
import DataFrameRendering.apps as apps
import numpy as np
from DataFrameRendering.models import ReviewData
from django import forms
import datetime
import matplotlib as plt
from matplotlib.pyplot import subplots as sub
from io import StringIO
import plotly.graph_objects as go
# Import the wordcloud library
from wordcloud import WordCloud
from datetime import datetime
from plotly.subplots import make_subplots
import random
import ipywidgets
import nltk
import nltk.sentiment.util
from nltk.tokenize import sent_tokenize, word_tokenize
import pprint
import re
import gensim
import gensim.corpora as corpora
import os
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
import string
import math

# todo add a method to add links
"""
The url of the webpage. Here so it can changed easily later
"""
# todo change
webpageUrl = "http://127.0.0.1:8000"

# todo add date filtering
"""
filters the dataframe and only selects the rows in the dataframe that meet the criteria
:param ReviewDataFrame: A dataframe of all of the reviews
:param context: a contianer dictonary of all of the url parameters
:return: A filtered set of data that contains the correct data for the parameters
"""


def filter_Data_Frame(ReviewDataFrame, context,sample = False):
    print("Filtering data")

    if not sample:
        filteredDataFrame = apps.ReviewDataFrame.copy()
    else:
        filteredDataFrame = apps.ExtraDataFrame.copy()
    param = '_param'

    customer_id_param = context["customer_id" + param]
    if customer_id_param != "":
        filteredDataFrame = filteredDataFrame[filteredDataFrame['customer_id'].str.contains(customer_id_param)]

    review_id_param = context["review_id" + param]
    if review_id_param != "":
        filteredDataFrame = filteredDataFrame[filteredDataFrame['review_id'].str.contains(review_id_param)]

    product_id_param = context["product_id" + param]
    if product_id_param != "":
        filteredDataFrame = filteredDataFrame[filteredDataFrame['product_id'].str.contains(product_id_param)]

    product_parent_param = context["product_parent" + param]
    if product_parent_param != "":
        filteredDataFrame = filteredDataFrame[filteredDataFrame['product_parent'].str.contains(product_parent_param)]

    product_title_param = context["product_title" + param]
    if product_title_param != "":
        filteredDataFrame = filteredDataFrame[filteredDataFrame['product_title'].str.contains(product_title_param)]

    star_rating_min_param = context["star_rating_min" + param]
    if star_rating_min_param != 1:
        filteredDataFrame = filteredDataFrame[filteredDataFrame['star_rating'] >= star_rating_min_param]

    star_rating_max_param = context["star_rating_max" + param]
    if star_rating_max_param != 5:
        filteredDataFrame = filteredDataFrame[filteredDataFrame['star_rating'] <= star_rating_max_param]

    helpful_votes_min_param = context["helpful_votes_min" + param]
    if helpful_votes_min_param != 0:
        filteredDataFrame = filteredDataFrame[filteredDataFrame['helpful_votes'] >= helpful_votes_min_param]

    helpful_votes_max_param = context["helpful_votes_max" + param]
    if helpful_votes_max_param != float('inf'):
        filteredDataFrame = filteredDataFrame[filteredDataFrame['helpful_votes'] <= helpful_votes_max_param]

    total_votes_min_param = context["total_votes_min" + param]
    if total_votes_min_param != 0:
        filteredDataFrame = filteredDataFrame[filteredDataFrame['total_votes'] >= total_votes_min_param]

    total_votes_max_param = context["total_votes_max" + param]
    if total_votes_max_param != float('inf'):
        filteredDataFrame = filteredDataFrame[filteredDataFrame['total_votes'] <= total_votes_max_param]

    vine_param = context["vine" + param]
    print(vine_param)
    if vine_param != "Both" and vine_param != "":
        print("should not trigger " + vine_param)
        filteredDataFrame = filteredDataFrame[filteredDataFrame['vine'] == vine_param]

    Verified_purchase_param = context["Verified_purchase" + param]
    print(Verified_purchase_param)
    if Verified_purchase_param != "Both" and Verified_purchase_param != "":
        print(Verified_purchase_param + " Should not trigger")
        filteredDataFrame = filteredDataFrame[filteredDataFrame['verified_purchase'] == Verified_purchase_param]



    review_headline_param = context["review_headline" + param]
    if review_headline_param != "":
        filteredDataFrame = filteredDataFrame[filteredDataFrame['review_headline'].str.contains(review_headline_param)]

    review_body_param = context["review_body" + param]
    if review_body_param != "":
        filteredDataFrame = filteredDataFrame[filteredDataFrame['review_body'].str.contains(review_body_param)]

    start_date_param = context["start_date" + param]
    if start_date_param != "" and start_date_param != "dd/mm/yyyy":
        pass
        filteredDataFrame = filteredDataFrame[filteredDataFrame['review_date'] >= start_date_param]

    end_date_param = context["end_date" + param]
    if end_date_param != "" and end_date_param != "dd/mm/yyyy":
        pass
        filteredDataFrame = filteredDataFrame[filteredDataFrame['review_date'] <= end_date_param]

    duplicate_param = context["Duplicate_reviews" + param]
    print(duplicate_param )
    if duplicate_param  != "Both" and duplicate_param  != "":
        duplicates = filteredDataFrame.duplicated(subset=['review_body'], keep=False)
        getOnlyDuplicates =  duplicate_param == "Y"
        print(getOnlyDuplicates)
        print("should not trigger " + duplicate_param)
        filteredDataFrame = filteredDataFrame[duplicates == getOnlyDuplicates]

    print("Finished filtering data")
    numberPerPage = context['number_per_page' + param]
    pageNum = max(int(context['page_num' + param]), 1)
    return filteredDataFrame[(pageNum - 1) * numberPerPage:numberPerPage * pageNum]


"""
Displays the table for the reviews as well as the search
:param request: the request made to the server
:return: a render object that will be displayed on the browser
"""


def get_reviews(request):
    global webpageUrl

    # ensure_data_loaded()
    # creates a context object dictoniary to use
    context = create_context(request)

    # seperated for testing if parameter is a then load 10 results

    filteredDataFrame = filter_Data_Frame(apps.ReviewDataFrame, context)

    print("Starting adding links")
    # add a links feild so it can be used in the html to use the link
    links = []
    j = 0
    for i, row in filteredDataFrame.iterrows():
        links.append(webpageUrl + "/product/?id=" + filteredDataFrame.iloc[j, 2])
        j += 1
    filteredDataFrame["link"] = links
    print("Added links")

    # add a links feild so it can be used in the html to use the link
    customerLinks = []
    j = 0
    for i, row in filteredDataFrame.iterrows():
        customerLinks.append(webpageUrl + "/customer/?id=" + filteredDataFrame.iloc[j, 0])
        j += 1
    filteredDataFrame["customerLinks"] = customerLinks
    print("Added links")
    print( len(filteredDataFrame))
    filteredDataFrame = run_lda_model_short(df = filteredDataFrame)
    filteredDataFrame['health_hazard'] = filteredDataFrame['health_hazard'].fillna(0)
    if (context[ 'health_hazard_param']):
        filteredDataFrame = filteredDataFrame[filteredDataFrame['health_hazard'] == 1.0]
    print(len(filteredDataFrame))
    # convert to json
    json_records = filteredDataFrame.reset_index().to_json(orient='records')
    data = json.loads(json_records)

    context['data'] = data
    print("About to render")
    return render(request, 'DataFrameRendering/Reviews.html', context)


"""
Displays the table for the sample reviews as well as the search
:param request: the request made to the server
:return: a render object that will be displayed on the browser
"""


def get_extra(request):
    global webpageUrl

    # ensure_data_loaded()
    # creates a context object dictoniary to use
    context = create_context(request)

    # seperated for testing if parameter is a then load 10 results

    filteredDataFrame = filter_Data_Frame(apps.ExtraDataFrame, context,True)
    print(filteredDataFrame.columns)
    print("Starting adding links")
    # add a links feild so it can be used in the html to use the link
    links = []
    j = 0
    for i, row in filteredDataFrame.iterrows():
        links.append(webpageUrl + "/product/?id=" + filteredDataFrame.iloc[j, 1])
        j += 1
    filteredDataFrame["link"] = links
    print("Added links")

    # add a links feild so it can be used in the html to use the link
    customerLinks = []
    j = 0
    for i, row in filteredDataFrame.iterrows():
        customerLinks.append(webpageUrl + "/customer/?id=" + filteredDataFrame.iloc[j, 0])
        j += 1
    filteredDataFrame["customerLinks"] = customerLinks
    print("Added links")
    print( len(filteredDataFrame))
    #filteredDataFrame = run_lda_model_short(df = filteredDataFrame)
    #filteredDataFrame['health_hazard'] = filteredDataFrame['health_hazard'].fillna(0)
    if (context[ 'health_hazard_param']):
        filteredDataFrame = filteredDataFrame[filteredDataFrame['health_hazard'] == 1.0]
    #print(len(filteredDataFrame))
    # convert to json
    json_records = filteredDataFrame.reset_index().to_json(orient='records')
    data = json.loads(json_records)

    context['data'] = data
    print("About to render")
    return render(request, 'DataFrameRendering/ReviewsExtra.html', context)





"""
Creates a context with all of the arguments from the url
:param request: the request made to the server
:param data: a panda dataframe to use to display information in the template
:return: dict_of_parameters a dictonary of the data and any arguments from the url
"""


def create_context(request):
    global webpageUrl
    param = "_param"
    dict_of_parameters = {'customer_id' + param: request.GET.get("customer_id", ""),
                          'review_id' + param: request.GET.get("review_id", ""),
                          'product_id' + param: request.GET.get("product_id", ""),
                          'product_parent' + param: request.GET.get("product_parent", ""),
                          'product_title' + param: request.GET.get("product_title", ""),
                          'star_rating_min' + param: request.GET.get("star_rating_min", 1),
                          'star_rating_max' + param: request.GET.get("star_rating_max", 5),
                          'helpful_votes_min' + param: request.GET.get("helpful_votes_min", ""),
                          'helpful_votes_max' + param: request.GET.get("helpful_votes_max", ""),
                          'total_votes_min' + param: request.GET.get("total_votes_min", ""),
                          'total_votes_max' + param: request.GET.get("total_votes_max", ""),
                          'vine' + param: request.GET.get("vine", "Both"),
                          'Verified_purchase' + param: request.GET.get("Verified_purchase", "Both"),
                          'review_headline' + param: request.GET.get("review_headline", ""),
                          'review_body' + param: request.GET.get("review_body", ""),
                          'start_date' + param: request.GET.get("start_date", "dd/mm/yyyy"),
                          'end_date' + param: request.GET.get("end_date", "dd/mm/yyyy"),
                          'Duplicate_reviews' + param: request.GET.get("Duplicate_reviews", "Both"),
                          'health_hazard' + param:request.GET.get("health_hazard", False),
                          'number_per_page' + param: request.GET.get("number_per_page", 100),
                          'page_num' + param: request.GET.get("page_num", 1),
                          "home_url": webpageUrl + "/",
                          "reviews_url": webpageUrl + "/reviews",
                          "products_url": webpageUrl + "/products?page_num=1",
                          "next_products_url":  "location.href=" + webpageUrl + "/products?page_num=" + str(int(request.GET.get("page_num", 1)) + 1),
                          "last_products_url": "location.href=" + webpageUrl + "/products?page_num=" + str(int(request.GET.get("page_num", 1)) - 1),
                          "customers_url": webpageUrl + "/customers",
                          "upload_files_url": webpageUrl + "/upload",
                          "run_model_url" : webpageUrl + "/run_model",
                          "sample_url": webpageUrl + "/sample"
                          }
    star_ratings = [1, 2, 3, 4, 5, "1", "2", "3", "4", "5"]
    if dict_of_parameters['star_rating_min' + param] == "":
        dict_of_parameters['star_rating_min' + param] = 1
    elif dict_of_parameters['star_rating_min' + param] not in star_ratings:
        dict_of_parameters['star_rating_min' + param] = 1
    else:
        dict_of_parameters['star_rating_min' + param] = int(dict_of_parameters['star_rating_min' + param])

    if dict_of_parameters['star_rating_max' + param] == "":
        dict_of_parameters['star_rating_max' + param] = 5
    elif dict_of_parameters['star_rating_max' + param] not in star_ratings:
        dict_of_parameters['star_rating_max' + param] = 5
    else:
        dict_of_parameters['star_rating_max' + param] = int(dict_of_parameters['star_rating_max' + param])

    if dict_of_parameters['helpful_votes_min' + param] == "":
        dict_of_parameters['helpful_votes_min' + param] = 0
    else:
        try:
            dict_of_parameters['helpful_votes_min' + param] = int(dict_of_parameters['helpful_votes_min' + param])
        except:
            dict_of_parameters['helpful_votes_min' + param] = 0

    if dict_of_parameters['helpful_votes_min' + param] == "":
        dict_of_parameters['helpful_votes_max' + param] = float('inf')
    else:
        try:
            dict_of_parameters['helpful_votes_max' + param] = int(dict_of_parameters['helpful_votes_max' + param])
        except:
            dict_of_parameters['helpful_votes_max' + param] = float('inf')

    if dict_of_parameters['total_votes_min' + param] == "":
        dict_of_parameters['total_votes_min' + param] = 0
    else:
        try:
            dict_of_parameters['total_votes_min' + param] = int(dict_of_parameters['total_votes_min' + param])
        except:
            dict_of_parameters['total_votes_min' + param] = 0

    if dict_of_parameters['total_votes_min' + param] == "":
        dict_of_parameters['total_votes_max' + param] = float('inf')
    else:
        try:
            dict_of_parameters['total_votes_max' + param] = int(dict_of_parameters['total_votes_max' + param])
        except:
            dict_of_parameters['total_votes_max' + param] = float('inf')

    try:
        date = datetime.datetime.strptime(dict_of_parameters['start_date' + param],'%y/%m/%d')
        if date != None:
            dict_of_parameters['start_date' + param] = date
        else:
            dict_of_parameters['start_date' + param] = "dd/mm/yyyy"
    except:
        dict_of_parameters['start_date' + param] = "dd/mm/yyyy"


    try:
        date = datetime.datetime.strptime(dict_of_parameters['end_date' + param],'%y/%m/%d')
        if date != None:
            dict_of_parameters['end_date' + param] = date
        else:
            dict_of_parameters['end_date' + param] = "dd/mm/yyyy"
    except:
        dict_of_parameters['end_date' + param] = "dd/mm/yyyy"

    if dict_of_parameters['number_per_page' + param] == "":
        dict_of_parameters['number_per_page' + param] = 100
    else:
        try:
            dict_of_parameters['number_per_page' + param] = int(dict_of_parameters['number_per_page' + param])
        except:
            dict_of_parameters['number_per_page' + param] = 100

    if dict_of_parameters['page_num' + param] == "":
        dict_of_parameters['page_num' + param] = 1
    else:
        try:
            dict_of_parameters['page_num' + param] = int(dict_of_parameters['page_num' + param])
        except:
            dict_of_parameters['page_num' + param] = 1



    return dict_of_parameters


"""
Displays the table for the products
:param request: the request made to the server
:return: a render object that will be displayed on the browser
"""


def get_products(request):
    # ensure_data_loaded(reviewData=False)
    context = create_context(request)

    df = apps.ProductDataFrame[100 *  (int(context["page_num_param" ])-1):100 * int(context["page_num_param"])]

    # add a links feild so it can be used in the html to use the link
    links = []
    j = 0
    for i, row in df.iterrows():
        links.append(webpageUrl + "/product/?id=" + df.iloc[j, 1])
        j += 1
    df["link"] = links

    # parsing the DataFrame in json format.
    json_records = df.reset_index().to_json(orient='records')
    data = json.loads(json_records)

    # creats a context dictonary

    context['data'] = data
    return render(request, 'DataFrameRendering/Products.html', context)



"""
Displays the table for the customers
:param request: the request made to the server
:return: a render object that will be displayed on the browser
"""


def get_customers(request):
    context = create_context(request)

    df = apps.CustomerDataFrame[:100]

    # add a links feild so it can be used in the html to use the link
    links = []
    j = 0
    for i, row in df.iterrows():
        links.append(webpageUrl + "/customer/?id=" + str(df.iloc[j, 1]))
        j += 1
    df["link"] = links

    # parsing the DataFrame in json format.
    json_records = df.reset_index().to_json(orient='records')
    data = json.loads(json_records)

    # creats a context dictonary

    context['data'] = data
    return render(request, 'DataFrameRendering/Customers.html', context)


def word_cloud(words, max_words, colour, contour_width=3, background_color='white'):
    # Join the different processed titles together.
    long_string = ','.join(list(words))

    # Create a WordCloud object
    wordcloud = WordCloud(background_color=background_color, max_words=max_words,
                          contour_width=contour_width, contour_color=colour)

    # Generate a word cloud
    wordcloud.generate(long_string)

    return wordcloud



"""
This displays the info for a product with an id
:param request: the request made to the server
:return: a render object that will be displayed on the browser
"""


def get_product_with_id(request):
    # ensure_data_loaded()
    context = create_context(request)

    # generate data for the review
    row_number = apps.ProductDataFrame['product_id'] == request.GET.get("id", "b")
    json_records = apps.ProductDataFrame[row_number].reset_index().to_json(orient='records')
    product_data = json.loads(json_records)

    # generate data for the product
    row_numbers_review = apps.ReviewDataFrame['product_id'] == request.GET.get("id", "b")

    json_records = apps.ReviewDataFrame[row_numbers_review].reset_index().to_json(orient='records')
    review_data = json.loads(json_records)

    # generate context dictionary

    context["reviewData"] = review_data
    context["data"] = product_data
    graph = review_scores_timeframe(df = apps.ReviewDataFrame[row_numbers_review],timeframe='W',xtitle = "Dates",ytitle='number of reviews',title='Average score and number of reviews per product')
    context["graph"] = graph.to_html(full_html=False, default_height=500, default_width=700)
    return render(request, 'DataFrameRendering/SingleProduct.html', context)


"""
This displays the info for a product with an id
:param request: the request made to the server
:return: a render object that will be displayed on the browser
"""


def get_customer_with_id(request):
    # ensure_data_loaded()
    context = create_context(request)

    # generate data for the review
    row_number = apps.CustomerDataFrame['customer_id'] == request.GET.get("id", "b")
    json_records = apps.CustomerDataFrame[row_number].reset_index().to_json(orient='records')
    product_data = json.loads(json_records)

    # generate data for the product
    row_numbers_review = apps.ReviewDataFrame['customer_id'] == request.GET.get("id", "b")
    json_records = apps.ReviewDataFrame[row_numbers_review].reset_index().to_json(orient='records')
    review_data = json.loads(json_records)

    # generate context dictionary

    context["reviewData"] = review_data
    context["data"] = product_data
    return render(request, 'DataFrameRendering/SingleCustomer.html', context)


def run_model_analaysis(request):
    context = create_context(request)
    context["accuracy"] = run_lda_model(df =  apps.ReviewDataFrame)
    return render(request, 'DataFrameRendering/RunModel.html', context)



from nltk.stem.porter import PorterStemmer


def run_lda_model(df):
    stemmer = PorterStemmer()
    try:
        df = df.drop(["marketplace", "customer_id", "product_parent", "product_category", "review_date"], axis=1)
    except:
        pass
    df = df[~df['review_body'].isnull()]
    df['review_body'] = df['review_headline'] + '. ' + df['review_body']
    df["health_hazard"] = np.nan
    df = df.set_index("review_id")
    neg_reviews = df.query("star_rating < 4", engine="python")
    stop_words = stopwords.words('english')
    stop_words.extend(['br'])
    translator = str.maketrans('', '', string.punctuation)

    # neg_reviews["tokened_review"] = np.nan
    all_tokens = []
    # neg_reviews.astype({"tokened_review": 'object'}).dtypes
    for index, row in neg_reviews.iterrows():
        text = row["review_body"].lower()
        text = text.translate(translator)
        text = word_tokenize(text)
        new_text = []
        for token in text:
            token = stemmer.stem(token)
            if token not in stop_words:
                new_text.append(token)
        all_tokens.append(new_text)
    neg_reviews["tokened_review"] = all_tokens
    hazardous_words = ["rotten", "mouldy", "moldy", "mold", "mould", "sick", "dangerous", "diarrhea", "poisoning",
                       "stale"]
    for word in hazardous_words:
        neg_reviews.loc[
            [word in tokened_review for tokened_review in neg_reviews["tokened_review"]], "health_hazard"] = 1
    num_labeled = len(neg_reviews.query("health_hazard == 1", engine="python"))
    non_hazardous = neg_reviews.query("health_hazard != 1 and polarity < 0", engine="python").sample(num_labeled)
    labeled = neg_reviews.query("health_hazard == 0 or health_hazard == 1", engine="python")
    reviews = labeled.loc[:, 'tokened_review'].values
    y = labeled.loc[:, 'health_hazard'].values
    for i in list(non_hazardous.index):
        neg_reviews.loc[i, "health_hazard"] = 0
    for i in range(len(reviews)):
        reviews[i] = ' '.join(reviews[i])
    from sklearn.feature_extraction.text import TfidfVectorizer
    matrix = TfidfVectorizer(max_features=200)
    X = matrix.fit_transform(reviews).toarray()
    # split train and test data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    from sklearn.naive_bayes import GaussianNB
    classifier = GaussianNB()

    # from sklearn.linear_model import LogisticRegression

    # classifier = LogisticRegression()

    classifier.fit(X_train, y_train)

    # Predict Class
    y_pred = classifier.predict(X_test)

    # Accuracy
    from sklearn.metrics import accuracy_score
    accuracy = accuracy_score(y_test, y_pred)

    print(accuracy)
    return accuracy



def run_lda_model_short(df):
    stemmer = PorterStemmer()
    try:
        df = df.drop(["marketplace", "customer_id", "product_parent", "product_category", "review_date"], axis=1)
    except:
        pass
    df = df[~df['review_body'].isnull()]
    df['review_body'] = df['review_headline'] + '. ' + df['review_body']
    df["health_hazard"] = np.nan
    df = df.set_index("review_id")
    neg_reviews = df.query("star_rating < 4", engine="python")
    stop_words = stopwords.words('english')
    stop_words.extend(['br'])
    translator = str.maketrans('', '', string.punctuation)

    # neg_reviews["tokened_review"] = np.nan
    all_tokens = []
    # neg_reviews.astype({"tokened_review": 'object'}).dtypes
    for index, row in df.iterrows():
        text = row["review_body"].lower()
        text = text.translate(translator)
        text = word_tokenize(text)
        new_text = []
        for token in text:
            token = stemmer.stem(token)
            if token not in stop_words:
                new_text.append(token)
        all_tokens.append(new_text)
    df["tokened_review"] = all_tokens
    hazardous_words = ["rotten", "mouldy", "moldy", "mold", "mould", "sick", "dangerous", "diarrhea", "poisoning",
                       "stale"]
    for word in hazardous_words:
        df.loc[
            [word in tokened_review for tokened_review in df["tokened_review"]], "health_hazard"] = 1
    num_labeled = len(df.query("health_hazard == 1", engine="python"))
    non_hazardous = df.query("health_hazard != 1 and polarity < 0", engine="python").sample(num_labeled)
    labeled = df.query("health_hazard == 0 or health_hazard == 1", engine="python")
    reviews = labeled.loc[:, 'tokened_review'].values
    y = labeled.loc[:, 'health_hazard'].values
    for i in list(non_hazardous.index):
        df.loc[i, "health_hazard"] = 0
    for i in range(len(reviews)):
        reviews[i] = ' '.join(reviews[i])

    return df

# takes a dataframe as input and the required timeframe set at default to 'D', format for which is available at
# https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases.
# Also take xaxis title and y axis title and graph title
def review_scores_timeframe(df, timeframe, xtitle, ytitle, title):
    df['review_date'] = pd.to_datetime(df['review_date'])
    sample = df.resample(timeframe, on='review_date').review_date.count()
    avg_score = df.resample(timeframe, on='review_date').star_rating.mean()
    dates = sample.index
    count = sample.values

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=dates, y=count, name=ytitle),
        secondary_y=False)

    fig.add_trace(
        go.Scatter(x=dates, y=avg_score.values, name='Average score'),
        secondary_y=True)

    # Add figure title
    fig.update_layout(
        xaxis_title=xtitle,
        title_text=title
    )

    return fig






"""
This displays the homepage of the website
:param request: the request made to the server
:return: a render object that will be displayed on the browser
"""


def get_homepage(request):
    context = create_context(request)
    return render(request, 'DataFrameRendering/Homepage.html', context)


"""
This class is a file form that takes in 2 file inputs which are then uploaded and set as the new data
"""


class UploadFileForm(forms.Form):
    ReviewDataFile = forms.FileField()
    ProductDataFile = forms.FileField()


"""
 This method serves the upload file page. If it recieves files then it saves them and loads the new data
:param request: the request made to the server
:return: a render object that will be displayed on the browser
"""


def upload_file(request):
    context = create_context(request)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print("Valid")
            handle_uploaded_file(request.FILES['ReviewDataFile'], 'reviewData.tsv')
            handle_uploaded_file(request.FILES['ProductDataFile'], 'productData.csv')
            handle_uploaded_file(request.FILES['CustomerDataFile'], 'customerData.csv')
            apps.loadNewData('reviewData.tsv', 'productData.csv','customerData.csv')
            return render(request, 'DataFrameRendering/Upload.html', context)
        else:
            print("Not Valid")
    else:
        form = UploadFileForm()
        context["form"] = form
    return render(request, 'DataFrameRendering/Upload.html', context)

"""
This plots an example grapgh of time vs review score
inputs df: Dataframe the dataframe that contains the data
outputs data: the imgdata of the graph
"""


def plot_example_grapgh(df):
    dates = []
    scores = []
    for index,row in df.iterrows():
        dates.append(row['review_date'])
        scores.append(row['star_rating'])
    fig, ax = sub(figsize=(12, 12))
    ax.bar(dates,
           scores,
           color='purple')
    ax.set(xlabel="Date",
           ylabel="Star ratings",
           title="Star ratings over time")
    ax.plot()
    imgdata = StringIO()
    fig.savefig(imgdata,format = 'svg')
    imgdata.seek(0)
    data = imgdata.getvalue()

    return data

"""
This handles saving a file from an upload to the server. It saves it in this directory as the filename.
:param f: the file object so save
:param fileName: String what to save the file as
"""

def handle_uploaded_file(f, fileName):
    with open(fileName, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


"""
For testing
"""

"""
For testing
"""


def ProductView(request):
    # ensure_data_loaded(reviewData=False)
    df = apps.ProductDataFrame
    template = 'DataFrameRendering/product.html'

    # Format the column headers for the Bootstrap table, they're just a list of field names,
    # duplicated and turned into dicts like this: {'field': 'foo', 'title: 'foo'}
    columns = [{'name': 'tes', 'title': 't'}]
    # Write the DataFrame to JSON (as easy as can be)
    json = df.to_json(orient='records')  # output just the records (no fieldnames) as a collection of tuples
    # Proceed to create your context object containing the columns and the data
    context = {
        'data': json,
        'columns': columns
    }
    print(columns)
    # And render it!
    return render(request, template, context)


""" # product_id = models.ForeignKey(ProductData, on_delete=models.CASCADE)
   product_id = models.CharField(max_length=20)
   product_parent = models.CharField(max_length=20)
   product_title = models.TextField()
   star_rating = models.IntegerField()
   helpful_votes = models.IntegerField()
   total_votes = models.IntegerField()
   vine = models.BinaryField()
   verified_purchase = models.BinaryField()
   review_headline = models.CharField(max_length=200)
   review_body = models.TextField()
   review_date = models.DateField()"""

"""
For testing
"""


class ReviewForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)
