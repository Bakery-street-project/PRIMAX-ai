import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
serve(async (req)=>{
  const { secretName } = await req.json();
  const supabaseClient = createClient(Deno.env.get('SUPABASE_URL') ?? '', Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '');
  const { data, error } = await supabaseClient.rpc('get_secret', {
    secret_name: secretName
  });
  if (error) return new Response(JSON.stringify({
    error: error.message
  }), {
    status: 400
  });
  return new Response(JSON.stringify({
    secret: data
  }), {
    status: 200
  });
});
