"""
This file contains all the prompts used for the Prescription Medicine Analyzer application.

Attributes:
    EXTRACT_MEDICINE_NAMES_PROMPT (str): Prompt for extracting medicine names, types, and strengths from a prescription image.
    EXTRACT_DOSAGE_AND_INSTRUCTIONS_PROMPT (str): Prompt for extracting dosage frequency and duration from a prescription image.
"""

# Prompt for extracting medicine names from prescription
EXTRACT_MEDICINE_NAMES_PROMPT = """
You are a specialized pharmaceutical recognition system with expertise in reading doctors' prescriptions.

The attached image shows a handwritten prescription with medication names.

TASK:
1. Identify ALL medication names written in the prescription (not just one).
2. For each identified medication, provide:
   - fullname: The full medication name as written in the prescription (with proper spelling correction if needed).
   - name: The cleaned/normalized brand or generic name.
   - dosage_type: The dosage form (tablet, capsule, syrup, injection, etc.), or "unknown" if unclear.
   - strength: The strength of the medication (e.g., "500 mg", "10 ml"), or "unknown" if unclear.

IMPORTANT CONTEXT:
- Focus specifically on medication names.
- Medication names often include "Tab.", "Cap.", "Syp.", "Inj." etc.
- Strength must be numeric + unit (mg, ml, gm). If no clear number+unit is visible, use "unknown".
- Do not guess medicine names—if unclear, return "unknown".
- Extract ALL medicines, not just the first one.
- **** There is no medicine name as Ts/Tas so if you find it then it will be tab or tablet

OUTPUT FORMAT:
Return the result strictly in this JSON format with lists:

{
  "fullname": ["Tab. Napa 500 mg", "Cap. Maxpro 20 mg"],
  "name": ["Napa", "Maxpro"],
  "dosage_type": ["tablet", "capsule"],
  "strength": ["500 mg", "20 mg"]
}
"""


CHATBOT_PROMPT = """ """