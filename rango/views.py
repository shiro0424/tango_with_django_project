from django.shortcuts import render
from django.http import HttpResponse
# Import the Category model
from rango.models import Category
from rango.models import Page
# Import forms
from rango.forms import CategoryForm
from rango.forms import PageForm
from django.shortcuts import redirect
from django.urls import reverse

def index(request):
	# Query the database for a list of ALL categories currently stored.
	# Order the categories by the number of likes in descending order.
	# Retrieve the top 5 only -- or all if less than 5.
	# Place the list in our context_dict dictionary (with our boldmessage!)
	# that will be passed to the template engine.
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]

	# return HttpResponse("Rango says hey there partner!"
	# 	+ "</br><a href='/rango/about/'>About</a>")
	# Construct a dictionary to pass to themplate engine as its context
	# Note the key boldmessage matches to {{ boldmessage }} in the template!
	context_dict = {}
	context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
	context_dict['categories'] = category_list
	context_dict['pages'] = page_list

	# Render the response and send it back!
	return render(request, 'rango/index.html', context=context_dict)

def about(request):
	context_dict = {'MEDIA_URL': '/media/'}
	return render(request, 'rango/about.html', context=context_dict)

def add_category(request):
	form = CategoryForm()

	# A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# Check whether the form is valid
		if form.is_valid():
			# Save the new category to the database.
			form.save(commit=True)
			# After the category is saved, 
			# redirect the user back to the index view.
			return redirect('/rango/')
		else:
			# If the supplied form contained errors
			# Print the error to the terminal
			print(form.errors)
	# Render the form
	return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None

	# A page cannot be added to a Category that does not exist...
	if category is None:
		return redirect('/rango/')

	form = PageForm()

	# A HTTP POST?
	if request.method == 'POST':
		form = PageForm(request.POST)

	# Check whether the form is valid
	if form.is_valid():
		if category:
			page = form.save(commit=False)
			page.category = category
			page.views = 0
			page.save()

			return redirect(reverse('rango:show_category',
									kwargs={'category_name_slug':
										category_name_slug}))
	else:
		# If the supplied form contained errors
		# Print the error to the terminal
		print(form.errors)
	# Render the form
	context_dict = {'form': form, 'category': category}
	return render(request, 'rango/add_page.html', context=context_dict)

def show_category(request, category_name_slug):
	# Create a context dictionary which we can pass
	# to the template rendering engine.
	context_dict = {}

	try:
		# Can we find a category name slug with the given name?
		# If we can't, the .get() method raises a DoesNotExist exception.
		# The .get() method returns one model instance or raises an exception.
		category = Category.objects.get(slug=category_name_slug)

		# Retrieve all of the associated pages.
		# The filter() will return a list of page objects or an empty list.
		pages = Page.objects.filter(category=category)

		# Adds our results list to the template context under name pages.
		context_dict['pages'] = pages
		# We also add the category object from
		# the database to the context dictionary.
		# We'll use this in the template to verify that the category exists.
		context_dict['category'] = category
	except Category.DoesNotExist:
		# We get here if we didn't find the specified category.
		# Don't do anything -
		# the template will display the "no category" message for us.
		context_dict['category'] = None
		context_dict['pages'] = None

	# Go render the response and return it to the client.
	return render(request, 'rango/category.html', context=context_dict)

def show_page(request, page_name_slug):
	# Create a context dictionary which we can pass
	# to the template rendering engine.
	context_dict = {}

	try:
		category = Page.objects.get(slug=page_name_slug)

		pages = Page.objects.filter(page=page)

		context_dict['pages'] = pages
		context_dict['category'] = category
	except Category.DoesNotExist:
		context_dict['category'] = None
		context_dict['pages'] = None

	return render(request, 'rango/category.html', context=context_dict)