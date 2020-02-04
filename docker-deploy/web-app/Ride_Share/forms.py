# Ride_Share/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from .models import MyUser, Ride, Sharer
import datetime
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from .global_vars import MAX_RIDE_CAPACITY, VEHICLE_TYPE_, VT2CAP


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = MyUser
        fields = ('username', 'email')


class RideCreationForm(forms.Form):
    dest = forms.CharField(max_length=100)
    pickup_time = forms.DateTimeField()
    owner_pass_num = forms.IntegerField(
        min_value=1, max_value=MAX_RIDE_CAPACITY)
    sharable = forms.BooleanField(required=False)
    vehicle_type = forms.ChoiceField(choices=VEHICLE_TYPE_)
    # actual_pass_num, ride_status, owner, driver
    
    def clean_dest(self):
        data = self.cleaned_data['dest']
        return data

    def clean_pickup_time(self):
        """Remove form content if invalid input is detected"""
        data = self.cleaned_data['pickup_time']
        if data <  timezone.now() + datetime.timedelta(minutes=5):
            raise ValidationError(_(
        'Invalid pickup datetime - too early, should be set at least 5 min after!'))
        if data > timezone.now() + datetime.timedelta(hours=12):
            raise ValidationError(_(
        'Invalid pickup datatime - too late, should be set at less than 12 hours ahead!'))

        return data

    def clean_owner_pass_num(self):
        data = self.cleaned_data['owner_pass_num']
        if data > MAX_RIDE_CAPACITY:
            raise ValidationError(_(
        'Invalid owner passenger number: should between 1 - {}'.format(MAX_INIT_RIDE_CAPACITY)))
        return data

    def clean_sharable(self):
        data = self.cleaned_data['sharable']
        return data

    def clean_vehicle_type(self):
        data = self.cleaned_data['vehicle_type']
        if self.cleaned_data['owner_pass_num'] > VT2CAP[data]:
            raise ValidationError(_('Invalid vehicle type - exeed the capacity of the vehicle type'))
        return data


class JoinRideForm(forms.Form): 
    destination = forms.CharField(max_length=100)
    earliest_pickup_time = forms.DateTimeField()
    latest_pickup_time = forms.DateTimeField()
    number_of_passengers = forms.IntegerField(min_value=1, max_value=MAX_RIDE_CAPACITY)
    
    def clean_destination(self):
        data = self.cleaned_data['destination']
        return data

    def clean_latest_pickup_time(self):
        """Remove form content if invalid input is detected"""
        data = self.cleaned_data['latest_pickup_time']
        if data <  timezone.now() + datetime.timedelta(minutes=5):
            raise ValidationError(_(
        'Invalid pickup datetime - too early, should be set at least 5 min after!'))
        if data > timezone.now() + datetime.timedelta(hours=12):
            raise ValidationError(_(
        'Invalid pickup datatime - too late, should be set at less than 12 hours ahead!'))
        
        # if data <= self.cleaned_data['earliest_pickup_time']:
        #     raise ValidationError(_('Invalid latest datetime - should be later than earliest datetime!'))

        return data

    def clean_earliest_pickup_time(self):
        """Remove form content if invalid input is detected"""
        data = self.cleaned_data['earliest_pickup_time']
        if data <  timezone.now() + datetime.timedelta(minutes=5):
            raise ValidationError(_(
        'Invalid pickup datetime - too early, should be set at least 5 min after!'))
        if data > timezone.now() + datetime.timedelta(hours=12):
            raise ValidationError(_(
        'Invalid pickup datatime - too late, should be set at less than 12 hours ahead!'))

        return data
    

    def clean_number_of_passengers(self):
        data = self.cleaned_data['number_of_passengers']
        if data > MAX_RIDE_CAPACITY:
            raise ValidationError(_(
        'Invalid number of passengers - should between 1 - {}'.format(MAX_RIDE_CAPACITY)))
        return data

class driverRegistrationForm(forms.Form):
    plate_num = forms.CharField(max_length=20)
    vehicle_type = forms.ChoiceField(choices=VEHICLE_TYPE_)

    def clean_plate_num(self):
        data = self.cleaned_data['plate_num']
        return data
    
    def clean_vehicle_type(self):
        data = self.cleaned_data['vehicle_type']
        return data