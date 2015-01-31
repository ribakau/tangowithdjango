from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}
    return render(request, 'rango/index.html', context_dict)


def about(request):
    return render(request, 'rango/about.html')


def category(request, category_name_slug):

    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        context_dict['name_slug'] = category.slug

        pages = Page.objects.filter(category=category)
        
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        return HttpResponseRedirect('/rango/add_category/')

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


def register(request):

    # Whether or not registration was successful.
    registered = False

    if request.method == 'POST':

        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
        
            user = user_form.save()
            
            # Setting a password.
            user.set_password(user.password)
            user.save()
            
            # Setting up user's profile. Not yet saving, since more details are to be added.
            profile = profile_form.save(commit=False)
            profile.user = user
            
            # If presented, picture is added to a User model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                
            # Saving user's profile.
            profile.save()

            registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )


def user_login(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        
        # Validation of user's username & password.
        user = authenticate(username=username, password=password)

        if user:

            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Your Rango account is disabled.")
                
        # Rerenders the login page and sends login_failed variable to login.html.
        # If login_failed == True, an error message is generated in the login page.
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return render(request, 'rango/login.html', {'login_failed': True})

    else:
        return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


@login_required
def user_logout(request):
    logout(request) 
    return HttpResponseRedirect('/rango/')