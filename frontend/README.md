# ReplyMint Frontend

A Next.js 14 application with NextAuth authentication and AI-powered email automation dashboard.

## Features

- **NextAuth.js Integration**: Email magic link authentication
- **Protected Routes**: Dashboard and settings require authentication
- **Role-Based Access**: Admin and user roles with different permissions
- **Real-time Dashboard**: Shows actual usage data from backend
- **Settings Management**: Configure email tone, signature, and preferences
- **Responsive Design**: Modern UI with Tailwind CSS

## Authentication Flow

1. **Sign In**: User enters email address
2. **Magic Link**: NextAuth sends verification email
3. **Verification**: User clicks link to authenticate
4. **Backend JWT**: Frontend gets JWT token from backend
5. **Protected Access**: User can access dashboard and settings

## Environment Variables

Copy `env.example` to `.env.local` and configure:

```bash
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-key-here

# Backend API
NEXT_PUBLIC_API_URL=https://your-api-gateway-url.execute-api.region.amazonaws.com/staging

# Email Server Configuration (for magic links)
EMAIL_SERVER_HOST=smtp.gmail.com
EMAIL_SERVER_PORT=587
EMAIL_SERVER_USER=your-email@gmail.com
EMAIL_SERVER_PASS=your-app-password
EMAIL_FROM=noreply@replymint.com
```

## Email Provider Options

### Gmail (Recommended for development)

```bash
EMAIL_SERVER_HOST=smtp.gmail.com
EMAIL_SERVER_PORT=587
EMAIL_SERVER_USER=your-email@gmail.com
EMAIL_SERVER_PASS=your-app-password
```

### SendGrid

```bash
EMAIL_SERVER_HOST=smtp.sendgrid.net
EMAIL_SERVER_PORT=587
EMAIL_SERVER_USER=apikey
EMAIL_SERVER_PASS=your-sendgrid-api-key
```

### Mailgun

```bash
EMAIL_SERVER_HOST=smtp.mailgun.org
EMAIL_SERVER_PORT=587
EMAIL_SERVER_USER=your-mailgun-username
EMAIL_SERVER_PASS=your-mailgun-password
```

## Getting Started

1. **Install dependencies**:

   ```bash
   npm install
   ```

2. **Set up environment variables**:

   ```bash
   cp env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Run development server**:

   ```bash
   npm run dev
   ```

4. **Open browser**: Navigate to `http://localhost:3000`

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── api/auth/          # NextAuth API routes
│   ├── auth/              # Authentication pages
│   ├── dashboard/         # Protected dashboard
│   └── settings/          # Protected settings
├── components/            # Reusable UI components
│   ├── auth/             # Authentication components
│   ├── layout/           # Layout components
│   └── ui/               # Base UI components
├── contexts/              # React contexts
├── lib/                   # Utility functions
└── providers/             # App providers
```

## Authentication Components

- **`ProtectedRoute`**: Wraps pages that require authentication
- **`AuthContext`**: Provides authentication state and methods
- **`Navigation`**: Shows different content based on auth status

## Backend Integration

The frontend integrates with the ReplyMint backend API:

- **JWT Authentication**: Uses backend JWT tokens for API calls
- **Real Data**: Dashboard shows actual usage from DynamoDB
- **Settings Sync**: User preferences stored in backend
- **Admin Features**: Role-based access to admin endpoints

## Development

### Adding New Protected Routes

1. Create page component
2. Wrap with `ProtectedRoute` component
3. Use `useAuth()` hook for user data

```tsx
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { useAuth } from "@/contexts/AuthContext";

export default function NewPage() {
  const { user } = useAuth();

  return (
    <ProtectedRoute>
      <div>Protected content for {user?.email}</div>
    </ProtectedRoute>
  );
}
```

### Adding Admin-Only Routes

```tsx
<ProtectedRoute requireAdmin={true}>
  <div>Admin-only content</div>
</ProtectedRoute>
```

## Deployment

1. **Build the application**:

   ```bash
   npm run build
   ```

2. **Deploy to Vercel**:
   - Connect GitHub repository
   - Set environment variables in Vercel dashboard
   - Deploy automatically on push to main branch

## Troubleshooting

### Magic Link Not Working

- Check email server configuration
- Verify `NEXTAUTH_URL` matches your domain
- Check spam folder for verification emails

### Backend API Errors

- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is running and accessible
- Verify JWT tokens are valid

### Authentication Issues

- Clear browser cookies and local storage
- Check `NEXTAUTH_SECRET` is set correctly
- Verify email provider credentials
