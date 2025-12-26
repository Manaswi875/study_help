'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FiHome, FiBook, FiCalendar, FiTrendingUp, FiSettings, FiEdit } from 'react-icons/fi';
import classNames from 'classnames';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: FiHome },
  { name: 'Courses', href: '/dashboard/courses', icon: FiBook },
  { name: 'Schedule', href: '/dashboard/schedule', icon: FiCalendar },
  { name: 'Mastery', href: '/dashboard/mastery', icon: FiTrendingUp },
  { name: 'Quiz', href: '/dashboard/quiz', icon: FiEdit },
  { name: 'Settings', href: '/dashboard/settings', icon: FiSettings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
      <div className="flex flex-col flex-grow bg-primary-700 pt-5 pb-4 overflow-y-auto">
        <div className="flex items-center flex-shrink-0 px-4">
          <h1 className="text-white text-xl font-bold">Study Planner</h1>
        </div>
        <nav className="mt-8 flex-1 px-2 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={classNames(
                  'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors',
                  {
                    'bg-primary-800 text-white': isActive,
                    'text-primary-100 hover:bg-primary-600': !isActive,
                  }
                )}
              >
                <item.icon className="mr-3 h-6 w-6" aria-hidden="true" />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
