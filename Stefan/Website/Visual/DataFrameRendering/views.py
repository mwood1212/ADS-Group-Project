from django.shortcuts import HttpResponse
from django.shortcuts import render
import pandas
from django.views.generic import ListView
import json
from DataFrameRendering.models import ReviewData
from django import forms
import datetime
import numpy as np

"""
Defines the 2 global variables that store the dataframes of the review data and a product data csv file I made
"""
ReviewDataFrame = None
ProductDataFrame = None
"""
The url of the webpage. Here so it can changed easily later
"""
# todo change
webpageUrl = "http://127.0.0.1:8000"

"""
Loads the DataFrames from the files
:param fileName: The string path to the file
:param Tsv: a bool of whether to use the \t seperator needed for tsv files. If false then it assumes a csv file
:return: a dataframe containing the data
"""


def load_data(fileName, Tsv):
    print("Loading data")
    if Tsv:
        return pandas.read_csv(fileName, sep='\t', header=0, error_bad_lines=False)
    else:
        return pandas.read_csv(fileName, header=0, error_bad_lines=False)


"""
Preprocess the dataFrames by ensuring
1) drop any rows with Nan in
2) reset column indexs
3)drop marketplace and product_category as they are pointless
4) ensure all star ratings are the same type int
5) if not quick then change dates to a datetime object instead of string
:param dataFrame: the dataframe that should be processed
:param quick: if it should run operations that take a lot longer - can take more time to convert dates then to actually load the data!
:return: a proccssed data frame
"""


def pre_process_data_frame(dataFrame, quick=True):
    df = dataFrame.dropna()
    df = df.reset_index(drop=True)
    df = df.drop(columns=['marketplace', 'product_category'])
    df['star_rating'] = df['star_rating'].astype(int)
    if not quick:
        df['review_date'].map(lambda a: datetime.strptime(a, "%Y-%m-%d"))
    return df


"""
This ensures that the data needed for the function is loaded before and cached.
Note the product data frame is sorted by score
:param reviewData: a bool of if reviewData should be loaded in order to speed up the request if it is not needed
:param ProductData:  a bool of if productData should be loaded in order to speed up the request if it is not needed
"""


def ensure_data_loaded(reviewData=True, ProductData=True):
    global ReviewDataFrame
    global ProductDataFrame

    if ReviewDataFrame is None and reviewData:
        ReviewDataFrame = load_data("datav1.tsv", Tsv=True)
        ReviewDataFrame = pre_process_data_frame(ReviewDataFrame, True)
    if ProductDataFrame is None and ProductData:
        ProductDataFrame = load_data("ProductDataFrame.csv", Tsv=False)
        ProductDataFrame = ProductDataFrame.sort_values(["scores"])


"""
Displays the table for the reviews as well as the search
:param request: the request made to the server
:return: a render object that will be displayed on the browser
"""


def get_reviews(request):
    global ReviewDataFrame
    global ProductDataFrame
    global webpageUrl
    ensure_data_loaded()

    # seperated for testing if parameter is a then load 10 results

    if request.GET.get("review_id", "b") == "a":

        df = ReviewDataFrame[:10]

        # add a links feild so it can be used in the html to use the link
        links = []
        j = 0
        for i, row in df.iterrows():
            links.append(webpageUrl + "/product/?id=" + df.iloc[j, 2])
            j += 1
        df["link"] = links

        # convert to json
        json_records = df.reset_index().to_json(orient='records')
        data = json.loads(json_records)

        # creates a context object dictoniary to use
        context = create_context(request, data)

        return render(request, 'DataFrameRendering/Reviews.html', context)

    else:
        df = ReviewDataFrame[:100]

        # add a links feild so it can be used in the html to use the link
        links = []
        j = 0
        for i, row in df.iterrows():
            links.append(webpageUrl + "/product/?id=" + df.iloc[j, 2])
            j += 1
        df["link"] = links

        # convert to json
        json_records = df.reset_index().to_json(orient='records')
        data = json.loads(json_records)

        # creates a context object dictoniary to use
        context = create_context(request, data)

        return render(request, 'DataFrameRendering/Reviews.html', context)


"""
Creates a context with all of the arguments from the url
:param request: the request made to the server
:param data: a panda dataframe to use to display information in the template
:return: dict a dictonary of the data and any arguments from the url
"""


def create_context(request, data):
    dict = {'data': data, 'review_id_param': request.GET.get("review_id", "b")}
    dict['data'] = data
    dict['review_id_param'] = request.GET.get("review_id", "")
    dict['product_id_param'] = request.GET.get("product_id", "")
    dict['product_parent_param'] = request.GET.get("product_parent", "")
    dict['product_title_param'] = request.GET.get("product_title", "")
    dict['star_rating_param'] = request.GET.get("review_id", "")
    return dict


"""
Displays the table for the products
:param request: the request made to the server
:return: a render object that will be displayed on the browser
"""


def get_products(request):
    global ReviewDataFrame
    global ProductDataFrame

    ensure_data_loaded(reviewData=False)
    df = ProductDataFrame[:100]

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
    context = create_context(request, data)

    return render(request, 'DataFrameRendering/Products.html', context)


"""
This displays the info for a product with an id
:param request: the request made to the server
:return: a render object that will be displayed on the browser
"""


def get_product_with_id(request):
    global ReviewDataFrame
    global ProductDataFrame

    ensure_data_loaded()

    # generate data for the review
    row_number = ProductDataFrame['product_id'] == request.GET.get("id", "b")
    json_records = ProductDataFrame[row_number].reset_index().to_json(orient='records')
    product_data = json.loads(json_records)

    #generate data for the product
    row_numbers_review = ReviewDataFrame['product_id'] == request.GET.get("id", "b")
    json_records = ReviewDataFrame[row_numbers_review].reset_index().to_json(orient='records')
    review_data = json.loads(json_records)

    #generate context dictionary
    context = create_context(request, product_data)
    context["reviewData"] = review_data

    return render(request, 'DataFrameRendering/SingleProduct.html', context)


"""
For testing
"""


def addToDatabase(df):
    review = df
    # Not able to iterate directly over the DataFrame
    df_records = df.to_dict('records')

    model_instances = [ReviewData(
        customer_id=record['customer_id'],
        review_id=record['review_id'],
        product_id=record['product_id'],
        # field_2=record['field_2'],
        # field_2=record['field_2'],
        # field_2=record['field_2'],
        # field_2=record['field_2'],
        # field_2=record['field_2'],
        # field_2=record['field_2'],
        # field_2=record['field_2'],
    ) for record in df_records]

    ReviewData.objects.bulk_create(model_instances)


"""
For testing
"""


class PublisherList(ListView):
    model = ReviewData


"""
For testing
"""


def ProductView(request):
    ensure_data_loaded(reviewData=False)
    df = ProductDataFrame
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
