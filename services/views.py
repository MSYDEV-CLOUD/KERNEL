from django.shortcuts import render, redirect
from .forms import IFTACalculatorForm

def ifta_service_view(request):
    if request.method == 'POST':
        form = IFTACalculatorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the valid form data to the database
            return redirect('ifta_success')  # Redirect after successful submission
    else:
        form = IFTACalculatorForm()
    
    return render(request, 'services/ifta_service.html', {'form': form})
