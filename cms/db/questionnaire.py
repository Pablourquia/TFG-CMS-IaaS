from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, Integer, Unicode, String
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from . import Filename, Digest
from . import Codename, Base


class Questionnaire(Base):

    __tablename__ = 'questionnaires'

    # Auto increment primary key.
    id = Column(
        Integer,
        primary_key=True)

    # Name of the questionnaire.
    name = Column(
        String,
        unique=True)

    # Relation with the questions
    questions = relationship(
        'QuestionNew',
        back_populates='questionnaire')

class QuestionNew(Base):
    
    __tablename__ = 'questions_new'

    # Auto increment primary key.
    id = Column(
        Integer,
        primary_key=True)

    # Question name
    name = Column(
        String,
        unique=True)

    # Questionnaire relation.
    questionnaire_id = Column(
        Integer,
        ForeignKey('questionnaires.id'))

    questionnaire = relationship(
        'Questionnaire',
        back_populates='questions')

    digest = Column(
        Digest,
        nullable=False)

    # Type of question.
    type = Column(
        String)

    # Question description.
    question = Column(
        Filename)

    # Options
    options = Column(
        ARRAY(String),
        nullable=True)
    
    # Number of inputs
    number_of_inputs = Column(
        Integer)

    contest_id = Column(
        Integer,
        nullable=True)

    num = Column(
        Integer,
        nullable=True)


class Answer(Base):
    
    __tablename__ = 'answers'

    # Auto increment primary key.
    id = Column(
        Integer,
        primary_key=True)

    name_question = Column(
        String)
    
    answer = Column(
        ARRAY(String),
        nullable=False)

    name_user = Column(
        String)

class SubmissionsAnswers(Base):
    
    __tablename__ = 'submissions_answers'

    # Auto increment primary key.
    id = Column(
        Integer,
        primary_key=True)
    
    name_user = Column(
        String)

    name_question = Column(
        String)

    question_id = Column(
        Integer)
    
    user_id = Column(
        Integer)

    answer = Column(
        ARRAY(String),
        nullable=False)

    correct = Column(
        Boolean)

    