#!/usr/bin/env python3
"""
Script para inicializar o banco de dados com dados de exemplo
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.models.user import db, User
from src.models.portal import Portal
from src.models.category import Category
from src.models.tag import Tag
from src.models.review import Review
from src.models.exploration import Exploration

def init_database():
    """Inicializa o banco de dados com dados de exemplo"""
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")
        
        # Verificar se já existem dados
        if User.query.first():
            print("⚠️ Banco de dados já contém dados. Pulando inserção de dados de exemplo.")
            return
        
        # Criar categorias de exemplo
        categories = [
            Category(name="Arte Clássica", slug="arte-classica", description="Obras do período clássico", icon="palette", color="#8B5CF6"),
            Category(name="Arte Moderna", slug="arte-moderna", description="Arte dos séculos XIX e XX", icon="brush", color="#F59E0B"),
            Category(name="Arte Contemporânea", slug="arte-contemporanea", description="Arte atual e experimental", icon="sparkles", color="#EF4444"),
            Category(name="Fotografia", slug="fotografia", description="Arte fotográfica", icon="camera", color="#10B981"),
            Category(name="Escultura", slug="escultura", description="Arte tridimensional", icon="cube", color="#6366F1"),
        ]
        
        for category in categories:
            db.session.add(category)
        
        # Criar tags de exemplo
        tags = [
            Tag(name="Renascimento", slug="renascimento"),
            Tag(name="Impressionismo", slug="impressionismo"),
            Tag(name="Surrealismo", slug="surrealismo"),
            Tag(name="Abstrato", slug="abstrato"),
            Tag(name="Retrato", slug="retrato"),
            Tag(name="Paisagem", slug="paisagem"),
            Tag(name="Natureza Morta", slug="natureza-morta"),
            Tag(name="Arte Digital", slug="arte-digital"),
        ]
        
        for tag in tags:
            db.session.add(tag)
        
        # Criar usuários de exemplo
        users = [
            User(
                id="user_demo_1",
                name="Leonardo da Vinci",
                email="leonardo@portales.com",
                bio="Artista renascentista, inventor e cientista",
                location="Florença, Itália",
                is_verified=True
            ),
            User(
                id="user_demo_2", 
                name="Frida Kahlo",
                email="frida@portales.com",
                bio="Pintora mexicana conhecida por seus autorretratos",
                location="Cidade do México, México",
                is_verified=True
            ),
            User(
                id="user_demo_3",
                name="Vincent van Gogh",
                email="vincent@portales.com", 
                bio="Pintor pós-impressionista holandês",
                location="Arles, França"
            )
        ]
        
        for user in users:
            db.session.add(user)
        
        # Commit para obter os IDs
        db.session.commit()
        
        # Criar portais de exemplo
        portals = [
            Portal(
                title="Mona Lisa",
                description="O retrato mais famoso do mundo, pintado por Leonardo da Vinci",
                image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/687px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
                creator_id="user_demo_1",
                category_id=categories[0].id,
                location="Museu do Louvre, Paris",
                latitude=48.8606,
                longitude=2.3376,
                is_featured=True
            ),
            Portal(
                title="A Última Ceia",
                description="Afresco que retrata a última refeição de Jesus com seus discípulos",
                image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/%C3%9Altima_Cena_-_Da_Vinci_5.jpg/1280px-%C3%9Altima_Cena_-_Da_Vinci_5.jpg",
                creator_id="user_demo_1",
                category_id=categories[0].id,
                location="Santa Maria delle Grazie, Milão",
                latitude=45.4661,
                longitude=9.1706
            ),
            Portal(
                title="Autorretrato com Colar de Espinhos",
                description="Um dos autorretratos mais conhecidos de Frida Kahlo",
                image_url="https://upload.wikimedia.org/wikipedia/en/thumb/6/6a/Frida_Kahlo_%28self_portrait%29.jpg/473px-Frida_Kahlo_%28self_portrait%29.jpg",
                creator_id="user_demo_2",
                category_id=categories[1].id,
                location="Museu Frida Kahlo, Cidade do México",
                latitude=19.3547,
                longitude=-99.1622,
                is_featured=True
            )
        ]
        
        for portal in portals:
            db.session.add(portal)
        
        # Commit para obter os IDs dos portais
        db.session.commit()
        
        # Associar tags aos portais
        portals[0].tags.extend([tags[0], tags[4]])  # Mona Lisa: Renascimento, Retrato
        portals[1].tags.extend([tags[0]])  # A Última Ceia: Renascimento
        portals[2].tags.extend([tags[4]])  # Autorretrato: Retrato
        
        # Criar algumas avaliações de exemplo
        reviews = [
            Review(
                portal_id=portals[0].id,
                user_id="user_demo_2",
                rating=5,
                title="Obra-prima absoluta",
                comment="Uma das pinturas mais enigmáticas e belas da história da arte."
            ),
            Review(
                portal_id=portals[0].id,
                user_id="user_demo_3",
                rating=5,
                title="Inspiradora",
                comment="O sorriso da Mona Lisa é verdadeiramente cativante."
            ),
            Review(
                portal_id=portals[2].id,
                user_id="user_demo_1",
                rating=5,
                title="Expressão poderosa",
                comment="Frida consegue transmitir tanta emoção em seus autorretratos."
            )
        ]
        
        for review in reviews:
            db.session.add(review)
        
        # Criar algumas explorações de exemplo
        explorations = [
            Exploration(
                user_id="user_demo_2",
                portal_id=portals[0].id,
                scan_image_url="https://example.com/scan1.jpg",
                detection_confidence=0.95,
                ar_activated=True,
                latitude=48.8606,
                longitude=2.3376
            ),
            Exploration(
                user_id="user_demo_3",
                portal_id=portals[2].id,
                scan_image_url="https://example.com/scan2.jpg",
                detection_confidence=0.88,
                ar_activated=True,
                latitude=19.3547,
                longitude=-99.1622
            )
        ]
        
        for exploration in explorations:
            db.session.add(exploration)
        
        # Commit final
        db.session.commit()
        
        print("✅ Dados de exemplo inseridos com sucesso!")
        print(f"📊 Criados: {len(categories)} categorias, {len(tags)} tags, {len(users)} usuários, {len(portals)} portais")
        print(f"📝 Criadas: {len(reviews)} avaliações, {len(explorations)} explorações")

if __name__ == "__main__":
    init_database()

