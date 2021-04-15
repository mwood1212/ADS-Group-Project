import pandas
import time
import datetime

ReviewDataFrame = None
ProductDataFrame = None

def loadData(fileName):
    print("Loading data")
    return pandas.read_csv(fileName, sep='\t', header=0, error_bad_lines=False)


def preProcessDataFrame(dataFrame, quick=True):
    df = dataFrame.dropna()
    df = df.reset_index(drop=True)
    df = df.drop(columns=['marketplace', 'product_category'])
    df['star_rating'] = df['star_rating'].astype(int)
    if not quick:
        df['review_date'].map(lambda a: datetime.strptime(a, "%Y-%m-%d"))
    return df


def createProudctDataFrame(ReviewDataFrame):
    global ProductDataFrame
    if ReviewDataFrame is None:
        return None

    print("Start Generating")

    # add dictonary to store the id of the product to a list of the rows that have this product
    dict = {}

    # add a list of the rows that are in the other file
    for index, row in ReviewDataFrame.iterrows():
        id = row["product_id"]
        if id in dict.keys():
            list = dict[id]
            dict[id].append(index)
            dict[id] = list
        else:
            dict[id] = [index]
        # prints progress
        if (index % 100000) == 0:
            print(index)

    print("Generated dictIds")

    # make empty data frame
    productDataFrame = pandas.DataFrame()

    # set the ids
    productDataFrame["product_id"] = dict.keys()

    # set the list of rows
    productDataFrame['indexs_of_reviews'] = dict.values()

    print("Generated inital data frame")

    # a list of scores
    scores = []

    # sums the review score then divides by the length and saves it as score
    for index, row in productDataFrame.iterrows():
        score = 0
        for i in (row[1]):
            score += int(ReviewDataFrame.iloc[i, 5])
        scores.append(score / len(row[1]))
        if (index % 100000) == 0:
            print(index)

    productDataFrame["scores"] = scores

    # empty list of product names
    names = []

    for index, row in productDataFrame.iterrows():
        names.append(ReviewDataFrame.iloc[row[1][0], 4])

    productDataFrame["names"] = names

    ProductDataFrame = productDataFrame
    return productDataFrame


def createCustomerDataFrame(ReviewDataFrame):
    global CustomerDataFrame
    if ReviewDataFrame is None:
        return None

    print("Start Generating")

    # add dictonary to store the id of the product to a list of the rows that have this product
    dict = {}
    countDict = {}
    # add a list of the rows that are in the other file
    for index, row in ReviewDataFrame.iterrows():
        id = row["customer_id"]
        if id in dict.keys():
            list = dict[id]
            countDict[id] = countDict[id] + 1
            dict[id].append(index)
            dict[id] = list
        else:
            dict[id] = [index]
            countDict[id] = 1
        # prints progress
        if (index % 100000) == 0:
            print(index)

    print("Generated dictIds")

    # make empty data frame
    customerDataFrame = pandas.DataFrame()

    # set the ids
    customerDataFrame["customer_id"] = dict.keys()

    # set the list of rows
    customerDataFrame['indexs_of_reviews'] = dict.values()

    customerDataFrame['count'] = countDict.values()

    print("Generated inital data frame")

    # a list of scores
    scores = []

    # sums the review score then divides by the length and saves it as score
    for index, row in customerDataFrame.iterrows():
        score = 0
        for i in (row[1]):
            score += int(ReviewDataFrame.iloc[i, 5])
        scores.append(score / len(row[1]))
        if (index % 100000) == 0:
            print(index)

    customerDataFrame["scores"] = scores



    ProductDataFrame = customerDataFrame
    return customerDataFrame

if __name__ == "__main__":
    ReviewDataFrame = None
    ProductDataFrame = None
    CustomerDataFrame = None
    if ReviewDataFrame is None:
        ReviewDataFrame = loadData("datav1.tsv")
        ReviewDataFrame = preProcessDataFrame(ReviewDataFrame, True)
    else:
        print(ReviewDataFrame)
    if ProductDataFrame is None:
        ProductDataFrame = createProudctDataFrame(ReviewDataFrame)
    else:
        print(ProductDataFrame)
    ProductDataFrame.to_csv("ProductDataFrame.csv")
    if CustomerDataFrame is None:
        CustomerDataFrame = createCustomerDataFrame(ReviewDataFrame)
    else:
        print(CustomerDataFrame)
    CustomerDataFrame.to_csv("CustomerDataFrame.csv")
    print("Succsefully generated CustomerDataFrame.csv")

