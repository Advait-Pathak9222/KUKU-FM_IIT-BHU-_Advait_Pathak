import json
import sys
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.database import init_db

def run_tests():
    init_db()
    client = TestClient(app)
    
    with open("test_cases/test_cases.json", "r", encoding="utf-8") as f:
        test_cases = json.load(f)
        
    print("=" * 70)
    print("RUNNING AI LAWYER EVALUATION SUITE (4 REALISTIC TEST CASES)")
    print("=" * 70)
    
    passed_count = 0
    
    for idx, tc in enumerate(test_cases, 1):
        session_id = f"test_session_{tc['id']}"
        print(f"\n--- [Test Case {idx}/4]: {tc['name']} ---")
        print(f"Category: {tc['category']} | Input Language: {tc['language']}")
        print(f"User Message:\n\"{tc['user_message']}\"")
        
        response = client.post(
            f"/chat/{session_id}",
            json={"message": tc["user_message"]}
        )
        
        if response.status_code != 200:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            continue
            
        data = response.json()
        print(f"\nAPI Result:")
        print(f"- Detected Domain: {data['domain']}")
        print(f"- Escalation Triggered: {data['escalation_triggered']}")
        print(f"- Case Complete (Draft ready): {data['is_complete']}")
        print(f"- Extracted Facts: {json.dumps(data['facts'], indent=2, ensure_ascii=False)}")
        print(f"- Missing Variables: {data['missing_variables']}")
        print(f"\nAssistant Reply:\n{data['reply']}")
        
        # Validation checks
        triage_match = (data['domain'] == tc['expected_triage'])
        escalation_match = (data['escalation_triggered'] == (tc['category'] == 'out_of_scope'))
        
        if triage_match and escalation_match:
            print(f" Status: PASSED (Triage & Guardrail match expected)")
            passed_count += 1
        else:
            print(f"❌ Status: FAILED (Expected {tc['expected_triage']}, got {data['domain']})")
            
        print("-" * 70)
        
    print(f"\nTEST SUITE SUMMARY: {passed_count}/{len(test_cases)} PASSED")

if __name__ == "__main__":
    run_tests()
