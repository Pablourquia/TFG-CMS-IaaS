#!/usr/bin/env python3

from .base import BaseHandler, SimpleHandler, require_permission
from cms.db import Questionnaire, QuestionNew, Session, Answer
from .base import BaseHandler, SimpleHandler, require_permission

class AddQuestionnaire(
    SimpleHandler("add_questionnaire.html", permission_all=True)):

    @require_permission(BaseHandler.PERMISSION_ALL)
    def post(self):
        fallback_page = self.url("")

        try:
            attrs = dict()

            self.get_string(attrs, "name", empty=None)
            assert attrs.get("name") is not None, "No questionnaire name specified."
            attrs["description"] = attrs["name"]

            # Create the questionnaire
            questionnaire = Questionnaire()
            questionnaire.name = attrs["name"]
            self.sql_session.add(questionnaire)

        except Exception as error:
            self.service.add_notification(
                make_datetime(), "Invalid field(s)", repr(error))
            self.redirect(fallback_page)
            return

        if self.try_commit():
            self.service.proxy_service.reinitialize()
            self.redirect(fallback_page)
        else:
            self.redirect(fallback_page)


class AddQuestionNew(
    SimpleHandler("add_question.html", permission_all=True)):
    @require_permission(BaseHandler.PERMISSION_ALL)
    def post(self):
        fallback_page = self.url("")

        try:
            attrs = dict()

            question_name = self.get_body_argument("question_name")
            question_statement = self.request.files.get("question_statement")[0]["filename"]
            question_type = self.get_body_argument("type_question")
            number_of_inputs = int(self.get_body_argument("number_answers", default="1"))
            number_options = int(self.get_body_argument("number_options", default="1"))
            questionnaire_name = self.get_body_argument("questionnaire_name")
            questionnaire_id = self.sql_session.query(Questionnaire).filter(Questionnaire.name == questionnaire_name).first().id

            statement = self.request.files.get("question_statement")[0]
            digest = self.service.file_cacher.put_file_content(
                statement["body"],
                "Statement for question %s (lang: %s)" % (question_name, "language"))

            question = QuestionNew(
                name=question_name,
                question=question_statement,
                type=question_type,
                number_of_inputs=number_of_inputs,
                digest=digest
            )
            question.questionnaire_id = questionnaire_id

            if question_type == "options":
                options = [self.get_body_argument(f"options_option_{i+1}") for i in range(number_options)]
                question.options = options
            self.sql_session.add(question)

            number_of_answers = int(self.get_body_argument("number_answers", default="1"))
            answers = [self.get_body_argument(f"answer_{i+1}") for i in range(number_of_answers)]
            
            answer = Answer(
                answer = answers
            )
            answer.name_question = question_name
            answer.name_user = self.current_user.name
            self.sql_session.add(answer)

        except Exception as error:
            self.service.add_notification(
                make_datetime(), "Invalid field(s)", repr(error))
            self.redirect(fallback_page)
            return

        if self.try_commit():
            self.service.proxy_service.reinitialize()
            self.redirect(fallback_page)
        else:
            self.redirect(fallback_page)
    def get(self):
        questionnaires = [q.name for q in self.sql_session.query(Questionnaire).all()]
        self.r_params = self.render_params()
        self.r_params["questionnaires"] = questionnaires
        self.render("add_question.html", **self.r_params)
