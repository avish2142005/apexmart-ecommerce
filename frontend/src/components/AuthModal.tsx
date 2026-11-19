import React, { useState } from 'react';
import { 
  X, Mail, Lock, User, Phone, Check, AlertCircle, Eye, EyeOff, ShieldCheck
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'signin' | 'signup';
}

export const AuthModal: React.FC<AuthModalProps> = ({ 
  isOpen, 
  onClose, 
  initialMode = 'signin' 
}) => {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<'signin' | 'signup'>(initialMode);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Form fields
  const [identifier, setIdentifier] = useState(''); // email or phone for signin
  const [password, setPassword] = useState('');
  
  // Sign up fields
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreeTerms, setAgreeTerms] = useState(true);

  if (!isOpen) return null;

  // Real-time password criteria evaluation
  const hasMinLength = password.length >= 8;
  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecial = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?/\\~`]/.test(password);
  const isPasswordValid = hasMinLength && hasUppercase && hasLowercase && hasNumber && hasSpecial;
  const passwordsMatch = password.length > 0 && password === confirmPassword;

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    if (!identifier.trim()) {
      setErrorMsg('Please enter your email or mobile phone number.');
      return;
    }
    if (!password) {
      setErrorMsg('Please enter your password.');
      return;
    }

    setLoading(true);
    try {
      await login(identifier.trim(), password);
      setSuccessMsg('Signed in successfully!');
      setTimeout(() => {
        onClose();
      }, 700);
    } catch (err: any) {
      setErrorMsg(err.message || 'Invalid email, mobile number, or password.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    if (fullName.trim().length < 3) {
      setErrorMsg('Your full name must be at least 3 characters long.');
      return;
    }
    if (!email.trim() || !email.includes('@')) {
      setErrorMsg('Please enter a valid email address.');
      return;
    }
    if (phone && phone.replace(/\D/g, '').length < 10) {
      setErrorMsg('Please enter a valid 10-digit mobile number.');
      return;
    }
    if (!isPasswordValid) {
      setErrorMsg('Please make sure your password satisfies all security criteria below.');
      return;
    }
    if (!passwordsMatch) {
      setErrorMsg('Passwords do not match. Please re-enter your password.');
      return;
    }
    if (!agreeTerms) {
      setErrorMsg('You must agree to the Conditions of Use & Sale to create an account.');
      return;
    }

    setLoading(true);
    try {
      await register({
        full_name: fullName.trim(),
        email: email.trim().toLowerCase(),
        phone: phone.trim() || undefined,
        password: password,
        terms_accepted: agreeTerms
      });
      setSuccessMsg('Account created successfully! Welcome to ApexMart.');
      setTimeout(() => {
        onClose();
      }, 900);
    } catch (err: any) {
      setErrorMsg(err.message || 'Error creating account. Please check your information.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden my-8">
        
        {/* Header Ribbon */}
        <div className="bg-amazon-dark text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <div className="bg-gradient-to-tr from-amber-500 to-orange-400 text-black font-black text-sm px-2 py-0.5 rounded tracking-tighter">
              APEX
            </div>
            <span className="font-bold text-sm tracking-tight">mart.in</span>
          </div>

          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white p-1 rounded-full hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Mode Tabs */}
        <div className="flex border-b border-gray-200 bg-gray-50 text-xs font-bold text-center">
          <button
            onClick={() => { setMode('signin'); setErrorMsg(null); }}
            className={`flex-1 py-3 transition-colors ${
              mode === 'signin' 
                ? 'border-b-2 border-amber-500 bg-white text-gray-900 font-extrabold' 
                : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => { setMode('signup'); setErrorMsg(null); }}
            className={`flex-1 py-3 transition-colors ${
              mode === 'signup' 
                ? 'border-b-2 border-amber-500 bg-white text-gray-900 font-extrabold' 
                : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-4">
          {/* Notifications */}
          {errorMsg && (
            <div className="bg-red-50 border border-red-300 rounded-lg p-3 text-xs text-red-700 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="bg-emerald-50 border border-emerald-300 rounded-lg p-3 text-xs text-emerald-800 flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {/* ========================================================= */}
          {/* SIGN IN FORM */}
          {/* ========================================================= */}
          {mode === 'signin' && (
            <form onSubmit={handleSignIn} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-gray-800 mb-1">
                  Email or Mobile Phone Number
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    placeholder="name@example.com or 10-digit mobile"
                    className="w-full p-2.5 pl-9 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-500 text-xs"
                    required
                  />
                  <Mail className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="block font-bold text-gray-800">Password</label>
                  <span className="text-[11px] text-blue-600 hover:underline cursor-pointer">
                    Forgot Password?
                  </span>
                </div>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full p-2.5 pl-9 pr-9 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-500 text-xs"
                    required
                  />
                  <Lock className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="remember"
                  defaultChecked
                  className="rounded border-gray-300 accent-amber-500 cursor-pointer"
                />
                <label htmlFor="remember" className="text-gray-600 cursor-pointer text-[11px]">
                  Keep me signed in on this device
                </label>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-amber-400 hover:bg-amber-500 disabled:bg-gray-300 text-gray-900 font-bold py-2.5 rounded-lg shadow-sm transition-colors text-xs flex items-center justify-center cursor-pointer"
              >
                {loading ? 'Verifying Credentials...' : 'Sign In'}
              </button>

              <div className="pt-2 text-center text-gray-500 text-[11px]">
                New to ApexMart?{' '}
                <button
                  type="button"
                  onClick={() => { setMode('signup'); setErrorMsg(null); }}
                  className="text-blue-600 font-bold hover:underline"
                >
                  Create your account
                </button>
              </div>
            </form>
          )}

          {/* ========================================================= */}
          {/* SIGN UP FORM WITH LIVE CRITERIA VALIDATION */}
          {/* ========================================================= */}
          {mode === 'signup' && (
            <form onSubmit={handleSignUp} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-bold text-gray-800 mb-1">
                  Your Full Name
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="First and last name"
                    className="w-full p-2.5 pl-9 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-500 text-xs"
                    required
                  />
                  <User className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                </div>
              </div>

              <div>
                <label className="block font-bold text-gray-800 mb-1">
                  Mobile Phone Number
                </label>
                <div className="relative">
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91 98765 43210"
                    className="w-full p-2.5 pl-9 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-500 text-xs font-mono"
                  />
                  <Phone className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                </div>
              </div>

              <div>
                <label className="block font-bold text-gray-800 mb-1">
                  Email Address
                </label>
                <div className="relative">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    className="w-full p-2.5 pl-9 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-500 text-xs"
                    required
                  />
                  <Mail className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                </div>
              </div>

              <div>
                <label className="block font-bold text-gray-800 mb-1">
                  Set Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="At least 8 characters"
                    className="w-full p-2.5 pl-9 pr-9 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-500 text-xs"
                    required
                  />
                  <Lock className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Live Password Security Criteria Checklist */}
              {password.length > 0 && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 space-y-1.5 text-[11px]">
                  <p className="font-bold text-gray-700">Password Requirements:</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-gray-600">
                    <div className={`flex items-center gap-1.5 ${hasMinLength ? 'text-emerald-700 font-semibold' : 'text-gray-400'}`}>
                      <Check className={`w-3.5 h-3.5 ${hasMinLength ? 'text-emerald-600' : 'text-gray-300'}`} />
                      <span>8+ Characters</span>
                    </div>
                    <div className={`flex items-center gap-1.5 ${hasUppercase ? 'text-emerald-700 font-semibold' : 'text-gray-400'}`}>
                      <Check className={`w-3.5 h-3.5 ${hasUppercase ? 'text-emerald-600' : 'text-gray-300'}`} />
                      <span>Uppercase (A-Z)</span>
                    </div>
                    <div className={`flex items-center gap-1.5 ${hasLowercase ? 'text-emerald-700 font-semibold' : 'text-gray-400'}`}>
                      <Check className={`w-3.5 h-3.5 ${hasLowercase ? 'text-emerald-600' : 'text-gray-300'}`} />
                      <span>Lowercase (a-z)</span>
                    </div>
                    <div className={`flex items-center gap-1.5 ${hasNumber ? 'text-emerald-700 font-semibold' : 'text-gray-400'}`}>
                      <Check className={`w-3.5 h-3.5 ${hasNumber ? 'text-emerald-600' : 'text-gray-300'}`} />
                      <span>Number (0-9)</span>
                    </div>
                    <div className={`col-span-full flex items-center gap-1.5 ${hasSpecial ? 'text-emerald-700 font-semibold' : 'text-gray-400'}`}>
                      <Check className={`w-3.5 h-3.5 ${hasSpecial ? 'text-emerald-600' : 'text-gray-300'}`} />
                      <span>Special Symbol (!@#$%^&*)</span>
                    </div>
                  </div>
                </div>
              )}

              <div>
                <label className="block font-bold text-gray-800 mb-1">
                  Re-enter Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm password"
                    className="w-full p-2.5 pl-9 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-500 text-xs"
                    required
                  />
                  <Lock className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                </div>
                {confirmPassword.length > 0 && (
                  <p className={`text-[10px] mt-1 ${passwordsMatch ? 'text-emerald-600 font-semibold' : 'text-red-500'}`}>
                    {passwordsMatch ? '✓ Passwords match' : '✗ Passwords do not match'}
                  </p>
                )}
              </div>

              <div className="flex items-start gap-2 pt-1">
                <input
                  type="checkbox"
                  id="terms"
                  checked={agreeTerms}
                  onChange={(e) => setAgreeTerms(e.target.checked)}
                  className="rounded border-gray-300 accent-amber-500 cursor-pointer mt-0.5"
                  required
                />
                <label htmlFor="terms" className="text-gray-500 text-[11px] leading-tight cursor-pointer">
                  I agree to ApexMart's <span className="text-blue-600 hover:underline">Conditions of Use & Sale</span> and <span className="text-blue-600 hover:underline">Privacy Notice</span>.
                </label>
              </div>

              <button
                type="submit"
                disabled={loading || !isPasswordValid || !passwordsMatch || !agreeTerms}
                className="w-full bg-amber-400 hover:bg-amber-500 disabled:bg-gray-300 text-gray-900 font-bold py-2.5 rounded-lg shadow-sm transition-colors text-xs flex items-center justify-center cursor-pointer"
              >
                {loading ? 'Creating Account...' : 'Create your ApexMart account'}
              </button>

              <div className="pt-2 text-center text-gray-500 text-[11px]">
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => { setMode('signin'); setErrorMsg(null); }}
                  className="text-blue-600 font-bold hover:underline"
                >
                  Sign in
                </button>
              </div>
            </form>
          )}

          {/* Trust Banner */}
          <div className="pt-3 border-t border-gray-100 flex items-center justify-center gap-1.5 text-[11px] text-gray-400">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>256-bit SSL Secure Authentication</span>
          </div>
        </div>
      </div>
    </div>
  );
};
