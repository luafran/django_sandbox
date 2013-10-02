from django.http import HttpResponse
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import condition
from django.views.decorators.cache import cache_control
import json
import time

@csrf_exempt
def index(request):
    return HttpResponse("You did a " + request.method + " at index view.")


class MyView(View):
    def get(self, request):
        return HttpResponse("You did a GET at MyView.")

    def post(self, request):
        return HttpResponse("You did a POST at MyView.")

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(MyView, self).dispatch(*args, **kwargs)


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders it's content into JSON.
    """
    def __init__(self, data, **kwargs):
        #content = JSONRenderer().render(data)
        content = json.dumps(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class JSONView(View):
    def get(self, request):
        response = {'msg': 'You did a GET at JSONView.'}
        return JSONResponse(response)

    def post(self, request):
        if request.body != 'None' and request.body != '':
            try:
                request_body = json.loads(request.body)
            except ValueError:
                    response = {'error': 1, 'msg': 'Invalid json in request'}
                    return JSONResponse(response, status = 400)
        else:
            request_body = {}

        response_body = {'msg': 'You did a POST at JSONView.', 'request_body': request_body}
        return JSONResponse(response_body, status = 201)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(JSONView, self).dispatch(*args, **kwargs)

class LoginView(View):

    def get(self, request):
        next_url = request.GET.get('next', None)
        response = {'next_url': next_url}
        return JSONResponse(response, status=200)

    def post(self, request):
        if request.body != 'None' and request.body != '':
            try:
                request_body = json.loads(request.body)
            except ValueError:
                response = {'error': 1, 'msg': 'Invalid json in request'}
                return JSONResponse(response, status = 400)
        else:
            response = {'error': 1, 'msg': 'Required body with username and password not found in request'}
            return JSONResponse(response, status = 400)

        username = request_body['username']
        password = request_body['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                next_url = request.GET.get('next', None)
                response = {'next_url': next_url}
                resp = JSONResponse(response, status=301)
                resp['Location'] = next_url
                return resp

            else:
                # Return a 'disabled account' error message
                response = {'error': 2, 'msg': 'User account is disabled'}
                return JSONResponse(response, status=401)
        else:
            # Return an 'invalid login' error message.
            response = {'error': 3, 'msg': 'Invalid user/password pair'}
            return JSONResponse(response, status=401)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

@csrf_exempt
def my_logout(request):
    logout(request)
    # Redirect to a success page.
    next_url = request.GET.get('next', None)
    response = {'next_url': next_url}
    resp = JSONResponse(response, status=301)
    resp['Location'] = next_url
    return resp

@login_required
def protected_view(request):
    return HttpResponse("You did a " + request.method + " at protected view.")

def calc_etag(request):
    return 'luciano1'

def calc_last_modified_time(request):
    import datetime
    #delta = datetime.timedelta(minutes=-30)
    delta = datetime.timedelta(minutes=-160)
    #delta = datetime.timedelta(minutes=-10)
    return datetime.datetime.utcnow() + delta

@condition(etag_func=calc_etag, last_modified_func=calc_last_modified_time)
def conditional_view(request):
    return HttpResponse("You did a " + request.method + " at conditional view.")

@condition(etag_func=calc_etag, last_modified_func=calc_last_modified_time)
#@cache_control(no_cache=True, must_revalidate=True, max_age=0)
#@cache_control(max_age=30, must_revalidate=True)
@cache_control(max_age=30, must_revalidate=True)
def cached_view(request):
    return HttpResponse("You did a " + request.method + " cached view at " + time.asctime())
