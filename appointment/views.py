from django.shortcuts import  render, redirect
from django.http import HttpResponse
from appointment.forms import NewUserForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required , permission_required
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.views.generic import TemplateView , ListView
from django.db.models import Q, Case, When, Value, IntegerField
from appointment.models import Doctor , Appointment

def get_prioritized_doctors(queryset=None):
	if queryset is None:
		queryset = Doctor.objects.all()
	priority_order = Case(
		When(Q(state__iexact='Varanasi') | Q(hospitalName__icontains='Varanasi'), then=Value(1)),
		When(Q(state__iexact='Dhanbad') | Q(hospitalName__icontains='Dhanbad'), then=Value(2)),
		When(Q(state__iexact='Kolkata') | Q(hospitalName__icontains='Kolkata') | Q(state__iexact='Calcutta'), then=Value(3)),
		default=Value(4),
		output_field=IntegerField()
	)
	return queryset.annotate(city_priority=priority_order).order_by('city_priority', 'name')

def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("login")
		else:
			messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="appointment/register.html", context={"register_form":form})


def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				next_url = request.GET.get('next') or request.POST.get('next') or '/auth/book-appointment'
				return redirect(next_url)
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="appointment/login.html", context={"login_form":form})


def search(request):
	if request.method == 'POST':
		if not request.user.is_authenticated:
			return HttpResponse("login_required", status=401)

		timeslot = request.POST.get('timeSlot', 'Right Now')
		doctorName = request.POST.get('doctorName', '')
		try:
			doc = Doctor.objects.get(name=doctorName)
		except Doctor.DoesNotExist:
			return HttpResponse("Doctor not found", status=404)

		docEmail = doc.email
		userName = request.user.username
		userMail = request.user.email or "patient@diagnoai.org"

		appointments = doc.appointment_set.all()
		if appointments.exists():
			meetId = appointments[0].meetingId
		else:
			meetId = f"https://diagnoai.daily.co/telehealth-consult-{doc.id}"

		subject = 'Request for Telehealth Appointment'
		message = f'Patient Name: {userName}\nPatient Email: {userMail}\nDoctor Name: {doctorName}\nDoctor Email: {docEmail}\nTime slot: {timeslot}\nMeeting Link: {meetId}' 
		from_email = settings.EMAIL_HOST_USER or "no-reply@diagnoai.org"
		recipient_list = [docEmail, userMail]
		try:
			send_mail(subject, message, from_email, recipient_list)
		except Exception:
			pass
		return HttpResponse("done")

	doctors = get_prioritized_doctors(Doctor.objects.all())
	context = {
		"doctors": doctors
	}
	return render(request, 'videocall/videocallpage.html', context)


class BookAppointment(ListView):
	model = Doctor
	template_name = 'videocall/output.html'
	context_object_name = 'appointment'

	def get_queryset(self):
		state = self.request.GET.get('state', '').strip()
		spec = self.request.GET.get('specialization', '').strip()
		
		queryset = self.model.objects.all()
		if state:
			queryset = queryset.filter(
				Q(state__icontains=state) | 
				Q(hospitalName__icontains=state)
			)
		if spec:
			queryset = queryset.filter(specialization__icontains=spec)
		return get_prioritized_doctors(queryset)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['search_state'] = self.request.GET.get('state', '')
		context['search_spec'] = self.request.GET.get('specialization', '')
		context['doctors'] = context.get('appointment', [])
		return context


def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("/")

