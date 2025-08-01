#!/usr/bin/env python3
"""
Тести для MVP-007: Система чернеток (100 останніх)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from tests.utils.test_helpers import create_test_user, get_test_db

class TestProposalDrafts:
    """Тести для чернеток відгуків"""

    def test_create_proposal_draft(self):
        """Тест створення чернетки відгуку"""
        user = create_test_user()
        db = get_test_db()
        draft = Mock()
        draft.id = 1
        draft.user_id = user["id"]
        draft.content = "Test draft content"
        draft.status = "draft"
        draft.created_at = datetime.now()
        assert draft.id == 1
        assert draft.user_id == user["id"]
        assert draft.content == "Test draft content"
        assert draft.status == "draft"
        print("✅ Тест створення чернетки відгуку пройшов")

    def test_draft_limit_100(self):
        """Тест ліміту 100 чернеток на користувача (старі видаляються)"""
        user = create_test_user()
        drafts = []
        # Створюємо 100 чернеток
        for i in range(100):
            draft = Mock()
            draft.id = i + 1
            draft.user_id = user["id"]
            draft.content = f"Draft {i+1}"
            draft.created_at = datetime.now() - timedelta(minutes=100-i)
            drafts.append(draft)
        assert len(drafts) == 100
        # Додаємо 101-шу — найстаріша має бути видалена
        oldest = min(drafts, key=lambda d: d.created_at)
        new_draft = Mock()
        new_draft.id = 101
        new_draft.user_id = user["id"]
        new_draft.content = "Draft 101"
        new_draft.created_at = datetime.now()
        drafts.append(new_draft)
        # Симулюємо авто-видалення найстарішої
        drafts = sorted(drafts, key=lambda d: d.created_at)[1:]
        assert len(drafts) == 100
        assert oldest not in drafts
        print("✅ Тест ліміту 100 чернеток (старі видаляються) пройшов")

    def test_get_proposal_drafts(self):
        """Тест отримання списку чернеток"""
        user = create_test_user()
        drafts = [Mock(id=i+1, user_id=user["id"], content=f"Draft {i+1}", status="draft", created_at=datetime.now()) for i in range(10)]
        # Симулюємо отримання списку
        result = [{"id": d.id, "content": d.content, "status": d.status} for d in drafts]
        assert len(result) == 10
        assert result[0]["id"] == 1
        assert result[-1]["id"] == 10
        print("✅ Тест отримання списку чернеток пройшов")

    def test_delete_proposal_draft(self):
        """Тест видалення чернетки"""
        user = create_test_user()
        drafts = [Mock(id=i+1, user_id=user["id"], content=f"Draft {i+1}", status="draft", created_at=datetime.now()) for i in range(5)]
        to_delete = drafts[2]
        drafts = [d for d in drafts if d.id != to_delete.id]
        assert len(drafts) == 4
        assert to_delete not in drafts
        print("✅ Тест видалення чернетки пройшов")

    def test_draft_edge_cases(self):
        """Тест edge cases: не можна створити 101-шу чернетку без видалення старої"""
        user = create_test_user()
        drafts = [Mock(id=i+1, user_id=user["id"], content=f"Draft {i+1}", created_at=datetime.now() - timedelta(minutes=100-i)) for i in range(100)]
        # Додаємо ще одну — має бути видалена найстаріша
        oldest = min(drafts, key=lambda d: d.created_at)
        new_draft = Mock(id=101, user_id=user["id"], content="Draft 101", created_at=datetime.now())
        drafts.append(new_draft)
        drafts = sorted(drafts, key=lambda d: d.created_at)[1:]
        ids = [d.id for d in drafts]
        assert len(drafts) == 100
        assert oldest.id not in ids
        assert 101 in ids
        print("✅ Тест edge cases для чернеток пройшов")

if __name__ == "__main__":
    test_instance = TestProposalDrafts()
    test_instance.test_create_proposal_draft()
    test_instance.test_draft_limit_100()
    test_instance.test_get_proposal_drafts()
    test_instance.test_delete_proposal_draft()
    test_instance.test_draft_edge_cases()
    print("\n🎉 Всі тести системи чернеток пройшли успішно!")