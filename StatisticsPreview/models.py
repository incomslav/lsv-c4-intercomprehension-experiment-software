from django.db import models

# Create your models here.


class ResultMenu(models.Model):
	menu_name = models.CharField(max_length=150)
	is_root = models.BooleanField(default=True)
	parent_id = models.ForeignKey('self', null=True, blank=True)
	is_active = models.BooleanField(default=True)
	has_child = models.BooleanField(default=False)
	menu_url = models.CharField(max_length=350, default='')

	def __str__(self):
		return self.menu_name


class ColumnName(models.Model):
	full_name = models.CharField(max_length=300)
	abbvr_name = models.CharField(max_length=40)
	is_active = models.BooleanField(default=True)


	def __str__(self):
		return self.abbvr_name