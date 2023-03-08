'''
Utility Modules
'''
from django.db import models


class TimestampedModel(models.Model):
    '''
    Timestamped Model 
    '''
    create_date = models.DateTimeField(('Create Date'), auto_now_add=True)
    modify_date = models.DateTimeField(('Modify Date'), auto_now=True)

    class Meta:
        abstract = True
        # db_table = "contracts_contracttypemodel"