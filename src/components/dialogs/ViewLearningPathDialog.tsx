import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { LearningPath } from "@/types";
import React from "react";

interface ViewLearningPathDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  viewPath: LearningPath | null;
}

const ViewLearningPathDialog: React.FC<ViewLearningPathDialogProps> = ({ open, onOpenChange, viewPath }) => (
  <Dialog open={open} onOpenChange={onOpenChange}>
    <DialogContent className="max-w-lg">
      <DialogHeader>
        <DialogTitle>View Learning Path</DialogTitle>
      </DialogHeader>
      {viewPath && (
        <div className="space-y-2">
          <div><b>Title:</b> {viewPath.title}</div>
          <div><b>Description:</b> {viewPath.description}</div>
          <div><b>Duration:</b> {viewPath.duration}</div>
          <div><b>Difficulty:</b> {viewPath.difficulty}</div>
          <div><b>Department:</b> {viewPath.department}</div>
          <div><b>Status:</b> {viewPath.status}</div>
        </div>
      )}
    </DialogContent>
  </Dialog>
);

export default ViewLearningPathDialog;
