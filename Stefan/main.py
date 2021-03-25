import pandas
import time

verbose = False
verboseprint = print if verbose else lambda *a, **k: None

def loadData(fileName):
    verboseprint("Loading data")
    return pandas.read_csv(fileName, sep='\t', header=0, error_bad_lines=False)


def assertAllLocationsUs(dataFrame):
    for (columnName, data) in dataFrame.iteritems():
        if columnName == "marketplace":
            for i in data:
                assert (i == "US")


def assertAllCatogriesGrocery(dataFrame):

    for (columnName, data) in dataFrame.iteritems():
        if columnName == "product_category":
            for i in data:
                assert (i == "Grocery")


def runAsserts(dataFrame):
    assertAllLocationsUs(dataFrame)
    assertAllCatogriesGrocery(dataFrame)


def modifyBadData(dataFrame):
    verboseprint("Removing bad data")
    verboseprint("Length of data at start " + str(len(dataFrame)))
    modifiedDataFrame = dataFrame
    modifiedDataFrame = modifiedDataFrame.drop(modifiedDataFrame[modifiedDataFrame.product_category != "Grocery"].index)
    modifiedDataFrame = modifiedDataFrame.drop(modifiedDataFrame[modifiedDataFrame.star_rating ].index)
    print(modifiedDataFrame.star_rating.unique())
    return modifiedDataFrame


if __name__ == "__main__":
    timeNow = time.time()

    print("Starting program")

    dataFrame = loadData("datav1.tsv")

    print(dataFrame.columns)

    #dataFrame = modifyBadData(dataFrame)

    #print(len(dataFrame))

    #runAsserts(dataFrame)

    nums = {}
    sentences = dataFrame["review_body"]

    i = 0

    for data in sentences:
        try:
            nums.update({i: data.count("!")})
        except:
            print("Error")
        i += 1

    #print(nums)

    print(time.time() - timeNow)

    print("Finished Program")
