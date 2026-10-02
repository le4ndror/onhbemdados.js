from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.escolher_edicao, name='escolher_edicao'),
    path('edicao/<int:edicao_id>/fases/', views.escolher_fase, name='escolher_fase'),
    path('fase/<int:fase_id>/questoes/', views.listar_questoes, name='listar_questoes'),
    path('questao/<int:questao_id>/', views.detalhes_questao, name='detalhes_questao'),
    path('busca/', views.busca_global, name='busca_global'),
]
