from cms.db import Contest, QuestionNew
from cmscommon.datetime import make_datetime

from .base import BaseHandler, require_permission


class ContestQuestionsHandler(BaseHandler):
    REMOVE_FROM_CONTEST = "Remove from contest"

    @require_permission(BaseHandler.AUTHENTICATED)
    def get(self, contest_id):
        self.contest = self.safe_get_item(Contest, contest_id)

        self.r_params = self.render_params()
        self.r_params["contest"] = self.contest
        self.r_params["unassigned_questions"] = \
            self.sql_session.query(QuestionNew)\
                .filter(QuestionNew.contest_id.is_(None))\
                .all()
        self.r_params["contest_questions"] = \
            self.sql_session.query(QuestionNew)\
                .filter(QuestionNew.contest_id == contest_id)\
                .all()
        self.render("contest_new_questions.html", **self.r_params)

    @require_permission(BaseHandler.PERMISSION_ALL)
    def post(self, contest_id):
        fallback_page = self.url("contest", contest_id, "new_questions")

        self.contest = self.safe_get_item(Contest, contest_id)

        try:
            question_id = self.get_argument("question_id")
            operation = self.get_argument("operation")
            assert operation in (
                self.REMOVE_FROM_CONTEST,
            ), "Please select a valid operation"
        except Exception as error:
            self.service.add_notification(
                make_datetime(), "Invalid field(s)", repr(error))
            self.redirect(fallback_page)
            return

        question = self.safe_get_item(QuestionNew, question_id)
        question2 = None

        question_num = question.num

        if operation == self.REMOVE_FROM_CONTEST:
            # Unassign the question to the contest.
            question.contest_id = None
            self.sql_session.flush()

            contest = self.safe_get_item(Contest, contest_id)
            ids = [q for q in contest.questions_ids]
            ids.remove(question.id)
            contest.questions_ids = ids

            for t in self.sql_session.query(QuestionNew)\
                         .filter(QuestionNew.contest_id == contest_id)\
                         .filter(QuestionNew.num > question_num)\
                         .order_by(QuestionNew.num)\
                         .all():
                t.num -= 1
                self.sql_session.flush()

        if self.try_commit():
            # Create the user on RWS.
            self.service.proxy_service.reinitialize()

        # Maybe they'll want to do this again (for another question)
        self.redirect(fallback_page)

class AddContestQuestionHandler(BaseHandler):
    @require_permission(BaseHandler.PERMISSION_ALL)
    def post(self, contest_id):
        fallback_page = self.url("contest", contest_id, "new_questions")

        self.contest = self.safe_get_item(Contest, contest_id)

        try:
            question_id = self.get_argument("question_id")
            # Check that the admin selected some question.
            assert question_id != "null", "Please select a valid question"
        except Exception as error:
            self.service.add_notification(
                make_datetime(), "Invalid field(s)", repr(error))
            self.redirect(fallback_page)
            return

        question = self.safe_get_item(QuestionNew, question_id)
        contest = self.safe_get_item(Contest, contest_id)
        ids = [q for q in contest.questions_ids]
        ids.append(question.id)
        contest.questions_ids = ids
        # Assign the question to the contest.
        question.num = len(self.contest.questions_ids)
        question.contest_id = contest_id

        if self.try_commit():
            # Create the user on RWS.
            self.service.proxy_service.reinitialize()

        # Maybe they'll want to do this again (for another question)
        self.redirect(fallback_page)