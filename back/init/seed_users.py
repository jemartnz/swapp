"""
    SEED DATA FOR THE DATABASE
"""
from back.models import db, User, Skill
from back.app import app

USERS = [
    {
        "first_name": "Kevin",
        "last_name": "Erazo",
        "status": "busy",
        "description": "Apasionado por la tecnología y el café. Siempre \
            buscando nuevos retos.",
        "email": "kevin@demo.com",
        "plain_password": "kevin123",
        "profile_picture": "/Hombre1.png",
        "skills": [
            "Desarrollo web",
            "Ciberseguridad básica",
            "Instalación de software"
        ]
    },
    {
        "first_name": "Maddy",
        "last_name": "García",
        "status": "away",
        "description": "Programadora, gamer y fan de los gatos.",
        "email": "maddy@demo.com",
        "plain_password": "maddy123",
        "profile_picture": "/Mujer1.png",
        "skills": [
            "Diseño gráfico",
            "Fotografía de viajes",
            "Publicidad digital"
        ]
    },
    {
        "first_name": "Juan",
        "last_name": "Martínez",
        "status": "online",
        "description": "Emprendedor, curioso y con ganas de aprender algo \
            nuevo cada día.",
        "email": "juan@demo.com",
        "plain_password": "juan123",
        "profile_picture": "/Hombre2.png",
        "skills": ["Branding", "Podcasting", "Mindfulness"]
    },
    {
        "first_name": "Nadia",
        "last_name": "Koukouss",
        "profile_picture": "/Mujer2.png",
        "status": "online",
        "description": "Creativa, soñadora y amante del arte en todas sus \
            formas",
        "email": "nadia@demo.com",
        "plain_password": "nadia123",
        "skills": [
            "Apoyo escolar",
            "Aprendizaje de idiomas",
            "Educación animal"
        ]
    },
    {
        "first_name": "Daniel",
        "last_name": "Andueza",
        "status": "busy",
        "description": "Jugador de ajedrez y amante de los libros de misterio",
        "email": "daniel@demo.com",
        "plain_password": "daniel123",
        "profile_picture": "/Hombre3.png",
        "skills": [
            "Ciberseguridad básica",
            "Hablar en público",
            "Asistencia virtual"
        ]
    },
    {
        "first_name": "Lucía",
        "last_name": "Torres",
        "status": "online",
        "description": "Me encanta bailar, reír y disfrutar de las \
            pequeñas cosas.",
        "email": "lucia@demo.com",
        "plain_password": "lucia123",
        "profile_picture": "/Mujer3.png",
        "skills": [
            "Decoración del hogar",
            "Jardinería",
            "Tareas domésticas"
        ]
    },
    {
        "first_name": "Carlos",
        "last_name": "Mendoza",
        "status": "online",
        "description": "Me gusta viajar, hacer senderismo y descubrir \
            lugares con buena comida.",
        "email": "carlos@demo.com",
        "plain_password": "carlos123",
        "profile_picture": "/Hombre4.png",
        "skills": [
            "Acompañamiento fitness",
            "Voluntariado",
            "Nutrición saludable"
        ]
    },
    {
        "first_name": "Sofía",
        "last_name": "Ramírez",
        "status": "busy",
        "email": "sofia@demo.com",
        "description": "Periodista viajera. Siempre con la cámara lista y \
            la mente abierta.",
        "plain_password": "sofia123",
        "profile_picture": "/Mujer4.png",
        "skills": [
            "Higiene y bienestar animal",
            "DJ y eventos",
            "Apoyo escolar"
        ]
    },
    {
        "first_name": "Andrés",
        "last_name": "Gutiérrez",
        "status": "busy",
        "description": "Fotógrafo urbano en busca de los mejores atardeceres.",
        "email": "andres@demo.com",
        "plain_password": "andres123",
        "profile_picture": "/Hombre5.png",
        "skills": [
            "Soporte técnico",
            "Programación en Python, Java o C++",
            "Animación infantil"
        ]
    },
    {
        "first_name": "Valeria",
        "last_name": "Martínez",
        "status": "away",
        "description": "Arquitecta enamorada del diseño minimalista y \
            las plantas.",
        "email": "valeria@demo.com",
        "plain_password": "valeria123",
        "profile_picture": "/Mujer5.png",
        "skills": [
            "Asesoría contable",
            "Marketing digital",
            "Maquillaje y peinados"
        ]
    }
]


def seed_users():
    """SEED USERS"""
    with app.app_context():
        for u in USERS:
            email = u["email"]
            user = User.query.filter_by(email=email).first()

            if not user:
                user = User(
                    first_name=u["first_name"],
                    last_name=u["last_name"],
                    email=email,
                    accepts_terms=True,
                    profile_picture=u["profile_picture"],
                    status=u["status"],
                    description=u["description"]
                )
                user.password = u["plain_password"]
                db.session.add(user)
                db.session.flush()

            # Clear and assign skills
            user.skills.clear()
            for skill_name in u["skills"]:
                skill = Skill.query.filter_by(
                    name=skill_name).first()
                if not skill:
                    skill = Skill(
                        name=skill_name, description="")
                    db.session.add(skill)
                    db.session.flush()
                user.skills.append(skill)

            db.session.commit()

        print(
            f"[SEED] Created or updated {len(USERS)} "
            "users with skills and profile pictures."
            )


if __name__ == "__main__":
    seed_users()
