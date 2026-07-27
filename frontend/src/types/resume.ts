export interface ResumeMeta {
  id: number;
  file_name: string;
  uploaded_at: string;
  file_path: string;
}

export interface ParsedResume {
  name: string;
  email: string;
  skills: string[];
  projects: string[];
  experience: string[];
  education: string[];
}

export interface ResumeResponse {
  resume: ResumeMeta;
  parsed_resume: ParsedResume;
}