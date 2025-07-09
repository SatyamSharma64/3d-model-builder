import type { Project } from "../../types/project";

interface Props {
  project: Project;
  onOpen: (id: string) => void;
}

export default function ProjectCard({ project, onOpen }: Props) {
  return (
    <div
      className="p-4 bg-white shadow rounded cursor-pointer hover:bg-gray-100"
      onClick={() => onOpen(project._id)}
    >
      <h3 className="text-lg font-bold">{project.name}</h3>
    </div>
  );
}
