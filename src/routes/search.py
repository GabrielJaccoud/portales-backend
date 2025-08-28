from flask import Blueprint, request
from src.models.user import db, User
from src.models.portal import Portal
from src.models.category import Category
from src.models.tag import Tag
from src.utils.helpers import success_response, error_response, paginate_query
from sqlalchemy import or_

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["GET"])
def search():
    """
    Busca global por portais, usuários e categorias
    """
    query = request.args.get("q", "").strip()
    search_type = request.args.get("type", "all")  # all, portals, users, categories
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    if not query:
        return error_response(
            "Parâmetro de busca 'q' é obrigatório",
            "VALIDATION_ERROR",
            status_code=400
        )
    
    results = {}
    
    if search_type in ["all", "portals"]:
        # Buscar portais
        portal_query = Portal.query.filter(
            Portal.is_public == True,
            Portal.is_active == True,
            or_(
                Portal.title.contains(query),
                Portal.description.contains(query)
            )
        ).order_by(Portal.created_at.desc())
        
        if search_type == "portals":
            portal_result = paginate_query(portal_query, page, per_page)
            results["portals"] = [portal.to_dict() for portal in portal_result["items"]]
            results["pagination"] = portal_result["pagination"]
        else:
            results["portals"] = [portal.to_dict() for portal in portal_query.limit(5).all()]
    
    if search_type in ["all", "users"]:
        # Buscar usuários
        user_query = User.query.filter(
            or_(
                User.name.contains(query),
                User.bio.contains(query)
            )
        ).order_by(User.created_at.desc())
        
        if search_type == "users":
            user_result = paginate_query(user_query, page, per_page)
            results["users"] = [user.to_dict() for user in user_result["items"]]
            results["pagination"] = user_result["pagination"]
        else:
            results["users"] = [user.to_dict() for user in user_query.limit(5).all()]
    
    if search_type in ["all", "categories"]:
        # Buscar categorias
        category_query = Category.query.filter(
            or_(
                Category.name.contains(query),
                Category.description.contains(query)
            )
        ).order_by(Category.name)
        
        if search_type == "categories":
            category_result = paginate_query(category_query, page, per_page)
            results["categories"] = [cat.to_dict() for cat in category_result["items"]]
            results["pagination"] = category_result["pagination"]
        else:
            results["categories"] = [cat.to_dict() for cat in category_query.limit(5).all()]
    
    return success_response(results)

@search_bp.route("/search/suggestions", methods=["GET"])
def search_suggestions():
    """
    Sugestões de busca baseadas em termos populares
    """
    query = request.args.get("q", "").strip()
    limit = request.args.get("limit", 10, type=int)
    
    suggestions = []
    
    if query:
        # Buscar portais que começam com o termo
        portal_suggestions = Portal.query.filter(
            Portal.is_public == True,
            Portal.is_active == True,
            Portal.title.like(f"{query}%")
        ).limit(limit).all()
        
        suggestions.extend([portal.title for portal in portal_suggestions])
        
        # Buscar tags que começam com o termo
        tag_suggestions = Tag.query.filter(
            Tag.name.like(f"{query}%")
        ).limit(limit - len(suggestions)).all()
        
        suggestions.extend([tag.name for tag in tag_suggestions])
    
    return success_response({"suggestions": suggestions[:limit]})

@search_bp.route("/tags", methods=["GET"])
def get_tags():
    """
    Lista tags populares
    """
    trending = request.args.get("trending", type=bool)
    limit = request.args.get("limit", 50, type=int)
    
    query = Tag.query
    
    if trending:
        # Para tags em tendência, ordenar por número de portais associados
        query = query.join(Tag.portals).group_by(Tag.id).order_by(db.func.count(Portal.id).desc())
    else:
        query = query.order_by(Tag.name)
    
    tags = query.limit(limit).all()
    
    return success_response({
        "tags": [tag.to_dict() for tag in tags]
    })

