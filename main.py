import datetime
import sys
import time
from prawcore.exceptions import Forbidden
from praw.exceptions import RedditAPIException
import praw
import itertools
import secrets
import random
from pprint import pprint, pformat


class DebtBot():
    def __init__(self):
        self.r = praw.Reddit(
            client_id=secrets.CLIENT_ID,
            client_secret=secrets.SECRET,
            user_agent=f'{secrets.USERNAME} (by /u/headgasketidiot)',
            username=secrets.USERNAME,
            password=secrets.PASSWORD
        )
        self.opt_out_submission = praw.models.Submission(
            self.r,
            id='wwkeyx',
        )
        self.EXCLUDED_USERS = ['AutoModerator']
        self.EXCLUDED_SUBS = []
        self.terms = ['student loan', 'student debt', 'school debt', 'school loan']

        self.intros = [
            "Have student loans? You are not alone and you are not a loan!",
        ]
        self.calls_to_action = [
            "If you owe the bank $100, the bank owns you. If you owe $1 million, you own the bank. [Debt Collective](https://debtcollective.org/) is organizing [a student debt strike](https://actionnetwork.org/forms/cant-pay-wont-pay-join-the-student-debt-strike).",
            "Together our debts make us powerful. [Debt Collective](https://debtcollective.org/) is organizing [a student debt strike](https://actionnetwork.org/forms/cant-pay-wont-pay-join-the-student-debt-strike)."
        ]
        self.testimonials = [
            "The movement has abolished more than $5 Billion in student debt, medical debt, payday loans, probation debt, and credit card debt.",
            "Debt Collective provides members with a suite of debt dispute tools that keep money in their pockets.",
            "In 2015, Debt Collective organized the nation’s first student debt strike in collaboration with members who had attended Corinthian Colleges, a predatory for-profit college chain, winning over $2 billion in student debt abolition.",
            "Through Debt Collective's debt abolition debt buying process, they’ve abolished $31,982,455.76 in existing debt and counting."
        ]
        self.footnote = """
*****

^(I'm a bot. My purpose is to help people with student debt. I'm not affilied with Debt Collective or any other organization.)

[^Opt ^Out ](https://np.reddit.com/r/studentdebtbot/comments/wwkeyx/unsubscribe/)

"""
    def already_in_thread(self, comment):
        try:
            comment.refresh()
        except praw.exceptions.ClientException as e:
            sys.stderr.write(
                f'Could not refresh comment {comment}. Exception: {e}. Ignoring'
            )
        if comment.author is None:
            return True
        elif comment.author.name.lower() == secrets.USERNAME.lower():
            return True

        if comment.parent_id == comment.link_id:
            return False
        else:
            return self.already_in_thread(comment.parent())

    def am_i_author(self, comment):
        try:
            if comment.author is not None:
                if comment.author.name.lower() == secrets.USERNAME:
                    return True
            return False
        except AttributeError as e:
                return True
        return False

    def already_replied(self, comment):
        for reply in comment.replies:
            if type(reply) is praw.models.MoreComments:
                for comment in rely.comments:
                    if self.already_replied(comment):
                        return True
            elif self.am_i_author(reply):
                return True
        return False

    def handle_opt_outs(self):
        replies = []
        for comment in self.opt_out_submission.comments:
            try:
                comment.refresh()
            except praw.exceptions.ClientException as e:
                sys.stderr.write(f'Could not refresh comment {comment}. Exception: {e}')
                continue

            if comment.author is None:
                continue
            elif comment.author.name.lower() in self.EXCLUDED_USERS:
                continue

            replies.append(
                self.reply(comment, message='Confirmed')
            )

            self.EXCLUDED_USERS.append(comment.author.name.lower())

        print(f'Opted out users: {pformat(self.EXCLUDED_USERS)}')
        return replies


    def clean_comment(self, comment):
        return ' '.join(w.lower() for w in comment.body.split())

    def generate_message(self):
        intros = [
        ]

    def reply(self, comment, message=None):
        try:
            comment.refresh()
        except (praw.exceptions.ClientException, AttributeError) as e:
            sys.stderr.write(f'Could not refresh comment {comment}. Exception: {e}')
            return

        if self.already_replied(comment):
            return

        if message is None:
            message = '\n\n'.join([
                random.choice(self.intros),
                random.choice(self.calls_to_action),
                random.choice(self.testimonials)
            ])
        message = '\n\n'.join((message, self.footnote))

        try:
            result = comment.reply(message)
            print(f'Made comment {result.permalink}')
        except Exception as e:
            if type(e) is Forbidden:
                self.EXCLUDED_SUBS.append(comment.subreddit.display_name)
                sys.stderr.write(
                    f'Found new banned subreddit {comment.subreddit.display_name}'
                )
            elif type(e) is RedditAPIException:
                # for now, probably handle differently later?
                sys.stderr.write(
                    f'Reply failed with exception {e}'
                )
            else:
                sys.stderr.write(
                    f'Reply failed with exception {e}'
                )

    # def avoid_spam_filters(self):
    #     time.sleep()

    def main(self):
        self.handle_opt_outs()
        submission_stream = self.r.subreddit(
            'studentdebtbot'
        ).stream.comments()
        mentions_stream = praw.models.util.stream_generator(
            self.r.inbox.mentions
        )
        for comment in itertools.chain(submission_stream, mentions_stream):
            if (
                    comment.author.name.lower() == secrets.USERNAME or
                    comment.subreddit.display_name.lower() in self.EXCLUDED_SUBS or
                    comment.author.name.lower() in self.EXCLUDED_USERS
            ):
                continue

            text = self.clean_comment(comment)
            if any([term in text for term in self.terms]):
                if not self.already_in_thread(comment):
                    self.reply(comment)
                    #self.avoid_spam_filters()

            if random.random() < .001:
                # every 1000 comments or so, process any new opt outs
                self.handle_opt_outs()

if __name__ == '__main__':
    DebtBot().main()
