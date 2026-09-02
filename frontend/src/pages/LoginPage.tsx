import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LogIn, ShieldCheck } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Alert } from '../components/ui/Alert';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Return to intended page or dashboard
  const from = (location.state as { from?: { pathname?: string } })?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setErrorMsg('Please enter both your email address and password.');
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMsg(null);
      await login({ email: email.trim(), password });
      navigate(from, { replace: true });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Invalid credentials. Please try again.';
      setErrorMsg(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-ivory-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Brand Header */}
        <div className="flex flex-col items-center">
          <div className="w-14 h-14 rounded-2xl bg-teal-900 text-white flex items-center justify-center shadow-warm-md">
            <svg
              className="w-8 h-8 text-sage-500"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M4 19C8 19 10 11 14 11C18 11 19 15 22 15" />
              <circle cx="22" cy="15" r="2" fill="#E07A5F" />
              <circle cx="4" cy="19" r="2" fill="#FAF7F2" />
            </svg>
          </div>
          <h2 className="mt-4 text-center font-heading font-bold text-3xl text-teal-900">
            Welcome to CleftPath
          </h2>
          <p className="mt-1 text-center text-xs text-charcoal-600 font-medium">
            Every journey deserves a path forward.
          </p>
        </div>

        {/* Login Card */}
        <Card className="mt-8 sm:mx-auto sm:w-full sm:max-w-md p-6 sm:p-8 space-y-6">
          {errorMsg && (
            <Alert variant="danger" title="Authentication Error">
              {errorMsg}
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                Email Address
              </label>
              <input
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="sarah.parent@example.com"
                className="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900 transition"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                Password
              </label>
              <input
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900 transition"
              />
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full justify-center"
              isLoading={isSubmitting}
              leftIcon={<LogIn className="w-4 h-4" />}
            >
              Sign In to Your Journey
            </Button>
          </form>

          {/* Quick Demo Credentials Info */}
          <div className="p-3 bg-teal-50/70 border border-teal-100 rounded-xl text-xs text-teal-900 space-y-1">
            <div className="font-bold flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-teal-900" />
              <span>Demo Account Credentials:</span>
            </div>
            <p className="text-[11px] text-teal-800">
              Email: <code className="font-mono font-bold">demo.parent@example.com</code>
            </p>
          </div>

          <div className="pt-2 border-t border-stone-100 text-center text-xs text-charcoal-600">
            Don’t have a family account?{' '}
            <Link to="/register" className="font-bold text-teal-900 hover:text-coral-600 underline">
              Create your profile
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};
