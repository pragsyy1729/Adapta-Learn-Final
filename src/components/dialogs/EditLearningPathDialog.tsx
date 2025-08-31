import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { LearningPath } from "@/types";
import React from "react";

interface EditLearningPathDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  editPath: LearningPath | null;
  setEditPath: (lp: LearningPath | null) => void;
  availableModules: any[];
  modulesLoading: boolean;
  modulesError: string | null;
  openModulesDropdownFor: string | null;
  setOpenModulesDropdownFor: (id: string | null) => void;
  editMutation: any;
}

const EditLearningPathDialog: React.FC<EditLearningPathDialogProps> = ({
  open,
  onOpenChange,
  editPath,
  setEditPath,
  availableModules,
  modulesLoading,
  modulesError,
  openModulesDropdownFor,
  setOpenModulesDropdownFor,
  editMutation,
}) => (
  <Dialog open={open} onOpenChange={onOpenChange}>
  <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Edit Learning Path</DialogTitle>
      </DialogHeader>
      {editPath && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="lp-title">Path Title</Label>
              <Input id="lp-title" value={editPath.title || ''} onChange={e => setEditPath({ ...editPath, title: e.target.value })} placeholder="e.g., React Development Track" />
            </div>
            <div>
              <Label htmlFor="lp-duration">Duration (weeks)</Label>
              <Input id="lp-duration" value={editPath.duration || ''} onChange={e => setEditPath({ ...editPath, duration: e.target.value })} placeholder="e.g., 12" />
            </div>
          </div>
          <div>
            <Label htmlFor="lp-description">Description</Label>
            <Textarea id="lp-description" value={editPath.description || ''} onChange={e => setEditPath({ ...editPath, description: e.target.value })} placeholder="Describe what learners will achieve in this path..." className="min-h-[100px]" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="lp-difficulty">Difficulty Level</Label>
              <Select value={editPath.difficulty || ''} onValueChange={val => setEditPath({ ...editPath, difficulty: val })}>
                <SelectTrigger>
                  <SelectValue placeholder="Select difficulty" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Beginner">Beginner</SelectItem>
                  <SelectItem value="Intermediate">Intermediate</SelectItem>
                  <SelectItem value="Advanced">Advanced</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div>
            <Label htmlFor="lp-modules">Modules</Label>
            <div className="relative modules-dropdown">
              <Button
                type="button"
                variant="outline"
                className="w-full flex justify-between items-center modules-dropdown"
                onClick={() => setOpenModulesDropdownFor(editPath.id === openModulesDropdownFor ? null : editPath.id)}
                id="lp-modules"
                aria-haspopup="listbox"
                aria-expanded={openModulesDropdownFor === editPath.id ? 'true' : 'false'}
              >
                {editPath.modules && editPath.modules.length > 0
                  ? availableModules.filter(m => editPath.modules.includes(m.id)).map(m => m.name || m.title).join(", ")
                  : "Select modules"}
                <span className="ml-2">▼</span>
              </Button>
              {openModulesDropdownFor === editPath.id && (
                <div className="absolute z-10 mt-1 w-full bg-popover border rounded shadow-lg max-h-60 overflow-auto modules-dropdown-menu">
                  {modulesLoading && (
                    <div className="p-2 text-sm text-muted-foreground">Loading...</div>
                  )}
                  {modulesError && (
                    <div className="p-2 text-sm text-destructive">Error loading modules</div>
                  )}
                  {!modulesLoading && !modulesError && availableModules.map(mod => (
                    <label key={mod.id} className="flex items-center px-3 py-2 hover:bg-accent cursor-pointer">
                      <input
                        type="checkbox"
                        className="mr-2"
                        checked={editPath.modules?.includes(mod.id) || false}
                        onChange={e => {
                          const selected = new Set(editPath.modules ?? []);
                          if (e.target.checked) {
                            selected.add(mod.id);
                          } else {
                            selected.delete(mod.id);
                          }
                          setEditPath({ ...editPath, modules: Array.from(selected) });
                        }}
                      />
                      {mod.name || mod.title} <span className="ml-1 text-xs text-muted-foreground">({mod.type || 'module'})</span>
                    </label>
                  ))}
                </div>
              )}
            </div>
            <div className="text-xs text-muted-foreground mt-1">Select one or more modules</div>
          </div>
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={() => setEditPath(null)}>Cancel</Button>
            <Button
              onClick={() => editMutation.mutate(editPath)}
              disabled={editMutation.isPending || !editPath.title || !editPath.description || !editPath.difficulty || !editPath.duration || !editPath.department}
            >
              {editMutation.isPending ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </div>
      )}
    </DialogContent>
  </Dialog>
);

export default EditLearningPathDialog;
