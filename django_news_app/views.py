import sys

from django.shortcuts import render
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import authenticate, login, forms, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.context_processors import csrf
from forms import *
from models import *
from signals import post_key_expired, generate_activation_key
from django.template import RequestContext
from django.contrib import messages
from datetime import datetime
from django.utils import timezone
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.core.mail import send_mail
from config import *
from tweet_classifier import *
from collections import OrderedDict   
@transaction.atomic()
def register_user(request):
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        args['form'] = form
        if form.is_valid():
            try: 
                save_point = transaction.savepoint()
                form.save()  # save user to database if form is valid
            except:
                transaction.savepoint_rollback(save_point)
                err_message = (sys.exc_info()[1])
                messages.add_message(request,messages.ERROR,err_message)
            else:
                transaction.savepoint_commit(save_point)
                messages.add_message(request,messages.SUCCESS,'Successfully registered and activation link has been sent to your mail')
                args['form'] = RegistrationForm()
#             return HttpResponseRedirect('/register_success/')            
    else:
        args['form'] = RegistrationForm()

    return render_to_response('register.html', args, context_instance=RequestContext(request))

@transaction.atomic()
def register_confirm(request, activation_key):
    #check if user is already logged in and if he is redirect him to some other url, e.g. home
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
               
    
    # check if there is UserProfile which matches the activation key (if not then display 404)
    user_profile = get_object_or_404(UserProfile, activation_key=activation_key)
        
    user = user_profile.user
    
    if 'reset' in request.GET and request.GET['reset'] == str(True) and user_profile.key_expired:
        try:
            save_point = transaction.savepoint()
            post_key_expired.send(sender=user_profile,key_expired=user_profile.key_expired)
        except:
            transaction.savepoint_rollback(save_point)
            err_message = (sys.exc_info()[1])
            messages.add_message(request,messages.ERROR,err_message)
        else:
            transaction.savepoint_commit(save_point)
            messages.add_message(request,messages.SUCCESS,'The activation link has been again sent to your mail')
        return render_to_response('confirm.html',{'user_profile':user_profile},context_instance=RequestContext(request)) 
    #check if th activation key has expired, if it hase then render confirm_expired.html
    if user_profile.key_expired:
        return render_to_response('activation_key_expired.html',{'user_profile':user_profile},context_instance=RequestContext(request))
        
    #if the key hasn't expired save user and set him as active and render some template to confirm activation
    if not user.is_active:
        try:
            save_point = transaction.savepoint()
            user.is_active = True
            user.save()
        except:
            transaction.savepoint_rollback(save_point)
            err_message = (sys.exc_info()[1])
            messages.add_message(request,messages.ERROR,err_message)
        else:
            transaction.savepoint_commit(save_point)
            messages.add_message(request,messages.SUCCESS,'Your account has been successfully activated')
    else:
        messages.add_message(request,messages.INFO,'Your account has been already activated')
                
    return render_to_response('confirm.html',{'user_profile':user_profile},context_instance=RequestContext(request))    


def login_user(request):
    state = "Please log in below..."
    username = password = ''
    
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)               
                state = "You're successfully logged in!"
                return HttpResponseRedirect(reverse('home'))
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."

    return render_to_response('auth.html',{'state':state, 'username': username}, context_instance=RequestContext(request))

@transaction.atomic()
def reset_password(request):
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        args['form'] = form
        if form.is_valid():
            try:
                save_point = transaction.savepoint()
                password_reset_token = generate_activation_key(form.cleaned_data['email'])
                user = User.objects.get(email=form.cleaned_data['email'])
                user.userprofile.password_token = password_reset_token
                user.userprofile.save() 
                email_subject = 'Password reset confirmation'
                email_body = "Hi %s, to reset the password, click this link http://127.0.0.1:8000/reset_password_confirm/%s" % (user.username, password_reset_token)
                send_mail(email_subject, email_body, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
            except:
                transaction.savepoint_rollback(save_point)
                err_message = (sys.exc_info()[1])
                messages.add_message(request,messages.ERROR,err_message)
            else:
                transaction.savepoint_commit(save_point)
                messages.add_message(request,messages.SUCCESS,'The Password reset confirmation link has been sent to your email')
                args['form'] = PasswordResetForm()        
    else:
        args['form'] = PasswordResetForm()
    return render_to_response('reset_password.html', args, context_instance=RequestContext(request))
        
@transaction.atomic()
def reset_password_confirm(request,password_reset_token):
    args = {}
    args.update(csrf(request))
    args['link_expired'] = False 
    args['password_reset_token'] = password_reset_token
    try:
        user_profile = get_object_or_404(UserProfile,password_token=password_reset_token)
        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            args['form'] = form
            if form.is_valid():
                try:
                    save_point = transaction.savepoint()
                    if user_profile.user.check_password(form.cleaned_data['password2']):
                       raise forms.ValidationError('New password should not be the same as old password')
                    user_profile.user.set_password(form.cleaned_data['password2'])
                    user_profile.user.save()
                    user_profile.password_token=None
                    user_profile.save()
                except forms.ValidationError as e:
                    transaction.savepoint_rollback(save_point)
                    messages.add_message(request,messages.ERROR,e.message)
                except:
                    transaction.savepoint_rollback(save_point)
                    err_message = (sys.exc_info()[1])
                    messages.add_message(request,messages.ERROR,err_message)
                else:
                    transaction.savepoint_commit(save_point)
                    messages.add_message(request,messages.SUCCESS,'Password has been successfully changed and the link has been expired')
                    args['link_expired'] = True               
        else:
            args['form'] = PasswordResetConfirmForm()
    except Http404 as e:
        args['link_expired'] = True
    return render_to_response('reset_password_confirm.html', args, context_instance=RequestContext(request))



def logout(request):
    if request.user.is_authenticated():
        if hasattr(request, 'user'):
            request.user = AnonymousUser()
        logout(request)
    request.session.flush()
    return HttpResponseRedirect(reverse('login'))

@login_required(login_url=reverse_lazy('login'))
def home(request):
    args={}
    args.update(csrf(request))
    args['categories'] = list()
    if request.method ==  'POST':
        form = NewsListForm(request.POST)
        args['form'] = form
        if form.is_valid():
            news_channel = form.cleaned_data.get('news_channel')
            try:
                classified_tweets,tweets_category_counter = classify_tweets(NewsList(int(news_channel)).ui_return())
            except:
                err_message = (sys.exc_info()[1])
                messages.add_message(request,messages.ERROR,err_message)
            else:   
                messages.add_message(request,messages.SUCCESS,'Tweets Successfully Classified')
                ordered_tweets = sorted(classified_tweets.items(),key=lambda category:category[0] in request.POST.getlist('category_selected'), reverse=True)
                args['classified_tweets'] = OrderedDict(ordered_tweets)
                args['categories'] = tweets_category_counter.most_common()        
                args['selected_category'] = request.POST.getlist('category_selected')
    else:
        args['form'] = NewsListForm()
    return render_to_response('home.html',args,context_instance=RequestContext(request))