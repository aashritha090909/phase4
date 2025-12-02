from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('add-patient/', views.add_patient_view, name = 'add_patient'),
    path('record-symptom/', views.record_symptom_view, name = 'record_symptom'),
    path('book-appointment/', views.book_appointment_view, name = 'book_appointment'),
    path('place-order/', views.place_order_view, name = 'place_order'),
    path('add-staff-to-dept/', views.add_staff_to_dept_view, name = 'add_staff_to_dept'),
    path("room-wise/", views.room_wise, name="room_wise"),
    path("symptoms/", views.symptoms_overview, name="symptoms"),
    path("staff/", views.medical_staff, name="medical_staff"),
    path("departments/", views.department_view, name="department_view"),
    path("charges/", views.outstanding_charges, name="outstanding_charges"),
    path('add-funds/', views.add_funds_view, name='add_funds'),
    path('assign-nurse-to-room/', views.assign_nurse_to_room_view, name='assign_nurse_to_room'),
]