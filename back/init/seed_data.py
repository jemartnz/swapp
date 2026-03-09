"""Seed Categories and Skills"""
from back.models import db, Category, Skill
from back.app import app

CATEGORIES_AND_SKILLS = {
    "Educación y Tutorías": [
        "Clases particulares",
        "Tutorías académicas",
        "Apoyo escolar",
        "Asesoría universitaria",
        "Aprendizaje de idiomas",
        "Educación ambiental"
    ],
    "Tecnología y Programación": [
        "Desarrollo web",
        "Programación en Python, Java o C++",
        "Soporte técnico",
        "Automatización con scripts",
        "Ciberseguridad básica",
        "Instalación de software"
    ],
    "Música y Audio": [
        "Producción musical",
        "Clases de guitarra o piano",
        "Grabación y mezcla de audio",
        "Composición musical",
        "DJ y eventos",
        "Podcasting"
    ],
    "Negocios y Finanzas": [
        "Emprendimiento",
        "Gestión financiera básica",
        "Marketing digital",
        "Planificación de proyectos",
        "Inversiones personales",
        "Asesoría contable"
    ],
    "Entretenimiento y Cultura": [
        "Actuación / teatro",
        "Organización de eventos",
        "Juegos de mesa / rol",
        "Cine / análisis de películas",
        "Espectáculos en vivo",
        "Animación infantil"
    ],
    "Dibujo y Pintura": [
        "Ilustración digital",
        "Retratos y caricaturas",
        "Pintura acrílica o acuarela",
        "Diseño de murales",
        "Creación de cómics",
        "Manualidades artísticas"
    ],
    "Deporte y Bienestar": [
        "Entrenamiento personal",
        "Yoga y meditación",
        "Boxeo o defensa personal",
        "Acompañamiento fitness",
        "Nutrición saludable",
        "Mindfulness"
    ],
    "Moda, Belleza y Cuidado Personal": [
        "Asesoría de imagen",
        "Moda sostenible",
        "Maquillaje y peinados",
        "Diseño y costura",
        "Cuidado de la piel",
        "Productos ecológicos DIY"
    ],
    "Hogar y Reparaciones": [
        "Electricidad básica",
        "Fontanería y mantenimiento",
        "Decoración del hogar",
        "Reciclaje y compostaje",
        "Reparación de muebles",
        "Jardinería"
    ],
    "Mascotas y Animales": [
        "Adiestramiento básico",
        "Cuidado de mascotas",
        "Paseo de perros",
        "Rescate y adopción",
        "Educación animal",
        "Higiene y bienestar animal"
    ],
    "Viajes y Estilo de Vida": [
        "Planificación de viajes",
        "Intercambio cultural",
        "Cocina internacional",
        "Fotografía de viajes",
        "Consejos para nómadas digitales",
        "Blog de experiencias"
    ],
    "Comunicación y Marketing": [
        "Creación de contenido",
        "Copywriting",
        "Branding",
        "Estrategia de redes sociales",
        "Publicidad digital",
        "Podcasting"
    ],
    "Desarrollo Personal y Coaching": [
        "Coaching de vida",
        "Productividad y gestión del tiempo",
        "Hablar en público",
        "Motivación personal",
        "Asesoría vocacional",
        "Mindfulness"
    ],
    "Otros / Misceláneos": [
        "Voluntariado",
        "Asesoría legal básica",
        "Apoyo psicológico (no profesional)",
        "Servicios comunitarios",
        "Asistencia virtual",
        "Tareas domésticas"
    ]
}


def seed_data():
    """Seed categories and skills into the database"""
    with app.app_context():
        s = 0
        for category_name, skill_names in CATEGORIES_AND_SKILLS.items():

            category = Category.query.filter_by(
                name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
                db.session.commit()

            for skill_name in skill_names:
                skill = Skill.query.filter_by(
                    name=skill_name).first()
                if not skill:
                    new_skill = Skill(
                        name=skill_name,
                        description="",
                        category_id=category.id
                    )
                    db.session.add(new_skill)
            s += len(skill_names)
        print(f"[SEED] Categories: {len(CATEGORIES_AND_SKILLS)}")
        print(f"[SEED] Skills: {s}")
        db.session.commit()


if __name__ == "__main__":
    seed_data()
