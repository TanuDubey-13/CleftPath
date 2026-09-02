import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { UserPlus, HeartHandshake } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Alert } from '../components/ui/Alert';
import { UserRole } from '../types';

export const RegisterPage: React.FC = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('caregiver');
  const [termsAccepted, setTermsAccepted] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!firstName.trim() || !lastName.trim() || !email.trim() || !password.trim()) {
      setErrorMsg('Please complete all required fields.');
      return;
    }

    if (!termsAccepted) {
      setErrorMsg('You must accept the terms and AI safety disclaimer to register.');
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMsg(null);
      await register({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        password,
        role,
        consents: {
          terms_accepted: true,
          privacy_policy_accepted: true,
          ai_safety_disclaimer_accepted: true,
        },
      });
      navigate('/dashboard', { replace: true });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Registration failed. Please check your details.';
      setErrorMsg(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-ivory-50 flex flex-col justify-center py-10 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-lg">
        {/* Brand Header */}
        <div className="flex flex-col items-center">
          <div className="w-14 h-14 rounded-2xl bg-teal-900 text-white flex items-center justify-center shadow-warm-md">
            <HeartHandshake className="w-8 h-8 text-sage-500" />
          </div>
          <h2 className="mt-4 text-center font-heading font-bold text-3xl text-teal-900">
            Create Your CleftPath Profile
          </h2>
          <p className="mt-1 text-center text-xs text-charcoal-600 font-medium">
            Begin tracking your family’s longitudinal cleft care roadmap.
          </p>
        </div>

        {/* Register Card */}
        <Card className="mt-8 sm:mx-auto sm:w-full sm:max-w-lg p-6 sm:p-8 space-y-6">
          {errorMsg && (
            <Alert variant="danger" title="Registration Issue">
              {errorMsg}
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Account Role Selection */}
            <div>
              <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1.5">
                I Am Navigating This Journey As:
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setRole('caregiver')}
                  className={`py-2 px-3 text-xs font-bold rounded-xl border text-center transition ${
                    role === 'caregiver'
                      ? 'bg-teal-900 text-white border-teal-900 shadow-warm-sm'
                      : 'bg-stone-50 text-charcoal-700 border-stone-200 hover:bg-stone-100'
                  }`}
                >
                  Parent / Caregiver
                </button>
                <button
                  type="button"
                  onClick={() => setRole('patient_adult')}
                  className={`py-2 px-3 text-xs font-bold rounded-xl border text-center transition ${
                    role === 'patient_adult'
                      ? 'bg-teal-900 text-white border-teal-900 shadow-warm-sm'
                      : 'bg-stone-50 text-charcoal-700 border-stone-200 hover:bg-stone-100'
                  }`}
                >
                  Adult Patient
                </button>
                <button
                  type="button"
                  onClick={() => setRole('clinician')}
                  className={`py-2 px-3 text-xs font-bold rounded-xl border text-center transition ${
                    role === 'clinician'
                      ? 'bg-teal-900 text-white border-teal-900 shadow-warm-sm'
                      : 'bg-stone-50 text-charcoal-700 border-stone-200 hover:bg-stone-100'
                  }`}
                >
                  Cleft Specialist
                </button>
              </div>
            </div>

            {/* Names */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                  First Name
                </label>
                <input
                  type="text"
                  required
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="Sarah"
                  className="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900 transition"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                  Last Name
                </label>
                <input
                  type="text"
                  required
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  placeholder="Jenkins"
                  className="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900 transition"
                />
              </div>
            </div>

            {/* Email */}
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

            {/* Password */}
            <div>
              <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                Password
              </label>
              <input
                type="password"
                autoComplete="new-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 8 chars with uppercase, number"
                className="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900 transition"
              />
              <p className="text-[11px] text-charcoal-500 mt-1">
                Must be at least 8 characters and include uppercase, lowercase, and numeric digits.
              </p>
            </div>

            {/* Consent agreement */}
            <div className="pt-2">
              <label className="flex items-start gap-2.5 text-xs text-charcoal-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={termsAccepted}
                  onChange={(e) => setTermsAccepted(e.target.checked)}
                  className="mt-0.5 rounded border-stone-300 text-teal-900 focus:ring-teal-700"
                />
                <span>
                  I agree to the <strong className="text-teal-900">Terms of Service</strong>,{' '}
                  <strong className="text-teal-900">Privacy Policy</strong>, and acknowledge that CleftPath
                  provides educational & organizational support and does not replace medical diagnosis.
                </span>
              </label>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full justify-center mt-2"
              isLoading={isSubmitting}
              leftIcon={<UserPlus className="w-4 h-4" />}
            >
              Create Account
            </Button>
          </form>

          <div className="pt-2 border-t border-stone-100 text-center text-xs text-charcoal-600">
            Already have an account?{' '}
            <Link to="/login" className="font-bold text-teal-900 hover:text-coral-600 underline">
              Sign in
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};
