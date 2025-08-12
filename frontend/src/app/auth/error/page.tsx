"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertTriangle, ArrowLeft, RefreshCw, Sparkles } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function AuthErrorPage() {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    setError(searchParams.get("error"));
  }, []);

  const getErrorDetails = (errorCode: string | null) => {
    switch (errorCode) {
      case "Configuration":
        return {
          title: "Server Configuration Error",
          description: "There was a problem with the server configuration. Please try again later.",
          icon: AlertTriangle,
          color: "text-red-600",
          bgColor: "bg-red-100"
        };
      case "AccessDenied":
        return {
          title: "Access Denied",
          description: "You don't have permission to access this resource. Please contact your administrator.",
          icon: AlertTriangle,
          color: "text-red-600",
          bgColor: "bg-red-100"
        };
      case "Verification":
        return {
          title: "Verification Failed",
          description: "The verification link has expired or is invalid. Please request a new one.",
          icon: AlertTriangle,
          color: "text-orange-600",
          bgColor: "bg-orange-100"
        };
      default:
        return {
          title: "Authentication Error",
          description: "An unexpected error occurred during authentication. Please try again.",
          icon: AlertTriangle,
          color: "text-red-600",
          bgColor: "bg-red-100"
        };
    }
  };

  const errorDetails = getErrorDetails(error || null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              ReplyMint
            </span>
          </Link>
        </div>

        <Card className="border-0 shadow-2xl bg-white/80 backdrop-blur-sm">
          <CardContent className="pt-8 pb-8 text-center">
            <div className={`w-16 h-16 mx-auto mb-6 rounded-full ${errorDetails.bgColor} flex items-center justify-center`}>
              <errorDetails.icon className={`h-8 w-8 ${errorDetails.color}`} />
            </div>
            
            <h2 className="text-2xl font-bold text-gray-900 mb-3">{errorDetails.title}</h2>
            
            <p className="text-gray-600 mb-6">
              {errorDetails.description}
            </p>
            
            <div className="space-y-3">
              <Link href="/auth/signin" className="block">
                <Button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Try Again
                </Button>
              </Link>
              
              <Link href="/" className="block">
                <Button variant="outline" className="w-full">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back to Home
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            Still having trouble?{" "}
            <Link href="/support" className="text-blue-600 hover:text-blue-700 font-medium">
              Contact support
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
