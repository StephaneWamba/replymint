"use client";

import { useAuth } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState } from "react";
import { Save, Loader2, Settings as SettingsIcon, User, MessageSquare } from "lucide-react";

interface UserSettings {
  tone: string;
  max_length: number;
  signature: string;
  auto_reply_enabled: boolean;
  notifications: {
    email: boolean;
    slack: boolean;
  };
}

export default function SettingsPage() {
  const { user, backendToken } = useAuth();
  const [settings, setSettings] = useState<UserSettings>({
    tone: "professional",
    max_length: 700,
    signature: "",
    auto_reply_enabled: true,
    notifications: {
      email: true,
      slack: false,
    },
  });
  const [isLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);





  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/settings`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${backendToken}`,
        },
        body: JSON.stringify(settings),
      });

      if (response.ok) {
        // Show success message
        alert("Settings saved successfully!");
      } else {
        alert("Failed to save settings");
      }
    } catch (error) {
      console.error("Failed to save settings:", error);
      alert("Failed to save settings");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Settings</h2>
            <p className="text-gray-600">Fetching your preferences...</p>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center space-x-3">
              <SettingsIcon className="h-10 w-10 text-blue-600" />
              <span>Settings</span>
            </h1>
            <p className="text-lg text-gray-600">
              Configure your email automation preferences and account settings
            </p>
          </div>

          <div className="space-y-6">
            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <MessageSquare className="h-5 w-5 text-green-600" />
                  <span>Email Reply Settings</span>
                </CardTitle>
                <CardDescription>
                  Customize how ReplyMint generates your email responses
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <Label htmlFor="tone" className="text-sm font-medium text-gray-700">
                      Reply Tone
                    </Label>
                    <Select
                      value={settings.tone}
                      onValueChange={(value) => setSettings({ ...settings, tone: value })}
                    >
                      <SelectTrigger className="h-11">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="professional">Professional</SelectItem>
                        <SelectItem value="friendly">Friendly</SelectItem>
                        <SelectItem value="casual">Casual</SelectItem>
                        <SelectItem value="formal">Formal</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-gray-500">
                      Choose the tone that best matches your communication style
                    </p>
                  </div>

                  <div className="space-y-3">
                    <Label htmlFor="max_length" className="text-sm font-medium text-gray-700">
                      Maximum Reply Length
                    </Label>
                    <Input
                      id="max_length"
                      type="number"
                      value={settings.max_length}
                      onChange={(e) => setSettings({ ...settings, max_length: parseInt(e.target.value) })}
                      min="100"
                      max="1000"
                      className="h-11"
                    />
                    <p className="text-xs text-gray-500">Characters (100-1000)</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <Label htmlFor="signature" className="text-sm font-medium text-gray-700">
                    Email Signature
                  </Label>
                  <Textarea
                    id="signature"
                    placeholder="Enter your email signature..."
                    value={settings.signature}
                    onChange={(e) => setSettings({ ...settings, signature: e.target.value })}
                    rows={3}
                    className="resize-none"
                  />
                  <p className="text-xs text-gray-500">
                    This will be automatically added to your AI-generated replies
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="h-5 w-5 text-purple-600" />
                  <span>Account Information</span>
                </CardTitle>
                <CardDescription>Your current account details and status</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <Label className="text-sm text-gray-600">Email Address</Label>
                    <p className="text-sm font-medium text-gray-900 bg-gray-50 px-3 py-2 rounded-md">
                      {user?.email}
                    </p>
                  </div>
                  <div className="space-y-3">
                    <Label className="text-sm text-gray-600">Current Plan</Label>
                    <Badge variant="secondary" className="text-sm px-3 py-1">
                      {user?.role === "admin" ? "Admin" : "User"}
                    </Badge>
                  </div>
                  <div className="space-y-3">
                    <Label className="text-sm text-gray-600">User Role</Label>
                    <Badge variant={user?.role === "admin" ? "destructive" : "secondary"} className="text-sm px-3 py-1">
                      {user?.role}
                    </Badge>
                  </div>
                  <div className="space-y-3">
                    <Label className="text-sm text-gray-600">Subscription Status</Label>
                    <Badge variant="outline" className="text-sm px-3 py-1">
                      Active
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="flex justify-end">
              <Button 
                onClick={handleSave} 
                disabled={isSaving}
                size="lg"
                className="px-8 h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-5 w-5" />
                    Save Settings
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
