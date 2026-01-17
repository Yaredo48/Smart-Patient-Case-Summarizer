from openai import OpenAI
from typing import List, Dict, Any, Optional
import logging
import json
import re

logger = logging.getLogger(__name__)


class SummarizationService:
    """Service for generating clinical summaries using GPT-4."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_summary(
        self,
        patient_info: Dict[str, Any],
        documents_text: List[str],
        extracted_entities: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate a clinical summary from patient documents.
        
        Args:
            patient_info: Patient demographic information
            documents_text: List of extracted text from documents
            extracted_entities: Optional pre-extracted medical entities
            
        Returns:
            Dictionary containing summary_text, red_flags, lab_results, and medications
        """
        try:
            logger.info(f"Generating summary for patient {patient_info.get('mrn')}")
            
            # Combine all document texts
            combined_text = "\n\n--- Document Separator ---\n\n".join(documents_text)
            
            # Create the prompt
            prompt = self._create_summary_prompt(patient_info, combined_text, extracted_entities)
            
            # Call GPT-4
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical AI assistant helping doctors review patient cases. Create accurate, concise clinical summaries highlighting key information and red flags."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent medical summaries
                max_tokens=2000
            )
            
            summary_text = response.choices[0].message.content
            
            # Extract red flags from the summary
            red_flags = self._extract_red_flags(summary_text)
            
            # Extract lab results
            lab_results = self._extract_lab_results(combined_text)
            
            # Extract medications
            medications = self._extract_medications(combined_text)
            
            result = {
                "summary_text": summary_text,
                "red_flags": red_flags,
                "lab_results": lab_results,
                "medications": medications
            }
            
            logger.info("Summary generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
    
    def _create_summary_prompt(
        self,
        patient_info: Dict[str, Any],
        documents_text: str,
        extracted_entities: Optional[Dict] = None
    ) -> str:
        """Create the prompt for GPT-4 summarization."""
        
        patient_details = f"""
Patient Information:
- MRN: {patient_info.get('mrn', 'N/A')}
- Name: {patient_info.get('first_name', '')} {patient_info.get('last_name', '')}
- Age: {self._calculate_age(patient_info.get('date_of_birth'))} years
- Gender: {patient_info.get('gender', 'N/A')}
"""
        
        prompt = f"""{patient_details}

Patient Documents:
{documents_text[:4000]}  

Create a comprehensive clinical summary with the following sections:

## PATIENT DEMOGRAPHICS
Brief patient identification and demographics

## CHIEF COMPLAINT & SYMPTOMS
Main reason for visit and presenting symptoms

## RELEVANT MEDICAL HISTORY
- Past medical history
- Surgical history
- Family history (if relevant)
- Social history (if relevant)

## CURRENT MEDICATIONS
List current medications with dosages (if available)

## VITAL SIGNS & LABORATORY RESULTS
List all vital signs and lab values. Mark abnormal values with ⚠️ and critical values with 🔴.
For lab values, include reference ranges when possible.

## CLINICAL RED FLAGS
🔴 List any critical findings, abnormal vital signs, or concerning results that require immediate attention.
Use 🔴 for critical issues and ⚠️ for abnormal but non-critical findings.

## ASSESSMENT & RECOMMENDATIONS
Clinical assessment and recommended next steps

Use clear medical terminology. Be concise but thorough. Highlight abnormalities clearly.
"""
        
        return prompt
    
    def _calculate_age(self, date_of_birth) -> str:
        """Calculate age from date of birth."""
        if not date_of_birth:
            return "Unknown"
        
        from datetime import datetime
        try:
            if isinstance(date_of_birth, str):
                dob = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00'))
            else:
                dob = date_of_birth
            
            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return str(age)
        except:
            return "Unknown"
    
    def _extract_red_flags(self, summary_text: str) -> List[Dict[str, str]]:
        """Extract red flags from the summary text."""
        red_flags = []
        
        # Look for lines with red flag indicators
        lines = summary_text.split('\n')
        for line in lines:
            if '🔴' in line:
                red_flags.append({
                    "category": "critical",
                    "finding": line.replace('🔴', '').strip(),
                    "severity": "critical"
                })
            elif '⚠️' in line and 'RED FLAG' in summary_text[max(0, summary_text.find(line)-200):summary_text.find(line)]:
                red_flags.append({
                    "category": "abnormal",
                    "finding": line.replace('⚠️', '').strip(),
                    "severity": "medium"
                })
        
        return red_flags
    
    def _extract_lab_results(self, text: str) -> Dict[str, Any]:
        """Extract structured lab results from text."""
        # Simple regex patterns for common lab values
        lab_patterns = {
            'hemoglobin': r'(?:hemoglobin|hgb|hb)[:=\s]*(\d+\.?\d*)\s*(?:g/dl|mg/dl)?',
            'glucose': r'(?:glucose|blood sugar)[:=\s]*(\d+\.?\d*)\s*(?:mg/dl)?',
            'creatinine': r'(?:creatinine|cr)[:=\s]*(\d+\.?\d*)\s*(?:mg/dl)?',
            'wbc': r'(?:wbc|white blood cell)[:=\s]*(\d+\.?\d*)\s*(?:k/ul)?',
        }
        
        results = {}
        text_lower = text.lower()
        
        for lab_name, pattern in lab_patterns.items():
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                results[lab_name] = {
                    "value": match.group(1),
                    "unit": self._get_default_unit(lab_name)
                }
        
        return results
    
    def _extract_medications(self, text: str) -> List[Dict[str, str]]:
        """Extract medications from text."""
        # Common medication patterns
        medications = []
        
        # Look for medication sections
        med_section_match = re.search(
            r'(?:medications?|drugs?)[:：]\s*([^\n]+(?:\n[^\n]+)*)',
            text,
            re.IGNORECASE
        )
        
        if med_section_match:
            med_text = med_section_match.group(1)
            # Split by common delimiters
            med_lines = re.split(r'[,;\n]+', med_text)
            
            for line in med_lines[:10]:  # Limit to first 10
                line = line.strip()
                if line and len(line) > 3:
                    medications.append({
                        "name": line,
                        "dosage": "See original document"
                    })
        
        return medications
    
    def _get_default_unit(self, lab_name: str) -> str:
        """Get default unit for a lab test."""
        units = {
            'hemoglobin': 'g/dL',
            'glucose': 'mg/dL',
            'creatinine': 'mg/dL',
            'wbc': 'K/μL'
        }
        return units.get(lab_name, '')


def create_summarization_service(api_key: str, model: str = "gpt-4-turbo-preview") -> SummarizationService:
    """Factory function to create summarization service."""
    return SummarizationService(api_key, model)
