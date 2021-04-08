from django.shortcuts import HttpResponse
from django.shortcuts import render

from django.views.generic import ListView
import json
import DataFrameRendering.apps as apps
import numpy as np
from DataFrameRendering.models import ReviewData
from django import forms

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


def filter_Data_Frame(ReviewDataFrame, context):
    print("Filtering data")

    filteredDataFrame = apps.ReviewDataFrame.copy()
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

    # convert to json
    json_records = filteredDataFrame.reset_index().to_json(orient='records')
    data = json.loads(json_records)

    context['data'] = data
    print("About to render")
    return render(request, 'DataFrameRendering/Reviews.html', context)


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
                          'number_per_page' + param: request.GET.get("number_per_page", 100),
                          'page_num' + param: request.GET.get("page_num", 1),
                          "home_url": webpageUrl + "/",
                          "reviews_url": webpageUrl + "/reviews",
                          "products_url": webpageUrl + "/products",
                          "upload_files_url": webpageUrl + "/upload",
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

    df = apps.ProductDataFrame[:100]

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
    return render(request, 'DataFrameRendering/SingleProduct.html', context)


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
            apps.loadNewData('reviewData.tsv', 'productData.csv')
            return render(request, 'DataFrameRendering/Upload.html', context)
        else:
            print("Not Valid")
    else:
        form = UploadFileForm()
        context["form"] = form
    return render(request, 'DataFrameRendering/Upload.html', context)


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
