from django.http import HttpResponse

# Create your views here.
def index(request):
	return HttpResponse("Hello, world. You're at the polls index.")

# 브라우저에서 url을 통해 해당 view를 보려면 urls.py를 작성해야 함.
