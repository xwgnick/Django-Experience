# Ride_Share/views.py
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import SignupForm, RideCreationForm, JoinRideForm, driverRegistrationForm
from .models import Ride, MyUser, Sharer, RegisteredSharer, Vehicle
import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .global_vars import VT2CAP, REVERSE_RIDE_STATUS_
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', context={'form': form})


@login_required(login_url='../accounts/login/')
def create_ride(request):
    ride = Ride()
    if request.method == 'POST':
        form = RideCreationForm(request.POST)
        if form.is_valid():
            ride.dest = form.cleaned_data['dest']
            ride.pickup_time = form.cleaned_data['pickup_time']
            ride.owner_pass_num = form.cleaned_data['owner_pass_num']
            ride.sharable = form.cleaned_data['sharable']
            ride.actual_pass_num = ride.owner_pass_num
            ride.owner = request.user
            ride.vehicle_type = form.cleaned_data['vehicle_type']
            ride.avail_seats = VT2CAP[ride.vehicle_type] - 1 - ride.actual_pass_num
            ride.save()
            return HttpResponseRedirect(reverse('ride_created'))
    else:
        proposed_pickup_time = timezone.now()
        form = RideCreationForm(initial={'pickup_time': proposed_pickup_time, 'owner_pass_num': 1,})
    
    return render(request, 'create_ride.html', {'form': form, 'ride':ride})


def home(request):
    return render(request, "home.html")


@login_required(login_url='../accounts/login/')
def join_ride(request):
    sharer = Sharer()
    if request.method == 'POST':
        form = JoinRideForm(request.POST)
        if form.is_valid():
            sharer.pass_num = form.cleaned_data['number_of_passengers']
            sharer.earliest_date_time = form.cleaned_data['earliest_pickup_time']
            sharer.latest_date_time = form.cleaned_data['latest_pickup_time']
            if sharer.earliest_date_time >= sharer.latest_date_time:
                 raise ValidationError(_('Invalid latest datetime - should be greater than earliest datetime!'))
            sharer.dest = form.cleaned_data['destination']
            sharer.sharerid = request.user
            sharer.save()
            return HttpResponseRedirect(reverse('search_result'))
    else:
        proposed_pickup_time = timezone.now()
        form = JoinRideForm(
            initial={
                'earliest_pickup_time': proposed_pickup_time, 
                'latest_pickup_time': proposed_pickup_time,
                'number_of_passengers': 1,
            }
        )
    return render(request, 'join_ride.html', context={'form': form})


# def take_ride(request):
#     return render(request, 'takeable_rides.html')


def ride_created(request):
    return render(request, "ride_created.html")


@login_required(login_url='../accounts/login/')
def search_result(request):
    sharer = get_object_or_404(Sharer, pk=request.user)
    sharearable_rides = Ride.objects.filter(
        ride_status='opn',
        sharable=True,
        dest=sharer.dest, 
        pickup_time__gte=sharer.earliest_date_time,
        pickup_time__lte=sharer.latest_date_time,
        avail_seats__gte=sharer.pass_num,
    ).exclude(owner=request.user).exclude(share_id=request.user).order_by('pickup_time')
    if sharearable_rides.exists() == False:
        return render(request, "no_search_result.html")
    page = request.GET.get('page', 1)
    paginator = Paginator(sharearable_rides, 3)
    try:
        sharearable_rides = paginator.page(page)
    except PageNotAnInteger:
        sharearable_rides = paginator.page(1)
    except EmptyPage:
        sharearable_rides = paginator.page(paginator.num_pages)
    return render(
        request, "search_result.html", context={'sharearable_rides': sharearable_rides})
        

@login_required(login_url='../accounts/login/')
def check_owned_rides(request):
    owned_rides = Ride.objects.filter(owner=request.user).exclude(ride_status="cop").order_by('pickup_time')
    if owned_rides.exists() == False:
        return render(request, "no_owned_rides.html")
    page = request.GET.get('page', 1)
    paginator = Paginator(owned_rides, 3)
    try:
        owned_rides = paginator.page(page)
    except PageNotAnInteger:
        owned_rides = paginator.page(1)
    except EmptyPage:
        owned_rides = paginator.page(paginator.num_pages)
    return render(request, "owned_rides.html", context={'owned_rides': owned_rides})


@login_required(login_url='../accounts/login/')
def check_sharing_rides(request):
    if not RegisteredSharer.objects.filter(registered_sharer_id=request.user).exists():
        return render(request, "no_sharing_rides.html")
    sharing_rides = Ride.objects.filter(share_id=request.user).exclude(ride_status="cop").order_by('pickup_time')
    page = request.GET.get('page', 1)
    paginator = Paginator(sharing_rides, 3)
    try:
        sharing_rides = paginator.page(page)
    except PageNotAnInteger:
        sharing_rides = paginator.page(1)
    except EmptyPage:
        sharing_rides = paginator.page(paginator.num_pages)
    return render(request, "sharing_rides.html", context={'sharing_rides': sharing_rides})


@login_required(login_url='../accounts/login/')
def into_ride(request, joining_ride_id):
    # print("---------------------------------", type(joining_ride_id))
    sharing_ride = get_object_or_404(Ride, pk=joining_ride_id)
    sharer = get_object_or_404(Sharer, pk=request.user)
    sharing_ride.share_id = request.user
    sharing_ride.actual_pass_num += sharer.pass_num
    sharing_ride.avail_seats -= sharer.pass_num
    sharing_ride.save()

    if RegisteredSharer.objects.filter(registered_sharer_id=request.user).exists() == False:
        registeredSharer = RegisteredSharer(registered_sharer_id=request.user)
        registeredSharer.save()
    
    return render(request, "successfully_joined.html")


@login_required(login_url='../accounts/login/')
def driver_registration(request):
    user = get_object_or_404(MyUser, pk=request.user.id)
    vehicle = Vehicle()
    if request.method == 'POST':
        form = driverRegistrationForm(request.POST)
        if form.is_valid():
            vehicle.plate_num = form.cleaned_data['plate_num']
            vehicle.type = form.cleaned_data['vehicle_type']
            vehicle.capacity = VT2CAP[vehicle.type]
            vehicle.save()
            # vehicle = get_object_or_404(Vehicle, pk=form.cleaned_data['plate_num'])
            user.plate_num = vehicle
            user.save()
            return render(request, 'driver_register_succeed.html')
    else:
        form = driverRegistrationForm()
    
    return render(request, 'driver_registration.html', context={'form':form})


@login_required(login_url='../accounts/login/')
def search_takeable_rides(request):
    user = get_object_or_404(MyUser, pk=request.user.id)
    vehicle = user.plate_num
    takeable_rides = Ride.objects.filter(
        vehicle_type=vehicle.type, driver__isnull=True).exclude(owner=request.user).exclude(
            share_id__exact=request.user).exclude(ride_status="cop").order_by('pickup_time')
    if takeable_rides.exists() == False:
        return render(request, "no_takable_rides.html")
    page = request.GET.get('page', 1)
    paginator = Paginator(takeable_rides, 3)
    try:
        takeable_rides = paginator.page(page)
    except PageNotAnInteger:
        takeable_rides = paginator.page(1)
    except EmptyPage:
        takeable_rides = paginator.page(paginator.num_pages)
    return render(request, 'takeable_rides.html', context={'takeable_rides':takeable_rides})


@login_required(login_url='../accounts/login/')
def take_ride(request, take_ride_id):
    if not request.user.plate_num:
        raise ValidationError(_('You must become a driver to take a ride!'))
    ride_to_take = get_object_or_404(Ride, pk=take_ride_id)
    ride_to_take.driver = request.user
    ride_to_take.ride_status = 'con'
    ride_to_take.save()

    # if RegisteredSharer.objects.filter(registered_sharer_id=request.user).exists() == False:
    #     registeredSharer = RegisteredSharer(registered_sharer_id=request.user)
    #     registeredSharer.save()
    
    return render(request, "successfully_taken.html")
    # return render(request, "takeable_rides.html", context={'owned_rides': owned_rides})


@login_required(login_url='../accounts/login/')
def owned_ride_status(request, ride_id):
    owned_ride_status = get_object_or_404(Ride, pk=ride_id)
    owner_name = owned_ride_status.owner.username
    driver = None
    if not owned_ride_status.driver:
        driver = "No driver yet"
    else:
        driver = owned_ride_status.driver.username
    if not owned_ride_status.share_id:
        sharer = "No sharer yet"
    else:
        sharer = owned_ride_status.share_id.username
    destination = owned_ride_status.dest
    num_pass = owned_ride_status.actual_pass_num
    num_sharer_pass = owned_ride_status.actual_pass_num - owned_ride_status.owner_pass_num
    ride_status = REVERSE_RIDE_STATUS_[owned_ride_status.ride_status]

    if owned_ride_status.sharable == True:
        return render(request, 'owner_ride_status_sharer.html', 
                    context={'owner_name': owner_name, 'driver': driver,
                                'sharer': sharer, 'destination': destination,
                                'num_pass':num_pass, 'num_sharer_pass':num_sharer_pass,
                                'ride_status':ride_status})
    else:
         return render(request, 'owner_ride_status_no_sharer.html', 
                    context={'owner_name': owner_name, 'driver': driver,
                                'destination': destination,
                                'num_pass':num_pass,
                                'ride_status':ride_status})       


@login_required(login_url='../accounts/login/')
def check_taken_rides(request):
    taken_rides = Ride.objects.filter(driver=request.user).exclude(
        ride_status="cop").order_by('pickup_time')
    if taken_rides.exists() == False:
        return render(request, "no_taken_rides.html")
    page = request.GET.get('page', 1)
    paginator = Paginator(taken_rides, 3)
    try:
        taken_rides = paginator.page(page)
    except PageNotAnInteger:
        taken_rides = paginator.page(1)
    except EmptyPage:
        taken_rides = paginator.page(paginator.num_pages)
    return render(request, "taken_rides.html", context={'taken_rides': taken_rides})
