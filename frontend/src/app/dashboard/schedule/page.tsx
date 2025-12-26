'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiClient } from '@/lib/api';
import { format, addDays, startOfWeek } from 'date-fns';
import { FiCalendar, FiCheck, FiClock, FiRefreshCw } from 'react-icons/fi';
import { StudyTask } from '@/types';

export default function SchedulePage() {
  const queryClient = useQueryClient();
  const [view, setView] = useState<'today' | 'upcoming'>('today');
  const [showGenerateModal, setShowGenerateModal] = useState(false);

  const { data: todayTasks, isLoading: todayLoading } = useQuery<StudyTask[]>(
    'todayTasks',
    () => apiClient.getTodaySchedule()
  );

  const { data: upcomingTasks, isLoading: upcomingLoading } = useQuery<StudyTask[]>(
    'upcomingTasks',
    () => apiClient.getUpcomingTasks()
  );

  const updateStatusMutation = useMutation(
    ({ taskId, status }: { taskId: string; status: string }) =>
      apiClient.updateTaskStatus(taskId, status),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('todayTasks');
        queryClient.invalidateQueries('upcomingTasks');
      },
    }
  );

  const replanMutation = useMutation(() => apiClient.replanSchedule(), {
    onSuccess: () => {
      queryClient.invalidateQueries('todayTasks');
      queryClient.invalidateQueries('upcomingTasks');
    },
  });

  const handleStatusChange = (taskId: string, status: string) => {
    updateStatusMutation.mutate({ taskId, status });
  };

  const tasks = view === 'today' ? todayTasks : upcomingTasks;
  const loading = view === 'today' ? todayLoading : upcomingLoading;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Study Schedule</h1>
          <p className="mt-2 text-sm text-gray-600">
            Your adaptive learning schedule
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => replanMutation.mutate()}
            disabled={replanMutation.isLoading}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            <FiRefreshCw className={`mr-2 ${replanMutation.isLoading ? 'animate-spin' : ''}`} />
            Replan
          </button>
          <button
            onClick={() => setShowGenerateModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
          >
            <FiCalendar className="mr-2" />
            Generate Schedule
          </button>
        </div>
      </div>

      {/* View Toggle */}
      <div className="flex space-x-2 border-b border-gray-200">
        <button
          onClick={() => setView('today')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            view === 'today'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          Today
        </button>
        <button
          onClick={() => setView('upcoming')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            view === 'upcoming'
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          Upcoming
        </button>
      </div>

      {/* Tasks List */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4">
          {loading ? (
            <div className="text-center py-8">Loading tasks...</div>
          ) : tasks && tasks.length > 0 ? (
            <div className="space-y-4">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className={`border rounded-lg p-4 transition-colors ${
                    task.status === 'completed'
                      ? 'bg-green-50 border-green-200'
                      : 'border-gray-200 hover:border-primary-300'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="font-medium text-gray-900">{task.title}</h3>
                        <span
                          className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            task.task_type === 'study'
                              ? 'bg-blue-100 text-blue-800'
                              : task.task_type === 'review'
                              ? 'bg-purple-100 text-purple-800'
                              : task.task_type === 'practice'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {task.task_type}
                        </span>
                        <span className="text-xs text-gray-500">
                          Priority: {task.priority_score.toFixed(1)}
                        </span>
                      </div>
                      {task.description && (
                        <p className="mt-1 text-sm text-gray-600">{task.description}</p>
                      )}
                      <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <FiClock className="mr-1" />
                          {task.scheduled_start_time} - {task.scheduled_end_time}
                        </div>
                        <div>{task.estimated_duration} min</div>
                        <div>{format(new Date(task.scheduled_date), 'MMM d, yyyy')}</div>
                      </div>
                    </div>
                    <div className="ml-4">
                      <select
                        value={task.status}
                        onChange={(e) => handleStatusChange(task.id, e.target.value)}
                        className={`px-3 py-2 border rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                          task.status === 'completed'
                            ? 'border-green-300 text-green-800 bg-green-50'
                            : task.status === 'in_progress'
                            ? 'border-blue-300 text-blue-800 bg-blue-50'
                            : 'border-gray-300 text-gray-700'
                        }`}
                      >
                        <option value="pending">Pending</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                        <option value="skipped">Skipped</option>
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <FiCalendar className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks scheduled</h3>
              <p className="mt-1 text-sm text-gray-500">
                Generate a schedule to get started with your adaptive learning plan.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowGenerateModal(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
                >
                  <FiCalendar className="mr-2" />
                  Generate Schedule
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {showGenerateModal && (
        <GenerateScheduleModal onClose={() => setShowGenerateModal(false)} />
      )}
    </div>
  );
}

function GenerateScheduleModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient();
  const today = new Date();
  const [formData, setFormData] = useState({
    start_date: format(today, 'yyyy-MM-dd'),
    end_date: format(addDays(today, 7), 'yyyy-MM-dd'),
  });

  const mutation = useMutation(
    (data: any) => apiClient.generateSchedule(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('todayTasks');
        queryClient.invalidateQueries('upcomingTasks');
        onClose();
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <h2 className="text-xl font-bold mb-4">Generate Study Schedule</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Start Date</label>
            <input
              type="date"
              required
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">End Date</label>
            <input
              type="date"
              required
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <p className="text-sm text-gray-600">
            The system will generate an optimized study schedule based on your courses, mastery levels,
            and available time.
          </p>
          <div className="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isLoading}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
            >
              {mutation.isLoading ? 'Generating...' : 'Generate'}
            </button>
          </div>
          {mutation.error && (
            <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
              {(mutation.error as any)?.response?.data?.detail || 'Failed to generate schedule'}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
