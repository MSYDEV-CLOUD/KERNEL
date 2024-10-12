from django.db import models

class IFTARate(models.Model):
    state_province = models.CharField(max_length=100)
    us_diesel_rate = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    ca_diesel_rate = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    us_surcharge = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    ca_surcharge = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    date_scraped = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.state_province}: US Rate: {self.us_diesel_rate}, CA Rate: {self.ca_diesel_rate}"
