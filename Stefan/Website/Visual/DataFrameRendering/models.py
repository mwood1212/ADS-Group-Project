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
    #customer_id = models.ForeignKey(UsersData, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=20)
    review_id = models.CharField(max_length=20)
    #product_id = models.ForeignKey(ProductData, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=20)
    """product_parent = models.CharField(max_length=20)
    product_title = models.TextField()
    star_rating = models.IntegerField()
    helpful_votes = models.IntegerField()
    total_votes = models.IntegerField()
    vine = models.BinaryField()
    verified_purchase = models.BinaryField()
    review_headline = models.CharField(max_length=200)
    review_body = models.TextField()
    review_date = models.DateField()"""

    def __str__(self):
        return self.review_id