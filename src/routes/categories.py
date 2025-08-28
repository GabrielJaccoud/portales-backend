from flask import Blueprint, request
from src.models.user import db
from src.models.category import Category
from src.utils.helpers import success_response, error_response, validate_required_fields, create_slug

categories_bp = Blueprint("categories", __name__)

@categories_bp.route("/categories", methods=["GET"])
def get_categories():
    """
    Lista todas as categorias
    """
    categories = Category.query.all()
    return success_response({"categories": [cat.to_dict() for cat in categories]})

@categories_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    """
    Obtém detalhes de uma categoria específica
    """
    category = Category.query.get(category_id)
    if not category:
        return error_response(
            "Categoria não encontrada", "RESOURCE_NOT_FOUND", status_code=404
        )
    return success_response({"category": category.to_dict()})

@categories_bp.route("/categories", methods=["POST"])
def create_category():
    """
    Cria uma nova categoria
    (Apenas para uso interno/admin, sem autenticação por enquanto)
    """
    data = request.get_json()
    if not data:
        return error_response("Dados JSON inválidos", "VALIDATION_ERROR", status_code=400)

    required_fields = ["name"]
    missing_fields = validate_required_fields(data, required_fields)
    if missing_fields:
        return error_response(
            f"Campos obrigatórios ausentes: {', '.join(missing_fields)}",
            "VALIDATION_ERROR",
            {"missing_fields": missing_fields},
            status_code=400,
        )

    name = data["name"]
    slug = create_slug(name)

    if Category.query.filter_by(slug=slug).first():
        return error_response(
            "Categoria com este nome já existe", "VALIDATION_ERROR", status_code=409
        )

    category = Category(
        name=name,
        slug=slug,
        description=data.get("description"),
        icon=data.get("icon"),
        color=data.get("color"),
    )

    try:
        db.session.add(category)
        db.session.commit()
        return success_response({"category": category.to_dict()}, status_code=201)
    except Exception as e:
        db.session.rollback()
        return error_response(
            "Erro ao criar categoria", "INTERNAL_ERROR", status_code=500
        )

@categories_bp.route("/categories/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    """
    Atualiza uma categoria existente
    (Apenas para uso interno/admin, sem autenticação por enquanto)
    """
    category = Category.query.get(category_id)
    if not category:
        return error_response(
            "Categoria não encontrada", "RESOURCE_NOT_FOUND", status_code=404
        )

    data = request.get_json()
    if not data:
        return error_response("Dados JSON inválidos", "VALIDATION_ERROR", status_code=400)

    updatable_fields = ["name", "description", "icon", "color"]
    for field in updatable_fields:
        if field in data:
            setattr(category, field, data[field])

    if "name" in data:
        category.slug = create_slug(data["name"])
        existing_category = Category.query.filter(Category.slug == category.slug, Category.id != category_id).first()
        if existing_category:
            return error_response(
                "Categoria com este nome já existe", "VALIDATION_ERROR", status_code=409
            )

    try:
        db.session.commit()
        return success_response({"category": category.to_dict()})
    except Exception as e:
        db.session.rollback()
        return error_response(
            "Erro ao atualizar categoria", "INTERNAL_ERROR", status_code=500
        )

@categories_bp.route("/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    """
    Deleta uma categoria
    (Apenas para uso interno/admin, sem autenticação por enquanto)
    """
    category = Category.query.get(category_id)
    if not category:
        return error_response(
            "Categoria não encontrada", "RESOURCE_NOT_FOUND", status_code=404
        )

    if category.portals.count() > 0:
        return error_response(
            "Não é possível deletar categoria com portais associados",
            "VALIDATION_ERROR",
            status_code=400,
        )

    try:
        db.session.delete(category)
        db.session.commit()
        return success_response(status_code=204)
    except Exception as e:
        db.session.rollback()
        return error_response(
            "Erro ao deletar categoria", "INTERNAL_ERROR", status_code=500
        )


