from django.db   import models

from core.models import TimeStampModel

class Role(TimeStampModel):
    name = models.CharField(max_length = 50)

    class Meta:
        db_table = 'roles'

class User(TimeStampModel):
    role     = models.ForeignKey(Role, on_delete = models.CASCADE)
    email    = models.CharField(max_length = 200, unique = True)
    password = models.CharField(max_length = 500)
    name     = models.CharField(max_length = 50)

    class Meta:
        db_table = 'users'