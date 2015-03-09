from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserProfileForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query

def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits


    response = render(request,'rango/index.html', context_dict)

    return response


def about(request):
    
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0
    
    
    return render(request, 'rango/about.html', {'visits': count})


def category(request, category_name_slug):

    context_dict = {}
    result_list = []

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        context_dict['name_slug'] = category.slug

        pages = Page.objects.filter(category=category)
        
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        return HttpResponseRedirect('/rango/add_category/')
    
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list
            context_dict['query'] = query

    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)

            return HttpResponseRedirect('/rango/')
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                
                return HttpResponseRedirect('/rango/category/%s/' % category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()
    
    return render(request, 'rango/add_page.html', {'form':form, 'category': cat, 'name_slug': category_name_slug})


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


def track_url(request):
    
    if request.method == 'GET':
        if 'page_id' in request.GET:
            
            # Retrieves id from the request.
            page_id = request.GET['page_id']
            
            # Checks if there exists a page with a given id.
            try:
                page = Page.objects.get(id=page_id)
            except:
                page = None
            
            if page:
                page.views += 1
                page.save()
                return HttpResponseRedirect(page.url)
                
    return HttpResponseRedirect('/rango/')


@login_required
def password_change(request):
    dict = {}
    if request.method == 'POST':
        try:
            current_password = request.POST['current_password']
            new_password = request.POST['new_password']
            repeat_password = request.POST['repeat_password']
        except:
            dict['error_message'] = 'All the fields must be provided.'
        
        if authenticate(username=request.user.username, password=current_password) and new_password == repeat_password:
            request.user.set_password(new_password)
            request.user.save()
            dict['success'] = 'Your password has been changed successfully.'
        else:
            dict['error_message'] = 'Some of the details you provided were wrong.'
    
    return render(request, 'rango/password_change.html', dict)
        
@login_required
def user(request, username):
    context_dict = {}
    try:
        user = User.objects.get(username=username)
    except:
        user = None
    
    if user:
        context_dict['user_account'] = user
        try:
            user_profile = UserProfile.objects.get(user=user)
        except:
            user_profile = None
        if user_profile:
            context_dict['website'] = user_profile.website
            context_dict['website_name'] = user_profile.website.split('.')[1]
            context_dict['picture'] = user_profile.picture
        
        context_dict['logged_in'] = False
        if user == request.user:
            context_dict['logged_in'] = True
    return render(request, 'rango/user.html', context_dict)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(data=request.POST)
        
        try:
            profile = UserProfile.objects.get(user=request.user)
        except:
            profile = form.save(commit=False)
            profile.user = request.user
        
        if form.is_valid():
            if 'website' in request.POST:
                url = request.POST['website']
                if not url.startswith('http://'):
                    profile.website = 'http://' + url
                else:
                    profile.website = url
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
        return HttpResponseRedirect('/rango/user/%s' % request.user.username)
    else:
        form = UserProfileForm()
    return render(request, 'rango/edit_profile.html', {'profile' : form})


@login_required
def user_list(request):
    dict = {}
    try:
        user_list = User.objects.order_by('username')
        dict['users'] = user_list
    except:
        pass
    return render(request, 'rango/users.html', dict)
    