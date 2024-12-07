from django import forms
from .models import (
    Cattle, MilkProduction, HealthRecord, 
    Breeding, Feed, Notification
)

class CattleForm(forms.ModelForm):
    class Meta:
        model = Cattle
        fields = [
            'name', 'tag_number', 'breed', 
            'date_of_birth', 'gender', 'weight',
            'status', 'notes'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class MilkProductionForm(forms.ModelForm):
    class Meta:
        model = MilkProduction
        fields = [
            'cattle', 'date', 'milking_session',
            'quantity', 'fat_content', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import HealthRecord

class HealthRecordForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('cattle', css_class='form-group col-md-6'),
                Column('record_type', css_class='form-group col-md-6'),
            ),
            Row(
                Column('date', css_class='form-group col-md-6'),
                Column('vet_name', css_class='form-group col-md-6'),
            ),
            Row(
                Column('medicine', css_class='form-group col-md-6'),
                Column('dosage', css_class='form-group col-md-6'),
            ),
            Row(
                Column('cost', css_class='form-group col-md-6'),
                Column('next_checkup_date', css_class='form-group col-md-6'),
            ),
            'description',
            'attachment',
            Submit('submit', 'Save Health Record', css_class='btn btn-primary')
        )

    class Meta:
        model = HealthRecord
        fields = [
            'cattle',
            'record_type',
            'date',
            'description',
            'medicine',
            'dosage',
            'vet_name',
            'cost',
            'next_checkup_date',
            'attachment'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'next_checkup_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class BreedingForm(forms.ModelForm):
    class Meta:
        model = Breeding
        fields = [
            'cattle', 'breeding_type', 'date',
            'sire_details', 'status', 'expected_calving_date',
            'actual_calving_date', 'notes', 'cost'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'expected_calving_date': forms.DateInput(attrs={'type': 'date'}),
            'actual_calving_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class FeedForm(forms.ModelForm):
    class Meta:
        model = Feed
        fields = [
            'name', 'feed_type', 'quantity',
            'cost_per_unit', 'purchase_date',
            'expiry_date', 'supplier', 'notes'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'notification_type',
            'priority', 'related_to'
        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }

# Search Forms
class CattleSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search by name or tag number'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All')] + Cattle.STATUS_CHOICES,
        required=False
    )
    gender = forms.ChoiceField(
        choices=[('', 'All')] + Cattle.GENDER_CHOICES,
        required=False
    )

class MilkProductionSearchForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    cattle = forms.ModelChoiceField(
        queryset=Cattle.objects.all(),
        required=False,
        empty_label="All Cattle"
    )

class HealthRecordSearchForm(forms.Form):
    record_type = forms.ChoiceField(
        choices=[('', 'All')] + HealthRecord.RECORD_TYPES,
        required=False
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

# Filter Forms
class DateRangeFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

class FeedFilterForm(forms.Form):
    feed_type = forms.ChoiceField(
        choices=[('', 'All')] + Feed.FEED_TYPE_CHOICES,
        required=False
    )
    supplier = forms.CharField(required=False)
    expiring_soon = forms.BooleanField(required=False)
