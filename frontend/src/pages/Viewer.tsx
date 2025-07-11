import MainLayout from "../components/layout/MainLayout";
import ThreeCanvas from "../components/viewer/ThreeCanvas";
import MessageList from "../components/chat/MessageList";
import PromptInput from "../components/chat/PromptInput";
import { useNavigate, useParams } from "react-router-dom";
import { useDispatch } from "react-redux";
import { useEffect } from "react";
import  { setActiveProject } from "../features/projects/projectSlice"
import  { setActiveProjectId } from "../features/chat/chatSlice"
import { useProjects } from "@/hooks/useProjects";
import { Button } from "@/components/ui/button";
import DialogBox from "@/components/project/ProjectDialog";

export default function Viewer () {
  const { projectId } = useParams<{ projectId: string }>();
  const dispatch = useDispatch();
  const { projects } = useProjects();
  const navigate = useNavigate();

  useEffect(() => {
    if (projectId) {
      dispatch(setActiveProject(projectId));
      dispatch(setActiveProjectId(projectId));
    } else if (projects.length > 0) {
      navigate(`/viewer/${projects[0]._id}`);
    }
  }, [projectId, projects]);

  if (!projectId && projects.length === 0) {
    return (
      <MainLayout>
        <div className="flex flex-col h-full items-center justify-center text-center space-y-4">
          <h2 className="text-xl font-semibold text-white">No projects yet</h2>
          <p className="text-white">Start by creating your first 3D project!</p>
          
          <DialogBox 
          trigger = {<Button className="w-full text-white">+ Create Project</Button>} />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="flex flex-col h-full">
        <div className="flex-1">
          <ThreeCanvas projectId={projectId!} />
        </div>
        <div className="border-t border-gray-300 mt-2 p-2 bg-gray-100">
          <MessageList projectId={projectId!} />
          <PromptInput projectId={projectId!} />
        </div>
      </div>
    </MainLayout>
  );
};
