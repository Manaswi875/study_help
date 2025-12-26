'use client';

import { useAuth } from '@/contexts/AuthContext';

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-sm text-gray-600">
          Manage your account and preferences
        </p>
      </div>

      <div className="bg-white shadow rounded-lg divide-y divide-gray-200">
        {/* Profile Section */}
        <div className="px-6 py-5">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h2>
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Full Name</dt>
              <dd className="mt-1 text-sm text-gray-900">{user?.full_name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Email</dt>
              <dd className="mt-1 text-sm text-gray-900">{user?.email}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Academic Level</dt>
              <dd className="mt-1 text-sm text-gray-900">{user?.academic_level}</dd>
            </div>
          </dl>
        </div>

        {/* Study Preferences */}
        <div className="px-6 py-5">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Study Preferences</h2>
          <p className="text-sm text-gray-500 mb-4">
            Coming soon: Customize your study hours, break times, and notification preferences.
          </p>
        </div>

        {/* Integration Settings */}
        <div className="px-6 py-5">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Integrations</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">Google Calendar</h3>
                <p className="text-sm text-gray-500">Sync your study schedule with Google Calendar</p>
              </div>
              <button
                disabled
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-gray-50 cursor-not-allowed"
              >
                Coming Soon
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">Notion</h3>
                <p className="text-sm text-gray-500">Mirror your tasks to Notion workspace</p>
              </div>
              <button
                disabled
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-gray-50 cursor-not-allowed"
              >
                Coming Soon
              </button>
            </div>
          </div>
        </div>

        {/* About */}
        <div className="px-6 py-5">
          <h2 className="text-lg font-medium text-gray-900 mb-4">About</h2>
          <p className="text-sm text-gray-600">
            Adaptive Study Planner v1.0.0
            <br />
            An intelligent study planning system with adaptive scheduling
          </p>
        </div>
      </div>
    </div>
  );
}
