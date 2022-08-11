import email
from django.shortcuts import *
from .models import *
from django.conf import settings
from django.core.mail import send_mail
from random import randint

# Create your views here.

default_data = {
    "app_name" : "food delivery",    
    "no_header_pages":["index", "register_page", 'otp_page'],
} 
def index(request):
    default_data['current_page'] = 'index'
    return render(request, 'food_admin/login_page.html', default_data)

def dashboard_page(request):
    default_data['current_page'] = 'dashboard_page'
    return render(request, 'food_admin/dashboard_page.html', default_data)

def register_page(request):
    default_data['current_page'] = 'register_page'
    return render(request, 'food_admin/register_page.html', default_data)

def profile_page(request):
    default_data['current_page'] = 'profile_page'
    profile_data(request)    #call profile data method to collect profile data
    return render(request, 'food_admin/profile_page.html', default_data)

# otp page:

def otp_page(request):
    default_data['current_page'] = 'otp_page'
    return render(request, 'food_admin/otp_page.html', default_data)


# otp page and sending to email:

def create_otp(request):
    email_to_list = [request.session['reg_data']['email'],]
    subject = ('OTP verification for Food Delivery App')
    otp = randint(1000,9999)   
    print ('OTP is : ', otp)    
    request.session['otp'] = otp    
    message = f"Your one time password is : {otp}"    
    email_from = settings.EMAIL_HOST_USER    
    send_mail(subject, message, email_from, email_to_list)
    
# OTP verifications:

def verify_otp(request):
    otp = int(request.POST['otp'])
    
    if otp == request.session['otp']:
        master = Master.objects.create(
            Email = request.session['reg_data']['email'],
            Password = request.session['reg_data']['password'],
            IsActive = True,
        )
    
        Profile.objects.create(
            Master = master,
        )
        
        del request.session['otp']
        del request.session['reg_data']
        
        print('otp verify success !!')
        
        return redirect(index)
         
    else:
        print('invalid otp')
        
    return redirect(register_page)


def registration(request):
    print(request.POST)
    request.session['reg_data']={
        'email' :request.POST['email'],
        'password': request.POST['password'], 
    }
    
    create_otp(request)

    return redirect(otp_page)

# profile data collection
def profile_data(request):
    master = Master.objects.get(Email = request.session['email'])
    profile = Profile.objects.get(Master = master)
    default_data['profile_data'] = profile
    
# profile image update:

def profile_image_upload(request):
    master = Master.objects.get(Email = request.session['email'])
    profile = Profile.objects.get(Master = master)
    
    #if 'profile_image' in request.FILES:
    # when we have to create multipart form, like text format and file format:
    profile.ProfileImage = request.FILES['profile_image']
    profile.save()
    return redirect(profile_page)
    
# profile update:
def profile_update(request):
    master = Master.objects.get(Email = request.session['email'])
    profile = Profile.objects.get(Master = master)
    
    profile.FullName = request.POST['full_name']
    profile.City = request.POST['city']
    profile.State = request.POST['state']
    profile.PinCode = request.POST['pincode']
    profile.Gender = request.POST['gender']
    profile.Address = request.POST['address']
    
    dob = request.POST['dob'].split('-')
    profile.DOB = '-'.join(dob)
    profile.save()
    return redirect(profile_page)
    
   

def login(request):
    print(request.POST)
    try:
        master = Master.objects.get(Email = request.POST['email'])
        if master.Password == request.POST['password']:
            request.session['email'] = master.Email
            return redirect(profile_page)
        else:
            print("Incorrect Password.")      
    except Master.DoesNotExist as err:
        print(err)
        return redirect(index)
    
    return redirect(index)

def logout(request):
    if 'email' in request.session:
        del request.session['email']
    return redirect(index)