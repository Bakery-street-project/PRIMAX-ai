import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import Stripe from "npm:stripe@14";
import { createClient } from "npm:@supabase/supabase-js@2";

const stripe = new Stripe(Deno.env.get("STRIPE_SECRET_KEY")!, {
  apiVersion: "2024-11-20",
});
const cryptoProvider = Stripe.createSubtleCryptoProvider();

Deno.serve(async (req) => {
  const signature = req.headers.get("Stripe-Signature");
  const body = await req.text();

  let event: Stripe.Event;
  try {
    event = await stripe.webhooks.constructEventAsync(
      body,
      signature!,
      Deno.env.get("STRIPE_WEBHOOK_SECRET")!,
      undefined,
      cryptoProvider
    );
  } catch (err) {
    console.error("Webhook signature verification failed:", err);
    return new Response(JSON.stringify({ error: err.message }), { status: 400 });
  }

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
  );

  // Idempotency — skip already-processed events
  const { data: existing } = await supabase
    .from("stripe_webhook_events")
    .select("id")
    .eq("stripe_event_id", event.id)
    .single();

  if (existing) {
    return new Response(JSON.stringify({ ok: true, skipped: true }), { status: 200 });
  }

  // Log the event first
  await supabase.from("stripe_webhook_events").insert({
    stripe_event_id: event.id,
    event_type: event.type,
    payload: event.data,
  });

  try {
    switch (event.type) {
      case "checkout.session.completed": {
        const session = event.data.object as Stripe.Checkout.Session;
        if (session.mode === "subscription" && session.subscription) {
          const sub = await stripe.subscriptions.retrieve(
            session.subscription as string
          );
          await upsertSubscription(supabase, sub, session.customer as string);
        }
        break;
      }

      case "customer.subscription.created":
      case "customer.subscription.updated": {
        const sub = event.data.object as Stripe.Subscription;
        await upsertSubscription(supabase, sub, sub.customer as string);
        break;
      }

      case "customer.subscription.deleted": {
        const sub = event.data.object as Stripe.Subscription;
        await supabase
          .from("tenant_subscriptions")
          .update({ status: "canceled", updated_at: new Date().toISOString() })
          .eq("stripe_subscription_id", sub.id);
        break;
      }

      case "invoice.payment_succeeded": {
        const invoice = event.data.object as Stripe.Invoice;
        if (invoice.subscription) {
          await supabase
            .from("tenant_subscriptions")
            .update({ status: "active", last_synced_at: new Date().toISOString() })
            .eq("stripe_subscription_id", invoice.subscription as string);
        }
        break;
      }

      case "invoice.payment_failed": {
        const invoice = event.data.object as Stripe.Invoice;
        if (invoice.subscription) {
          await supabase
            .from("tenant_subscriptions")
            .update({ status: "past_due", last_synced_at: new Date().toISOString() })
            .eq("stripe_subscription_id", invoice.subscription as string);
        }
        break;
      }
    }
  } catch (err) {
    console.error(`Error handling ${event.type}:`, err);
    return new Response(JSON.stringify({ error: "Handler failed", detail: err.message }), {
      status: 500,
    });
  }

  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
});

async function upsertSubscription(
  supabase: ReturnType<typeof createClient>,
  sub: Stripe.Subscription,
  customerId: string
) {
  // Resolve tenant from Stripe customer ID
  const { data: tenant } = await supabase
    .from("tenants")
    .select("id")
    .eq("stripe_customer_id", customerId)
    .single();

  if (!tenant) {
    console.warn(`No tenant found for Stripe customer ${customerId}`);
    return;
  }

  const priceId = sub.items.data[0]?.price?.id ?? "";

  await supabase.from("tenant_subscriptions").upsert(
    {
      tenant_id: tenant.id,
      stripe_subscription_id: sub.id,
      stripe_price_id: priceId,
      status: sub.status,
      current_period_start: new Date(sub.current_period_start * 1000).toISOString(),
      current_period_end: new Date(sub.current_period_end * 1000).toISOString(),
      cancel_at_period_end: sub.cancel_at_period_end,
      trial_end: sub.trial_end
        ? new Date(sub.trial_end * 1000).toISOString()
        : null,
      last_synced_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    { onConflict: "stripe_subscription_id" }
  );
}
