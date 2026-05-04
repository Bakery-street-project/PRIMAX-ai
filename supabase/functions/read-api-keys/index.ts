import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

// Returns only non-sensitive config keys to authenticated users.
// Never exposes raw API keys — callers should use the primax-ai function directly.
Deno.serve(async (req) => {
  const authHeader = req.headers.get("Authorization");
  if (!authHeader) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
  );

  const { data: { user }, error } = await supabase.auth.getUser(
    authHeader.replace("Bearer ", "")
  );

  if (error || !user) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  return new Response(
    JSON.stringify({
      llm_backend: Deno.env.get("NIM_API_KEY")
        ? "nvidia-nim"
        : Deno.env.get("GEMINI_API_KEY")
        ? "gemini"
        : Deno.env.get("OPENAI_API_KEY")
        ? "openai"
        : "none",
      nim_model: Deno.env.get("NIM_MODEL") ?? "meta/llama-3.1-8b-instruct",
    }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
});
