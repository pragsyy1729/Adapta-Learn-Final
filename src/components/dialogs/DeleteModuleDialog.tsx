import React from "react";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";

interface DeleteModuleDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  moduleName: string;
  onDelete: () => void;
}

const DeleteModuleDialog: React.FC<DeleteModuleDialogProps> = ({ open, onOpenChange, moduleName, onDelete }) => (
  <AlertDialog open={open} onOpenChange={onOpenChange}>
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>Delete Module</AlertDialogTitle>
        <AlertDialogDescription>
          Are you sure you want to delete "{moduleName}"? This action cannot be undone.
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

export default DeleteModuleDialog;
