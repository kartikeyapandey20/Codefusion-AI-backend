from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .model import Question, QuestionExample, QuestionConstraint, QuestionTestCase

class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_question(
        self,
        title: str,
        description: str,
        difficulty_level: str,
        examples: List[dict],
        constraints: List[str],
        test_cases: List[dict]
    ) -> Question:
        # Create the main question
        question = Question(
            title=title,
            description=description,
            difficulty_level=difficulty_level
        )
        self.db.add(question)
        self.db.flush()  # Flush to get the question ID

        # Create examples
        for example in examples:
            question_example = QuestionExample(
                question_id=question.id,
                input=example["input"],
                output=example["output"]
            )
            self.db.add(question_example)

        # Create constraints
        for constraint in constraints:
            question_constraint = QuestionConstraint(
                question_id=question.id,
                description=constraint
            )
            self.db.add(question_constraint)

        # Create test cases
        for test_case in test_cases:
            question_test_case = QuestionTestCase(
                question_id=question.id,
                input=test_case["input"],
                exp_output=test_case["exp_output"]
            )
            self.db.add(question_test_case)

        self.db.commit()
        self.db.refresh(question)
        return question

    def get_question_by_id(self, question_id: int) -> Optional[Question]:
        return self.db.query(Question).filter(Question.id == question_id).first()

    def get_all_questions(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> List[Question]:
        return self.db.query(Question).order_by(desc(Question.created_at)).offset(skip).limit(limit).all()

    def update_question(
        self,
        question_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        examples: Optional[List[dict]] = None,
        constraints: Optional[List[str]] = None,
        test_cases: Optional[List[dict]] = None
    ) -> Optional[Question]:
        question = self.get_question_by_id(question_id)
        if not question:
            return None

        # Update main question fields
        if title is not None:
            question.title = title
        if description is not None:
            question.description = description
        if difficulty_level is not None:
            question.difficulty_level = difficulty_level

        # Update examples if provided
        if examples is not None:
            # Remove existing examples
            self.db.query(QuestionExample).filter(
                QuestionExample.question_id == question_id
            ).delete()
            
            # Add new examples
            for example in examples:
                question_example = QuestionExample(
                    question_id=question.id,
                    input=example["input"],
                    output=example["output"]
                )
                self.db.add(question_example)

        # Update constraints if provided
        if constraints is not None:
            # Remove existing constraints
            self.db.query(QuestionConstraint).filter(
                QuestionConstraint.question_id == question_id
            ).delete()
            
            # Add new constraints
            for constraint in constraints:
                question_constraint = QuestionConstraint(
                    question_id=question.id,
                    description=constraint
                )
                self.db.add(question_constraint)

        # Update test cases if provided
        if test_cases is not None:
            # Remove existing test cases
            self.db.query(QuestionTestCase).filter(
                QuestionTestCase.question_id == question_id
            ).delete()
            
            # Add new test cases
            for test_case in test_cases:
                question_test_case = QuestionTestCase(
                    question_id=question.id,
                    input=test_case["input"],
                    exp_output=test_case["exp_output"]
                )
                self.db.add(question_test_case)

        self.db.commit()
        self.db.refresh(question)
        return question

    def delete_question(self, question_id: int) -> bool:
        question = self.get_question_by_id(question_id)
        if not question:
            return False
            
        self.db.delete(question)
        self.db.commit()
        return True
