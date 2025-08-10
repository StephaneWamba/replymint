import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 to-zinc-100">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="text-2xl font-bold text-zinc-900">ReplyMint</div>
          <nav className="flex items-center space-x-6">
            <Link href="/pricing" className="text-zinc-600 hover:text-zinc-900">Pricing</Link>
            <Link href="/dashboard">
              <Button variant="outline">Dashboard</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <main className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-zinc-900 mb-6">Automated email replies that save hours</h1>
          <p className="text-xl text-zinc-600 mb-8">
            ReplyMint generates helpful, on-brand responses so you can focus on real work.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link href="/dashboard">
              <Button size="lg" className="px-8">Get started</Button>
            </Link>
            <Link href="/pricing">
              <Button variant="outline" size="lg" className="px-8">View pricing</Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-20 grid md:grid-cols-3 gap-8">
          <Card>
            <CardHeader>
              <CardTitle>Smart automation</CardTitle>
              <CardDescription>Understands context and tone</CardDescription>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Time saving</CardTitle>
              <CardDescription>From hours to seconds</CardDescription>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Professional quality</CardTitle>
              <CardDescription>Stay on brand and consistent</CardDescription>
            </CardHeader>
          </Card>
        </div>
      </main>
    </div>
  );
}
