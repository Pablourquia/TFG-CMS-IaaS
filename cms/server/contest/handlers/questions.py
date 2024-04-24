
import logging

try:
    import tornado4.web as tornado_web
except ImportError:
    import tornado.web as tornado_web

from cms.server import multi_contest
from cmscommon.mimetypes import get_type_for_file_name
from .contest import ContestHandler, FileHandler
from ..phase_management import actual_phase_required
from cms.db import QuestionNew, Answer, Contest, SubmissionsAnswers


logger = logging.getLogger(__name__)

class QuestionDescriptionHandler(ContestHandler):

    @tornado_web.authenticated
    @actual_phase_required(0, 3)
    @multi_contest
    def get(self, question_name):
        question = (self.sql_session.query(QuestionNew)
                    .filter(QuestionNew.name == question_name)
                    .first())

        self.r_params["question"] = question
        contest = self.sql_session.query(Contest).filter(Contest.id == question.contest_id).first()
        ids = contest.questions_ids
        size = max(ids)
        boolean_vector = [False]*(size+1)
        for i in ids:
            submission = (self.sql_session.query(SubmissionsAnswers).filter(SubmissionsAnswers.question_id == i, SubmissionsAnswers.user_id == self.current_user.id).first())
            if submission:
                if submission.correct:
                    boolean_vector[i] = True
        self.r_params["boolean_vector"] = boolean_vector

        self.render("new_question.html", **self.r_params)

    def post(self, question_name):
        question = (self.sql_session.query(QuestionNew)
                    .filter(QuestionNew.name == question_name)
                    .first())

        if not question:
            raise tornado_web.HTTPError(404)
        contest = self.sql_session.query(Contest).filter(Contest.id == question.contest_id).first()

        correct_answer  = self.sql_session.query(Answer).filter(Answer.name_question == question_name).first()
        submission = (self.sql_session.query(SubmissionsAnswers).filter(SubmissionsAnswers.question_id == question.id, SubmissionsAnswers.user_id == self.current_user.id).first())
        if question.type == "options":
            selected_option = self.get_argument('options')
            if selected_option == correct_answer.answer[0]:
                if submission:
                    submission.correct = True
                else:
                    new_submission = SubmissionsAnswers(answer = [selected_option])
                    new_submission.name_user = self.current_user.user.username
                    new_submission.name_question = question_name
                    new_submission.question_id = question.id
                    new_submission.user_id = self.current_user.id
                    new_submission.correct = True
                    self.sql_session.add(new_submission)
            else:
                if submission:
                    submission.correct = False
                else:
                    new_submission = SubmissionsAnswers(answer = [selected_option])
                    new_submission.name_user = self.current_user.user.username
                    new_submission.name_question = question_name
                    new_submission.question_id = question.id
                    new_submission.user_id = self.current_user.id
                    new_submission.correct = False
                    self.sql_session.add(new_submission)
                

        if question.type == "development":
            correct_answers = []
            answers = []
            for i in range(question.number_of_inputs):
                answer = self.get_argument('question' + str(i))
                answers.append(answer)
                if answer == correct_answer.answer[i]:
                    correct_answers.append(True)
                else:
                    correct_answers.append(False)
            if correct_answers == [True]*question.number_of_inputs:
                if submission:
                    submission.correct = True
                else:
                    new_submission = SubmissionsAnswers(answer = answers)
                    new_submission.name_user = self.current_user.user.username
                    new_submission.name_question = question_name
                    new_submission.question_id = question.id
                    new_submission.user_id = self.current_user.id
                    new_submission.correct = True
                    self.sql_session.add(new_submission)
            else: 
                if submission:
                    submission.correct = False
                else:
                    new_submission = SubmissionsAnswers(answer = answers)
                    new_submission.name_user = self.current_user.user.username
                    new_submission.name_question = question_name
                    new_submission.question_id = question.id
                    new_submission.user_id = self.current_user.id
                    new_submission.correct = False
                    self.sql_session.add(new_submission)
        
        self.sql_session.commit()
        all_questions = []
        for i in contest.questions_ids:
            submission = self.sql_session.query(SubmissionsAnswers).filter(SubmissionsAnswers.question_id == i, SubmissionsAnswers.user_id == self.current_user.id).first()
            if submission:
                if submission.correct:
                    all_questions.append(True)
                else:
                    all_questions.append(False)
            else:
                all_questions.append(False)
        if all(all_questions):
             self.notify_success(("Cuestionario completado correctamente"),
                            (f"Ahora puedes pasar al siguiente"))
        self.redirect("/")
       

class QuestionStatementHandler(FileHandler):
    
    @tornado_web.authenticated
    @actual_phase_required(0, 3)
    @multi_contest
    def get(self, question_name):
        question = (self.sql_session.query(QuestionNew)
                    .filter(QuestionNew.name == question_name)
                    .first())
        if question is None:
            raise tornado_web.HTTPError(404)

        statement = question.digest
        self.sql_session.close()

        filename = question.question
        content_type = get_type_for_file_name(filename)

        if content_type is None:
            raise tornado_web.HTTPError(404, "Unknown file type")

        self.fetch(statement, content_type, filename)