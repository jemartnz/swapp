"""
    Models of Swapp
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, Enum
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """
        Model: Users
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    _password = db.Column("password", db.String(255), nullable=True)
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(20))
    profile_picture = db.Column(db.String(255))
    description = db.Column(db.Text)
    status = db.Column(
        Enum("away", "online", "busy", name="user_status"),
        default="away",
        nullable=False)
    accepts_terms = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def password(self):
        """Password is not a readable attribute"""
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        """Set a hashed password"""
        self._password = generate_password_hash(password)

    def verify_password(self, password):
        """Verify the password"""
        return check_password_hash(self._password, password)

    @property
    def rating_average(self):
        """Average of received ratings in exchanges."""
        ratings = Rating.query.filter_by(rated_id=self.id).all()
        if not ratings:
            return 0
        return sum(r.score for r in ratings) / len(ratings)

    skills = db.relationship(
        "Skill",
        secondary="user_skills",
        back_populates="users")
    sent_messages = db.relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender", cascade="all, delete-orphan")
    received_messages = db.relationship(
        "Message", foreign_keys="Message.receiver_id",
        back_populates="receiver", cascade="all, delete-orphan")

    given_ratings = db.relationship(
        "Rating",
        foreign_keys="Rating.rater_id",
        back_populates="rater",
        cascade="all, delete-orphan"
    )
    received_ratings = db.relationship(
        "Rating",
        foreign_keys="Rating.rated_id",
        back_populates="rated",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"

    def to_dict(self):
        """
            Serialize the attributes of User
        """
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "birth_date": (
                self.birth_date.isoformat()
                if self.birth_date else None
                ),
            "profile_picture": self.profile_picture,
            "gender": self.gender,
            "description": self.description,
            "status": self.status,
            "rating_average": self.rating_average,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class Category(db.Model):
    """
        Model: Categories
    """
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    skills = db.relationship("Skill", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"

    def to_dict(self):
        """
            Serialize the attributes of Category
        """
        return {
            "id": self.id,
            "name": self.name
            }


class Skill(db.Model):
    """
        Model: Skills
    """
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey(
        "categories.id", onupdate="CASCADE", ondelete="SET NULL"))

    category = db.relationship("Category", back_populates="skills")
    users = db.relationship(
        "User",
        secondary="user_skills", back_populates="skills")

    def __repr__(self):
        return f"<Skill {self.name}>"

    def to_dict(self):
        """
            Serialize the attributes of Skill
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }


class UserSkill(db.Model):
    """
        Model: UserSkills (N:M)
    """
    __tablename__ = "user_skills"

    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.id", onupdate="CASCADE",
        ondelete="CASCADE"), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey(
        "skills.id", onupdate="CASCADE",
        ondelete="CASCADE"), primary_key=True)

    def __repr__(self):
        return f"<UserSkill user={self.user_id}, skill={self.skill_id}>"


class Message(db.Model):
    """
        Model: Messages
    """
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey(
        "users.id", onupdate="CASCADE",
        ondelete="CASCADE"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey(
        "users.id", onupdate="CASCADE",
        ondelete="CASCADE"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))
    seen = db.Column(db.Boolean, default=False)

    sender = db.relationship(
        "User", foreign_keys=[sender_id],
        back_populates="sent_messages")
    receiver = db.relationship(
        "User", foreign_keys=[receiver_id],
        back_populates="received_messages")

    def __repr__(self):
        return f"<Message from {self.sender_id} to {self.receiver_id}>"

    def to_dict(self, exclude=None):
        """
            Serialize the attributes of Message
        """
        serial = {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "sent_at": self.sent_at.strftime("%Y-%m-%d %H:%M:%S"),
            "seen": self.seen
        }
        if exclude:
            for key in exclude:
                serial.pop(key, None)
        return serial


class Rating(db.Model):
    """
        Model: Ratings
    """
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    exchange_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "exchanges.id", onupdate="CASCADE",
            ondelete="CASCADE"),
        nullable=False
    )
    rater_id = db.Column(db.Integer, db.ForeignKey(
        "users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False)
    rated_id = db.Column(db.Integer, db.ForeignKey(
        "users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False)

    score = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))

    exchange = db.relationship(
        "Exchange", back_populates="ratings")
    rater = db.relationship(
        "User", foreign_keys=[rater_id],
        back_populates="given_ratings")
    rated = db.relationship(
        "User", foreign_keys=[rated_id],
        back_populates="received_ratings")

    __table_args__ = (
        UniqueConstraint(
            "exchange_id",
            "rater_id",
            name="uq_exchange_rater"),
    )

    def __repr__(self):
        return f"<Rating {self.score} in exchange {self.exchange_id}>"

    def to_dict(self):
        """
            Serialize the attributes of Rating
        """
        return {
            "id": self.id,
            "exchange_id": self.exchange_id,
            "rater_id": self.rater_id,
            "rated_id": self.rated_id,
            "score": self.score,
            "comment": self.comment,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class Exchange(db.Model):
    """
        Model: Exchanges
        Represents skill exchanges between users
    """
    __tablename__ = "exchanges"

    id = db.Column(db.Integer, primary_key=True)
    offerer_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id", onupdate="CASCADE",
            ondelete="CASCADE"),
        nullable=False
    )
    demander_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id", onupdate="CASCADE",
            ondelete="CASCADE"),
        nullable=True
    )
    skill_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "skills.id", onupdate="CASCADE",
            ondelete="SET NULL"),
        nullable=True
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    offerer = db.relationship(
        "User",
        foreign_keys=[offerer_id],
        backref=db.backref(
            "offered_exchanges",
            cascade="all,delete-orphan")
    )
    demander = db.relationship(
        "User",
        foreign_keys=[demander_id],
        backref=db.backref(
            "received_exchanges",
            cascade="all,delete-orphan")
    )
    skill = db.relationship("Skill")
    ratings = db.relationship(
        "Rating",
        back_populates="exchange",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Exchange {self.id} between \
            {self.offerer_id} and {self.demander_id}>"

    def to_dict(self):
        """
            Serialize the attributes of Exchange
        """
        return {
            "id": self.id,
            "offerer_id": self.offerer_id,
            "demander_id": self.demander_id,
            "created_at": (
                self.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.created_at else None
            ),
            "is_completed": self.is_completed,
            "completed_at": (
                self.completed_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.completed_at else None
            ),
            "skill": (
                self.skill.to_dict()
                if self.skill else None
            ),
            "ratings": [r.to_dict() for r in self.ratings]
        }
