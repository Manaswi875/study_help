'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { FiLogOut, FiUser } from 'react-icons/fi';

export default function Header() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/auth/login');
  };

  return (
    <header className="bg-white shadow-sm">
      <div className="px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Welcome back, {user?.full_name}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              {user?.academic_level}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center text-gray-700">
              <FiUser className="mr-2" />
              <span className="text-sm">{user?.email}</span>
            </div>
            <button
              onClick={handleLogout}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <FiLogOut className="mr-2" />
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
