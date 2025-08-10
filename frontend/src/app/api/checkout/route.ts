import { NextResponse } from 'next/server';

interface ErrorResponse {
  detail?: string;
}

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as { priceId?: string };
    const priceId: string | undefined = body?.priceId;

    if (!priceId) {
      return NextResponse.json({ error: 'Missing priceId' }, { status: 400 });
    }

    // Call the backend API to create checkout session
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://hhm64ykogk.execute-api.eu-central-1.amazonaws.com/staging';

    const response = await fetch(`${backendUrl}/api/v1/stripe/create-checkout-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ priceId }),
    });

    if (!response.ok) {
      const errorData: ErrorResponse = await response.json().catch(() => ({}) as ErrorResponse);
      return NextResponse.json({ error: errorData.detail || 'Failed to create checkout session' }, { status: response.status });
    }

    const sessionData = (await response.json()) as { data?: { url?: string } } | { url?: string };
    const url = (sessionData as any)?.data?.url ?? (sessionData as any)?.url;

    if (!url) {
      return NextResponse.json({ error: 'No checkout URL returned' }, { status: 502 });
    }

    return NextResponse.json({ url }, { status: 200 });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
