from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import forms,models
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib import auth
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.core.mail import send_mail
from django.shortcuts import render, redirect
#from librarymanagement.settings import EMAIL_HOST_USER


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/index.html')

#for showing signup/login button for member
def memberclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/memberclick.html')

#for showing signup/login button for librarian
def librarianclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/librarianclick.html')

def librariansignup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()


            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)

            return HttpResponseRedirect('librarianlogin')
    return render(request,'library/librariansignup.html',{'form':form})

def membersignup_view(request):
    form1=forms.StudentUserForm()
    form2=forms.StudentExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST)
        form2=forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            user2=f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

        return HttpResponseRedirect('memberlogin')
    return render(request,'library/membersignup.html',context=mydict)

def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

def afterlogin_view(request):
    if is_admin(request.user):
        return render(request,'library/librarianafterlogin.html')
    else:
        return render(request,'library/memberafterlogin.html')


@login_required(login_url='librarianlogin')
@user_passes_test(is_admin)
def addbook_view(request):
    #now it is empty book form for sending to html
    form=forms.BookForm()
    if request.method=='POST':
        #now this form have data from html
        form=forms.BookForm(request.POST)
        if form.is_valid():
            user=form.save()
            return render(request,'library/bookadded.html')
    return render(request,'library/addbook.html',{'form':form})

@login_required(login_url='librarianlogin')
@user_passes_test(is_admin)
def viewbook_view(request):
    books=models.Book.objects.all()
    return render(request,'library/viewbook.html',{'books':books})

@login_required(login_url='librarianlogin')
@user_passes_test(is_admin)
def updatebook_view(request, id):  # sourcery skip: extract-method
    
    queryset = models.Book.objects.get(id = id)
    print(queryset)
    if request.method == "POST":
        data = request.POST
        queryset.name  = data.get('name')
        queryset.isbn = data.get('isbn')
        queryset.author = data.get('author')
        queryset.category = data.get('category')
        print(data)
        queryset.save()
        return redirect('/viewbook')
    return render(request, 'library/updatebook.html', {'form':queryset})

@login_required(login_url='librarianlogin')
@user_passes_test(is_admin)
def updatemember_view(request, id):  # sourcery skip: extract-method
    
    queryset = models.StudentExtra.objects.get(id = id)
    print(queryset)
    if request.method == "POST":
        data = request.POST
        print('data',data.get('id'))
        queryset.id = data.get('id')
        queryset.enrollment = data.get('enrollment')
        queryset.branch = data.get('branch')
        print(data)
        print(queryset)
        queryset.save()
        return redirect('/viewmember')
    return render(request, 'library/updatemember.html', {'form':queryset})

@login_required(login_url='librarianlogin')
@user_passes_test(is_admin)
def deletebook_view(request, id):
    queryset = models.Book.objects.get(id = id)
    queryset.delete()
    return redirect('/viewbook')

@login_required(login_url='librarianlogin')
@user_passes_test(is_admin)
def deletemember_view(request, id):
    queryset =  models.StudentExtra.objects.get(id = id)
    queryset.delete()
    return redirect('/viewbook')

@login_required(login_url='librarianlogin')
@user_passes_test(is_admin)
def issuebook_view(request):
    form=forms.IssuedBookForm()
    if request.method=='POST':
        #now this form have data from html
        form=forms.IssuedBookForm(request.POST)
        if form.is_valid():
            obj=models.IssuedBook()
            obj.enrollment=request.POST.get('enrollment2')
            obj.isbn=request.POST.get('isbn2')
            obj.save()
            return render(request,'library/bookissued.html')
    return render(request,'library/issuebook.html',{'form':form})

@login_required(login_url='librarianlogin')
@user_passes_test(is_admin)
def viewissuedbook_view(request):
    issuedbooks=models.IssuedBook.objects.all()
    li=[]
    for ib in issuedbooks:
        issdate=str(ib.issuedate.day)+'-'+str(ib.issuedate.month)+'-'+str(ib.issuedate.year)
        expdate=str(ib.expirydate.day)+'-'+str(ib.expirydate.month)+'-'+str(ib.expirydate.year)
        #fine calculation
        days=(date.today()-ib.issuedate)
        print(date.today())
        d=days.days
        fine=0
        if d>15:
            day=d-15
            fine=day*10


        books=list(models.Book.objects.filter(isbn=ib.isbn))
        students=list(models.StudentExtra.objects.filter(enrollment=ib.enrollment))
        i=0
        for l in books:
            t=(students[i].get_name,students[i].enrollment,books[i].name,books[i].author,issdate,expdate,fine)
            i=i+1
            li.append(t)

    return render(request,'library/viewissuedbook.html',{'li':li})

@login_required(login_url='librarianlogin')
@user_passes_test(is_admin)
def viewmember_view(request):
    students=models.StudentExtra.objects.all()
    return render(request,'library/viewmember.html',{'students':students})


@login_required(login_url='memberlogin')
def viewissuedbookbymember(request):
    student=models.StudentExtra.objects.filter(user_id=request.user.id)
    issuedbook=models.IssuedBook.objects.filter(enrollment=student[0].enrollment)

    li1=[]

    li2=[]
    for ib in issuedbook:
        books=models.Book.objects.filter(isbn=ib.isbn)
        for book in books:
            t=(request.user,student[0].enrollment,student[0].branch,book.name,book.author)
            li1.append(t)
        issdate=str(ib.issuedate.day)+'-'+str(ib.issuedate.month)+'-'+str(ib.issuedate.year)
        expdate=str(ib.expirydate.day)+'-'+str(ib.expirydate.month)+'-'+str(ib.expirydate.year)
        #fine calculation
        days=(date.today()-ib.issuedate)
        print(date.today())
        d=days.days
        fine=0
        if d>15:
            day=d-15
            fine=day*10
        t=(issdate,expdate,fine)
        li2.append(t)

    return render(request,'library/viewissuedbookbymember.html',{'li1':li1,'li2':li2})
