from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import get_template

from .models import NewsletterUser, Newsletter
from .forms import NewsletterUserSignUpForm, NewsletterCreationForm

def newsletter_signup(request):
	form = NewsletterUserSignUpForm(request.POST or None)

	if form.is_valid():
		instance = form.save(commit=False)
		if NewsletterUser.objects.filter(email=instance.email).exists():
			messages.warning(request,'your email already exists in our database', "alert alert-warning alert-dismissible")
		else:
			instance.save()
			messages.success(request, 'Your email has been submitted to the database', "alert alert-success alert-dismissible")
			subject = "Thank you for Joining Our NewsLetter"
			from_email = settings.EMAIL_HOST_USER
			to_email = [instance.email]
			with open(settings.BASE_DIR + "/newsletter/templates/newsletter/sign_up_email.txt") as f:
				signup_message = f.read()
			message = EmailMultiAlternatives(subject=subject, body=signup_message, from_email=from_email, to=to_email)
			html_template = get_template("newsletter/sign_up_email.html").render()
			message.attach_alternative(html_template, "text/html")
			message.send()

	context = {
		"form": form,
	}
	# template = "newsletter/sign_up.html"
	return render(request,"newsletter/sign_up.html" , context)

def newsletter_unsubscribe(request):
	form = NewsletterUserSignUpForm(request.POST or None)

	if form.is_valid():
		instance = form.save(commit=False)
		if NewsletterUser.objects.filter(email=instance.email).exists():
			NewsletterUser.objects.filter(email=instance.email).delete()
			messages.success(request, 'You have Being unsubscribe', 'alert alert-success alert-dismissible')

			subject = "You have being Unsubscribe"
			from_email = settings.EMAIL_HOST_USER
			to_email = [instance.email]
			with open(settings.BASE_DIR + "/newsletter/templates/newsletter/unsubscribe_email.txt") as f:
				signup_message = f.read()
			message = EmailMultiAlternatives(subject=subject, body=signup_message, from_email=from_email, to=to_email)
			html_template = get_template("newsletter/unsubscribe_email.html").render()
			message.attach_alternative(html_template, "text/html")
			message.send()
		else:
			messages.warning(request,'your email is not in the database', "alert alert-warning alert-dismissible")
	context = {
		"form": form,
	}

	template = "newsletter/unsubscribe.html"
	return render(request, template, context)

def control_newsletter(request):
	form = NewsletterCreationForm(request.POST or None)

	if form.is_valid():
		instance = form.save()
		newsletter = Newsletter.objects.get(id=instance.id)
		if newsletter.status == "Published":
			subject = newsletter.subject
			body = newsletter.body
			from_email =settings.EMAIL_HOST_USER
			for email in newsletter.email.all():
				send_mail(subject=subject, from_email=from_email, recipient_list=[ email ], message=body, fail_silently=True)

	context = {
		"form":form,
	}
	template = "control_panel/control_newsletter.html"
	return render(request, template, context)

def control_newsletter_list(request):
	newsletter = Newsletter.objects.all()

	paginator = Paginator(newsletter, 10)
	page = request.GET.get('page')

	try:
		items = paginator.page(page)
	except PageNotAnInteger:
		items = paginator.page(1)
	except EmptyPage:
		items = paginator.page(paginator.num_pages)

	index = items.number -1
	max_index = len(paginator.page_range)
	start_index = index -5 if index >= 5 else 0
	end_index = index + 5 if index <= max_index -5 else max_index
	page_range = paginator.page_range[start_index:end_index]

	context= {
		"items":items,
		"page_range":page_range
	}
	template = "control_panel/control_newsletter_list.html"
	return render(request, template, context)
