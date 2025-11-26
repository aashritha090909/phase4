from django.urls import path
from . import views

urlpatterns = [
    path('add-patient/', views.add_patient_view, name = 'add_patient'),
    path('record-symptom/', views.record_symptom_view, name = 'record_symptom'),
    path('book-appointment/', views.book_appointment_view, name = 'book_appointment'),
    path('place-order/', views.place_order_view, name = 'place_order'),

]