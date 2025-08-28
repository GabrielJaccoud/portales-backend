from flask import Blueprint, request, g
from src.models.user import db, User
from src.models.portal import Portal
from src.models.review import Review
from src.models.exploration import Exploration
from src.utils.auth import auth_required, optional_auth
from src.utils.helpers import success_response, error_response
from datetime import datetime, timedelta
from sqlalchemy import func, desc

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/analytics/dashboard", methods=["GET"])
@auth_required
def get_dashboard_analytics():
    """
    Estatísticas gerais da plataforma (para admins)
    """
    days = request.args.get("days", 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Estatísticas gerais
    total_users = User.query.count()
    total_portals = Portal.query.filter_by(is_public=True, is_active=True).count()
    total_reviews = Review.query.count()
    total_explorations = Exploration.query.count()
    
    # Usuários ativos (que fizeram alguma ação nos últimos 30 dias)
    active_users = User.query.filter(
        User.last_login >= start_date
    ).count() if hasattr(User, 'last_login') else 0
    
    # Portais mais populares (por número de curtidas)
    popular_portals = Portal.query.join(Portal.liked_by).group_by(Portal.id).order_by(
        desc(func.count(User.id))
    ).limit(10).all()
    
    # Crescimento diário (últimos 7 dias)
    daily_growth = {}
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        new_users = User.query.filter(
            func.date(User.created_at) == date.date()
        ).count()
        
        new_portals = Portal.query.filter(
            func.date(Portal.created_at) == date.date()
        ).count()
        
        new_reviews = Review.query.filter(
            func.date(Review.created_at) == date.date()
        ).count()
        
        daily_growth[date_str] = {
            "new_users": new_users,
            "new_portals": new_portals,
            "new_reviews": new_reviews
        }
    
    return success_response({
        "total_users": total_users,
        "total_portals": total_portals,
        "total_reviews": total_reviews,
        "total_explorations": total_explorations,
        "active_users": active_users,
        "popular_portals": [portal.to_dict() for portal in popular_portals],
        "daily_growth": daily_growth
    })

@analytics_bp.route("/analytics/user/<user_id>", methods=["GET"])
@auth_required
def get_user_analytics(user_id):
    """
    Analytics específicas do usuário
    """
    # Verificar se o usuário está consultando suas próprias analytics
    if g.current_user_id != user_id:
        return error_response(
            "Você só pode acessar suas próprias analytics",
            "AUTHORIZATION_ERROR",
            status_code=403
        )
    
    user = User.query.get(user_id)
    if not user:
        return error_response(
            "Usuário não encontrado",
            "RESOURCE_NOT_FOUND",
            status_code=404
        )
    
    # Estatísticas do usuário
    portals_count = Portal.query.filter_by(creator_id=user_id).count()
    reviews_count = Review.query.filter_by(user_id=user_id).count()
    explorations_count = Exploration.query.filter_by(user_id=user_id).count()
    
    # Total de curtidas recebidas nos portais do usuário
    total_likes = db.session.query(func.count()).select_from(
        Portal.query.filter_by(creator_id=user_id).join(Portal.liked_by).subquery()
    ).scalar() or 0
    
    # Portais mais populares do usuário
    popular_portals = Portal.query.filter_by(creator_id=user_id).join(
        Portal.liked_by
    ).group_by(Portal.id).order_by(
        desc(func.count(User.id))
    ).limit(5).all()
    
    return success_response({
        "portals_count": portals_count,
        "reviews_count": reviews_count,
        "explorations_count": explorations_count,
        "total_likes_received": total_likes,
        "followers_count": len(user.followers),
        "following_count": len(user.following),
        "popular_portals": [portal.to_dict() for portal in popular_portals]
    })

@analytics_bp.route("/analytics/portal/<int:portal_id>", methods=["GET"])
@auth_required
def get_portal_analytics(portal_id):
    """
    Analytics específicas do portal
    """
    portal = Portal.query.get(portal_id)
    if not portal:
        return error_response(
            "Portal não encontrado",
            "RESOURCE_NOT_FOUND",
            status_code=404
        )
    
    # Verificar se o usuário é o criador do portal
    if g.current_user_id != portal.creator_id:
        return error_response(
            "Você só pode acessar analytics dos seus próprios portais",
            "AUTHORIZATION_ERROR",
            status_code=403
        )
    
    # Estatísticas do portal
    likes_count = len(portal.liked_by)
    favorites_count = len(portal.favorited_by)
    reviews_count = Review.query.filter_by(portal_id=portal_id).count()
    explorations_count = Exploration.query.filter_by(portal_id=portal_id).count()
    
    # Avaliação média
    avg_rating = db.session.query(func.avg(Review.rating)).filter_by(
        portal_id=portal_id
    ).scalar() or 0
    
    # Visualizações por dia (últimos 30 dias)
    # Nota: Isso requereria um sistema de tracking de views
    # Por enquanto, retornamos dados simulados
    daily_views = {}
    for i in range(30):
        date = datetime.utcnow() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        daily_views[date_str] = 0  # Placeholder
    
    return success_response({
        "likes_count": likes_count,
        "favorites_count": favorites_count,
        "reviews_count": reviews_count,
        "explorations_count": explorations_count,
        "average_rating": round(float(avg_rating), 2) if avg_rating else 0,
        "daily_views": daily_views
    })

@analytics_bp.route("/analytics/trending", methods=["GET"])
@optional_auth
def get_trending():
    """
    Portais em tendência
    """
    limit = request.args.get("limit", 20, type=int)
    days = request.args.get("days", 7, type=int)
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Portais com mais curtidas nos últimos dias
    trending_portals = Portal.query.filter(
        Portal.is_public == True,
        Portal.is_active == True,
        Portal.created_at >= start_date
    ).join(Portal.liked_by).group_by(Portal.id).order_by(
        desc(func.count(User.id))
    ).limit(limit).all()
    
    return success_response({
        "trending_portals": [portal.to_dict() for portal in trending_portals]
    })

@analytics_bp.route("/analytics/track", methods=["POST"])
@optional_auth
def track_event():
    """
    Rastrear evento personalizado
    """
    data = request.get_json()
    if not data:
        return error_response(
            "Dados JSON inválidos",
            "VALIDATION_ERROR",
            status_code=400
        )
    
    event_type = data.get("event_type")
    if not event_type:
        return error_response(
            "Campo 'event_type' é obrigatório",
            "VALIDATION_ERROR",
            status_code=400
        )
    
    # Por enquanto, apenas logamos o evento
    # Em uma implementação real, isso seria salvo em uma tabela de analytics
    print(f"Event tracked: {event_type} by user {g.current_user_id if hasattr(g, 'current_user_id') else 'anonymous'}")
    
    return success_response({"message": "Evento rastreado com sucesso"})

