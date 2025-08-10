import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

export default function AppDashboardPage() {
  return (
    <div className="min-h-screen bg-zinc-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-2xl font-bold text-zinc-900">
              ReplyMint
            </Link>
            <Badge variant="secondary">Dashboard</Badge>
          </div>
          <nav className="flex items-center space-x-4">
            <Link href="/pricing" className="text-zinc-600 hover:text-zinc-900">
              Pricing
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" size="sm">
                Settings
              </Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-zinc-900 mb-2">Welcome back</h1>
          <p className="text-zinc-600">Manage email automation and view analytics</p>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-600">Total replies</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-zinc-900">1,247</div>
              <p className="text-xs text-zinc-600 mt-1">+12% vs last month</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-600">Response rate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-zinc-900">94%</div>
              <p className="text-xs text-zinc-600 mt-1">+2% vs last month</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-600">Time saved</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-zinc-900">47h</div>
              <p className="text-xs text-zinc-600 mt-1">This month</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-600">Active templates</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-zinc-900">12</div>
              <p className="text-xs text-zinc-600 mt-1">+3 new</p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity & Quick Actions */}
        <div className="grid md:grid-cols-2 gap-8">
          <Card>
            <CardHeader>
              <CardTitle>Recent replies</CardTitle>
              <CardDescription>Latest automated responses</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-green-600 rounded-full" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-zinc-900">Support inquiry response</p>
                    <p className="text-xs text-zinc-600">2 minutes ago</p>
                  </div>
                </div>
                <Separator />
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-blue-600 rounded-full" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-zinc-900">Meeting confirmation</p>
                    <p className="text-xs text-zinc-600">15 minutes ago</p>
                  </div>
                </div>
                <Separator />
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-green-600 rounded-full" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-zinc-900">Product inquiry</p>
                    <p className="text-xs text-zinc-600">1 hour ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick actions</CardTitle>
              <CardDescription>Common tasks</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Button className="w-full justify-start" variant="outline">Create template</Button>
                <Button className="w-full justify-start" variant="outline">View analytics</Button>
                <Button className="w-full justify-start" variant="outline">Manage integrations</Button>
                <Button className="w-full justify-start" variant="outline">Support</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
