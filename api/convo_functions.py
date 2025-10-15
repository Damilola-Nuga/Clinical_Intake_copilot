# These are the fucntions that will handle the Hardcoded aspects of the Clerking Process
from .ai import handle_hpc, generate_final_summary

def handle_biodata(session, user_message: str):

    biodata_fields = [
        ("name", "what is your full name?"),
        ("age", "How old are you?"),
        ("gender", "What is your gender?"),
        ("occupation", "What is your occupation?"),
    ]


    collected = session.collected_data.get("biodata", {})


    current_index = len(collected)
    if current_index >= len(biodata_fields):
        session.current_section = "presenting_complaint"
        session.save()
        return {
            "next_question": "Thank you! What brings you in today?",
            "current_section": session.current_section,
            "session_active": True,
        }
    

    field_name, _ = biodata_fields[current_index]
    collected[field_name] = user_message.strip()

    # Save updated biodata
    session.collected_data["biodata"] = collected
    session.save()

    # If we still have more biodata fields to ask
    if current_index + 1 < len(biodata_fields):
        next_field, next_question = biodata_fields[current_index + 1]
        return {
            "next_question": next_question,
            "current_section": "biodata",
            "session_active": True,
        }

    # If biodata collection is complete
    session.current_section = "presenting_complaint"
    session.save()

    return {
        "next_question": "Thank you. Please enter a number (1 or 2) for how many symptoms you have.",
        "current_section": "presenting_complaint",
        "session_active": True,
    }

def handle_pc(session, user_message: str):

    collected = session.collected_data


    if "symptom_count" not in collected:
        try:
            count = int(user_message.strip())
        except ValueError:
            return {
            "next_question": "Please enter a number (1 or 2) for how many symptoms you have.",
            "current_section": "presenting_complaint",
            "session_active": True,
        }


        if count < 1 or count > 2:
            return {
                "next_question": "Please enter a valid number (1 or 2) for how many symptoms you have.",
                "current_section": "presenting_complaint",
                "session_active": True,
            }
        
        collected["symptom_count"] = count
        collected["presenting_complaints"] = []
        session.collected_data = collected
        session.save()

        return {
            "next_question": "Please tell me your first symptom.",
            "current_section": "presenting_complaint",
            "session_active": True,
        }
    

    if "presenting_complaints" in collected:
        complaints = collected["presenting_complaints"]
        complaints.append(user_message.strip())
        collected["presenting_complaints"] = complaints
        session.collected_data = collected
        session.save()


        if len(complaints) < collected["symptom_count"]:
            return {
                "next_question": f"Please tell me your next symptom.",
                "current_section": "presenting_complaint",
                "session_active": True,
            }
        else:
            # Done collecting symptoms — move to HPC
            session.current_section = "hpc"
            collected["current_complaint_index"] = 0  # for tracking during HPC
            session.collected_data = collected
            session.save()

            #import handle_hpc  # adjust import path as needed
            return handle_hpc(session, user_message=None)

def handle_pmh(session, user_message: str):

    collected = session.collected_data.get("past_medical_history", {})

    pmh_questions = [
        ("chronic_conditions",
         "Do you have any chronic medical conditions such as hypertension, diabetes, asthma, sickle cell disease, or HIV? Please reply with 'Yes – [list them]' or 'No'."),
        ("previous_similar_illness",
         "Have you ever had this same problem or been diagnosed with a similar condition before? Please reply with 'Yes – [explain briefly]' or 'No'."),
        ("recent_hospital_admission",
         "Have you been admitted to the hospital or had any surgery in the past year? Please reply with 'Yes – [state what and when]' or 'No'.")
    ]

    current_index = len(collected)

    if current_index < len(pmh_questions):
        # Identify which question we're answering
        field_name, _ = pmh_questions[current_index]

        # Save the user's answer for the current question
        collected[field_name] = user_message.strip()

        # Move to the next question
        next_index = current_index + 1

        if next_index < len(pmh_questions):
            next_question = pmh_questions[next_index][1]
            session.collected_data["past_medical_history"] = collected
            session.save()

            return {
                "next_question": next_question,
                "current_section": "past_medical_history",
                "session_active": True
            }

        else:
            # All PMH questions done
            session.collected_data["past_medical_history"] = collected
            session.current_section = "drug_history"
            session.save()

            return {
                "next_question": "Do you take any regular medications? Please reply with 'Yes – [list them]' or 'No'.",
                "current_section": "drug_history",
                "session_active": True
            }


def handle_drug_history(session, user_message: str):
    
    collected = session.collected_data.get("drug_history", {})

    drug_history_questions = [
        ("regular_medications",
         "Do you take any regular medications? Please reply with 'Yes – [list them]' or 'No'."),
        ("allergies",
         "Do you have any drug or food allergies? Please reply with 'Yes – [specify which and what reaction]' or 'No'.")
    ]

    current_index = len(collected) 

    if current_index < len(drug_history_questions):
        field_name, _ = drug_history_questions[current_index]

        # Save user's current response
        collected[field_name] = user_message.strip()

        # Move to the next question
        next_index = current_index + 1

        if next_index < len(drug_history_questions):
            next_question = drug_history_questions[next_index][1]
            session.collected_data["drug_history"] = collected
            session.save()

            return {
                "next_question": next_question,
                "current_section": "drug_history",
                "session_active": True
            }

        else:
            # All drug history questions answered
            session.collected_data["drug_history"] = collected
            session.current_section = "social_history"
            session.save()

            return {
                "next_question": "Do you drink alcohol? Please reply with ‘Yes – [how much/how often]’ or ‘No’.",
                "current_section": "social_history",
                "session_active": True
            }


def handle_social_history(session, user_message: str):

    collected = session.collected_data.get("social_history", {})

    social_questions = [
        ("alcohol", "Do you drink alcohol? Please reply with 'Yes – [how much/how often]' or 'No'."),
        ("smoking", "Do you smoke? Please reply with 'Yes – [how much/how often]' or 'No'.")
    ]

    current_index = len(collected)

    if current_index < len(social_questions):
        field_name, _ = social_questions[current_index]

        # Save user's current response
        collected[field_name] = user_message.strip()

        # Move to next question
        next_index = current_index + 1

        if next_index < len(social_questions):
            next_question = social_questions[next_index][1]
            session.collected_data["social_history"] = collected
            session.save()

            return {
                "next_question": next_question,
                "current_section": "social_history",
                "session_active": True
            }

        else:
            # All social history questions answered
            session.collected_data["social_history"] = collected
            session.current_section = "completed"
            session.is_active = False
            session.save()

            return {
                "next_question": "Social history completed. You can now view the session summary.",
                "current_section": "completed",
                "session_active": False
            }


def process_message(session, user_message: str):

    current_section = session.current_section

    if current_section == "biodata":
        # Call biodata handler
        return handle_biodata(session, user_message)

    elif current_section == "presenting_complaint":
        # Call presenting complaint handler
        return handle_pc(session, user_message)

    elif current_section == "hpc":
        # Call HPC handler (LLM-powered)
        return handle_hpc(session, user_message)

    elif current_section == "pmh":
        # Call past medical history handler
        return handle_pmh(session, user_message)

    elif current_section == "drug_history":
        # Call drug and allergy history handler
        return handle_drug_history(session, user_message)

    elif current_section == "social_history":
        # Call social history handler
        return handle_social_history(session, user_message)
    
    elif current_section == "completed":
        return {
            "next_question": "The session is already completed. You can view the final summary.",
            "current_section": "completed",
            "session_active": False
        }

    else:
        # Safety: unknown section
        return {
            "next_question": "Error: Unknown conversation section. Please start a new session.",
            "current_section": None,
            "session_active": False,
        }