export interface Chapter {
  name: string;
  material: string;
  type: string;
  file?: File;
}

export interface Module {
  id: string;
  name?: string;
  title?: string;
  description: string;
  chapters?: Chapter[];
  chapter_count?: number;
  learning_path_id?: string;
  duration_hours?: number;
  order?: number;
}
