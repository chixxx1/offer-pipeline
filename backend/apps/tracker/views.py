# from django.shortcuts import render
from django.utils import timezone

from rest_framework import viewsets, status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Vacancy, Application, VacancyRecommendation
from django.contrib.auth.models import User
from .serializers import (
    VacancySerializer,
    ApplicationSerializer,
    UserSerializer,
    RegisterSerializer,
    VacancyRecommendationSerializer,
)
from apps.tracker.services.matching import sync_user_recommendations
from apps.users.models import Profile, ProfileVariant


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        vacancy_id = request.data.get('vacancy_id')
        existing = Application.objects.filter(vacancy_id=vacancy_id, user=request.user).first()

        if existing:
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class RecommendationViewSet(viewsets.GenericViewSet):
    serializer_class = VacancyRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = VacancyRecommendation.objects.filter(user=user, is_dismissed=False)

        variant_id = self.request.query_params.get('variant_id')
        if variant_id:
            queryset = queryset.filter(variant_id=variant_id)

        only_new = self.request.query_params.get('only_new')
        if only_new is not None and str(only_new).lower() == 'true':
            queryset = queryset.filter(is_new=True)

        min_score = self.request.query_params.get('min_score')
        if min_score is not None:
            try:
                queryset = queryset.filter(score__gte=int(min_score))
            except ValueError:
                pass

        # Сначала по свежести вакансии (-vacancy__published_at, -created_at), затем по -score.
        queryset = queryset.order_by('-vacancy__published_at', '-created_at', '-score')
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def sync(self, request):
        user = request.user
        variant = None
        variant_id = request.data.get('variant_id')
        if variant_id:
            variant = get_object_or_404(
                ProfileVariant, id=variant_id, profile__user=user
            )

        profile = Profile.get_for_user(user)
        # Запускаем синхронизацию рекомендаций с hh.ru.
        sync_user_recommendations(user, variant=variant, fetch_from_hh=True)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={
            'profile': profile,
            'variant': variant,
        })
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        recommendation = get_object_or_404(
            VacancyRecommendation, id=pk, user=request.user
        )
        recommendation.is_dismissed = True
        recommendation.is_new = False
        recommendation.save(update_fields=['is_dismissed', 'is_new', 'updated_at'])
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='mark-seen')
    def mark_seen(self, request):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            return Response({'error': 'ids должен быть списком'}, status=400)

        VacancyRecommendation.objects.filter(
            user=request.user, id__in=ids, is_new=True
        ).update(is_new=False, updated_at=timezone.now())
        return Response({'updated': len(ids)})
