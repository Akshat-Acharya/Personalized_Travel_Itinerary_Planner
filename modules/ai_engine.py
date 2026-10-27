"""
AI Engine supporting Groq (primary live dynamic SDK) and Google Gemini with seamless Demo Mode,
robust structured JSON parsing, automatic model fallback, and .env configuration.
"""

import os
import json
import re
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv

# Automatically load environment variables from .env file
load_dotenv(override=True)


def extract_json(raw_text: str) -> Optional[Dict[str, Any]]:
    """Robustly extracts JSON from an LLM response string."""
    if not raw_text:
        return None
    
    # Strip markdown backticks if present
    cleaned = raw_text.strip()
    if "```json" in cleaned:
        cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.MULTILINE)
    if "```" in cleaned:
        cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()

    # Try direct parsing first
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Regex find outermost {...}
    match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # Try fixing common JSON trailing comma issues
    try:
        fixed = re.sub(r",\s*([\]}])", r"\1", cleaned)
        return json.loads(fixed)
    except Exception:
        pass

def get_available_groq_models(api_key: str) -> list:
    """Dynamically queries Groq for chat completion models available on the given key."""
    fallback_models = ["openai/gpt-oss-120b", "llama-3.3-70b-versatile", "openai/gpt-oss-20b", "llama-3.1-8b-instant", "qwen/qwen3.8-27b"]
    if not api_key or not api_key.startswith("gsk_"):
        return fallback_models
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        all_models = client.models.list().data
        chat_models = []
        for m in all_models:
            mid = m.id
            if any(skip in mid.lower() for skip in ["whisper", "guard", "orpheus"]):
                continue
            chat_models.append(mid)

        # Prioritize top models at the front
        preferred_order = ["openai/gpt-oss-120b", "llama-3.3-70b-versatile", "openai/gpt-oss-20b", "llama-3.1-8b-instant", "qwen/qwen3.8-27b"]
        ordered = [m for m in preferred_order if m in chat_models]
        remaining = [m for m in chat_models if m not in ordered]
        result = ordered + remaining
        return result if result else fallback_models
    except Exception:
        return fallback_models


class AIEngine:
    """Unified AI Engine handling Groq SDK as primary dynamic generator, Gemini, and Demo Mode."""

    def __init__(self, provider: str = "groq", api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.provider = provider.lower() if provider else "groq"
        raw_key = api_key.strip() if api_key else ""

        # Auto-check environment variables if key not directly passed
        if not raw_key:
            if self.provider == "groq":
                raw_key = os.getenv("GROQ_API_KEY", "").strip()
            elif self.provider == "gemini":
                raw_key = os.getenv("GEMINI_API_KEY", "").strip()

        # Check if the key is just the dummy placeholder from .env.example
        if raw_key in ["your_groq_api_key_here", "your_gemini_api_key_here", ""]:
            self.api_key = ""
        else:
            self.api_key = raw_key

        self.model_name = model_name

    def is_demo(self) -> bool:
        """True only if user explicitly selects demo or if no valid API key is present."""
        return self.provider == "demo" or not self.api_key

    def generate_json(self, prompt: str, system_instruction: str = "") -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Generates content from the LLM and parses JSON.
        Returns (parsed_json_dict, error_message).
        """
        if self.is_demo():
            return None, "Demo mode is active (no API key configured). Please add your GROQ_API_KEY to .env or the sidebar."

        if self.provider == "groq":
            return self._call_groq(prompt, system_instruction)
        elif self.provider == "gemini":
            return self._call_gemini(prompt, system_instruction)
        else:
            return None, f"Unknown provider: {self.provider}"

    def _call_groq(self, prompt: str, system_instruction: str = "") -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Executes live dynamic generation via official Groq Python SDK with auto-fallback."""
        try:
            from groq import Groq
            client = Groq(api_key=self.api_key)
            chosen_model = self.model_name or "llama-3.3-70b-versatile"

            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": f"{system_instruction} Strictly output valid JSON format."})
            else:
                messages.append({
                    "role": "system",
                    "content": "You are a professional travel SaaS architect and dynamic trip planner. Always output strictly valid JSON with no conversational filler."
                })

            messages.append({"role": "user", "content": prompt})

            # Attempt primary model
            try:
                response = client.chat.completions.create(
                    model=chosen_model,
                    messages=messages,
                    temperature=0.6,
                    max_completion_tokens=4096,
                    response_format={"type": "json_object"}
                )
                raw_text = response.choices[0].message.content
            except Exception as primary_err:
                # If rate-limited (429) or overloaded, fallback seamlessly to fast llama-3.1-8b-instant
                err_str = str(primary_err)
                if ("429" in err_str or "rate_limit" in err_str.lower() or "overloaded" in err_str.lower()) and chosen_model != "llama-3.1-8b-instant":
                    print(f"Groq primary model {chosen_model} rate-limited. Falling back to llama-3.1-8b-instant...")
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages,
                        temperature=0.6,
                        max_completion_tokens=4096,
                        response_format={"type": "json_object"}
                    )
                    raw_text = response.choices[0].message.content
                else:
                    raise primary_err

            parsed = extract_json(raw_text)
            if parsed:
                return parsed, None
            return None, f"Failed to parse JSON from Groq response: {raw_text[:200]}..."

        except Exception as e:
            err_msg = str(e)
            if "Invalid API Key" in err_msg or "401" in err_msg:
                return None, "Invalid Groq API Key. Please verify your GROQ_API_KEY in .env or the sidebar."
            return None, f"Groq API Error: {err_msg}"

    def _call_gemini(self, prompt: str, system_instruction: str = "") -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            chosen_model = self.model_name or "gemini-1.5-flash"
            generation_config = {
                "temperature": 0.4,
                "top_p": 0.95,
                "top_k": 40,
                "response_mime_type": "application/json",
            }
            
            model = genai.GenerativeModel(
                model_name=chosen_model,
                system_instruction=system_instruction if system_instruction else None,
                generation_config=generation_config
            )

            full_prompt = f"{prompt}\n\nStrict output requirement: Return ONLY a valid JSON object matching the requested schema. No markdown backticks, no explanatory conversational text."
            response = model.generate_content(full_prompt)
            
            if not response.text:
                return None, "Gemini returned an empty response."

            parsed = extract_json(response.text)
            if parsed:
                return parsed, None
            return None, f"Failed to parse JSON from Gemini response: {response.text[:200]}..."

        except Exception as e:
            return None, f"Gemini API Error: {str(e)}"
