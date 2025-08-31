import React from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

import type { Module, Chapter } from "@/types/module";

interface EditModuleDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  module: Module | null;
  setModule: (mod: Module | null) => void;
  onSave: () => void;
  isSaving: boolean;
}

const EditModuleDialog: React.FC<EditModuleDialogProps> = ({ open, onOpenChange, module, setModule, onSave, isSaving }) => (
  <Dialog open={open} onOpenChange={onOpenChange}>
    <DialogContent className="max-w-md max-h-[80vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{module && !module.id ? 'Add Module' : 'Edit Module'}</DialogTitle>
      </DialogHeader>
      {module && (
        <div className="space-y-4">
          <div>
            <Label htmlFor="mod-name">Name</Label>
            <Input id="mod-name" value={module.name} onChange={e => setModule({ ...module, name: e.target.value })} />
          </div>
          <div>
            <Label htmlFor="mod-description">Description</Label>
            <Textarea id="mod-description" value={module.description} onChange={e => setModule({ ...module, description: e.target.value })} />
          </div>

          <div>
            <Label>Chapters</Label>
            <ul className="space-y-2">
              {module.chapters && module.chapters.length > 0 ? module.chapters.map((ch, idx) => (
                <li key={idx} className="border rounded p-2">
                  <details>
                    <summary className="cursor-pointer font-semibold">{ch.name || `Chapter ${idx + 1}`}</summary>
                    <div className="mt-2 space-y-2">
                      <Input
                        className="mb-1"
                        placeholder="Chapter Name"
                        value={ch.name}
                        onChange={e => {
                          const chapters = [...module.chapters];
                          chapters[idx] = { ...chapters[idx], name: e.target.value };
                          setModule({ ...module, chapters });
                        }}
                      />
                      <Input
                        className="mb-1"
                        placeholder="Material"
                        value={ch.material}
                        onChange={e => {
                          const chapters = [...module.chapters];
                          chapters[idx] = { ...chapters[idx], material: e.target.value };
                          setModule({ ...module, chapters });
                        }}
                      />
                      <div>
                        <Label htmlFor={`chapter-type-${idx}`}>Type</Label>
                        <select
                          id={`chapter-type-${idx}`}
                          className="mb-1 w-full border rounded px-2 py-1"
                          value={ch.type}
                          onChange={e => {
                            const chapters = [...module.chapters];
                            chapters[idx] = { ...chapters[idx], type: e.target.value };
                            setModule({ ...module, chapters });
                          }}
                        >
                          <option value="">Select type</option>
                          <option value="video">Video</option>
                          <option value="text">Text</option>
                          <option value="audio">Audio</option>
                          <option value="slides">Slides</option>
                          <option value="assessment">Assessment</option>
                          <option value="resource">Resource</option>
                        </select>
                      </div>
                      <div>
                        <Label htmlFor={`chapter-file-${idx}`}>Upload File</Label>
                        <input
                          id={`chapter-file-${idx}`}
                          type="file"
                          accept="*/*,video/mp4"
                          className="mb-1 w-full border rounded px-2 py-1"
                          onChange={e => {
                            const file = e.target.files && e.target.files[0];
                            if (file) {
                              const chapters = [...module.chapters];
                              chapters[idx] = { ...chapters[idx], file };
                              setModule({ ...module, chapters });
                            }
                          }}
                        />
                        {ch.file && (
                          <div className="text-xs text-muted-foreground mt-1">Selected: {ch.file.name}</div>
                        )}
                      </div>
                      <Button size="sm" variant="destructive" onClick={() => {
                        const chapters = module.chapters.filter((_, i) => i !== idx);
                        setModule({ ...module, chapters });
                      }}>Delete</Button>
                    </div>
                  </details>
                </li>
              )) : <li>No chapters</li>}
            </ul>
            <Button
              size="sm"
              className="mt-2"
              onClick={() => setModule({ ...module, chapters: [...(module.chapters || []), { name: '', material: '', type: '' }] })}
            >Add Chapter</Button>
          </div>
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={() => setModule(null)}>Cancel</Button>
            <Button onClick={onSave} disabled={isSaving}>{isSaving ? "Saving..." : "Save"}</Button>
          </div>
        </div>
      )}
    </DialogContent>
  </Dialog>
);

export default EditModuleDialog;
