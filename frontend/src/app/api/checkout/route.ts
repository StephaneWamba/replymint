import { NextResponse } from 'next/server';
import Stripe from 'stripe';
import { headers } from 'next/headers';

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as { priceId?: string };
    const priceId: string | undefined = body?.priceId;

    if (!priceId) {
      return NextResponse.json({ error: 'Missing priceId' }, { status: 400 });
    }

    const secretKey = process.env.STRIPE_SECRET_KEY;
    if (!secretKey) {
      return NextResponse.json({ error: 'Server misconfiguration: STRIPE_SECRET_KEY not set' }, { status: 500 });
    }

    const stripe = new Stripe(secretKey, { apiVersion: '2023-08-16' });

    const hdrs = await headers();
    const origin = hdrs.get('origin') || 'http://localhost:3000';

    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      success_url: `${origin}/dashboard?checkout=success&session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/pricing?checkout=cancel`,
      allow_promotion_codes: true,
    });

    return NextResponse.json({ id: session.id, url: session.url }, { status: 200 });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
