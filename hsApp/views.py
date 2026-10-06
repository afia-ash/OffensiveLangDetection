from django import views
from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
# Create your views here.


def index(request):
    return render(request, "index.html")


def login(request):
    if request.method == "POST":
        email = request.POST['name']
        password = request.POST['password']

        user = authenticate(username=email, password=password)
        if user is not None:
            request.session['email'] = email
            if user.is_active:
                if user.is_superuser:
                    return redirect("/adminHome")
                else:
                    sf = Users.objects.get(email=email)
                    request.session['id'] = sf.id
                    return redirect("/sfHome")
            else:
                msg = "Account is not Active..."
                return render(request, "login.html", {"msg": msg})
        else:
            msg = "User Dosent Exists..."
            return render(request, "login.html", {"msg": msg})
    else:
        return render(request, "login.html")


def sfReg(request):
    flag = 0
    msg = ""
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        password = request.POST['password']
        img = request.FILES["file"]

        if User.objects.filter(username=email).exists():
            msg = "Email already exists..."

        else:
            user = User.objects.create_user(
                username=email, password=password, is_active=1)
            user.save()
            sf = Users.objects.create(
                name=name, email=email, phone=phone, address=address, document=img, user=user)
            sf.save()
            msg = "Registration Successful..."
            flag = 1

    return render(request, "sfReg.html", {"msg": msg, "flag": flag})


def adminHome(request):
    return render(request, "adminHome.html")


def adminStartUp(request):
    data = Users.objects.filter(user__is_active=0)
    dataActive = Users.objects.filter(user__is_active=1)
    return render(request, "adminStartup.html", {"data": data, "dataActive": dataActive})


def approveStartUp(request):
    id = request.GET['id']
    status = request.GET['status']
    sf = User.objects.get(id=id)
    sf.is_active = status
    sf.save()
    return redirect("/adminStartUp")


def deleteStartUp(request):
    id = request.GET['id']
    user = Users.objects.get(user_id=id)
    user.delete()
    return redirect("/adminStartUp")


def adminViewFeedback(request):

    data = Feedback.objects.all()
    return render(request, "adminViewFeedback.html", {"data": data})


def adminViewDetections(request):

    data = Detection.objects.all()
    return render(request, "adminViewDetections.html", {"data": data})


def sfHome(request):
    id = request.session['id']

    data = Users.objects.get(id=id)
    post = Post.objects.exclude(user=id)
    if request.method == "POST":
        search = request.POST['search']
        post = Post.objects.filter(idea__contains=search).exclude(user=id)
    return render(request, "sfHome.html", {"data": data, "post": post})


def sfProfile(request):
    id = request.session['id']

    data = Users.objects.get(id=id)
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        password = request.POST['password']
        proUp = Users.objects.get(id=id)
        proUp.name = name
        proUp.email = email
        proUp.phone = phone
        proUp.address = address
        proUp.save()
        logUp = User.objects.get(username=data.user)
        logUp.set_password(password)
        logUp.username = email
        logUp.save()
        return redirect("/sfHome")
    return render(request, "sfProfile.html", {"data": data})


def sfChangeImage(request):
    id = request.session['id']
    data = Users.objects.get(id=id)
    if request.method == "POST":
        img = request.FILES["file"]

        data.document = img
        data.save()
        return redirect("/sfHome")
    return render(request, "sfChangeImage.html", {"data": data})


def sfPost(request):
    id = request.session['id']
    user = Users.objects.get(id=id)
    msg = ''
    if request.method == "POST":
        idea = request.POST['idea']
        description = request.POST['description']
        from bad_word_detector import main as check
        resultTitle = check(idea)
        resultDesc = check(description)
        if resultDesc == 'Good' and resultTitle == 'Good':
            db = Post.objects.create(idea=idea, desc=description, user=user)
            db.save()
        else:
            det = Detection.objects.create(
                user=user, title=idea, desc=description)
            det.save()
            msg = "Offensive language used. Cant post the content"

    return render(request, "sfPost.html", {"msg": msg})


def sfViewSelfPost(request):
    id = request.session['id']

    data = Post.objects.filter(user=id)
    return render(request, "sfViewSelfPost.html", {"data": data})


def sfUpdateIdea(request):
    id = request.GET['id']
    data = Post.objects.get(id=id)
    if request.method == "POST":
        idea = request.POST['idea']
        description = request.POST['description']
        data.idea = idea
        data.desc = description
        data.save()
        return redirect("/sfViewSelfPost")
    return render(request, "sfUpdateIdea.html", {"data": data})


def sfDeleteIdea(request):
    id = request.GET['id']
    data = Post.objects.get(id=id)
    data.delete()

    return redirect("/sfViewSelfPost")


def sfViewIdea(request):
    id = request.GET['post']
    sfid = request.session['id']
    data = Post.objects.get(id=id)
    msg = ''
    if request.method == "POST":
        comment = request.POST['comment']
        from bad_word_detector import main as check
        resultComment = check(comment)
        
        if resultComment == 'Good':
            user = Users.objects.get(id=sfid)
            db = Comments.objects.create(comment=comment, idea=data, user=user)
            db.save()
        else:
            msg = "Offensive language used. Cant post the comment"

    comments = Comments.objects.filter(idea=id)
    return render(request, "sfViewIdea.html", {"data": data, "comments": comments, "msg": msg})


def sfViewSf(request):
    id = request.GET['sfid']
    user = Users.objects.get(id=id)

    post = Post.objects.filter(user=id)
    return render(request, "sfViewSf.html", {"user": user, "post": post})


def sfAddFeedBack(request):
    id = request.session['id']
    if request.method == "POST":
        feedback = request.POST['feedback']
        user = Users.objects.get(id=id)

        db = Feedback.objects.create(feedback=feedback, user=user)
        db.save()
    data = Feedback.objects.filter(user=id)
    return render(request, "sfAddFeedBack.html", {"data": data})


def sfChat(request):
    sender = request.session["email"]
    data = Chat.objects.filter(
        Q(sender=sender) | Q(receiver=sender)).distinct()
    print(data)
    newData = set()
    for d in data:
        if d.sender != sender:
            newData.add(d.sender)
        else:
            newData.add(d.receiver)

    data = newData
    return render(request, "sfChat.html", {"data": data, "user": sender})


def sfChatPer(request):
    sender = request.session['email']
    receiver = request.GET['email']
    if request.method == "POST":
        msg = request.POST['msg']
        db = Chat.objects.create(sender=sender, receiver=receiver, message=msg)
        db.save()
    messages = Chat.objects.filter(
        Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender))
    status = None
    if messages:
        status = messages[0]
    return render(request, "sfChatPer.html", {"messages": messages, "user": sender, "status": status, "receiver": receiver})


def userBlock(request):
    id = request.GET['id']
    sender = request.session['email']
    status = request.GET['status']
    print(status)
    messages = Chat.objects.filter(
        Q(sender=sender, receiver=id) | Q(sender=id, receiver=sender)).update(blocked=status,blockedby=sender)
    return redirect("/sfChat")

def adminUpdatePostStatus(request):
    id = request.GET['id']
    status = request.GET['status']
    det = Detection.objects.get(id=id)
    if status == "Detected":
        det.status = "Vulgar Content"
    else:
        det.status = "Not Vulgar Content"
        user = det.user
        post = det.title
        desc = det.desc
        post = Post.objects.create(idea=post,desc=desc,user=user)
        post.save()
    det.save()
    return redirect("/adminViewDetections")








