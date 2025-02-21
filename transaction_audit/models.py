from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from simple_history.models import HistoricalRecords

class Transaction(models.Model):
    PENDING_STATUS = "P"
    COMPLETE_STATUS = "C"
    FAILED_STATUS = "F"
    STATUS_CHOICES = [
        (PENDING_STATUS, "Pending"),
        (COMPLETE_STATUS, "Complete"),
        (FAILED_STATUS, "Failed"),
    ]
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING_STATUS)
    merchant = models.CharField(max_length=100)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_flagged = models.BooleanField(default=False)
    history = HistoricalRecords()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.merchant} - ${self.amount}"
    
    def clean(self):
        
        if self.pk is not None:
            #Rules when updating an existing transaction
            og_transaction = Transaction.objects.get(pk=self.pk)
            
            #Amount shouldn't be editable
            if self.amount != og_transaction.amount:
                raise ValidationError("Amount is not editable")
            
            #Merchant shouldn't be editable
            if self.merchant != og_transaction.merchant:
                raise ValidationError("Merchant is not editable")
            
            #If transaction is complete, status shouldn't be editable
            if og_transaction.status == self.COMPLETE_STATUS and self.status != og_transaction.status:
                raise ValidationError("Status is not editable")
            
            #If transaction is failed, status shouldn't be editable
            if og_transaction.status == self.FAILED_STATUS and self.status != og_transaction.status:
                raise ValidationError("Status is not editable")
            
            #if transaction new status is complete, approved_by must have a value
            if self.status == self.COMPLETE_STATUS and self.approved_by is None:
                raise ValidationError("Approved by must have a value")
            
            #if approved_by is set without changing status to complete, invalidate
            if self.status != self.COMPLETE_STATUS and self.approved_by is not None:
                raise ValidationError("Approved by must be set when status is complete")
            
        else:
            #Rules when creating a new transaction
            
            #Merchant must not be empty
            if not self.merchant.strip():
                raise ValidationError("Merchant must not be empty")
            
            #Amount must be greater than 0
            if self.amount <= 0:
                raise ValidationError("Amount must be greater than 0")
            
            #New Transaction must start with the status of pending
            if self.status != self.PENDING_STATUS:
                raise ValidationError("New transaction must have a status of pending")
            
            #New Transaction must not have an approved_by value
            if self.approved_by is not None:
                raise ValidationError("New transaction must not have an approved_by value")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        self.merchant = self.merchant.lower()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "merchant"]),
        ]