# portal/views/ngo_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.contrib import messages
from ..models import DonationCamp, Donation, NGOProfile
from ..forms import DonationCampForm, NGOProfileForm

@login_required(login_url='login_page')
def ngo_dashboard_overview(request):
    if request.user.user_type != 'NGO': return redirect('index')
    ngo_profile = request.user.ngo_profile
    stats = {
        'active_camps': DonationCamp.objects.filter(ngo=ngo_profile, is_active=True).count(),
        'total_volunteers': ngo_profile.volunteers.count(),
        'donations_to_verify': Donation.objects.filter(target_camp__ngo=ngo_profile, status='VERIFYING').count(),
        'total_donations_received': Donation.objects.filter(target_camp__ngo=ngo_profile, status='DELIVERED').count()
    }
    context = {'stats': stats}
    return render(request, 'ngo/dashboard_overview.html', context)

@login_required(login_url='login_page')
def ngo_manage_camps(request):
    if request.user.user_type != 'NGO': return redirect('index')
    ngo_profile = request.user.ngo_profile
    view_param = request.GET.get('view', None)

    if request.method == 'POST':
        form = DonationCampForm(request.POST)
        if form.is_valid():
            camp = form.save(commit=False)
            camp.ngo = ngo_profile
            camp.save()
            messages.success(request, 'New camp created successfully!')
            return redirect('ngo_manage_camps')
    else:
        form = DonationCampForm()

    active_camps = DonationCamp.objects.filter(ngo=ngo_profile, is_active=True).order_by('start_time')
    completed_camps = DonationCamp.objects.filter(ngo=ngo_profile, is_active=False).order_by('-completed_at')
    donations_to_verify = Donation.objects.filter(target_camp__ngo=ngo_profile, status='VERIFYING').order_by('delivered_at')
    
    context = {
        'form': form, 
        'active_camps': active_camps, 
        'completed_camps': completed_camps, 
        'donations_to_verify': donations_to_verify,
        'active_tab': view_param
    }
    return render(request, 'ngo/manage_camps.html', context)

@login_required(login_url='login_page')
def ngo_manage_volunteers(request):
    if request.user.user_type != 'NGO': return redirect('index')
    ngo_profile = request.user.ngo_profile
    registered_volunteers = ngo_profile.volunteers.annotate(active_deliveries=Count('assigned_donations', filter=Q(assigned_donations__status__in=['ACCEPTED', 'COLLECTED']))).order_by('full_name')
    context = {'volunteers': registered_volunteers}
    return render(request, 'ngo/manage_volunteers.html', context)

@login_required(login_url='login_page')
def ngo_profile(request):
    if request.user.user_type != 'NGO':
        return redirect('index')
    
    profile = get_object_or_404(NGOProfile, user=request.user)

    if request.method == 'POST':
        form = NGOProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('ngo_profile')
    else:
        form = NGOProfileForm(instance=profile)

    context = {'form': form}
    return render(request, 'ngo/profile.html', context)

@login_required(login_url='login_page')
def ngo_settings(request):
    if request.user.user_type != 'NGO': return redirect('index')
    return render(request, 'ngo/settings.html')