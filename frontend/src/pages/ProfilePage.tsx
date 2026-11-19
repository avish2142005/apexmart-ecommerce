import React, { useState } from 'react';
import { User, MapPin, Phone, Mail, Shield, Check, ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface ProfilePageProps {
  onNavigate: (page: string, params?: any) => void;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({ onNavigate }) => {
  const { user, updateProfile, login } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || 'John Doe');
  const [phone, setPhone] = useState(user?.phone || '+919876543210');
  const [street, setStreet] = useState(user?.address?.street || 'Flat 402, Green Glen Layout, Bellandur');
  const [city, setCity] = useState(user?.address?.city || 'Bengaluru');
  const [state, setState] = useState(user?.address?.state || 'Karnataka');
  const [zip, setZip] = useState(user?.address?.zip || '560103');
  const [savedMsg, setSavedMsg] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await updateProfile({
        full_name: fullName,
        phone,
        address_street: street,
        address_city: city,
        address_state: state,
        address_zip: zip
      });
      setSavedMsg(true);
      setTimeout(() => setSavedMsg(false), 3000);
    } catch (err: any) {
      alert(err.message || 'Error updating profile');
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center gap-3 pb-4 border-b border-gray-200">
        <button onClick={() => onNavigate('home')} className="p-1.5 hover:bg-gray-100 rounded-full">
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Your Account Profile & Addresses</h1>
          <p className="text-xs text-gray-500">Manage your shipping destinations, credentials, and role permissions</p>
        </div>
      </div>

      {savedMsg && (
        <div className="bg-emerald-50 border border-emerald-300 text-emerald-800 p-3 rounded-lg text-xs font-semibold flex items-center gap-2">
          <Check className="w-4 h-4 text-emerald-600" />
          <span>Profile updated successfully!</span>
        </div>
      )}

      {/* Main Profile Edit Form */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-gray-800 pb-2 border-b border-gray-100">
          Personal Information
        </h2>

        <form onSubmit={handleSave} className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block font-semibold text-gray-700 mb-1">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full p-2.5 border border-gray-300 rounded focus:outline-none"
            />
          </div>

          <div>
            <label className="block font-semibold text-gray-700 mb-1">Phone Number</label>
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full p-2.5 border border-gray-300 rounded focus:outline-none font-mono"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block font-semibold text-gray-700 mb-1">Street Address</label>
            <input
              type="text"
              value={street}
              onChange={(e) => setStreet(e.target.value)}
              className="w-full p-2.5 border border-gray-300 rounded focus:outline-none"
            />
          </div>

          <div>
            <label className="block font-semibold text-gray-700 mb-1">City</label>
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="w-full p-2.5 border border-gray-300 rounded focus:outline-none"
            />
          </div>

          <div>
            <label className="block font-semibold text-gray-700 mb-1">State</label>
            <input
              type="text"
              value={state}
              onChange={(e) => setState(e.target.value)}
              className="w-full p-2.5 border border-gray-300 rounded focus:outline-none"
            />
          </div>

          <div>
            <label className="block font-semibold text-gray-700 mb-1">PIN Code</label>
            <input
              type="text"
              value={zip}
              onChange={(e) => setZip(e.target.value)}
              className="w-full p-2.5 border border-gray-300 rounded focus:outline-none font-mono"
            />
          </div>

          <div className="sm:col-span-2 pt-3 flex justify-end">
            <button
              type="submit"
              className="bg-amber-400 hover:bg-amber-500 font-bold text-gray-900 px-6 py-2.5 rounded-lg shadow text-xs transition-colors"
            >
              Save Profile Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
