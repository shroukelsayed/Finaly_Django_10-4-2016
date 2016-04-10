from django.shortcuts import render,render_to_response
from django.http import HttpResponse ,HttpResponseRedirect
from .models import *
from django.conf import settings
import datetime
import os
from django.contrib.auth.models import User
from _mysql import result
from html5lib.treewalkers._base import to_text
from django.contrib.auth import authenticate
from .forms import UserForm
from django.template import RequestContext
from django.db.models import Count
import re
from .forms import *
from random import randint
from django.core.mail import send_mail , BadHeaderError


# Create your views here.
def addArticaleForm(request):
    #adding article is depending on user's rolles --> Sarah
    # user = request.user
    # if user.is_staff or user.is_superuser:
        #Salma
    return render(request, 'blog/addArtical.html')
    # else :
    #     return render(request, 'blog/permissionDenied.html')

def updateArticaleForm(request, articale_id,user_id):
    articale=Articles.objects.get(pk=articale_id)
    #adding article is depending on user's rolles --> Sarah
    # user = request.user
    # if user.is_staff or user.is_superuser:
    return render(request, 'blog/updateArticale.html', {'articale':articale})
    # else :
    #     return render(request, 'blog/permissionDenied.html')

def deleteArticaleForm(request, articale_id):
    #adding article is depending on user's rolles --> Sarah
    # user = request.user
    # if user.is_staff or user.is_superuser:
        #salma
    return render(request, 'blog/deleteArticale.html', {'articale_id':articale_id})
    # else :
    #     return render(request, 'blog/permissionDenied.html')

def addArticale(request,user_id):
    content = request.POST['content']
    user=User.objects.get(pk=user_id)
    title = request.POST['title']
    if request.FILES.has_key('img') :
        image = request.FILES['img']
    else:
        image = ''
    c = Articles(article_content=content, article_title=title, article_creationDate=datetime.datetime.now(), article_image=image,user_id=user)
    c.save()
    #adding article is depending on user's rolles --> Sarah
    # user = request.user
    # if user.is_staff or user.is_superuser:
        #Salma
    return render(request, 'blog/addArtical.html')
    # else :
    #     return render(request, 'blog/permissionDenied.html')

#Salma
def updateArticale(request, articale_id,user_id):
    articale = Articles.objects.get(pk=articale_id)
    if articale.article_image :
        os.remove(os.path.join(settings.MEDIA_ROOT, articale.article_image.name))
    articale.article_title = request.POST['title']
    articale.article_content = request.POST['content']
    articale.article_image = request.FILES['img']
    articale.save()
    #adding article is depending on user's rolles --> Sarah
    # user = request.user
    # if user.is_staff or user.is_superuser:
        #salma
    articales = data_myArticalesForm(user_id)
    return render(request, 'blog/myArticales.html',{'articales':articales})
    # else :
    #     return render(request, 'blog/permissionDenied.html')

def deleteArticale(request, articale_id, user_id):
    articale = Articles.objects.get(pk=articale_id)
    if articale.article_image :
        os.remove(os.path.join(settings.MEDIA_ROOT, articale.article_image.name))
    articale.delete()
    articales=data_myArticalesForm(user_id)
    #adding article is depending on user's rolles --> Sarah
    # user = request.user
    # if user.is_staff or user.is_superuser:
        #Salma
    return render(request, 'blog/myArticales.html',{'articales':articales})
    # else :
    #     return render(request, 'blog/permissionDenied.html')

# def selectAllArticales(request):
# 	articales = Articles.objects.all().order_by('-id')[:5]
# 	return render(request, 'blog/firstPage.html',{'articales':articales})

def data_singleArticalePage(request,articale_id):
    articale = Articles.objects.get(pk=articale_id)
    comments=articale.comments_set.all()
    likes=Comments.objects.filter(article_id__id=articale_id).annotate(num_likes=Count('likes')) # number of users liked each comment in this articale
    tags=articale.tags_set.all();
    related_articles=data_relatedArticales(articale_id)   
    numViews=articale.viewedBy.count()
    writer=articale.user_id

    if "user_id" in request.session :
        user=User.objects.get(pk=request.session['user_id'])
        isLike=user.likedBy.filter(article_id=articale_id).values_list('id', flat=True)
        isMarked=Articles.objects.filter(readLater__id=request.session['user_id'],pk=articale_id).exists()
        return {'articale':articale,'comments':comments,'likes':likes,'isLike':isLike,'tags':tags,'related_articles':related_articles,'isMarked':isMarked,'numViews':numViews,'writer':writer}
    else:
        return {'articale':articale,'comments':comments,'likes':likes,'tags':tags,'related_articles':related_articles,'numViews':numViews,'writer':writer}

def data_relatedArticales(article_id):
    article_tags=Articles.objects.get(pk=article_id).tags_set.values_list('id', flat=True)
    articles=Articles.objects.exclude(pk=article_id).filter(tags__id__in=article_tags).annotate(c=Count(id)).order_by('-c','-article_creationDate')[0:5]
    return articles

def selectAnArticale(request,articale_id):
    data=data_singleArticalePage(request,articale_id)
    if "user_id" in request.session :
        user=User.objects.get(pk=request.session['user_id'])
        data['articale'].viewedBy.add(user)
    return render(request, 'blog/singleArticale.html',data)

def readLater(request,article_id,user_id):
    user=User.objects.get(pk=user_id)
    data=data_singleArticalePage(request,article_id)
    if data['isMarked']:
        data['articale'].readLater.remove(user)
        data['isMarked']=False
    else:
        data['articale'].readLater.add(user)
        data['isMarked']=True
    return render(request, 'blog/singleArticale.html',data)

def readLaterPage(request,user_id):
    user=User.objects.get(pk=user_id)
    articles=user.markedArticles.all()
    return render(request, 'blog/readLater.html',{'articles':articles})

def like(request,comment_id,user_id):
    comment=Comments.objects.get(pk=comment_id)
    articale_id=comment.article_id.id
    data=data_singleArticalePage(request,articale_id)
    user=User.objects.get(pk=user_id)
    comment.likes.add(user)
    return render(request, "blog/singleArticale.html", data)

def unlike(request,comment_id,user_id):
    comment=Comments.objects.get(pk=comment_id)
    articale_id=comment.article_id.id
    data=data_singleArticalePage(request,articale_id)
    user=User.objects.get(pk=user_id)
    comment.likes.remove(user)
    return render(request, "blog/singleArticale.html", data)


def likes2(request,articale_id,user_id):
    articale = Articles.objects.get(pk=articale_id)
    comments=articale.comments_set.all() #all comments on this articale
    user=User.objects.get(pk=user_id)
    isLike=user.likedBy.filter(article_id=articale_id)
    return render(request, "blog/likes.html", {'isLike':isLike})

def baned_words_filteration(massege):
    words=Banwords.objects.all().values('word')
    arr=[]
    for w in words:
        arr.append(' '+w['word']+' ')
    prohibitedWords = ['Some', 'Random', 'Words']
    big_regex = re.compile('|'.join(map(re.escape, arr)),flags=re.IGNORECASE)
    return big_regex.sub("*****", massege)

def addComment(request,articale_id,user_id):
    comment = request.POST['comment']
    new_comment = baned_words_filteration(comment)
    articale=Articles.objects.get(pk=articale_id)
    user=User.objects.get(pk=user_id)
    c = Comments(comment_content=new_comment, comment_creationDate=datetime.datetime.now(), article_id=articale, user_id=user)
    c.save()
    data=data_singleArticalePage(request,articale_id)

    return render(request, 'blog/singleArticale.html',data)

def addReply(request,articale_id,comment_id,user_id):
    reply = request.POST['reply']
    new_reply=baned_words_filteration(reply)
    articale=Articles.objects.get(pk=articale_id)
    comment=Comments.objects.get(pk=comment_id)
    user=User.objects.get(pk=user_id)
    c = Comments(comment_content=new_reply, comment_creationDate=datetime.datetime.now(), article_id=articale,parent_id=comment,user_id=user)
    c.save()
    data=data_singleArticalePage(request,articale_id)
    return render(request, 'blog/singleArticale.html',data)

def data_myArticalesForm(user_id):
    articales=Articles.objects.filter(user_id=user_id).order_by('-id')
    return articales

def myArticales(request,user_id):
    articales=data_myArticalesForm(user_id)
    return render(request, 'blog/myArticales.html',{'articales':articales})

# list all users --> Sarah
def listAllUsers(request):
    users = User.objects.all()
    result = "<table border='1'><th>First name</th>"
    result += "<th>Last name</th><th>username</th>"
    result += "<th>email</th><th>Last Login</th>"
    result += "<th>date joined</th><th>is active?</th>"
    result += "<th>is staff?</th><th>is super user?</th>"
    for user in users :
        result += '<tr><td>' + user.first_name + '</td>'
        result += '<td>' + user.last_name + '</td>'
        result += '<td>' + user.username + '</td>'
        result += '<td>' + user.email + '</td>'
        result += '<td>' + to_text(user.last_login) + '</td>'
        result += '<td>' + to_text(user.date_joined) + '</td>'
        result += '<td>' + to_text(user.is_active) + '</td>'
        result += '<td>' + to_text(user.is_staff) + '</td>'
        result += '<td>' + to_text(user.is_superuser) + '</td></tr>'

    result += "<table>"
    return HttpResponse(result)

# Login Part  With Sessions  -->  Shrouk (functions : home,signin,logout)
def signin(request):
    context = RequestContext(request)
    articales = Articles.objects.filter(article_isApproved=True).order_by('-id')
    if "rememberMe" in request.COOKIES or "user_id" in request.session:
        return render(request, 'blog/home.html',{'user_id':request.session["user_id"],'articales':articales})
    else:
        if request.method == 'POST':
            userName = request.POST['u_name']
            password = request.POST['pass']
            print userName 
            print password

            user = authenticate(username=userName, password=password)

            if user:
                if user.is_active:
                    print "active"
                    # login(request, user)
                    request.session["user_id"] = user.id
                       
                    if request.POST.get('remember_me') == "checked":
                        request.session.set_test_cookie()
                        request.COOKIES['rememberMe'] = request.POST['remember_me']
                    return render(request, 'blog/home.html',{'User':user,'articales':articales})
                else:
                    return render(request, 'blog/activeAccount.html')
            else:
                return HttpResponseRedirect('/blog/register')
        else:
            return render(request,'blog/signin.html', context)

# def signin(request):
#     users = User.objects.all()
#     try:
#         for user in users:
#             # check for username and pass in DB ...
#             if (user.username == request.POST['u_name'] and user.password == request.POST['pass']):
#             # the password verified for the user ...
#                 if user.is_active:
#                     # User is valid, active and authenticated ...
#                     #set user session to move around pages ...
#                     request.session["user_id"] = user.id
#                     #check if the user marked the remember me checkbox to set cookie ...
#                     if request.POST.get('remember_me') == "checked":
#                         request.session.set_test_cookie()
#                         # if request.session.test_cookie_worked():
#                         #     print "cookie wokrs"
#                         #set user cookie to remember when logged in again ...
#                         request.COOKIES['rememberMe'] = request.POST['remember_me']
#                     return render(request, 'blog/home.html',{'User':user})
#                 else:
#                     #The password is valid, but the account has been disabled! ...
#                     return render(request, 'blog/activeAccount.html')
#     except:
#         try:
#             if "user_id" in request.session :
#                 return  render(request, 'blog/home.html')
#             else:
#                 return render(request, 'blog/signin.html')
#         except:
#             return render(request, 'blog/signin.html')
#     return render(request, 'blog/register.html')

def home(request):
    #check if the user logged in redirect to home page with a session
    articales = Articles.objects.filter(article_isApproved=True).order_by('-id')
    if "user_id" in request.session :
        user_id = request.session["user_id"]
        return  render(request, 'blog/home.html',{'user_id':user_id,'articales':articales})
    return render(request,'blog/home.html',{'articales':articales})

def logout(request):
    #delete user session ...
    del request.session["user_id"]
    #check if there's cookie to delete it  ...
    if request.session.test_cookie_worked():
       request.session.delete_test_cookie()
    return render(request,'blog/signin.html')


#Forget Password Part --> shrouk (functions : randomConfirm ,forgetPass ,confirm ,resetPass)
def randomConfirm(length=3):
    #create random number to send it within an email for user email to set his password ...
    return randint(100**(length-1), (100**(length)-1))

def forgetPass(request):
    form = forgetPassForm(request.POST or None)
   
    if form.is_valid():
        email = form.cleaned_data.get("email")
        userName = form.cleaned_data.get("username")
        global forgetPass_user
        users = User.objects.all()
        try:
            for user in users :
                if user.username == userName :
                    # print user.username
                    # print userName
                    forgetPass_user = userName
                    subject = " Hi ,Somebody recently asked to reset your Facebook password. "
                    global msg
                    msg = str(randomConfirm())
                    fromEmail = settings.EMAIL_HOST_USER
                    toEmail = [email]
                    try:
                        send_mail(subject,msg,fromEmail,toEmail,fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return HttpResponseRedirect('/confirm/',{'User':user})
        except:
            return render(request,'blog/forgetPassword.html',{'form':form })
        return render(request,'blog/forgetPassword.html',{'form':form })
    return render(request,'blog/forgetPassword.html',{'form':form })

def confirm(request):
    form = confirmPassForm(request.POST or None)
    if form.is_valid():
        code = form.cleaned_data.get("code")
        print code
        print msg
        if code == msg :
            return HttpResponseRedirect('/reset/')
    context = {
        "form" : form,
    }
    return render(request,'blog/confirmMail.html',context)

def resetPass(request):
    form = resetPassForm(request.POST or None)
    if form.is_valid():
        password = form.cleaned_data.get("password")
        passwordConf = form.cleaned_data.get("confirmPassword")
        if password == passwordConf :
            user = User.objects.get(username=forgetPass_user)
            user.set_password(password)
            user.save()
            request.session["user_id"] = user.id
            return render(request,'blog/home.html')
       
    context = {
        "form" : form,
    }
    return render(request,'blog/resetPass.html',context) 





def index(request) :
	context = {}
	return render(request,'blog/index.html',context)

def validate(request):

        return render(request,'blog/index.html',context)

def register(request):
    context = RequestContext(request)
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid()and profile_form.is_valid():
            user=user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'image' in request.FILES:
                profile.image = request.FILES['image']

            profile.save()
            registered = True
            email=user.email
            subject = " welcome . "
            msg = "welcome in our site."
            fromEmail = settings.EMAIL_HOST_USER
            toEmail = [email]
            try:
                send_mail(subject, msg, fromEmail, toEmail, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
        else:

            print user_form.errors, profile_form.errors

    else:
        user_form=UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
        'blog/register.html',
        {'user_form':user_form, 'profile_form': profile_form,'registered':registered},context
    )




#Sarah
def userProfile(request):
    user = User.objects.get(pk=request.session["user_id"])
    avatar = UserProfile.objects.get(user_id=request.session["user_id"])
    return render(request, 'blog/profile.html', {'user':user, 'avatar':avatar})


#sarah
def updateInfo(request):
    user = User.objects.get(pk=request.session["user_id"])
    if request.method == 'POST' :
        user.first_name=request.POST['fname']
        user.last_name=request.POST['lname']
        user.email=request.POST['email']
        if request.POST['password'] != '' :
            user.set_password(request.POST['password'])
        user.save()
        #call UserProfile here
    return HttpResponseRedirect('/profile')

def updateImages(request):
    if request.method=='POST':
        form = ImageUploadForm(request.POST,request.FILES)
        if form.is_valid():
            img = UserProfile.objects.get(user_id=request.session["user_id"])
            img.image = form.cleaned_data['image']
            img.save()
    return HttpResponseRedirect('/profile')


