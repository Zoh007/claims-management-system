from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Claim(models.Model):
    """Insurance claim data model"""
    
    STATUS_CHOICES = [
        ('Denied', 'Denied'),
        ('Under Review', 'Under Review'),
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    ]
    
    claim_id = models.CharField(max_length=50, unique=True, verbose_name="Claim ID")
    patient_name = models.CharField(max_length=200, verbose_name="Patient Name")
    billed_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Billed Amount")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Paid Amount")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name="Status")
    insurer_name = models.CharField(max_length=100, verbose_name="Insurer Name")
    discharge_date = models.DateField(verbose_name="Discharge Date")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        verbose_name = "Claim"
        verbose_name_plural = "Claims"
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Claim {self.claim_id} - {self.patient_name}'
    
    @property
    def underpayment_amount(self):
        """Calculate underpayment amount"""
        return self.billed_amount - self.paid_amount


class ClaimDetail(models.Model):
    """Additional claim information"""
    
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='details', verbose_name="Claim")
    cpt_codes = models.TextField(blank=True, null=True, verbose_name="CPT Codes")
    denial_reason = models.TextField(blank=True, null=True, verbose_name="Denial Reason")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    
    class Meta:
        verbose_name = "Claim Detail"
        verbose_name_plural = "Claim Details"
    
    def __str__(self):
        return f'Detail {self.id} for Claim {self.claim.claim_id}'


class Flag(models.Model):
    """Flag marking a claim for review"""
    
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='flags', verbose_name="Claim")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    reason = models.CharField(max_length=200, verbose_name="Flag Reason")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    
    class Meta:
        verbose_name = "Flag"
        verbose_name_plural = "Flags"
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Flag {self.id} for Claim {self.claim.claim_id}'


class Note(models.Model):
    """User annotation attached to a claim"""
    
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='notes', verbose_name="Claim")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    content = models.TextField(verbose_name="Note Content")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Note {self.id} for Claim {self.claim.claim_id}'


class UserProfile(models.Model):
    """Additional user information"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="User")
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name="Department")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f'Profile for {self.user.username}'
