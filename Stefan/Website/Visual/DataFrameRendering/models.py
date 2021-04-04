from django.db import models
from django_pandas.managers import DataFrameManager


"""
For testing
"""

class UsersData(models.Model):
    customer_id = models.CharField(max_length=20)

    #def reviewTotal(self):


    def __str__(self):
        return self.customer_id



"""
For testing
"""

class ProductData(models.Model):
    product_id = models.CharField(max_length=20)

    def __str__(self):
        return self.product_id


"""
For testing
"""
class Product(models.Model):
  product_name=models.TextField()
  objects = models.Manager()
  pdobjects = DataFrameManager()  # Pandas-Enabled Manager


"""
For testing
"""


class ReviewData(models.Model):
    customer_id = models.CharField(max_length=20,default="None")
    review_id = models.CharField(max_length=20,default="None",unique=True)
    #product_id = models.CharField(max_length=20,default="None")
    #product_parent = models.CharField(max_length=20,default="None")
    #product_title = models.TextField(default="None")
    #star_rating = models.IntegerField(default=0)
    #helpful_votes = models.IntegerField(default=0)
    #total_votes = models.IntegerField(default=0)
    #vine = models.BooleanField(default=True)
    #verified_purchase = models.BooleanField(default=True)
    #review_headline = models.CharField(max_length=200,default="None")
    #review_body = models.TextField(default="None")
    #review_date = models.DateField(default=datetime.date.today )

    def __str__(self):
        return self.review_id