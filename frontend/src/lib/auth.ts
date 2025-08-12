import { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: "email",
      credentials: {
        email: { label: "Email", type: "email" }
      },
      async authorize(credentials) {
        if (!credentials?.email) return null;
        
        try {
          // Call our backend to authenticate
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/login`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: credentials.email,
            }),
          });

          if (response.ok) {
            const data = await response.json();
            return {
              id: data.user.tenantId || data.user.id,
              email: credentials.email,
              name: data.user.name || credentials.email,
              plan_tier: data.user.plan_tier || "starter",
              subscription_status: data.user.subscription_status || "trial",
              role: data.user.role || "user",
              backendToken: data.token,
            };
          }
        } catch (error) {
          console.error("Authentication error:", error);
        }
        
        return null;
      }
    }),
  ],
  pages: {
    signIn: "/auth/signin",
    error: "/auth/error",
  },
  callbacks: {
    async jwt({ token, user, account }) {
      // Initial sign in
      if (account && user) {
        // Get JWT from our backend
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/login`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: user.email,
              name: user.name,
            }),
          });

          if (response.ok) {
            const data = await response.json();
            token.backendToken = data.token;
            token.user = data.user;
          }
        } catch (error) {
          console.error("Failed to get backend JWT:", error);
        }
      }

      return token;
    },
    async session({ session, token }) {
      // Send properties to the client
      session.user = token.user as {
        id: string;
        email: string;
        name: string;
        plan_tier: string;
        subscription_status: string;
        role: string;
      };
      session.backendToken = token.backendToken as string;
      return session;
    },
  },
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  jwt: {
    secret: process.env.NEXTAUTH_SECRET,
  },
  secret: process.env.NEXTAUTH_SECRET,
};

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      email: string;
      name: string;
      plan_tier: string;
      subscription_status: string;
      role: string;
    };
    backendToken: string;
  }

  interface User {
    id: string;
    email: string;
    name: string;
    plan_tier: string;
    subscription_status: string;
    role: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    backendToken: string;
    user: {
      id: string;
      email: string;
      name: string;
      plan_tier: string;
      subscription_status: string;
      role: string;
    };
  }
}
