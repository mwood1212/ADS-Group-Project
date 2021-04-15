from django.apps import AppConfig
import pandas as pandas
import datetime


"""
Defines the 2 global variables that store the dataframes of the review data and a product data csv file I made
"""
ReviewDataFrame = None
ProductDataFrame = None

"""
Loads files that are uploaded to the website
:param newReviewDataString: The string of the filename of the new reviews file
:param newProductDataString: The string of the filename of the new products file
:param newCustomerDataString: The string of the filename of the new customers file
"""


def loadNewData(newReviewDataString, newProductDataString, newCustomerDataString):
    ensure_data_loaded(newReviewDataString, newProductDataString,newCustomerDataString)


"""
Loads the DataFrames from the files
:param fileName: The string path to the file
:param Tsv: a bool of whether to use the \t seperator needed for tsv files. If false then it assumes a csv file
:return: a dataframe containing the data
"""


def load_data(fileName, Tsv):
    print("Loading data from file " + fileName)
    if Tsv:
        return pandas.read_csv(fileName, sep='\t', header=0, error_bad_lines=False)
    else:
        return pandas.read_csv(fileName, header=0, error_bad_lines=False)


"""
Preprocess the dataFrames by ensuring
1) drop any rows with Nan in
2) reset column indexs
3) drop marketplace and product_category as they are pointless
4) ensure all star ratings are the same type int
5) make customer id and product parent as the type strings
6) if not quick then change dates to a datetime object instead of string
:param dataFrame: the dataframe that should be processed
:param quick: if it should run operations that take a lot longer - can take more time to convert dates then to actually load the data!
:return: a proccssed data frame
"""


def pre_process_data_frame(dataFrame):
    df = dataFrame.dropna()
    df = df.reset_index(drop=True)
    df = df.drop(columns=['marketplace', 'product_category'])
    df['star_rating'] = df['star_rating'].astype(int)
    df['customer_id'] = df['customer_id'].astype(str)
    df['product_parent'] = df['product_parent'].astype(str)
    pandas.to_datetime(df["review_date"],format="%Y-%m-%d")
    return df


"""
This ensures that the data needed for the function is loaded before and cached.
Note the product data frame is sorted by score and Customer data frame is sorted by the number of reivews
:param reviewFileLocation the string location relative to this directory of where to load the data from
:param productFileLocation the string location relative to this directory of where to load the data from
:param customerFileLocation the string location relative to this directory of where to load the data from
"""


def ensure_data_loaded(reviewFileLocation, productFileLocation, customerFileLocation):
    global ReviewDataFrame
    global ProductDataFrame
    global CustomerDataFrame
    ReviewDataFrame = load_data(reviewFileLocation, Tsv=True)
    ReviewDataFrame = pre_process_data_frame(ReviewDataFrame)
    ProductDataFrame = load_data(productFileLocation, Tsv=False)
    ProductDataFrame = ProductDataFrame.sort_values(["scores"])
    CustomerDataFrame = load_data(customerFileLocation, Tsv=False)
    CustomerDataFrame = CustomerDataFrame.sort_values(["count"],ascending=False)


"""
This class is called once when the server is started
It loads all of the data into the dataframes
There will be no response until this is finished
"""


class DataframerenderingConfig(AppConfig):
    name = 'DataFrameRendering'
    ensure_data_loaded("datav1.tsv", "ProductDataFrame.csv","CustomerDataFrame.csv")
    print("dataLoaded")
