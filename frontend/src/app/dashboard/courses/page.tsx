'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiClient } from '@/lib/api';
import Link from 'next/link';
import { FiPlus, FiEdit2, FiTrash2, FiBook } from 'react-icons/fi';
import { Course } from '@/types';

export default function CoursesPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);

  const { data: courses, isLoading } = useQuery<Course[]>('courses', () =>
    apiClient.getCourses()
  );

  const deleteMutation = useMutation(
    (id: string) => apiClient.deleteCourse(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('courses');
      },
    }
  );

  const handleEdit = (course: Course) => {
    setEditingCourse(course);
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this course?')) {
      await deleteMutation.mutateAsync(id);
    }
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading courses...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Courses</h1>
          <p className="mt-2 text-sm text-gray-600">
            Manage your courses and track your progress
          </p>
        </div>
        <button
          onClick={() => {
            setEditingCourse(null);
            setShowModal(true);
          }}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
        >
          <FiPlus className="mr-2" />
          Add Course
        </button>
      </div>

      {courses && courses.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <div
              key={course.id}
              className="bg-white rounded-lg shadow hover:shadow-md transition-shadow overflow-hidden"
            >
              <div
                className="h-3"
                style={{ backgroundColor: course.color || '#3B82F6' }}
              />
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{course.name}</h3>
                    <p className="text-sm text-gray-600">{course.code}</p>
                    <p className="text-xs text-gray-500 mt-1">{course.semester}</p>
                    {course.description && (
                      <p className="text-sm text-gray-600 mt-2">{course.description}</p>
                    )}
                  </div>
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <Link
                    href={`/dashboard/courses/${course.id}`}
                    className="text-sm font-medium text-primary-600 hover:text-primary-500"
                  >
                    View Details →
                  </Link>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(course)}
                      className="p-2 text-gray-400 hover:text-primary-600"
                    >
                      <FiEdit2 />
                    </button>
                    <button
                      onClick={() => handleDelete(course.id)}
                      className="p-2 text-gray-400 hover:text-red-600"
                    >
                      <FiTrash2 />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <FiBook className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No courses</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating your first course.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              <FiPlus className="mr-2" />
              Add Course
            </button>
          </div>
        </div>
      )}

      {showModal && (
        <CourseModal
          course={editingCourse}
          onClose={() => {
            setShowModal(false);
            setEditingCourse(null);
          }}
        />
      )}
    </div>
  );
}

function CourseModal({
  course,
  onClose,
}: {
  course: Course | null;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    name: course?.name || '',
    code: course?.code || '',
    semester: course?.semester || '',
    description: course?.description || '',
    color: course?.color || '#3B82F6',
  });

  const mutation = useMutation(
    (data: any) =>
      course
        ? apiClient.updateCourse(course.id, data)
        : apiClient.createCourse(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('courses');
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
          {course ? 'Edit Course' : 'Add New Course'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Course Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., Calculus I"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Course Code</label>
            <input
              type="text"
              required
              value={formData.code}
              onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., MATH 101"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Semester</label>
            <input
              type="text"
              required
              value={formData.semester}
              onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., Fall 2025"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Description (Optional)</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Color</label>
            <input
              type="color"
              value={formData.color}
              onChange={(e) => setFormData({ ...formData, color: e.target.value })}
              className="mt-1 block w-20 h-10 border border-gray-300 rounded-md"
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
              {mutation.isLoading ? 'Saving...' : course ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
