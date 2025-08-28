from flask import Blueprint, request, g
from src.models.user import db, User
from src.models.portal import Portal
from src.models.review import Review
from src.utils.auth import auth_required
from src.utils.helpers import success_response, error_response, validate_required_fields, paginate_query

reviews_bp = Blueprint("reviews", __name__)

@reviews_bp.route("/portals/<int:portal_id>/reviews", methods=["GET"])
def get_reviews_for_portal(portal_id):
    """
    Lista reviews para um portal específico
    """
    portal = Portal.query.get(portal_id)
    if not portal:
        return error_response(
            "Portal não encontrado", "RESOURCE_NOT_FOUND", status_code=404
        )

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = Review.query.filter_by(portal_id=portal_id).order_by(Review.created_at.desc())
    result = paginate_query(query, page, per_page)

    return success_response({
        "reviews": [review.to_dict() for review in result["items"]],
        "pagination": result["pagination"],
    })

@reviews_bp.route("/portals/<int:portal_id>/reviews", methods=["POST"])
@auth_required
def create_review(portal_id):
    """
    Cria uma nova review para um portal
    """
    data = request.get_json()
    if not data:
        return error_response("Dados JSON inválidos", "VALIDATION_ERROR", status_code=400)

    required_fields = ["rating"]
    missing_fields = validate_required_fields(data, required_fields)
    if missing_fields:
        return error_response(f"Campos obrigatórios ausentes: {', '.join(missing_fields)}",            "VALIDATION_ERROR",
            {"missing_fields": missing_fields},
            status_code=400,
        )

    portal = Portal.query.get(portal_id)
    if not portal:
        return error_response(
            "Portal não encontrado", "RESOURCE_NOT_FOUND", status_code=404
        )

    # Verificar se o usuário já fez uma review para este portal
    existing_review = Review.query.filter_by(portal_id=portal_id, user_id=g.current_user_id).first()
    if existing_review:
        return error_response(
            "Você já avaliou este portal", "VALIDATION_ERROR", status_code=409
        )

    if not (1 <= data["rating"] <= 5):
        return error_response(
            "A avaliação deve ser entre 1 e 5", "VALIDATION_ERROR", status_code=400
        )

    review = Review(
        portal_id=portal_id,
        user_id=g.current_user_id,
        rating=data["rating"],
        title=data.get("title"),
        comment=data.get("comment"),
    )

    try:
        db.session.add(review)
        db.session.commit()
        return success_response({"review": review.to_dict()}, status_code=201)
    except Exception as e:
        db.session.rollback()
        return error_response(
            "Erro ao criar review", "INTERNAL_ERROR", status_code=500
        )

@reviews_bp.route("/reviews/<int:review_id>", methods=["PUT"])
@auth_required
def update_review(review_id):
    """
    Atualiza uma review existente
    """
    review = Review.query.get(review_id)
    if not review:
        return error_response(
            "Review não encontrada", "RESOURCE_NOT_FOUND", status_code=404
        )

    if review.user_id != g.current_user_id:
        return error_response(
            "Você não tem permissão para editar esta review",
            "AUTHORIZATION_ERROR",
            status_code=403,
        )

    data = request.get_json()
    if not data:
        return error_response("Dados JSON inválidos", "VALIDATION_ERROR", status_code=400)

    updatable_fields = ["rating", "title", "comment"]
    for field in updatable_fields:
        if field in data:
            setattr(review, field, data[field])

    if "rating" in data and not (1 <= data["rating"] <= 5):
        return error_response(
            "A avaliação deve ser entre 1 e 5", "VALIDATION_ERROR", status_code=400
        )

    try:
        db.session.commit()
        return success_response({"review": review.to_dict()})
    except Exception as e:
        db.session.rollback()
        return error_response(
            "Erro ao atualizar review", "INTERNAL_ERROR", status_code=500
        )

@reviews_bp.route("/reviews/<int:review_id>", methods=["DELETE"])
@auth_required
def delete_review(review_id):
    """
    Deleta uma review
    """
    review = Review.query.get(review_id)
    if not review:
        return error_response(
            "Review não encontrada", "RESOURCE_NOT_FOUND", status_code=404
        )

    if review.user_id != g.current_user_id:
        return error_response(
            "Você não tem permissão para deletar esta review",
            "AUTHORIZATION_ERROR",
            status_code=403,
        )

    try:
        db.session.delete(review)
        db.session.commit()
        return success_response(status_code=204)
    except Exception as e:
        db.session.rollback()
        return error_response(
            "Erro ao deletar review", "INTERNAL_ERROR", status_code=500
        )


