import joblib
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from core.classifier import predict_toxicity, train
from core.models import CommentData


class IndexView(TemplateView):
    template_name = 'index.html'


@csrf_exempt
def classify_view(request):
    text = request.POST['text']
    base_path = settings.BASE_DIR / 'models'
    model = joblib.load(base_path / 'toxic_classifier_model.pkl')
    vectorizer = joblib.load(base_path / 'toxic_vectorizer.pkl')
    prediction, probability = predict_toxicity(text, vectorizer, model)
    return JsonResponse({'is_toxic': bool(prediction == 1), 'probability': f'{probability:.1%}'})


@csrf_exempt
def fit_view(request):
    text = request.POST['text']
    is_toxic = request.POST['is_toxic'] == '1'
    is_trusted = request.user.is_superuser
    success_response = JsonResponse({'success': True})

    text_exists = CommentData.objects.filter(text=text).exists()
    if text_exists:
        return success_response

    CommentData.objects.create(text=text, is_toxic=is_toxic, is_trusted=is_trusted)
    train()
    return success_response
