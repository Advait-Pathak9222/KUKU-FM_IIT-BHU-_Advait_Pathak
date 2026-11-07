import os
import json
from pathlib import Path
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.database import init_db, get_db_connection

OUTPUT_DIR = Path(__file__).resolve().parent / "raw_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_raw_outputs():
    init_db()
    with get_db_connection() as conn:
        conn.execute("DELETE FROM chat_history WHERE session_id LIKE 'eval_%'")
        conn.execute("DELETE FROM case_state WHERE session_id LIKE 'eval_%'")
        conn.commit()
    client = TestClient(app)
    
    with open("test_cases/test_cases.json", "r", encoding="utf-8") as f:
        test_cases = json.load(f)
        
    print("=" * 70)
    print("GENERATING RAW OUTPUTS FOR KUKU FM SUBMISSION")
    print(f"Target Directory: {OUTPUT_DIR}")
    print("=" * 70)
    
    summary_records = []
    
    for idx, tc in enumerate(test_cases, 1):
        tc_id = tc["id"]
        session_id = f"eval_{tc_id.lower()}"
        print(f"\nProcessing [{idx}/{len(test_cases)}] {tc['name']} ...")
        
        # Turn 1
        res1 = client.post(f"/chat/{session_id}", json={"message": tc["user_message"]})
        data1 = res1.json()
        
        conversation_log = [
            {"turn": 1, "role": "user", "content": tc["user_message"]},
            {"turn": 1, "role": "assistant", "content": data1["reply"], "state_snapshot": data1}
        ]
        
        final_data = data1
        
        # If incomplete and missing only 1 or 2 fields, simulate follow-up resolution turn
        if not data1["is_complete"] and tc["category"] != "out_of_scope":
            missing = data1.get("missing_variables", [])
            followup_text = ""
            if len(missing) <= 2:
                if "tenant_name" in missing:
                    followup_text = "Mera poora naam Advait Pathak hai."
                elif "employee_name" in missing or "designation" in missing:
                    followup_text = "Mera naam Rahul Verma hai aur main wahan Senior Software Engineer tha."
            
            if followup_text:
                print(f"  -> Simulating Turn 2 follow-up resolution: \"{followup_text}\"")
                res2 = client.post(f"/chat/{session_id}", json={"message": followup_text})
                data2 = res2.json()
                conversation_log.append({"turn": 2, "role": "user", "content": followup_text})
                conversation_log.append({"turn": 2, "role": "assistant", "content": data2["reply"], "state_snapshot": data2})
                final_data = data2

        # Save individual raw output JSON
        output_file = OUTPUT_DIR / f"{tc_id}.json"
        with open(output_file, "w", encoding="utf-8") as out_f:
            json.dump({
                "test_case_metadata": tc,
                "conversation_history": conversation_log,
                "final_case_state": final_data
            }, out_f, indent=2, ensure_ascii=False)
            
        # If notice was generated, save the markdown draft
        if final_data.get("legal_notice_draft"):
            notice_file = OUTPUT_DIR / f"{tc_id}_LEGAL_NOTICE.md"
            with open(notice_file, "w", encoding="utf-8") as nf:
                nf.write(final_data["legal_notice_draft"])
                
        summary_records.append({
            "id": tc_id,
            "name": tc["name"],
            "category": tc["category"],
            "detected_domain": final_data["domain"],
            "is_complete": final_data["is_complete"],
            "escalation_triggered": final_data["escalation_triggered"],
            "facts_extracted": len(final_data.get("facts", {})),
            "notice_generated": bool(final_data.get("legal_notice_draft"))
        })
        print(f"  ✓ Saved {output_file.name}")

    # Generate Evaluation Summary Markdown
    summary_path = OUTPUT_DIR / "EVALUATION_SUMMARY.md"
    with open(summary_path, "w", encoding="utf-8") as sf:
        sf.write("# NyayaMitra - Raw Outputs & Evaluation Run Log\n\n")
        sf.write(f"Generated at: `2026-11-06` | Total Test Scenarios: {len(test_cases)}\n\n")
        sf.write("| Test ID | Name | Domain | Complete? | Escalated? | Facts Extracted | Notice Generated |\n")
        sf.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for s in summary_records:
            sf.write(f"| `{s['id']}` | {s['name']} | `{s['detected_domain']}` | {'✅' if s['is_complete'] else '❌'} | {'🚨 Yes' if s['escalation_triggered'] else 'No'} | {s['facts_extracted']} | {'📄 Yes' if s['notice_generated'] else 'No'} |\n")
            
    print(f"\n✅ All raw outputs and summary report saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_raw_outputs()
