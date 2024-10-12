from django.db import models

class IFTACalculatorService(models.Model):
    company_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)  # For storing phone numbers
    email = models.EmailField()  # Ensures valid email format
    document = models.FileField(upload_to='ifta_documents/', blank=True, null=True)  # Optional document upload
    form_data_submitted = models.BooleanField(default=False)
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"IFTA Service for {self.company_name}"



