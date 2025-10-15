import os
import logging
from groq import Groq
from typing import Dict
from dotenv import load_dotenv
from openai import OpenAI
from .models import Session

load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))


# Basic logging config — prints INFO and above to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

logger = logging.getLogger(__name__)



def handle_hpc(session, user_message: str):
    # Always work with the latest session data
    collected = session.collected_data
    complaints = collected.get("presenting_complaints", [])
    current_index = collected.get("current_symptom_index", 0)

    # Base case: all symptoms processed
    if current_index >= len(complaints):
        session.current_section = "pmh"
        session.save()
        return {
            "next_question": "Do you have any chronic medical conditions such as hypertension, diabetes, asthma, sickle cell disease, or HIV? Please reply with 'Yes – [list them]' or 'No'.",
            "current_section": "pmh",
            "session_active": True,
        }

    current_symptom = complaints[current_index]
    
    # Initialize data structures
    if "hpc" not in collected:
        collected["hpc"] = {}
    if current_symptom not in collected["hpc"]:
        collected["hpc"][current_symptom] = []
    
    symptom_hpc = collected["hpc"][current_symptom]

    # Store user message if provided
    if user_message and user_message.strip():
        symptom_hpc.append({"user": user_message.strip()})

    # Prepare LLM context
    biodata = collected.get("biodata", {})
    presenting_complaints = complaints
    previous_hpc = symptom_hpc

    system_prompt = f"""
You are a medical assistant conducting a History of Presenting Complaint (HPC) for: {current_symptom}.

**CRITICAL INSTRUCTIONS:**
- Ask ONE focused, clinical question at a time that can be answered in 1-2 words or a short phrase
- Focus on essential diagnostic information: onset, duration, severity, character, location, radiation, aggravating/relieving factors, associated symptoms
- Be efficient - prioritize the most clinically important questions first
- When you have sufficient information for a basic HPC, respond with just: "DONE"!! Remember just the Output "DONE"!!
- Be precise in your questioning, do not repeat what user has already said!!
- Maximum 8-10 questions per symptom (you don't know the limit, but be concise)
- Do NOT ask open-ended questions like "tell me more" or "describe"
- Do NOT provide diagnoses or medical advice

**Patient Context:**
- Biodata: {biodata}
- All presenting complaints: {presenting_complaints}
- Conversation history for this symptom: {previous_hpc}

**Current task:** {"Begin HPC for this symptom" if not user_message else "Follow up on the patient's response"}
"""

    # Determine user prompt for LLM
    llm_user_prompt = user_message.strip() if user_message and user_message.strip() else "Begin the HPC for this symptom."

    # Call LLM
    next_question = call_llm(system_prompt, llm_user_prompt)

    # Store assistant response
    symptom_hpc.append({"assistant": next_question})
    collected["hpc"][current_symptom] = symptom_hpc
    session.collected_data = collected
    session.save()

    # Check for completion
    assistant_count = sum(1 for m in symptom_hpc if "assistant" in m)
    if next_question.upper() == "DONE" or assistant_count >= 10:
        collected["current_symptom_index"] = current_index + 1
        session.collected_data = collected
        session.save()
        return handle_hpc(session, None)  # Move to next symptom or finish

    session.save()
    return {
        "next_question": next_question,
        "current_section": "hpc",
        "session_active": True,
    }



def call_llm(system_prompt: str, user_prompt: str, model: str = os.getenv("OPENAI_MODEL", "gpt-4")) -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()},
            ],
            temperature=0.1,  # Lower temperature for more consistent medical questions
            max_tokens=500,   # Shorter responses - just the question
        )
        content = response.choices[0].message.content.strip()
        logger.debug(f"LLM response for HPC: {content}")
        
        # Clean up response - remove any prefixes like "Question:"
        if content.lower().startswith("question:"):
            content = content[9:].strip()
            
        return content
    except Exception as e:
        logger.error(f"LLM API error: {e}")
        return "Please tell me more about that symptom."
    




    # llm.py


def generate_final_summary(session: Session) -> dict:
    """
    Generate the final summary, differentials, and triage for a completed session.
    """

    collected = session.collected_data

    # Extract all history sections
    biodata = collected.get("biodata", {})
    presenting_complaints = collected.get("presenting_complaints", [])
    hpc = collected.get("hpc", {})
    pmh = collected.get("pmh", {})
    drug_allergy_history = collected.get("drug_allergy_history", {})
    social_history = collected.get("social_history", {})

    # Flatten HPC into a readable string
    hpc_text = ""
    for symptom, exchanges in hpc.items():
        hpc_text += f"\nSymptom: {symptom}\n"
        for msg in exchanges:
            role, text = list(msg.items())[0]
            hpc_text += f"{role}: {text}\n"

    # Prepare system prompt for the summary LLM
    system_prompt = f"""
You are a medical AI assistant creating a structured clinical summary. Output ONLY valid JSON.

**CRITICAL RULES:**
- Base conclusions ONLY on provided history
- Triage: "Routine", "Urgent", or "Emergency" 
- Confidence: "High", "Medium", or "Low"
- Maximum 3 differentials

**PATIENT DATA:**
Biodata: {biodata}
Presenting: {presenting_complaints}
HPC: {hpc_text}
PMH: {pmh}
Meds/Allergies: {drug_allergy_history}
Social: {social_history}

**JSON FORMAT:**
{{
    "hpc_summary": "2-3 sentence summary",
    "differentials": [{{"diagnosis": "...", "confidence": "..."}}],
    "triage_level": "..."
}}
"""

    # User prompt is optional; can be empty
    user_prompt = "Generate the patient summary, differentials, and triage in JSON format."

    llm_response = call_llm(system_prompt, user_prompt)


    logger.info(f"LLM raw response: {llm_response}")

    # Parse the LLM response safely
    import json

    # --- Robust parsing ---
    summary_data = {
        "hpc_summary": "Unable to generate summary.",
        "differentials": [],
        "triage_level": "Routine",
    }

    try:
        parsed = json.loads(llm_response)

        # Ensure parsed is a dict
        if isinstance(parsed, dict):
            # HPC summary
            summary_data["hpc_summary"] = parsed.get("hpc_summary", summary_data["hpc_summary"])

            # Differentials: must be a list of dicts
            diffs = parsed.get("differentials", [])
            if isinstance(diffs, list):
                filtered_diffs = [
                    d for d in diffs if isinstance(d, dict) and "diagnosis" in d and "confidence" in d
                ]
                summary_data["differentials"] = filtered_diffs

            # Triage level
            triage = parsed.get("triage_level")
            if triage in ["Routine", "Urgent", "Emergency"]:
                summary_data["triage_level"] = triage

    except Exception:
        # fallback keeps defaults
        pass
    
    # try:
    #     summary_data = json.loads(llm_response)
    # except Exception:
    #     # fallback if LLM returns invalid JSON
    #     summary_data = {
    #         "hpc_summary": "Unable to generate summary.",
    #         "differentials": [],
    #         "triage_level": None,
    #     }

    # Compare LLM triage with hardcoded real-time triage
    hc_triage = collected.get("hardcoded_triage", "Routine")
    llm_triage = summary_data.get("triage_level")
    if llm_triage != hc_triage:
        # Take the more severe triage as final
        triage_order = {"Routine": 1, "Urgent": 2, "Emergency": 3}
        final_triage = hc_triage if triage_order[hc_triage] > triage_order.get(llm_triage, 0) else llm_triage
        summary_data["triage_level"] = final_triage

    return summary_data
