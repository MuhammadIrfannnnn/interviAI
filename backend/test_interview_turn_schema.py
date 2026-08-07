import unittest

from app.schemas.interview_state import InterviewState
from app.schemas.interview_turn import InterviewTurn


class InterviewTurnSchemaTest(unittest.TestCase):
    def test_interview_turn_parses_nested_state_and_question(self):
        state = InterviewState()
        payload = {
            "evaluation": "The candidate answered clearly and showed solid reasoning.",
            "action": "continue_topic",
            "updated_state": state.model_dump(),
            "next_question": "Can you walk through the tradeoffs in your design?",
        }

        turn = InterviewTurn(**payload)

        self.assertEqual(turn.evaluation, payload["evaluation"])
        self.assertEqual(turn.action, "continue_topic")
        self.assertIsInstance(turn.updated_state, InterviewState)
        self.assertEqual(turn.next_question, payload["next_question"])


if __name__ == "__main__":
    unittest.main()
