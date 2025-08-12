"use client";

import { useAuth } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Mail, Settings, BarChart3, Clock, Zap, Activity, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useState, useCallback } from "react";

interface DashboardData {
  plan: {
    name: string;
    monthly_limit: number;
    current_usage: number;
    remaining: number;
  };
  status: string;
  monthly_stats: {
    sent: number;
    received: number;
    success_rate: number;
  };
}

export default function DashboardPage() {
  const { user, backendToken } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchDashboardData = useCallback(async (showLoading = true) => {
    if (showLoading) {
      setIsLoading(true);
    } else {
      setIsRefreshing(true);
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/dashboard/overview`, {
        headers: {
          Authorization: `Bearer ${backendToken}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data.data);
      }
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [backendToken]);



  const handleRefresh = () => {
    fetchDashboardData(false);
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Dashboard</h2>
            <p className="text-gray-600">Fetching your email automation data...</p>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  const usagePercentage = dashboardData ? (dashboardData.plan.current_usage / dashboardData.plan.monthly_limit) * 100 : 0;
  const getUsageVariant = (percentage: number) => {
    if (percentage >= 90) return "destructive";
    if (percentage >= 75) return "secondary";
    if (percentage >= 50) return "default";
    return "outline";
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-4xl font-bold text-gray-900 mb-2">Dashboard</h1>
                <p className="text-lg text-gray-600">
                  Welcome back, {user?.email}! Here&apos;s your email automation overview.
                </p>
              </div>
              <Button 
                variant="outline" 
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="flex items-center space-x-2 hover:bg-blue-50 hover:text-blue-700 transition-colors"
              >
                <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Current Plan</CardTitle>
                <Badge variant="secondary" className="text-xs">
                  {dashboardData?.plan.name}
                </Badge>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">{dashboardData?.plan.monthly_limit}</div>
                <p className="text-xs text-gray-500 mt-1">emails per month</p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Usage This Month</CardTitle>
                <Mail className="h-4 w-4 text-gray-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">{dashboardData?.plan.current_usage}</div>
                <p className="text-xs text-gray-500 mt-1">
                  {dashboardData?.plan.remaining} remaining
                </p>
                <div className="mt-2">
                  <Badge variant={getUsageVariant(usagePercentage)} className="text-xs">
                    {usagePercentage.toFixed(1)}% used
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Success Rate</CardTitle>
                <BarChart3 className="h-4 w-4 text-gray-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">
                  {dashboardData?.monthly_stats.success_rate}%
                </div>
                <p className="text-xs text-gray-500 mt-1">of emails sent successfully</p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Status</CardTitle>
                <Clock className="h-4 w-4 text-gray-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900 capitalize">{dashboardData?.status}</div>
                <p className="text-xs text-gray-500 mt-1">subscription status</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="h-5 w-5 text-blue-600" />
                  <span>Quick Actions</span>
                </CardTitle>
                <CardDescription>Manage your ReplyMint account</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Link href="/settings">
                  <Button variant="outline" className="w-full justify-start group hover:bg-green-50 hover:text-green-700 hover:border-green-200 transition-colors">
                    <Settings className="mr-2 h-4 w-4 group-hover:text-green-600" />
                    Configure Email Settings
                  </Button>
                </Link>
                <Link href="/logs">
                  <Button variant="outline" className="w-full justify-start group hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 transition-colors">
                    <Mail className="mr-2 h-4 w-4 group-hover:text-blue-600" />
                    View Email Logs
                  </Button>
                </Link>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Activity className="h-5 w-5 text-purple-600" />
                  <span>Account Information</span>
                </CardTitle>
                <CardDescription>Your current account details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Email:</span>
                  <span className="text-sm font-medium text-gray-900">{user?.email}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Plan:</span>
                  <Badge variant="secondary" className="text-xs">
                    {dashboardData?.plan.name || "N/A"}
                  </Badge>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Role:</span>
                  <Badge variant={user?.role === "admin" ? "destructive" : "secondary"}>
                    {user?.role || "user"}
                  </Badge>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-sm text-gray-600">Status:</span>
                  <Badge variant="outline">{dashboardData?.status || "N/A"}</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
