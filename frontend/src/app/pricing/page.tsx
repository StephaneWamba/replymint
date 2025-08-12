'use client';


import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Check, Sparkles, Zap, Crown, Star, ArrowRight } from 'lucide-react';

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
      icon: Sparkles,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
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
      icon: Zap,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
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
      icon: Crown,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <main className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto mb-16">
          <div className="inline-flex items-center space-x-2 bg-blue-50 border border-blue-200 rounded-full px-4 py-2 mb-6">
            <Star className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-700">Simple Pricing</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6 leading-tight">
            Choose your{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              automation
            </span>{' '}
            level
          </h1>
          <p className="text-xl md:text-2xl text-slate-600 max-w-2xl mx-auto">
            Start with a 14-day free trial. No credit card required. Cancel anytime.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan) => (
            <Card 
              key={plan.name} 
              className={`relative border-0 shadow-xl bg-white/80 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 ${
                plan.popular ? 'ring-2 ring-green-500 shadow-2xl scale-105' : ''
              }`}
            >
              {plan.popular && (
                <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-4 py-1 text-sm font-medium shadow-lg">
                  <Star className="h-3 w-3 mr-1" />
                  Most Popular
                </Badge>
              )}
              <CardHeader className="text-center pb-6">
                <div className={`w-16 h-16 mx-auto mb-4 rounded-full ${plan.bgColor} flex items-center justify-center`}>
                  <plan.icon className={`h-8 w-8 ${plan.color}`} />
                </div>
                <CardTitle className="text-2xl font-bold text-slate-900">{plan.name}</CardTitle>
                <CardDescription className="text-slate-600 text-base">{plan.description}</CardDescription>
                <div className="mt-6">
                  <span className="text-5xl font-bold text-slate-900">{plan.price}</span>
                  <span className="text-slate-600 text-lg">{plan.period}</span>
                </div>
                <div className="text-sm text-slate-600 mt-2">{plan.replies}</div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start">
                      <Check className="h-5 w-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-slate-700 leading-relaxed">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button 
                  className={`w-full h-12 text-base font-medium ${
                    plan.popular 
                      ? 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 shadow-lg hover:shadow-xl' 
                      : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-md hover:shadow-lg'
                  } transition-all`}
                  onClick={() => startCheckout(PRICE_IDS[plan.key as keyof typeof PRICE_IDS])}
                >
                  Start Free Trial
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="text-center mt-16">
          <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-8 max-w-2xl mx-auto border border-white/20">
            <h3 className="text-2xl font-bold text-slate-900 mb-4">Need a custom plan?</h3>
            <p className="text-slate-600 mb-6">
              Contact us for enterprise solutions with custom pricing and dedicated support.
            </p>
            <Button variant="outline" size="lg" className="px-8 h-12">
              Contact Sales
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
