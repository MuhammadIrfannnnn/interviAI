import { useState, useRef, useEffect, useMemo } from "react";

const ROLE_SUGGESTIONS = [
  // Technology
  "Software Engineer",
  "Frontend Developer",
  "Backend Developer",
  "Full Stack Developer",
  "Data Analyst",
  "Data Scientist",
  "Data Engineer",
  "Machine Learning Engineer",
  "DevOps Engineer",
  "Cloud Engineer",
  "QA Engineer",
  "Cybersecurity Analyst",
  "Systems Administrator",
  "Network Engineer",
  "Database Administrator",
  "IT Support Specialist",
  // Business
  "Business Analyst",
  "Project Manager",
  "Product Manager",
  "Operations Manager",
  "Management Consultant",
  "Strategy Consultant",
  "Business Development Manager",
  "Program Manager",
  // Finance
  "Financial Analyst",
  "Investment Analyst",
  "Accountant",
  "Auditor",
  "Financial Manager",
  "Investment Banker",
  "Risk Analyst",
  "Credit Analyst",
  // Marketing
  "Marketing Manager",
  "Digital Marketing Specialist",
  "SEO Specialist",
  "Brand Manager",
  "Content Strategist",
  "Social Media Manager",
  "Marketing Analyst",
  // Sales
  "Sales Representative",
  "Sales Manager",
  "Account Executive",
  "Customer Success Manager",
  // Human Resources
  "HR Manager",
  "Human Resources Specialist",
  "Recruiter",
  "Talent Acquisition Specialist",
  "Learning and Development Specialist",
  // Healthcare
  "Doctor",
  "Physician",
  "Registered Nurse",
  "Nurse Practitioner",
  "Pharmacist",
  "Dentist",
  "Physiotherapist",
  "Medical Assistant",
  "Clinical Research Associate",
  "Healthcare Administrator",
  // Engineering (non-software)
  "Mechanical Engineer",
  "Electrical Engineer",
  "Civil Engineer",
  "Chemical Engineer",
  "Industrial Engineer",
  "Aerospace Engineer",
  "Biomedical Engineer",
  "Environmental Engineer",
  // Science
  "Research Scientist",
  "Biologist",
  "Chemist",
  "Physicist",
  "Laboratory Technician",
  // Education
  "Teacher",
  "Lecturer",
  "Professor",
  "School Counselor",
  "Curriculum Developer",
  "Education Coordinator",
  // Legal
  "Lawyer",
  "Attorney",
  "Paralegal",
  "Legal Assistant",
  "Compliance Officer",
  // Design / Creative
  "UI Designer",
  "UX Designer",
  "Product Designer",
  "Graphic Designer",
  "Interior Designer",
  "Fashion Designer",
  "Journalist",
  "Copywriter",
  "Editor",
  "Photographer",
  "Video Producer",
  "Animator",
  // Architecture
  "Architect",
  "Urban Planner",
  "Landscape Architect",
  // Hospitality
  "Hotel Manager",
  "Restaurant Manager",
  "Event Manager",
  "Travel Consultant",
  // Public / Nonprofit
  "Policy Analyst",
  "Public Relations Specialist",
  "Nonprofit Coordinator",
  "Community Outreach Coordinator",
  // Retail
  "Store Manager",
  "Retail Manager",
  "Merchandising Specialist",
  "Buyer",
  // Trades
  "Electrician",
  "Plumber",
  "Carpenter",
  "Welder",
  "HVAC Technician",
];

interface RoleComboboxProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  error?: string;
  placeholder?: string;
}

export function RoleCombobox({
  value,
  onChange,
  disabled,
  error,
  placeholder = "e.g. Backend Developer",
}: RoleComboboxProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [highlightIndex, setHighlightIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  const filtered = useMemo(() => {
    if (!value.trim()) return []; // don't flood with suggestions on empty input
    const lower = value.toLowerCase();
    return ROLE_SUGGESTIONS.filter((role) =>
      role.toLowerCase().includes(lower)
    );
  }, [value]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Scroll highlighted item into view
  useEffect(() => {
    if (highlightIndex >= 0 && listRef.current) {
      const item = listRef.current.children[highlightIndex] as HTMLElement | undefined;
      item?.scrollIntoView({ block: "nearest" });
    }
  }, [highlightIndex]);

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!isOpen) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setIsOpen(true);
        setHighlightIndex(0);
      }
      return;
    }

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setHighlightIndex((prev) => Math.min(prev + 1, filtered.length - 1));
        break;
      case "ArrowUp":
        e.preventDefault();
        setHighlightIndex((prev) => Math.max(prev - 1, 0));
        break;
      case "Enter":
        e.preventDefault();
        if (highlightIndex >= 0 && highlightIndex < filtered.length) {
          onChange(filtered[highlightIndex]);
          setIsOpen(false);
        }
        break;
      case "Escape":
        e.preventDefault();
        setIsOpen(false);
        break;
    }
  }

  function selectSuggestion(role: string) {
    onChange(role);
    setIsOpen(false);
    inputRef.current?.focus();
  }

  const showDropdown = isOpen && filtered.length > 0 && !disabled;

  return (
    <div ref={containerRef} className="relative flex flex-col gap-1.5">
      <label className="text-sm font-medium text-text-secondary">Role</label>
      <input
        ref={inputRef}
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          setIsOpen(true);
          setHighlightIndex(0);
        }}
        onFocus={() => {
          setIsOpen(true);
          setHighlightIndex(0);
        }}
        onKeyDown={handleKeyDown}
        onBlur={() => {
          // Small delay so click on suggestion registers
          setTimeout(() => setIsOpen(false), 150);
        }}
        disabled={disabled}
        placeholder={placeholder}
        autoComplete="off"
        role="combobox"
        aria-expanded={showDropdown}
        aria-autocomplete="list"
        className={`h-10 rounded-md border bg-surface px-3 text-sm text-text-primary
          placeholder:text-text-muted outline-none transition-colors duration-150
          focus:border-accent focus:ring-1 focus:ring-accent disabled:opacity-50
          ${error ? "border-danger" : "border-border"}`}
      />
      {error && <p className="text-xs text-danger">{error}</p>}

      {showDropdown && (
        <ul
          ref={listRef}
          role="listbox"
          className="absolute top-full z-10 mt-1 max-h-48 w-full overflow-y-auto rounded-md border border-border bg-surface shadow-md"
        >
          {filtered.map((role, index) => (
            <li
              key={role}
              role="option"
              aria-selected={index === highlightIndex}
              onMouseDown={(e) => {
                e.preventDefault();
                selectSuggestion(role);
              }}
              onMouseEnter={() => setHighlightIndex(index)}
              className={`cursor-pointer px-3 py-2 text-sm transition-colors duration-100 ${
                index === highlightIndex
                  ? "bg-accent-soft text-accent"
                  : "text-text-primary hover:bg-accent-soft"
              }`}
            >
              {role}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
