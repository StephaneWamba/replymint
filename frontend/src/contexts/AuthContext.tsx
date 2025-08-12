"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useSession, signIn, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";

interface AuthContextType {
  user: { email?: string; role?: string } | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signIn: (email: string) => Promise<{ ok: boolean; error?: string | null }>;
  signOut: () => Promise<void>;
  backendToken: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const [backendToken, setBackendToken] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    if (session?.backendToken) {
      setBackendToken(session.backendToken);
    } else {
      setBackendToken(null);
    }
  }, [session]);

  const handleSignIn = async (email: string) => {
    try {
      const result = await signIn("email", { 
        email, 
        redirect: false 
      });
      
      if (result?.ok) {
        // Sign in successful, session will be updated
        console.log("Sign in successful");
        return { ok: true };
      } else {
        console.error("Sign in failed:", result?.error);
        return { ok: false, error: result?.error };
      }
    } catch (error) {
      console.error("Sign in error:", error);
      return { ok: false, error: "Sign in failed" };
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut({ redirect: false });
      router.push("/");
    } catch (error) {
      console.error("Sign out error:", error);
    }
  };

  const value: AuthContextType = {
    user: session?.user || null,
    isLoading: status === "loading",
    isAuthenticated: status === "authenticated",
    signIn: handleSignIn,
    signOut: handleSignOut,
    backendToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
