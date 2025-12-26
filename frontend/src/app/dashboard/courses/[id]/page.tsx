'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiClient } from '@/lib/api';
import { useParams, useRouter } from 'next/navigation';
import { FiArrowLeft, FiPlus, FiEdit2, FiTrash2, FiTrendingUp } from 'react-icons/fi';
import Link from 'next/link';
import { Course, Topic } from '@/types';

export default function CourseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const courseId = params.id as string;
  const queryClient = useQueryClient();
  const [showTopicModal, setShowTopicModal] = useState(false);
  const [editingTopic, setEditingTopic] = useState<Topic | null>(null);

  const { data: course, isLoading: courseLoading } = useQuery<Course>(
    ['course', courseId],
    () => apiClient.getCourse(courseId)
  );

  const { data: topics, isLoading: topicsLoading } = useQuery<Topic[]>(
    ['topics', courseId],
    () => apiClient.getTopics(courseId)
  );

  const { data: courseMastery } = useQuery(
    ['courseMastery', courseId],
    () => apiClient.getCourseMastery(courseId),
    { enabled: !!courseId }
  );

  const deleteTopicMutation = useMutation(
    (topicId: string) => apiClient.deleteTopic(courseId, topicId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['topics', courseId]);
        queryClient.invalidateQueries(['courseMastery', courseId]);
      },
    }
  );

  const handleEditTopic = (topic: Topic) => {
    setEditingTopic(topic);
    setShowTopicModal(true);
  };

  const handleDeleteTopic = async (topicId: string) => {
    if (confirm('Are you sure you want to delete this topic?')) {
      await deleteTopicMutation.mutateAsync(topicId);
    }
  };

  if (courseLoading) {
    return <div className="text-center py-8">Loading course...</div>;
  }

  if (!course) {
    return <div className="text-center py-8">Course not found</div>;
  }

  const averageMastery = (courseMastery as any)?.average_mastery || 0;

  return (
    <div className="space-y-6">
      <div>
        <Link
          href="/dashboard/courses"
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-4"
        >
          <FiArrowLeft className="mr-2" />
          Back to Courses
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <div
              className="w-16 h-2 rounded-full mb-3"
              style={{ backgroundColor: course.color || '#3B82F6' }}
            />
            <h1 className="text-3xl font-bold text-gray-900">{course.name}</h1>
            <p className="mt-2 text-gray-600">{course.code} • {course.semester}</p>
            {course.description && (
              <p className="mt-2 text-sm text-gray-600">{course.description}</p>
            )}
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Average Mastery</div>
            <div className="text-3xl font-bold text-primary-600">
              {Math.round(averageMastery)}%
            </div>
          </div>
        </div>
      </div>

      {/* Topics Section */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-medium text-gray-900">Topics</h2>
          <button
            onClick={() => {
              setEditingTopic(null);
              setShowTopicModal(true);
            }}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
          >
            <FiPlus className="mr-2" />
            Add Topic
          </button>
        </div>

        <div className="px-6 py-4">
          {topicsLoading ? (
            <div className="text-center py-8">Loading topics...</div>
          ) : topics && topics.length > 0 ? (
            <div className="space-y-3">
              {topics.map((topic) => {
                const topicMastery = (courseMastery as any)?.topics?.find(
                  (t: any) => t.topic_id === topic.id
                );
                return (
                  <div
                    key={topic.id}
                    className="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{topic.name}</h3>
                        <div className="mt-1 flex items-center space-x-3">
                          <span
                            className={`px-2 py-1 text-xs font-semibold rounded-full ${
                              topic.estimated_difficulty === 'easy'
                                ? 'bg-green-100 text-green-800'
                                : topic.estimated_difficulty === 'medium'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {topic.estimated_difficulty}
                          </span>
                          {topicMastery && (
                            <div className="flex items-center text-sm text-gray-600">
                              <FiTrendingUp className="mr-1" />
                              {Math.round(topicMastery.mastery)}% mastery
                              <span className="ml-2 text-xs">
                                ({topicMastery.trend})
                              </span>
                            </div>
                          )}
                        </div>
                        {topic.notes && (
                          <p className="mt-2 text-sm text-gray-600">{topic.notes}</p>
                        )}
                      </div>
                      <div className="flex space-x-2 ml-4">
                        <button
                          onClick={() => handleEditTopic(topic)}
                          className="p-2 text-gray-400 hover:text-primary-600"
                        >
                          <FiEdit2 />
                        </button>
                        <button
                          onClick={() => handleDeleteTopic(topic.id)}
                          className="p-2 text-gray-400 hover:text-red-600"
                        >
                          <FiTrash2 />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-sm text-gray-500 mb-4">No topics yet. Add your first topic!</p>
              <button
                onClick={() => setShowTopicModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
              >
                <FiPlus className="mr-2" />
                Add Topic
              </button>
            </div>
          )}
        </div>
      </div>

      {showTopicModal && (
        <TopicModal
          courseId={courseId}
          topic={editingTopic}
          onClose={() => {
            setShowTopicModal(false);
            setEditingTopic(null);
          }}
        />
      )}
    </div>
  );
}

function TopicModal({
  courseId,
  topic,
  onClose,
}: {
  courseId: string;
  topic: Topic | null;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    name: topic?.name || '',
    estimated_difficulty: topic?.estimated_difficulty || 'medium',
    notes: topic?.notes || '',
  });

  const mutation = useMutation(
    (data: any) =>
      topic
        ? apiClient.updateTopic(courseId, topic.id, data)
        : apiClient.createTopic(courseId, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['topics', courseId]);
        queryClient.invalidateQueries(['courseMastery', courseId]);
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
        <h2 className="text-xl font-bold mb-4">
          {topic ? 'Edit Topic' : 'Add New Topic'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Topic Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., Limits and Continuity"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Difficulty</label>
            <select
              value={formData.estimated_difficulty}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  estimated_difficulty: e.target.value as 'easy' | 'medium' | 'hard',
                })
              }
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Notes (Optional)</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              rows={3}
              placeholder="Additional notes about this topic..."
            />
          </div>
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
              {mutation.isLoading ? 'Saving...' : topic ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
