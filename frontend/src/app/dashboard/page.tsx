'use client';

import { useQuery } from 'react-query';
import { apiClient } from '@/lib/api';
import Link from 'next/link';
import { FiBook, FiCalendar, FiTrendingUp, FiCheckCircle } from 'react-icons/fi';

export default function DashboardPage() {
  const { data: courses } = useQuery('courses', () => apiClient.getCourses());
  const { data: todayTasks } = useQuery('todayTasks', () => apiClient.getTodaySchedule());
  const { data: masteryOverview } = useQuery('masteryOverview', () => apiClient.getMasteryOverview());

  const stats = [
    {
      name: 'Active Courses',
      value: (courses as any)?.length || 0,
      icon: FiBook,
      color: 'bg-blue-500',
      href: '/dashboard/courses',
    },
    {
      name: "Today's Tasks",
      value: (todayTasks as any)?.length || 0,
      icon: FiCalendar,
      color: 'bg-green-500',
      href: '/dashboard/schedule',
    },
    {
      name: 'Overall Mastery',
      value: `${Math.round((masteryOverview as any)?.overall_mastery || 0)}%`,
      icon: FiTrendingUp,
      color: 'bg-purple-500',
      href: '/dashboard/mastery',
    },
    {
      name: 'Completed Today',
      value: (todayTasks as any)?.filter((t: any) => t.status === 'completed')?.length || 0,
      icon: FiCheckCircle,
      color: 'bg-orange-500',
      href: '/dashboard/schedule',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm text-gray-600">
          Your adaptive learning overview
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Link
            key={stat.name}
            href={stat.href}
            className="relative bg-white pt-5 px-4 pb-12 sm:pt-6 sm:px-6 shadow rounded-lg overflow-hidden hover:shadow-md transition-shadow"
          >
            <dt>
              <div className={`absolute ${stat.color} rounded-md p-3`}>
                <stat.icon className="h-6 w-6 text-white" aria-hidden="true" />
              </div>
              <p className="ml-16 text-sm font-medium text-gray-500 truncate">
                {stat.name}
              </p>
            </dt>
            <dd className="ml-16 pb-6 flex items-baseline sm:pb-7">
              <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
            </dd>
          </Link>
        ))}
      </div>

      {/* Today's Tasks */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Today's Schedule</h2>
        </div>
        <div className="px-6 py-4">
          {todayTasks && (todayTasks as any).length > 0 ? (
            <ul className="space-y-3">
              {(todayTasks as any).slice(0, 5).map((task: any) => (
                <li key={task.id} className="flex items-center justify-between py-2">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{task.title}</p>
                    <p className="text-xs text-gray-500">
                      {task.scheduled_start_time} - {task.scheduled_end_time} • {task.estimated_duration} min
                    </p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      task.status === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : task.status === 'in_progress'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {task.status}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No tasks scheduled for today. Generate your schedule!</p>
          )}
          <div className="mt-4">
            <Link
              href="/dashboard/schedule"
              className="text-sm font-medium text-primary-600 hover:text-primary-500"
            >
              View full schedule →
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Courses */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Your Courses</h2>
        </div>
        <div className="px-6 py-4">
          {courses && (courses as any).length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {(courses as any).slice(0, 6).map((course: any) => (
                <Link
                  key={course.id}
                  href={`/dashboard/courses/${course.id}`}
                  className="border border-gray-200 rounded-lg p-4 hover:border-primary-500 transition-colors"
                >
                  <div
                    className="w-full h-2 rounded-full mb-3"
                    style={{ backgroundColor: course.color || '#3B82F6' }}
                  />
                  <h3 className="font-medium text-gray-900">{course.name}</h3>
                  <p className="text-sm text-gray-500">{course.code}</p>
                  <p className="text-xs text-gray-400 mt-1">{course.semester}</p>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-sm text-gray-500 mb-4">No courses yet. Start by adding your first course!</p>
              <Link
                href="/dashboard/courses"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
              >
                Add Course
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
