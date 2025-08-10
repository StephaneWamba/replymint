'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Check } from 'lucide-react';

const PRICE_IDS = {
  starter: process.env.NEXT_PUBLIC_STRIPE_PRICE_ID_STARTER,
  growth: process.env.NEXT_PUBLIC_STRIPE_PRICE_ID_GROWTH,
  scale: process.env.NEXT_PUBLIC_STRIPE_PRICE_ID_SCALE,
};

async function startCheckout(priceId?: string | null) {
  if (!priceId) return;

  try {
    const res = await fetch('/api/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ priceId }),
    });

    if (res.ok) {
      const data: { url?: string } = await res.json();
      if (data?.url) {
        window.location.href = data.url;
        return;
      }
    }
  } catch (error) {
    console.error('Checkout error:', error);
  }
}

export default function PricingPage() {
  const plans = [
    {
      key: 'starter',
      name: 'Starter',
      price: '$9',
      period: '/month',
      replies: '200 replies',
      description: 'Perfect for individuals and small teams',
      features: [
        '200 automated replies per month',
        'Basic email templates',
        'Simple analytics',
        '14-day free trial',
        'Email support'
      ],
      popular: false
    },
    {
      key: 'growth',
      name: 'Growth',
      price: '$29',
      period: '/month',
      replies: '1000 replies',
      description: 'Ideal for growing businesses',
      features: [
        '1000 automated replies per month',
        'Advanced templates',
        'Detailed analytics',
        '14-day free trial',
        'Priority support',
        'Custom branding'
      ],
      popular: true
    },
    {
      key: 'scale',
      name: 'Scale',
      price: '$79',
      period: '/month',
      replies: '3000 replies',
      description: 'For demanding teams',
      features: [
        '3000 automated replies per month',
        'Custom AI training',
        'Advanced integrations',
        '14-day free trial',
        'Dedicated support',
        'White-label options',
        'API access'
      ],
      popular: false
    }
  ] as const;

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 to-zinc-100">
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-zinc-900">
            ReplyMint
          </Link>
          <nav className="flex items-center space-x-6">
            <Link href="/pricing" className="text-zinc-600 hover:text-zinc-900 font-medium">
              Pricing
            </Link>
            <Link href="/dashboard">
              <Button variant="outline">Dashboard</Button>
            </Link>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-20">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h1 className="text-4xl font-bold text-zinc-900 mb-4">Simple, transparent pricing</h1>
          <p className="text-xl text-zinc-600">
            Choose the plan that fits your needs. All plans include a 14-day free trial.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan) => (
            <Card key={plan.name} className={`relative ${plan.popular ? 'ring-2 ring-blue-500 shadow-lg' : ''}`}>
              {plan.popular && (
                <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-500 text-white">
                  Most popular
                </Badge>
              )}
              <CardHeader className="text-center">
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-zinc-900">{plan.price}</span>
                  <span className="text-zinc-600">{plan.period}</span>
                </div>
                <div className="text-sm text-zinc-600">{plan.replies}</div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center">
                      <Check className="h-4 w-4 text-green-600 mr-2 flex-shrink-0" />
                      <span className="text-sm text-zinc-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button className="w-full" onClick={() => startCheckout(PRICE_IDS[plan.key as keyof typeof PRICE_IDS])}>
                  Start free trial
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}
