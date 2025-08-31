export interface LearningPath {
  id: string;
  title: string;
  description: string;
  modules?: string[];
  duration?: string;
  difficulty?: string;
  enrolledUsers?: number;
  status?: string;
  department?: string;
}
