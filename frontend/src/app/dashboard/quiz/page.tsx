'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiClient } from '@/lib/api';
import { FiBook, FiCheck } from 'react-icons/fi';
import { Course, Topic } from '@/types';

export default function QuizPage() {
  const [selectedCourse, setSelectedCourse] = useState<string>('');
  const [selectedTopic, setSelectedTopic] = useState<string>('');
  const [quizStarted, setQuizStarted] = useState(false);
  const [quizData, setQuizData] = useState({
    score: 0,
    questionCount: 10,
    difficulty: 'medium' as 'easy' | 'medium' | 'hard',
  });

  const { data: courses } = useQuery<Course[]>('courses', () => apiClient.getCourses());

  const { data: topics } = useQuery<Topic[]>(
    ['topics', selectedCourse],
    () => apiClient.getTopics(selectedCourse),
    { enabled: !!selectedCourse }
  );

  const queryClient = useQueryClient();
  const updateMasteryMutation = useMutation(
    (data: any) => apiClient.updateMastery(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('masteryOverview');
        queryClient.invalidateQueries(['courseMastery', selectedCourse]);
        queryClient.invalidateQueries(['topicMastery', selectedTopic]);
      },
    }
  );

  const handleStartQuiz = () => {
    if (!selectedTopic) {
      alert('Please select a topic');
      return;
    }
    setQuizStarted(true);
  };

  const handleSubmitQuiz = () => {
    const data = {
      topic_id: selectedTopic,
      quiz_score: quizData.score,
      question_count: quizData.questionCount,
      difficulty_level: quizData.difficulty,
    };

    updateMasteryMutation.mutate(data, {
      onSuccess: () => {
        alert('Quiz submitted successfully! Your mastery has been updated.');
        setQuizStarted(false);
        setQuizData({ score: 0, questionCount: 10, difficulty: 'medium' });
      },
    });
  };

  if (!quizStarted) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Quiz & Practice</h1>
          <p className="mt-2 text-sm text-gray-600">
            Take a quiz to update your mastery level
          </p>
        </div>

        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Setup Your Quiz</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Course
              </label>
              <select
                value={selectedCourse}
                onChange={(e) => {
                  setSelectedCourse(e.target.value);
                  setSelectedTopic('');
                }}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">Choose a course...</option>
                {courses?.map((course) => (
                  <option key={course.id} value={course.id}>
                    {course.name} ({course.code})
                  </option>
                ))}
              </select>
            </div>

            {selectedCourse && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Topic
                </label>
                <select
                  value={selectedTopic}
                  onChange={(e) => setSelectedTopic(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">Choose a topic...</option>
                  {topics?.map((topic) => (
                    <option key={topic.id} value={topic.id}>
                      {topic.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {selectedTopic && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Number of Questions
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={quizData.questionCount}
                    onChange={(e) =>
                      setQuizData({ ...quizData, questionCount: parseInt(e.target.value) })
                    }
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Difficulty Level
                  </label>
                  <select
                    value={quizData.difficulty}
                    onChange={(e) =>
                      setQuizData({
                        ...quizData,
                        difficulty: e.target.value as 'easy' | 'medium' | 'hard',
                      })
                    }
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>

                <button
                  onClick={handleStartQuiz}
                  className="w-full mt-4 px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
                >
                  Start Quiz
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Take Quiz</h1>
        <p className="mt-2 text-sm text-gray-600">
          After completing the quiz, enter your score below
        </p>
      </div>

      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-medium text-blue-900">Quiz Information</h3>
          <ul className="mt-2 space-y-1 text-sm text-blue-700">
            <li>Total Questions: {quizData.questionCount}</li>
            <li>Difficulty: {quizData.difficulty}</li>
          </ul>
        </div>

        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            This is a simplified quiz interface. In a production environment, this would display
            actual quiz questions. For now, complete your quiz externally and enter your results below.
          </p>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Score (0-100)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={quizData.score}
              onChange={(e) =>
                setQuizData({ ...quizData, score: parseFloat(e.target.value) })
              }
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., 85"
            />
          </div>

          <div className="flex space-x-3">
            <button
              onClick={() => setQuizStarted(false)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmitQuiz}
              disabled={updateMasteryMutation.isLoading}
              className="flex-1 px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
            >
              {updateMasteryMutation.isLoading ? 'Submitting...' : 'Submit Quiz'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
