from django.test import TestCase
from .views import *


# Create your tests here.
class DecisionHandlingTests(TestCase):
    def test_handle_done_decision_success(self):
            request = self.factory.post('/priemka/decision/')
            request.user = self.deputy_user
            
            response = handle_done_decision(
                request, 
                self.decision, 
                self.user_info, 
                can_edit=True
            )
            
            self.decision.refresh_from_db()
            self.assertEqual(response.status_code, 302)
            self.assertEqual(self.decision.status.id, 4)
            self.assertTrue(self.decision.is_archived)


    def test_handle_decline_decision_no_permission(self):
        request = self.factory.post('/priemka/decision/')
        request.user = self.deputy_user
        
        response = handle_decline_decision(
            request, 
            self.decision, 
            self.user_info, 
            can_edit=False
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context_data)
        self.assertEqual(self.decision.status.id, 3)