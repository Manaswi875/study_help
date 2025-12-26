'use client';

import { useQuery } from 'react-query';
import { apiClient } from '@/lib/api';
import { FiTrendingUp, FiTrendingDown, FiMinus } from 'react-icons/fi';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import Link from 'next/link';

const COLORS = ['#0ea5e9', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444'];

export default function MasteryPage() {
  const { data: overview, isLoading } = useQuery('masteryOverview', () =>
    apiClient.getMasteryOverview()
  );

  if (isLoading) {
    return <div className="text-center py-8">Loading mastery data...</div>;
  }

  const masteryOverview = overview as any;

  // Prepare chart data
  const courseChartData = masteryOverview?.courses?.map((course: any, index: number) => ({
    name: course.course_name.length > 15 ? course.course_name.substring(0, 15) + '...' : course.course_name,
    mastery: Math.round(course.average_mastery),
    color: COLORS[index % COLORS.length],
  })) || [];

  // Mastery distribution
  const masteryDistribution = [
    {
      name: 'Mastered (80-100%)',
      value: 0,
      color: '#10b981',
    },
    {
      name: 'Good (60-79%)',
      value: 0,
      color: '#0ea5e9',
    },
    {
      name: 'Learning (40-59%)',
      value: 0,
      color: '#f59e0b',
    },
    {
      name: 'Needs Work (<40%)',
      value: 0,
      color: '#ef4444',
    },
  ];

  masteryOverview?.courses?.forEach((course: any) => {
    course.topics?.forEach((topic: any) => {
      const mastery = topic.mastery;
      if (mastery >= 80) masteryDistribution[0].value++;
      else if (mastery >= 60) masteryDistribution[1].value++;
      else if (mastery >= 40) masteryDistribution[2].value++;
      else masteryDistribution[3].value++;
    });
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Mastery Tracking</h1>
        <p className="mt-2 text-sm text-gray-600">
          Track your learning progress across all topics
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-500">Overall Mastery</div>
          <div className="mt-2 flex items-baseline">
            <div className="text-3xl font-bold text-primary-600">
              {Math.round(masteryOverview?.overall_mastery || 0)}%
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-500">Active Courses</div>
          <div className="mt-2 flex items-baseline">
            <div className="text-3xl font-bold text-gray-900">
              {masteryOverview?.total_courses || 0}
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-500">Total Topics</div>
          <div className="mt-2 flex items-baseline">
            <div className="text-3xl font-bold text-gray-900">
              {masteryOverview?.total_topics || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Course Mastery Bar Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Mastery by Course</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={courseChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="mastery" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Mastery Distribution Pie Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Topic Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={masteryDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {masteryDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Course Details */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Detailed Progress</h2>
        </div>
        <div className="px-6 py-4">
          {masteryOverview?.courses && masteryOverview.courses.length > 0 ? (
            <div className="space-y-6">
              {masteryOverview.courses.map((course: any, courseIndex: number) => (
                <div key={course.course_id} className="border-b border-gray-200 last:border-0 pb-6 last:pb-0">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{course.course_name}</h3>
                      <p className="text-sm text-gray-500">
                        Average: {Math.round(course.average_mastery)}%
                      </p>
                    </div>
                    <Link
                      href={`/dashboard/courses/${course.course_id}`}
                      className="text-sm text-primary-600 hover:text-primary-500"
                    >
                      View Course →
                    </Link>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {course.topics?.map((topic: any) => {
                      const TrendIcon =
                        topic.trend === 'improving'
                          ? FiTrendingUp
                          : topic.trend === 'declining'
                          ? FiTrendingDown
                          : FiMinus;
                      const trendColor =
                        topic.trend === 'improving'
                          ? 'text-green-600'
                          : topic.trend === 'declining'
                          ? 'text-red-600'
                          : 'text-gray-600';

                      return (
                        <div
                          key={topic.topic_id}
                          className="border border-gray-200 rounded-lg p-3"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className="text-sm font-medium text-gray-900">
                                {topic.topic_name}
                              </h4>
                              <div className="mt-2 flex items-center">
                                <div className="flex-1 bg-gray-200 rounded-full h-2">
                                  <div
                                    className="bg-primary-600 h-2 rounded-full"
                                    style={{ width: `${topic.mastery}%` }}
                                  />
                                </div>
                                <span className="ml-2 text-sm font-medium text-gray-900">
                                  {Math.round(topic.mastery)}%
                                </span>
                              </div>
                            </div>
                            <TrendIcon className={`ml-2 ${trendColor}`} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-sm text-gray-500">No mastery data yet. Start by adding courses and taking quizzes!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
