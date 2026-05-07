"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PRIMAX AI - Groq LLM Client                                ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  WATERMARK: PRIMAX-AI-GROQ-BSP-2025                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import logging
import httpx
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("primax-groq")


@dataclass
class CodeGenerationResult:
    """Result from code generation"""
    code: str
    language: str
    explanation: str
    watermark: str = "PRIMAX-AI-BSP-2025"
    generated_at: str = ""

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "language": self.language,
            "explanation": self.explanation,
            "watermark": self.watermark,
            "generated_at": self.generated_at
        }


class GroqClient:
    """Client for Groq API (llama3-groq-70b model)"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama3-groq-70b-8192-tool-use-preview"  # Fast, powerful model
        self.available = bool(self.api_key)

        if not self.available:
            logger.debug("GROQ_API_KEY not set — Groq client disabled (Ollama fallback handles requests).")

    async def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None
    ) -> CodeGenerationResult:
        """
        Generate code using Groq LLM

        Args:
            prompt: What to generate
            language: Programming language
            context: Additional context

        Returns:
            CodeGenerationResult
        """
        if not self.available:
            raise RuntimeError("Groq API key not configured")

        # Build system prompt
        system_prompt = f"""You are PRIMAX AI, an expert code generator.

Generate clean, production-ready {language} code following best practices.

IMPORTANT:
- Include comprehensive docstrings/comments
- Add error handling
- Follow language conventions
- Make code modular and testable
- Add the PRIMAX-AI-BSP-2025 watermark in comments

Return format:
1. The complete code
2. A brief explanation of what it does
"""

        # Build user prompt
        user_prompt = f"Generate {language} code for: {prompt}"
        if context:
            user_prompt += f"\n\nContext: {context}"

        # Call Groq API
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2048
                    }
                )

                if response.status_code != 200:
                    logger.error(f"Groq API error: {response.text}")
                    raise RuntimeError(f"Groq API failed: {response.status_code}")

                data = response.json()
                generated_text = data["choices"][0]["message"]["content"]

                # Parse response (extract code and explanation)
                code, explanation = self._parse_response(generated_text, language)

                return CodeGenerationResult(
                    code=code,
                    language=language,
                    explanation=explanation
                )

        except httpx.TimeoutException:
            raise RuntimeError("Groq API timeout")
        except Exception as e:
            logger.error(f"Code generation error: {e}")
            raise

    async def chat(
        self,
        message: str,
        conversation_history: Optional[list] = None
    ) -> str:
        """
        Chat with Groq LLM

        Args:
            message: User message
            conversation_history: Previous messages

        Returns:
            Assistant response
        """
        if not self.available:
            raise RuntimeError("Groq API key not configured")

        messages = conversation_history or []
        messages.append({"role": "user", "content": message})

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.8,
                        "max_tokens": 1024
                    }
                )

                if response.status_code != 200:
                    raise RuntimeError(f"Groq API failed: {response.status_code}")

                data = response.json()
                return data["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise

    def _parse_response(self, text: str, language: str) -> tuple[str, str]:
        """Parse LLM response to extract code and explanation"""
        # Try to extract code blocks
        if "```" in text:
            parts = text.split("```")
            if len(parts) >= 3:
                code_block = parts[1]
                # Remove language identifier if present
                if code_block.startswith(language):
                    code_block = code_block[len(language):].strip()
                elif code_block.startswith("python"):
                    code_block = code_block[6:].strip()

                explanation = parts[2].strip() if len(parts) > 2 else parts[0].strip()
                return code_block.strip(), explanation

        # If no code blocks, assume entire response is code
        lines = text.strip().split("\n")
        # Try to find explanation (lines starting with # or after blank line)
        code_lines = []
        explanation_lines = []
        in_explanation = False

        for line in lines:
            if line.strip().startswith("#") and not code_lines:
                explanation_lines.append(line.strip("#").strip())
            elif not line.strip() and code_lines:
                in_explanation = True
            elif in_explanation:
                explanation_lines.append(line)
            else:
                code_lines.append(line)

        code = "\n".join(code_lines).strip()
        explanation = "\n".join(explanation_lines).strip() or "Generated code as requested"

        return code, explanation

    async def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code for quality, bugs, improvements

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Analysis results
        """
        if not self.available:
            raise RuntimeError("Groq API key not configured")

        prompt = f"""Analyze this {language} code:

```{language}
{code}
```

Provide:
1. Code quality score (1-10)
2. Potential bugs or issues
3. Suggested improvements
4. Security concerns
5. Performance considerations
"""

        try:
            response = await self.chat(prompt)
            return {
                "analysis": response,
                "language": language,
                "analyzed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Code analysis error: {e}")
            raise
