from .models import Psychologist

def psychologist(request):
    try:
        psychologist = Psychologist.objects.get(user=request.user)
    except Psychologist.DoesNotExist:
        psychologist = None
    return {'psychologist': psychologist}