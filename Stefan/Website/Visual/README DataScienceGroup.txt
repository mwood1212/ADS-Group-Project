In order for all of this to work you will need to install python 3.9, Django and some other python modules
You will also need to generate a ProductDataFrame.csv file which you can do by running the following - python GenerateProductDataFrame.py
It will print some numbers as it works so that you know it is still running but it can take a while still
The reason I have not committed it is due to github large file restrictions so also ensure you do not commit it to github
Following on from that you will also need to place a copy of the tsv with a name of datav1.tsv in this folder
To run the website please run the following command python manage.py runserver from this directory
To find the available urls check out Visual/urls.py
The web request has to load up the review data and the product data which can take a while so you will have to wait and
it will do this anytime you make changes

To add a html template place it in DataFrameRendering/templates/DataFrameRendering as a html file. Css and Js can also be placed here.

To add a new page first add a new method in views.py that takes a request and then return a render method with a content,template and context
Then in urls add a new url and set it to that new method