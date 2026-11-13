"""
AI Model Integration Service
Supports direct conversational queries against:
- Google Gemini
- OpenAI
- Anthropic Claude
- Groq
- OpenRouter
- Other / Custom OpenAI-compatible endpoints (DeepSeek, Ollama, Together AI, Mistral, Local vLLM, etc.)
"""

import requests
import json
from typing import Dict, Any

def query_ai_model(
    provider: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    dossier_text: str = "",
    custom_endpoint: str = ""
) -> Dict[str, Any]:
    
    provider = provider.lower().strip()
    full_prompt = f"{user_prompt}\n\n[VERIFIED SIX-CULTURE NATAL DOSSIER]:\n{dossier_text}" if dossier_text else user_prompt

    try:
        # 1. Google Gemini
        if provider == "gemini":
            selected_model = model or "gemini-2.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent?key={api_key}"
            payload = {
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 3000}
            }
            res = requests.post(url, json=payload, timeout=60)
            if res.status_code != 200:
                return {"error": f"Gemini Error ({res.status_code}): {res.text}"}
            data = res.json()
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"reply": reply, "provider": "gemini", "model": selected_model}

        # 2. OpenAI
        elif provider == "openai":
            selected_model = model or "gpt-4o"
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": selected_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                "temperature": 0.7
            }
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code != 200:
                return {"error": f"OpenAI Error ({res.status_code}): {res.text}"}
            data = res.json()
            reply = data["choices"][0]["message"]["content"]
            return {"reply": reply, "provider": "openai", "model": selected_model}

        # 3. Anthropic Claude
        elif provider == "anthropic":
            selected_model = model or "claude-3-5-sonnet-20241022"
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            payload = {
                "model": selected_model,
                "max_tokens": 3000,
                "system": system_prompt,
                "messages": [{"role": "user", "content": full_prompt}]
            }
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code != 200:
                return {"error": f"Anthropic Error ({res.status_code}): {res.text}"}
            data = res.json()
            reply = data["content"][0]["text"]
            return {"reply": reply, "provider": "anthropic", "model": selected_model}

        # 4. Groq
        elif provider == "groq":
            selected_model = model or "llama-3.3-70b-versatile"
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": selected_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                "temperature": 0.7
            }
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code != 200:
                return {"error": f"Groq Error ({res.status_code}): {res.text}"}
            data = res.json()
            reply = data["choices"][0]["message"]["content"]
            return {"reply": reply, "provider": "groq", "model": selected_model}

        # 5. OpenRouter
        elif provider == "openrouter":
            selected_model = model or "meta-llama/llama-3.3-70b-instruct"
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://astrocheck.local",
                "X-Title": "AstroCheck Six-Culture Chart"
            }
            payload = {
                "model": selected_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ]
            }
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code != 200:
                return {"error": f"OpenRouter Error ({res.status_code}): {res.text}"}
            data = res.json()
            reply = data["choices"][0]["message"]["content"]
            return {"reply": reply, "provider": "openrouter", "model": selected_model}

        # 6. Other / Custom Endpoint (OpenAI-compatible)
        elif provider in ["other", "custom"]:
            endpoint = (custom_endpoint or "").strip()
            if not endpoint:
                return {"error": "Please provide a valid Custom Base URL or Endpoint for 'Other'."}
            
            # Auto-append /chat/completions if user provided a base URL like https://api.deepseek.com/v1
            if not endpoint.endswith("/chat/completions"):
                if endpoint.endswith("/"):
                    endpoint = endpoint + "chat/completions"
                else:
                    endpoint = endpoint + "/chat/completions"
            
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            selected_model = model or "default"
            payload = {
                "model": selected_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                "temperature": 0.7
            }
            res = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            if res.status_code != 200:
                return {"error": f"Custom API Error ({res.status_code}): {res.text}"}
            data = res.json()
            if "choices" in data and len(data["choices"]) > 0:
                reply = data["choices"][0]["message"]["content"]
            else:
                reply = json.dumps(data, indent=2)
            return {"reply": reply, "provider": "custom", "model": selected_model}

        else:
            return {"error": f"Unsupported AI provider: {provider}."}

    except Exception as e:
        return {"error": f"Connection exception: {str(e)}"}
