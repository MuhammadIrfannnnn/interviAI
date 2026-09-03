import { useCallback, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  UploadCloud,
  FileText,
  RefreshCcw,
  Loader2,
  GraduationCap,
  Wrench,
  Briefcase,
  Mail,
} from "lucide-react";
import { AxiosError } from "axios";

import { AppLayout } from "../../layouts/AppLayout";
import { Button } from "../../components/ui/Button";
import { resumeService } from "../../services/resumeService";
import { extractErrorMessage } from "../../utils/ExtractErrorMessage";
import type { ResumeResponse } from "../../types/resume";

type Status = "loading" | "empty" | "ready" | "uploading" | "error";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function Resume() {
  const [status, setStatus] = useState<Status>("loading");
  const [resume, setResume] = useState<ResumeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await resumeService.getResume();
        if (!cancelled) {
          setResume(data);
          setStatus("ready");
        }
      } catch (err) {
        if (cancelled) return;
        // A 404 here just means "no resume uploaded yet" — not a real error.
        if (err instanceof AxiosError && err.response?.status === 404) {
          setStatus("empty");
        } else {
          setErrorMessage("Couldn't load your resume. Try refreshing the page.");
          setStatus("error");
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleFile = useCallback(async (file: File) => {
    if (file.type !== "application/pdf" || !file.name.toLowerCase().endsWith(".pdf")) {
      setErrorMessage("Only PDF files are supported.");
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setErrorMessage("File is too large. Maximum size is 5 MB.");
      return;
    }

    if (file.size === 0) {
      setErrorMessage("The selected file is empty.");
      return;
    }

    setErrorMessage(null);
    setStatus("uploading");
    try {
      const data = await resumeService.uploadResume(file);

      // Parsing (via Gemini, per the backend) can take a moment. If the
      // upload response comes back before parsing finishes, parsed_resume
      // (or even the resume metadata block) may be incomplete — poll
      // GET /resume/ briefly until it looks ready rather than rendering
      // with holes or crashing on missing fields.
      const looksParsed = (r: ResumeResponse) =>
        !!r.resume?.file_name &&
        !!r.parsed_resume?.name &&
        Array.isArray(r.parsed_resume?.skills);

      if (looksParsed(data)) {
        setResume(data);
        setStatus("ready");
        return;
      }

      let attempts = 0;
      const maxAttempts = 8;
      const poll = async (): Promise<void> => {
        attempts += 1;
        const fresh = await resumeService.getResume();
        if (looksParsed(fresh) || attempts >= maxAttempts) {
          setResume(fresh);
          setStatus("ready");
          return;
        }
        await new Promise((r) => setTimeout(r, 1500));
        return poll();
      };
      await poll();
    } catch (err) {
      setErrorMessage(extractErrorMessage(err, "Upload failed. Try again."));
      setStatus(resume ? "ready" : "empty");
    }
  }, [resume]);

  const onDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const onFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    e.target.value = "";
  };

  return (
    <AppLayout>
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="mx-auto max-w-2xl"
      >
        <h1 className="text-xl font-semibold text-text-primary">Resume</h1>
        <p className="mt-1 text-sm text-text-secondary">
          Upload your resume so interview questions can be tailored to your background.
        </p>

        {errorMessage && (
          <div className="mt-4 rounded-md border border-danger bg-danger-soft px-4 py-2.5 text-sm text-danger">
            {errorMessage}
          </div>
        )}

        <div className="mt-6">
          {status === "loading" && (
            <div className="flex h-48 items-center justify-center">
              <Loader2 className="h-5 w-5 animate-spin text-text-muted" />
            </div>
          )}

          {(status === "empty" || status === "uploading") && (
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={onDrop}
              onClick={() => status !== "uploading" && fileInputRef.current?.click()}
              className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-16 text-center transition-colors duration-150 ${
                isDragging ? "border-accent bg-accent-soft" : "border-border hover:border-border-strong"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                className="hidden"
                onChange={onFileInputChange}
              />
              {status === "uploading" ? (
                <>
                  <Loader2 className="h-8 w-8 animate-spin text-accent" />
                  <p className="mt-4 text-sm text-text-secondary">Uploading and parsing your resume…</p>
                </>
              ) : (
                <>
                  <UploadCloud className="h-8 w-8 text-text-muted" />
                  <p className="mt-4 text-sm font-medium text-text-primary">
                    Drop your resume here, or click to browse
                  </p>
                  <p className="mt-1 text-xs text-text-muted">PDF only</p>
                </>
              )}
            </div>
          )}

          {status === "ready" && resume && (
            <AnimatePresence mode="wait">
              <motion.div
                key="resume-view"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col gap-4"
              >
                <div className="flex items-center justify-between rounded-lg border border-border bg-surface p-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-md bg-surface-raised">
                      <FileText className="h-4 w-4 text-text-secondary" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-text-primary">
                        {resume.resume?.file_name || "—"}
                      </p>
                      <p className="text-xs text-text-muted">
                        {resume.resume?.updated_at
                          ? `Updated ${formatDate(resume.resume.updated_at)}`
                          : resume.resume?.uploaded_at
                          ? `Uploaded ${formatDate(resume.resume.uploaded_at)}`
                          : "Upload date unavailable"}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="application/pdf"
                      className="hidden"
                      onChange={onFileInputChange}
                    />
                    <Button variant="ghost" onClick={() => fileInputRef.current?.click()}>
                      <RefreshCcw className="h-4 w-4" />
                      Replace
                    </Button>
                  </div>
                </div>

                <div className="rounded-lg border border-border bg-surface p-5">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-text-primary">
                      {resume.parsed_resume?.name || "—"}
                    </p>
                  </div>
                  <div className="mt-1 flex items-center gap-1.5 text-xs text-text-muted">
                    <Mail className="h-3.5 w-3.5" />
                    {resume.parsed_resume?.email || "—"}
                  </div>

                  {(resume.parsed_resume?.skills?.length ?? 0) > 0 && (
                    <div className="mt-5">
                      <div className="flex items-center gap-1.5 text-xs uppercase tracking-wide text-text-muted">
                        <Wrench className="h-3.5 w-3.5" />
                        Skills
                      </div>
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {resume.parsed_resume.skills.map((skill) => (
                          <span
                            key={skill}
                            className="rounded-full border border-border-subtle bg-surface-raised px-2.5 py-1 text-xs text-text-secondary"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {(resume.parsed_resume?.projects?.length ?? 0) > 0 && (
                    <div className="mt-5">
                      <div className="flex items-center gap-1.5 text-xs uppercase tracking-wide text-text-muted">
                        <Briefcase className="h-3.5 w-3.5" />
                        Projects
                      </div>
                      <ul className="mt-2 flex flex-col gap-1.5">
                        {resume.parsed_resume.projects.map((project) => (
                          <li key={project} className="text-sm text-text-secondary">
                            {project}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {(resume.parsed_resume?.education?.length ?? 0) > 0 && (
                    <div className="mt-5">
                      <div className="flex items-center gap-1.5 text-xs uppercase tracking-wide text-text-muted">
                        <GraduationCap className="h-3.5 w-3.5" />
                        Education
                      </div>
                      <ul className="mt-2 flex flex-col gap-1.5">
                        {resume.parsed_resume.education.map((edu) => (
                          <li key={edu} className="text-sm text-text-secondary">
                            {edu}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </motion.div>
            </AnimatePresence>
          )}
        </div>
      </motion.div>
    </AppLayout>
  );
}
