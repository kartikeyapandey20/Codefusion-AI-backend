from typing import List, Optional
from sqlalchemy.orm import Session
from .repository import QuestionRepository
from .model import Question

class QuestionDomain:
    def __init__(self, db: Session):
        self.question_repository = QuestionRepository(db)
    
    def create_question(
        self,
        title: str,
        description: str,
        difficulty_level: str,
        examples: List[dict],
        constraints: List[str],
        test_cases: List[dict]
    ) -> Question:
        # Validate difficulty level
        valid_difficulty_levels = ["Easy", "Medium", "Hard"]
        if difficulty_level not in valid_difficulty_levels:
            raise ValueError(f"Difficulty level must be one of {valid_difficulty_levels}")
            
        # Validate examples format
        for example in examples:
            if not isinstance(example, dict) or "input" not in example or "output" not in example:
                raise ValueError("Each example must contain 'input' and 'output' fields")

        # Validate test cases format
        for test_case in test_cases:
            if not isinstance(test_case, dict) or "input" not in test_case or "exp_output" not in test_case:
                raise ValueError("Each test case must contain 'input' and 'exp_output' fields")

        return self.question_repository.create_question(
            title=title,
            description=description,
            difficulty_level=difficulty_level,
            examples=examples,
            constraints=constraints,
            test_cases=test_cases
        )

    def get_question(self, question_id: int) -> Optional[Question]:
        question = self.question_repository.get_question_by_id(question_id)
        if not question:
            raise ValueError(f"Question with id {question_id} not found")
        return question

    def get_questions(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> List[Question]:
        # Validate pagination parameters
        if skip < 0:
            raise ValueError("Skip value cannot be negative")
        if limit < 1:
            raise ValueError("Limit must be greater than 0")
        if limit > 1000:
            raise ValueError("Limit cannot exceed 1000")

        return self.question_repository.get_all_questions(
            skip=skip,
            limit=limit
        )

    def update_question(
        self,
        question_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        examples: Optional[List[dict]] = None,
        constraints: Optional[List[str]] = None,
        test_cases: Optional[List[dict]] = None
    ) -> Question:
        # Validate question exists
        if not self.question_repository.get_question_by_id(question_id):
            raise ValueError(f"Question with id {question_id} not found")

        # Validate difficulty level if provided
        if difficulty_level and difficulty_level not in ["Easy", "Medium", "Hard"]:
            raise ValueError("Invalid difficulty level")

        # Validate examples format if provided
        if examples:
            for example in examples:
                if not isinstance(example, dict) or "input" not in example or "output" not in example:
                    raise ValueError("Each example must contain 'input' and 'output' fields")

        # Validate test cases format if provided
        if test_cases:
            for test_case in test_cases:
                if not isinstance(test_case, dict) or "input" not in test_case or "exp_output" not in test_case:
                    raise ValueError("Each test case must contain 'input' and 'exp_output' fields")

        updated_question = self.question_repository.update_question(
            question_id=question_id,
            title=title,
            description=description,
            difficulty_level=difficulty_level,
            examples=examples,
            constraints=constraints,
            test_cases=test_cases
        )
        
        if not updated_question:
            raise ValueError(f"Failed to update question with id {question_id}")
            
        return updated_question

    def delete_question(self, question_id: int) -> bool:
        # Validate question exists
        if not self.question_repository.get_question_by_id(question_id):
            raise ValueError(f"Question with id {question_id} not found")

        success = self.question_repository.delete_question(question_id)
        if not success:
            raise ValueError(f"Failed to delete question with id {question_id}")
            
        return success
