import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";
import React from "react";

interface DeleteLearningPathDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  pathTitle: string;
  onDelete: () => void;
}

const DeleteLearningPathDialog: React.FC<DeleteLearningPathDialogProps> = ({ open, onOpenChange, pathTitle, onDelete }) => (
  <AlertDialog open={open} onOpenChange={onOpenChange}>
    <AlertDialogTrigger asChild>
      <Button variant="ghost" size="sm" className="text-destructive">
        <Trash2 className="w-4 h-4" />
      </Button>
    </AlertDialogTrigger>
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>Delete Learning Path</AlertDialogTitle>
        <AlertDialogDescription>
          Are you sure you want to delete "{pathTitle}"? This action cannot be undone.
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel>Cancel</AlertDialogCancel>
        <AlertDialogAction className="bg-destructive text-destructive-foreground" onClick={onDelete}>
          Delete
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
);

export default DeleteLearningPathDialog;
