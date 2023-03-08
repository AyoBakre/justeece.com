from django.db import models
from justeece.core.utils import TimestampedModel
from accounts.models import User
from app.models import S3ImageField
# Create your models here.

class ContractTypeModel(TimestampedModel):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name    

class ContractsModel(TimestampedModel):

    DRAFT = 1
    PENDING = 2
    IN_PROGRESS = 3
    COMPLETED = 4
    CANCELED = 5
    DISPUTE = 6
    REJECTED = 7

    CONTRACT_STATUS_CHOICES = (
        (DRAFT, ('Draft')),
        (PENDING, ('Pending')),
        (IN_PROGRESS, ('In Progress')),
        (COMPLETED, ('Completed')),
        (CANCELED, ('Canceled')),
        (DISPUTE, ('Dispute')),
        (REJECTED, ('Rejected'))
    )
    contract_name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_user")
    created_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_with_user", null=True, blank=True)
    created_with_email = models.EmailField(max_length=150, null=True, blank=True)
    contract_type = models.ForeignKey(ContractTypeModel, on_delete=models.CASCADE, related_name="create_contract_type")
    subcategory = models.CharField(max_length=100)
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    summary = models.TextField(max_length=500)
    payment_included = models.BooleanField(default=False)
    amount = models.BigIntegerField(null=True, blank=True)
    status = models.SmallIntegerField(choices=CONTRACT_STATUS_CHOICES, default=DRAFT)
    contract_completed_date = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = "create_contract"
        verbose_name = "Contract"
        verbose_name_plural = "Contracts"

    def __str__(self):
        return self.contract_name


class EndContractReasonChoiceModel(TimestampedModel):
    reason = models.CharField(max_length=100)

    class Meta:
        verbose_name = "End Contract Reason Choice"
        verbose_name_plural = "End Contract Reason Choices"

    def __str__(self):
        return str(self.reason)

class RejectContractReasonChoiceModel(TimestampedModel):
    reason = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Reject Contract Reason Choice"
        verbose_name_plural = "Reject Contract Reason Choices"

    def __str__(self):
        return str(self.reason)

class CancelContractReasonChoiceModel(TimestampedModel):
    reason = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Cancel Contract Reason Choice"
        verbose_name_plural = "Cancel Contract Reason Choices"

    def __str__(self):
        return str(self.reason)

class ContractCloseFeedback(TimestampedModel):
    REJECT_CONTRACT = 1
    ACCEPT_CONTRACT = 2
    END_CONTRACT = 3
    CANCEL_CONTRACT = 4

    STATUS_CHOICES = (
        (REJECT_CONTRACT, ('Reject Contract')),
        (ACCEPT_CONTRACT, ('Accept Contract')),
        (END_CONTRACT, ('End Contract')),
        (CANCEL_CONTRACT, ('Cancel Contract')),
    )

    contract = models.ForeignKey(
        ContractsModel,
        on_delete=models.DO_NOTHING,
        related_name="contract_feedback"
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES)
    feedback = models.TextField(max_length=200, null=True, blank=True)
    end_contract_reason = models.ForeignKey(
        EndContractReasonChoiceModel, 
        on_delete=models.DO_NOTHING, null=True, blank=True
        )
    reject_contract_reason = models.ForeignKey(
        RejectContractReasonChoiceModel,
        on_delete=models.DO_NOTHING, null=True, blank=True
    )
    cancel_contract_reason = models.ForeignKey(
        CancelContractReasonChoiceModel,
        on_delete=models.DO_NOTHING, null=True, blank=True
    )
    rating = models.SmallIntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.contract.contract_name


class ContractTemplateTag(TimestampedModel):
    tag = models.CharField(max_length=40)

    def __str__(self):
        return self.tag


class ContractTemplate(TimestampedModel):
    title = models.CharField(max_length=60)
    description = models.CharField(max_length=200)
    agreement = models.TextField(blank=True)
    logo =  S3ImageField(upload_to='contract_image', null=True, blank=True)
    tag = models.ManyToManyField(ContractTemplateTag)
    #logo = models.ImageField(upload_to ='uploads/', null=True, blank=True)
    contract_type = models.ForeignKey(ContractTypeModel, on_delete=models.CASCADE, 
                    related_name="contract_type", null=True, blank=True)

    def __str__(self):
        return self.title


