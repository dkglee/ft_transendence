from django.shortcuts import render, redirect

# Create your views here.
def transcendencePage(request, *args, **kwargs):
	if not request.user.is_authenticated:
		return redirect("pingpong:login-user")
	context = {}
	return render(request, "transcendence/transcendencePage.html", context)
