from django.urls import path
from .views import (
    CustomLoginView,
    RegisterStep1View, RegisterStep2View, RegisterStep3View,
    CreateChildProfileView
)

urlpatterns = [
    path('register/step1/', RegisterStep1View.as_view(), name='register-step1'),
    path('register/step2/', RegisterStep2View.as_view(), name='register-step2'),
    path('register/step3/', RegisterStep3View.as_view(), name='register-step3'),
    path('profiles/add-child/', CreateChildProfileView.as_view(), name='add-child-profile'),
    path('login/', CustomLoginView.as_view(), name='login'),
]
