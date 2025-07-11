import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { useState, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { createNewProject } from "@/features/projects/projectSlice"; // Your thunk

interface DialogBoxProps {
  trigger?: ReactNode;
}

export default function DialogBox ({trigger}: DialogBoxProps) {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [nameError, setNameError] = useState("");

  const handleCreateProject = async () => {
    const trimmedName = newProjectName.trim();

    // Basic validation
    if (!trimmedName) {
      setNameError("Project name is required");
      return;
    }
    if (trimmedName.length < 3) {
      setNameError("Project name must be at least 3 characters");
      return;
    }
    if (trimmedName.length > 50) {
      setNameError("Project name must be under 50 characters");
      return;
    }
    if (!/^[a-zA-Z0-9 ]+$/.test(trimmedName)) {
      setNameError("Only letters, numbers, and spaces are allowed");
      return;
    }
    
    const result = await dispatch(createNewProject(newProjectName) as any);
    const newProject = result.payload;

    if (newProject && newProject._id){
      setDialogOpen(false);
      setNewProjectName("");
      navigate(`/viewer/${newProject._id}`);
    }
  }

    return (
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
                {trigger ? trigger : <Button>+ Create Project</Button>}
            </DialogTrigger>

            <DialogContent className="z-[9999] bg-white rounded-lg p-6">
                <DialogHeader>
                <DialogTitle>New Project</DialogTitle>
                </DialogHeader>
                <div className="space-y-2">
                <Input
                    placeholder="Enter project name"
                    value={newProjectName}
                    onChange={(e) => {
                    setNewProjectName(e.target.value);
                    setNameError(""); // Clear previous error
                    }}
                    className={nameError ? "border-red-500" : ""}
                />
                {nameError && (
                    <p className="text-sm text-red-600">{nameError}</p>
                )}
                </div>
                <DialogFooter className="mt-4">
                <Button onClick={handleCreateProject}>Create</Button>
                </DialogFooter>
            </DialogContent>
            </Dialog>
    );
}
