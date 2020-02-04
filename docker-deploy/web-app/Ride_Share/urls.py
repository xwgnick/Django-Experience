# Ride_Share/urls.py
from django.urls import path

from . import views


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('createRide/', views.create_ride, name='create_ride'),
    path('createRide/rideCreated', views.ride_created, name='ride_created'),
    path('joinRide/', views.join_ride, name='join_ride'),
    path('joinRide/searchResult', views.search_result, name='search_result'),
    path('joinRide/searchResult/<int:joining_ride_id>', views.into_ride, name='into_ride'),
    path('takeableRides/<int:take_ride_id>', views.take_ride, name='take_ride'),
    path('takenRides', views.check_taken_rides, name='taken_rides'),
    # path('takeRide/', views.take_ride, name='take_ride'),  # dont use, this line has been given up
    path('ownedRides/', views.check_owned_rides, name='owned_rides'),
    path('sharingRides/', views.check_sharing_rides, name='sharing_rides'),
    path('driverRegistration', views.driver_registration, name='driver_registration'),
    path('takeableRides', views.search_takeable_rides, name='search_takeable_rides'),
    path('ownedRideStatus<int:ride_id>', views.owned_ride_status, name='owned_ride_status'),
    path('', views.home, name='home'),
]