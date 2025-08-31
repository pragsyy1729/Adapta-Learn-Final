import React, { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, Upload, FileText, Video, BookOpen } from "lucide-react";
import { Module } from "@/types/module";
import QuizCreationDialog from "./QuizCreationDialog";

interface MaterialManagerDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  module: Module | null;
  onMaterialUploaded?: () => void;
}

interface Chapter {
  id: string;
  title: string;
  materials: {
    visual: any[];
    auditory: any[];
    reading_writing: any[];
  };
}

const MaterialManagerDialog: React.FC<MaterialManagerDialogProps> = ({
  open,
  onOpenChange,
  module,
  onMaterialUploaded
}) => {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(false);
  const [newChapterTitle, setNewChapterTitle] = useState("");
  const [selectedChapter, setSelectedChapter] = useState<string>("");
  const [uploadType, setUploadType] = useState<"pdf_reading" | "mp4_video" | "pdf_usecase">("pdf_reading");
  const [learningStyle, setLearningStyle] = useState<"visual" | "auditory" | "reading_writing">("reading_writing");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadDescription, setUploadDescription] = useState("");
  const [showQuizDialog, setShowQuizDialog] = useState(false);
  const [quizDifficulty, setQuizDifficulty] = useState<"beginner" | "intermediate" | "advanced">("beginner");

  // Load chapters when module changes
  useEffect(() => {
    if (module && open) {
      loadChapters();
    }
  }, [module, open]);

  const loadChapters = async () => {
    if (!module) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/admin/modules/${module.id}/chapters`);
      if (response.ok) {
        const data = await response.json();
        setChapters(data.chapters || []);
      }
    } catch (error) {
      console.error("Error loading chapters:", error);
    } finally {
      setLoading(false);
    }
  };

  const createChapter = async () => {
    if (!module || !newChapterTitle.trim()) return;

    try {
      const response = await fetch(`/api/admin/modules/${module.id}/chapters`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newChapterTitle })
      });

      if (response.ok) {
        setNewChapterTitle("");
        loadChapters();
      }
    } catch (error) {
      console.error("Error creating chapter:", error);
    }
  };

  const uploadMaterial = async () => {
    if (!module || !selectedChapter || !uploadFile) return;

    const formData = new FormData();
    formData.append("file", uploadFile);
    formData.append("material_type", uploadType);
    formData.append("learning_style", learningStyle);
    formData.append("title", uploadTitle || uploadFile.name);
    formData.append("description", uploadDescription);

    try {
      const response = await fetch(`/api/admin/modules/${module.id}/chapters/${selectedChapter}/materials`, {
        method: "POST",
        body: formData
      });

      if (response.ok) {
        setUploadFile(null);
        setUploadTitle("");
        setUploadDescription("");
        loadChapters();
        onMaterialUploaded?.();
      }
    } catch (error) {
      console.error("Error uploading material:", error);
    }
  };

  const createQuiz = async (difficulty: "beginner" | "intermediate" | "advanced") => {
    if (!module || !selectedChapter) return;

    setQuizDifficulty(difficulty);
    setShowQuizDialog(true);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Manage Materials - {module?.title || module?.name}</DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="chapters" className="space-y-4">
          <TabsList>
            <TabsTrigger value="chapters">Chapters</TabsTrigger>
            <TabsTrigger value="materials">Upload Materials</TabsTrigger>
            <TabsTrigger value="quizzes">Create Quizzes</TabsTrigger>
          </TabsList>

          <TabsContent value="chapters" className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="New chapter title"
                value={newChapterTitle}
                onChange={(e) => setNewChapterTitle(e.target.value)}
              />
              <Button onClick={createChapter} disabled={!newChapterTitle.trim()}>
                <Plus className="w-4 h-4 mr-2" />
                Add Chapter
              </Button>
            </div>

            <div className="grid gap-4">
              {chapters.map((chapter) => (
                <Card key={chapter.id}>
                  <CardHeader>
                    <CardTitle className="text-lg">{chapter.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <strong>Visual:</strong> {chapter.materials.visual.length} materials
                      </div>
                      <div>
                        <strong>Auditory:</strong> {chapter.materials.auditory.length} materials
                      </div>
                      <div>
                        <strong>Reading:</strong> {chapter.materials.reading_writing.length} materials
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="materials" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="chapter-select">Select Chapter</Label>
                <Select value={selectedChapter} onValueChange={setSelectedChapter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a chapter" />
                  </SelectTrigger>
                  <SelectContent>
                    {chapters.length === 0 ? (
                      <div className="p-2 text-sm text-muted-foreground">No chapters available</div>
                    ) : (
                      chapters.map((chapter) => (
                        <SelectItem key={chapter.id} value={chapter.id}>
                          {chapter.title}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="material-type">Material Type</Label>
                <Select value={uploadType} onValueChange={(value: any) => setUploadType(value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pdf_reading">
                      <div className="flex items-center">
                        <BookOpen className="w-4 h-4 mr-2" />
                        PDF (Reading Material)
                      </div>
                    </SelectItem>
                    <SelectItem value="mp4_video">
                      <div className="flex items-center">
                        <Video className="w-4 h-4 mr-2" />
                        MP4 Video
                      </div>
                    </SelectItem>
                    <SelectItem value="pdf_usecase">
                      <div className="flex items-center">
                        <FileText className="w-4 h-4 mr-2" />
                        PDF (Use Cases)
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="learning-style">Learning Style</Label>
                <Select value={learningStyle} onValueChange={(value: any) => setLearningStyle(value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="visual">Visual</SelectItem>
                    <SelectItem value="auditory">Auditory</SelectItem>
                    <SelectItem value="reading_writing">Reading/Writing</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="file-upload">File</Label>
                <Input
                  id="file-upload"
                  type="file"
                  accept={
                    uploadType === 'pdf_reading' ? '.pdf' :
                    uploadType === 'mp4_video' ? '.mp4,.avi,.mov,.wmv' :
                    uploadType === 'pdf_usecase' ? '.pdf' : ''
                  }
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  {uploadType === 'pdf_reading' && 'Upload PDF files for reading materials'}
                  {uploadType === 'mp4_video' && 'Upload MP4, AVI, MOV, or WMV video files'}
                  {uploadType === 'pdf_usecase' && 'Upload PDF files containing use cases and examples'}
                </p>
              </div>
            </div>

            <div>
              <Label htmlFor="material-title">Title</Label>
              <Input
                id="material-title"
                value={uploadTitle}
                onChange={(e) => setUploadTitle(e.target.value)}
                placeholder="Material title"
              />
            </div>

            <div>
              <Label htmlFor="material-description">Description</Label>
              <Textarea
                id="material-description"
                value={uploadDescription}
                onChange={(e) => setUploadDescription(e.target.value)}
                placeholder="Material description"
              />
            </div>

            <Button
              onClick={uploadMaterial}
              disabled={!selectedChapter || !uploadFile}
              className="w-full"
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload Material
            </Button>
          </TabsContent>

          <TabsContent value="quizzes" className="space-y-4">
            <div>
              <Label htmlFor="quiz-chapter">Select Chapter</Label>
              <Select value={selectedChapter} onValueChange={setSelectedChapter}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a chapter" />
                </SelectTrigger>
                <SelectContent>
                  {chapters.map((chapter) => (
                    <SelectItem key={chapter.id} value={chapter.id}>
                      {chapter.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <Button
                onClick={() => createQuiz("beginner")}
                disabled={!selectedChapter}
                variant="outline"
              >
                Create Beginner Quiz
              </Button>
              <Button
                onClick={() => createQuiz("intermediate")}
                disabled={!selectedChapter}
                variant="outline"
              >
                Create Intermediate Quiz
              </Button>
              <Button
                onClick={() => createQuiz("advanced")}
                disabled={!selectedChapter}
                variant="outline"
              >
                Create Advanced Quiz
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
      <QuizCreationDialog
        open={showQuizDialog}
        onOpenChange={setShowQuizDialog}
        module={module}
        chapterId={selectedChapter}
        onQuizCreated={onMaterialUploaded}
      />
    </Dialog>
  );
};

export default MaterialManagerDialog;
