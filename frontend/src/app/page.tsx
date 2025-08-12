"use client";

import { useAuth } from "@/contexts/AuthContext";
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

import { Sparkles, Zap, Clock, Shield, Mail, CheckCircle, Bot, TrendingUp } from 'lucide-react';
import Link from 'next/link';

export default function HomePage() {
  const { isAuthenticated, user } = useAuth();

  const features = [
    {
      icon: Bot,
      title: "AI-Powered Intelligence",
      description: "Advanced GPT-4o Mini technology that understands context and generates human-like responses",
      color: "text-blue-600",
      bgColor: "bg-blue-50"
    },
    {
      icon: Clock,
      title: "Time Saving",
      description: "Transform hours of email writing into seconds with intelligent automation",
      color: "text-green-600",
      bgColor: "bg-green-50"
    },
    {
      icon: Shield,
      title: "Professional Quality",
      description: "Maintain your brand voice and professional standards across all communications",
      color: "text-purple-600",
      bgColor: "bg-purple-50"
    }
  ];

  const benefits = [
    "24/7 automated email responses",
    "Customizable tone and style",
    "Smart context understanding",
    "Professional email signatures",
    "Usage analytics and insights",
    "Secure and private"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Hero Section */}
      <main className="container mx-auto px-4 py-20">
        <div className="text-center max-w-5xl mx-auto">
          <div className="inline-flex items-center space-x-2 bg-blue-50 border border-blue-200 rounded-full px-4 py-2 mb-6">
            <Sparkles className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-700">AI-Powered Email Automation</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6 leading-tight">
            Automated email replies that{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              save hours
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-slate-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            ReplyMint generates helpful, on-brand responses using advanced AI so you can focus on what matters most.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            {isAuthenticated ? (
              <>
                <Link href="/dashboard">
                  <Button size="lg" className="px-8 h-12 text-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all">
                    <Zap className="mr-2 h-5 w-5" />
                    Go to Dashboard
                  </Button>
                </Link>
                <Link href="/settings">
                  <Button variant="outline" size="lg" className="px-8 h-12 text-lg border-2 hover:bg-blue-50 hover:border-blue-300 transition-colors">
                    <Shield className="mr-2 h-5 w-5" />
                    Configure Settings
                  </Button>
                </Link>
              </>
            ) : (
              <>
                <Link href="/pricing">
                  <Button size="lg" className="px-8 h-12 text-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all">
                    <Sparkles className="mr-2 h-5 w-5" />
                    Get Started
                  </Button>
                </Link>
                <Link href="/auth/signin">
                  <Button variant="outline" size="lg" className="px-8 h-12 text-lg border-2 hover:bg-blue-50 hover:border-blue-300 transition-colors">
                    <Mail className="mr-2 h-5 w-5" />
                    Sign In
                  </Button>
                </Link>
              </>
            )}
          </div>
          
          {isAuthenticated && (
            <div className="inline-flex items-center space-x-3 p-4 bg-green-50 border border-green-200 rounded-xl shadow-sm">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <p className="text-green-800 font-medium">
                Welcome back, {user?.email}! You&apos;re signed in and ready to automate your emails.
              </p>
            </div>
          )}
        </div>

        {/* Features Grid */}
        <div className="mt-24 grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card key={index} className="border-0 shadow-xl bg-white/80 backdrop-blur-sm hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader className="text-center pb-4">
                <div className={`w-16 h-16 mx-auto mb-4 rounded-full ${feature.bgColor} flex items-center justify-center`}>
                  <feature.icon className={`h-8 w-8 ${feature.color}`} />
                </div>
                <CardTitle className="text-xl font-semibold text-slate-900">{feature.title}</CardTitle>
              </CardHeader>
              <CardDescription className="text-slate-600 text-center leading-relaxed px-6 pb-6">
                {feature.description}
              </CardDescription>
            </Card>
          ))}
        </div>

        {/* Benefits Section */}
        <div className="mt-24 text-center">
          <h2 className="text-3xl font-bold text-slate-900 mb-8">Why Choose ReplyMint?</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {benefits.map((benefit, index) => (
              <div key={index} className="flex items-center space-x-3 p-4 bg-white/60 rounded-lg border border-white/20 hover:bg-white/80 transition-colors">
                <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                <span className="text-slate-700 font-medium">{benefit}</span>
              </div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-24 text-center">
          <Card className="border-0 shadow-2xl bg-gradient-to-r from-blue-600 to-purple-600 text-white max-w-2xl mx-auto">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl font-bold">Ready to Transform Your Email Workflow?</CardTitle>
              <CardDescription className="text-blue-100">
                Join thousands of professionals who are already saving hours every week
              </CardDescription>
            </CardHeader>
            <div className="text-center pb-6">
              {isAuthenticated ? (
                <Link href="/dashboard">
                  <Button size="lg" variant="secondary" className="px-8 h-12 text-lg">
                    <TrendingUp className="mr-2 h-5 w-5" />
                    View Dashboard
                  </Button>
                </Link>
              ) : (
                <Link href="/pricing">
                  <Button size="lg" variant="secondary" className="px-8 h-12 text-lg">
                    <Sparkles className="mr-2 h-5 w-5" />
                    Start Free Trial
                  </Button>
                </Link>
              )}
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
}
