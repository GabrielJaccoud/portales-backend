from flask import Blueprint, request, g
from src.models.user import db, User
from src.models.portal import Portal
from src.models.exploration import Exploration
from src.utils.auth import auth_required
from src.utils.helpers import success_response, error_response, validate_required_fields, paginate_query

explorations_bp = Blueprint("explorations", __name__)

@explorations_bp.route("/explorations", methods=["GET"])
@auth_required
def get_explorations():
    """
    Lista explorações do usuário autenticado
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = Exploration.query.filter_by(user_id=g.current_user_id).order_by(Exploration.created_at.desc())
    result = paginate_query(query, page, per_page)

    return success_response({
        "explorations": [exp.to_dict() for exp in result["items"]],
        "pagination": result["pagination"],
    })

@explorations_bp.route("/explorations", methods=["POST"])
@auth_required
def create_exploration():
    """
    Cria uma nova exploração
    """
    data = request.get_json()
    if not data:
        return error_response("Dados JSON inválidos", "VALIDATION_ERROR", status_code=400)

    required_fields = ["scan_image_url"]
    missing_fields = validate_required_fields(data, required_fields)
    if missing_fields:
        return error_response(
            f"Campos obrigatórios ausentes: {', '.join(missing_fields)}",
            "VALIDATION_ERROR",
            {"missing_fields": missing_fields},
            status_code=400,
        )

    # Opcional: verificar se o portal_id existe
    portal = None
    if "portal_id" in data and data["portal_id"] is not None:
        portal = Portal.query.get(data["portal_id"])
        if not portal:
            return error_response(
                "Portal associado não encontrado", "RESOURCE_NOT_FOUND", status_code=404
            )

    exploration = Exploration(
        user_id=g.current_user_id,
        portal_id=data.get("portal_id"),
        scan_image_url=data["scan_image_url"],
        detection_confidence=data.get("detection_confidence"),
        ar_activated=data.get("ar_activated", False),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
    )

    try:
        db.session.add(exploration)
        db.session.commit()
        return success_response({"exploration": exploration.to_dict()}, status_code=201)
    except Exception as e:
        db.session.rollback()
        return error_response(
            "Erro ao criar exploração", "INTERNAL_ERROR", status_code=500
        )

@explorations_bp.route("/explorations/<int:exploration_id>", methods=["GET"])
@auth_required
def get_exploration(exploration_id):
    """
    Obtém detalhes de uma exploração específica do usuário autenticado
    """
    exploration = Exploration.query.get(exploration_id)
    if not exploration:
        return error_response(
            "Exploração não encontrada", "RESOURCE_NOT_FOUND", status_code=404
        )

    if exploration.user_id != g.current_user_id:
        return error_response(
            "Você não tem permissão para acessar esta exploração",
            "AUTHORIZATION_ERROR",
            status_code=403,
        )

    return success_response({"exploration": exploration.to_dict()})

@explorations_bp.route("/explorations/<int:exploration_id>", methods=["DELETE"])
@auth_required
def delete_exploration(exploration_id):
    """
    Deleta uma exploração
    """
    exploration = Exploration.query.get(exploration_id)
    if not exploration:
        return error_response(
            "Exploração não encontrada", "RESOURCE_NOT_FOUND", status_code=404
        )

    if exploration.user_id != g.current_user_id:
        return error_response(
            "Você não tem permissão para deletar esta exploração",
            "AUTHORIZATION_ERROR",
            status_code=403,
        )

    try:
        db.session.delete(exploration)
        db.session.commit()
        return success_response(status_code=204)
    except Exception as e:
        db.session.rollback()
        return error_response(
            "Erro ao deletar exploração", "INTERNAL_ERROR", status_code=500
        )


